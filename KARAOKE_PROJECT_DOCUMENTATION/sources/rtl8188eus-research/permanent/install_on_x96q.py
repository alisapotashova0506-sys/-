"""Install the already tested USB module and persist only its dedicated AP profile."""
import configparser
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

RELEASE = "6.6.44-current-sunxi64"
SHA256 = "d1c545d580901e3bd85504d7c970a729383aaf75b3217724a4940c3b4e353bc3"
USB = "wlxf0b040f7f699"
PROFILE = "67e9bd92-5f2a-4bab-9645-4afe89fcfc97"
TIMER = "rtl8188eus-rollback-ca123d7e5cc7.timer"
SOURCE = Path("/root/rtl8188eus-build-xs4977k0/8188eu-test.ko")
MODULE = Path("/lib/modules") / RELEASE / "updates/drivers/net/wireless/8188eu.ko"
HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, LC_ALL="C")
FILES = [
    (HERE / "rtl8188eu-bind.py", Path("/usr/local/libexec/rtl8188eu-bind.py"), 0o755),
    (HERE / "rtl8188eu-bind.service", Path("/etc/systemd/system/rtl8188eu-bind.service"), 0o644),
    (HERE / "8188eu-power.conf", Path("/etc/modprobe.d/8188eu-power.conf"), 0o644),
    (HERE / "80-rtl8188eu-bind.rules", Path("/etc/udev/rules.d/80-rtl8188eu-bind.rules"), 0o644),
    (SOURCE, MODULE, 0o644),
]
CHANGES = {
    "connection.id": "KARAOKE_USB_AP",
    "connection.autoconnect": "yes",
    "connection.autoconnect-priority": "100",
    "802-11-wireless.ssid": "KARAOKE",
    "802-11-wireless.cloned-mac-address": "permanent",
    "802-11-wireless-security.psk": "12345678",
    "ipv4.addresses": "192.168.100.1/24",
}


def run(*args, check=True, timeout=30):
    result = subprocess.run(args, text=True, capture_output=True, env=ENV, timeout=timeout)
    if check and result.returncode:
        # Do not print command arguments, which can include a WPA password.
        raise RuntimeError(args[0] + " failed: " + result.stdout + result.stderr)
    return result


def setting(key, uuid=PROFILE):
    return run("nmcli", "--escape", "no", "--show-secrets", "-g", key,
               "connection", "show", "uuid", uuid).stdout.rstrip("\n")


def profile_files(uuid):
    found = []
    for directory in ("/etc/NetworkManager/system-connections", "/usr/lib/NetworkManager/system-connections"):
        for file in Path(directory).glob("*"):
            if not file.is_file():
                continue
            parser = configparser.RawConfigParser(strict=False)
            try:
                parser.read(file)
                if parser.get("connection", "uuid", fallback="") == uuid:
                    found.append(file)
            except (configparser.Error, UnicodeError):
                continue
    return found


def check_ssh():
    fields = os.environ.get("SSH_CONNECTION", "").split()
    if len(fields) != 4 or fields[2] != "192.168.1.102":
        raise RuntimeError("Use SSH to 192.168.1.102 from your home network")
    routes = json.loads(run("ip", "-j", "-4", "route", "get", fields[0],
                            "from", fields[2]).stdout)
    if not routes or any(route.get("dev") != "wlan0" for route in routes):
        raise RuntimeError("Return the computer to your home Wi-Fi and reconnect SSH to 192.168.1.102")


def modify(values):
    arguments = ["nmcli", "connection", "modify", "uuid", PROFILE]
    for key, value in values.items():
        arguments.extend((key, value))
    run(*arguments)


def main():
    if os.geteuid() != 0 or platform.machine() != "aarch64" or platform.release() != RELEASE:
        raise RuntimeError("Requires root and ARM64 kernel " + RELEASE)
    check_ssh()
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA256:
        raise RuntimeError("Tested module checksum differs")
    device = Path("/sys/class/net") / USB / "device"
    if (device / "driver").resolve(strict=True).name != "8188eu":
        raise RuntimeError("The USB adapter must still use the tested 8188eu driver")
    parent = device.resolve(strict=True).parent
    if tuple((parent / name).read_text().strip() for name in ("idVendor", "idProduct")) != ("0bda", "8179"):
        raise RuntimeError("USB identity differs")
    active = run("nmcli", "-g", "GENERAL.CON-UUID", "device", "show", USB).stdout.strip()
    if active != PROFILE or setting("802-11-wireless.mode") != "ap":
        raise RuntimeError("The expected temporary USB AP profile is not active")
    if setting("802-11-wireless.ssid") != "KARAOKE_USB_TEST" or profile_files(PROFILE):
        raise RuntimeError("The trial profile has already changed or been saved; stop for review")
    builtin = run("nmcli", "-g", "GENERAL.CON-UUID", "device", "show", "wlan0").stdout.strip()
    if not builtin or not profile_files(builtin) or setting("connection.autoconnect", builtin) != "yes":
        raise RuntimeError("The builtin Wi-Fi profile must be saved with autoconnect=yes before a reboot test")
    for source, target, mode in FILES:
        if target.exists() or target.is_symlink():
            raise RuntimeError("Refusing to overwrite existing file: " + str(target))
        if not source.is_file():
            raise RuntimeError("Missing installer input: " + str(source))
    run("systemctl", "is-active", "--quiet", TIMER)
    run("systemctl", "restart", TIMER)
    old = {key: setting(key) for key in CHANGES}
    old_device_auto = run("nmcli", "-g", "GENERAL.AUTOCONNECT", "device", "show", USB).stdout.strip()
    if old_device_auto not in ("yes", "no"):
        raise RuntimeError("Cannot capture the USB device autoconnect flag")
    backup = Path(tempfile.mkdtemp(prefix="karaoke-usb-install-", dir="/root"))
    backup.chmod(0o700)
    (backup / "profile-before.json").write_text(json.dumps(old, indent=2) + "\n")
    (backup / "profile-before.json").chmod(0o600)
    rollback = backup / "rollback.sh"
    shutil.copyfile(HERE / "rollback.sh", rollback)
    rollback.chmod(0o700)
    print("Backup and rollback:", backup, flush=True)
    created = []
    profile_changed = False
    try:
        print("Installing tested driver and USB boot service", flush=True)
        for source, target, mode in FILES:
            target.parent.mkdir(parents=True, exist_ok=True)
            created.append(target)
            shutil.copyfile(source, target)
            target.chmod(mode)
        run("depmod", "-a", RELEASE)
        selected = Path(run("modinfo", "-n", "8188eu").stdout.strip())
        if selected.resolve() != MODULE.resolve():
            raise RuntimeError("modprobe would select another module")
        run("systemd-analyze", "verify", "/etc/systemd/system/rtl8188eu-bind.service")
        run("udevadm", "control", "--reload-rules")
        run("systemctl", "daemon-reload")
        run("systemctl", "enable", "rtl8188eu-bind.service")
        run("systemctl", "start", "rtl8188eu-bind.service", timeout=100)
        result = run("systemctl", "show", "rtl8188eu-bind.service", "-p", "Result", "--value").stdout.strip()
        if result != "success":
            raise RuntimeError("USB boot service validation failed: " + result)
        print("Saving KARAOKE, WPA2 and 192.168.100.1", flush=True)
        profile_changed = True
        modify(CHANGES)
        saved = profile_files(PROFILE)
        if len(saved) != 1:
            raise RuntimeError("The AP profile was not saved to exactly one keyfile")
        saved[0].chmod(0o600)
        run("nmcli", "device", "set", USB, "autoconnect", "yes")
        run("nmcli", "--wait", "45", "connection", "up", "uuid", PROFILE, "ifname", USB, timeout=55)
        check_ssh()
        addresses = json.loads(run("ip", "-j", "-4", "address", "show", "dev", USB).stdout)
        if not any(a.get("local") == "192.168.100.1" for d in addresses for a in d.get("addr_info", [])):
            raise RuntimeError("The USB AP address was not applied")
        for key, expected in CHANGES.items():
            if setting(key) != expected:
                raise RuntimeError("Saved setting differs: " + key)
        run("systemctl", "is-enabled", "--quiet", "rtl8188eu-bind.service")
        os.sync()
        # Cancel the experiment's timer only after all persistent pieces passed.
        run("systemctl", "stop", TIMER)
        print("INSTALL COMPLETE", flush=True)
        print("SSID: KARAOKE; password: 12345678; URL: http://192.168.100.1:8080/", flush=True)
        print("Saved profile:", saved[0], flush=True)
        print("Rollback: bash", rollback, flush=True)
        print("A reboot test remains to be done.", flush=True)
    except BaseException:
        print("Installation failed; restoring the previous trial settings", flush=True)
        def cleanup(label, action):
            try:
                action()
            except BaseException as error:
                print("Cleanup needs attention (" + label + "):", error, flush=True)
        if profile_changed:
            cleanup("profile settings", lambda: modify(old))
            cleanup("trial AP activation", lambda: run("nmcli", "--wait", "40", "connection", "up", "uuid", PROFILE, "ifname", USB, timeout=50))
        cleanup("USB autoconnect", lambda: run("nmcli", "device", "set", USB, "autoconnect", old_device_auto))
        cleanup("boot service", lambda: run("systemctl", "disable", "--now", "rtl8188eu-bind.service", check=False))
        for target in reversed(created):
            cleanup(str(target), lambda path=target: path.unlink(missing_ok=True))
        cleanup("module index", lambda: run("depmod", "-a", RELEASE))
        cleanup("udev rules", lambda: run("udevadm", "control", "--reload-rules"))
        cleanup("systemd configuration", lambda: run("systemctl", "daemon-reload"))
        print("The USB trial rollback timer remains available; backup:", backup, flush=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR:", error, flush=True)
        raise SystemExit(1)
