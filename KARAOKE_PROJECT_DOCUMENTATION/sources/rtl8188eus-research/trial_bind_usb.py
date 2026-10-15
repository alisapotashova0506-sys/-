"""Temporarily bind one RTL8188EU USB adapter and report its AP capability.

Run through the built-in wlan0 SSH connection after loading 8188eu separately.
This script creates no AP, installs nothing, and leaves a 45-minute USB rollback
timer active after a successful trial.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

RELEASE = "6.6.44-current-sunxi64"
SSH_ADDRESS = "192.168.1.102"
BUILTIN_INTERFACE = "wlan0"
OLD_DRIVER = "rtl8xxxu"
NEW_DRIVER = "8188eu"
USB_DRIVERS = Path("/sys/bus/usb/drivers")
ENV = dict(os.environ, LC_ALL="C")


def command(arguments, *, check=True, timeout=15):
    result = subprocess.run(arguments, text=True, capture_output=True,
                            env=ENV, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError("Command failed: " + repr(arguments) + "\n" +
                           result.stdout + result.stderr)
    return result


def bound_driver(usb_path):
    try:
        return (usb_path / "driver").resolve(strict=True).name
    except FileNotFoundError:
        return None


def check_usb_identity(usb_path):
    if ((usb_path.parent / "idVendor").read_text().strip().lower(),
            (usb_path.parent / "idProduct").read_text().strip().lower()) != ("0bda", "8179"):
        raise RuntimeError("USB identity is not 0bda:8179")


def check_ssh_route(client):
    addresses = json.loads(command(["ip", "-j", "-4", "address", "show",
                                   "dev", BUILTIN_INTERFACE]).stdout)
    if not any(address.get("local") == SSH_ADDRESS
               for interface in addresses
               for address in interface.get("addr_info", [])):
        raise RuntimeError("wlan0 no longer has " + SSH_ADDRESS)
    routes = json.loads(command(["ip", "-j", "-4", "route", "get", client,
                                "from", SSH_ADDRESS]).stdout)
    if not routes or any(route.get("dev") != BUILTIN_INTERFACE for route in routes):
        raise RuntimeError("The SSH client route does not use wlan0")


def wait_for_usb_interface(usb_path, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        names = sorted(path.name for path in (usb_path / "net").glob("*"))
        if len(names) > 1:
            raise RuntimeError("Unexpected multiple USB network interfaces: " + repr(names))
        if names:
            return names[0]
        time.sleep(0.1)
    raise RuntimeError("No network interface appeared for the USB adapter")


def suppress_usb_autoconnect(usb_path):
    # The recreated device may reach NetworkManager after its kernel netdev does.
    # Change only this device's runtime flag; leave every saved profile unchanged.
    deadline = time.monotonic() + 12
    detail = "USB network interface is not ready"
    while time.monotonic() < deadline:
        try:
            interface = wait_for_usb_interface(usb_path, timeout=2)
        except RuntimeError as error:
            detail = str(error)
            continue
        result = command(["nmcli", "--wait", "2", "device", "set", interface,
                          "autoconnect", "no"], check=False, timeout=4)
        detail = result.stderr
        if result.returncode == 0:
            state_result = command(["nmcli", "-g", "GENERAL.STATE", "device", "show",
                                    interface], check=False)
            if state_result.returncode == 0:
                break
        time.sleep(0.1)
    else:
        raise RuntimeError("Could not disable USB device autoconnect: " + detail)
    state_text = state_result.stdout.strip()
    state = int(state_text.split()[0])
    if 40 <= state <= 100:
        # Counter an activation that started before the runtime flag was set.
        command(["nmcli", "--wait", "5", "device", "disconnect", interface], timeout=8)
    return wait_for_usb_interface(usb_path)


ROLLBACK_PROGRAM = r'''"""Restore only the USB interface captured by the trial."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
STATE = json.loads((HERE / "state.json").read_text())

def driver(path):
    try:
        return (path / "driver").resolve(strict=True).name
    except FileNotFoundError:
        return None

def restore():
    path = (Path("/sys/bus/usb/devices") / STATE["usb_interface"]).resolve(strict=True)
    if ((path.parent / "idVendor").read_text().strip().lower(),
            (path.parent / "idProduct").read_text().strip().lower()) != ("0bda", "8179"):
        raise RuntimeError("USB identity changed; refusing to touch another device")
    current = driver(path)
    if current == "8188eu":
        Path("/sys/bus/usb/drivers/8188eu/unbind").write_text(STATE["usb_interface"] + "\n")
    elif current not in (None, "rtl8xxxu"):
        raise RuntimeError("Unexpected USB driver: " + repr(current))
    # Vendor disconnect resets the USB device, which may already restore binding.
    current = driver(path)
    if current is None:
        try:
            Path("/sys/bus/usb/drivers/rtl8xxxu/bind").write_text(STATE["usb_interface"] + "\n")
        except OSError:
            if driver(path) != "rtl8xxxu":
                raise
    if driver(path) != "rtl8xxxu":
        raise RuntimeError("USB did not return to rtl8xxxu")
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        names = sorted(item.name for item in (path / "net").glob("*"))
        if len(names) == 1:
            result = subprocess.run(
                ["nmcli", "--wait", "2", "device", "set", names[0],
                 "autoconnect", STATE["old_autoconnect"]],
                capture_output=True, text=True, timeout=4,
                env=dict(os.environ, LC_ALL="C"))
            if result.returncode == 0:
                print("USB restored:", names[0], "driver rtl8xxxu", flush=True)
                return
        time.sleep(0.1)
    raise RuntimeError("USB driver restored, but its NetworkManager flag was not restored")

with (HERE / "rollback.lock").open("a") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    with (HERE / "rollback.log").open("a", buffering=1) as log:
        try:
            restore()
            log.write("USB rollback completed\n")
        except Exception as error:
            log.write("USB rollback failed: " + repr(error) + "\n")
            raise
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usb-interface-name", default="wlxf0b040f7f699")
    parser.add_argument("--ssh-client", help="IPv4 SSH client, if SSH_CONNECTION is unavailable")
    parser.add_argument("--work-parent", default="/root")
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise RuntimeError("Run as root through the wlan0 SSH connection")
    if platform.machine() != "aarch64" or platform.release() != RELEASE:
        raise RuntimeError("This trial requires the expected ARM64 kernel " + RELEASE)
    for tool in ("ip", "iw", "nmcli", "systemd-run", "systemctl"):
        if not shutil.which(tool):
            raise RuntimeError("Missing command: " + tool)
    connection = os.environ.get("SSH_CONNECTION", "").split()
    if connection and (len(connection) != 4 or connection[2] != SSH_ADDRESS):
        raise RuntimeError("SSH must be connected to " + SSH_ADDRESS)
    client = args.ssh_client or (connection[0] if connection else None)
    if client is None or ipaddress.ip_address(client).version != 4:
        raise RuntimeError("An IPv4 SSH client is required for the wlan0 route check")
    check_ssh_route(client)
    if args.usb_interface_name == BUILTIN_INTERFACE:
        raise RuntimeError("Refusing to operate on wlan0")
    net_path = Path("/sys/class/net") / args.usb_interface_name
    usb_path = (net_path / "device").resolve(strict=True)
    usb_interface = usb_path.name
    if not re.fullmatch(r"\d+-\d+(?:\.\d+)*:\d+\.\d+", usb_interface):
        raise RuntimeError("The network interface is not a USB interface")
    check_usb_identity(usb_path)
    if bound_driver(usb_path) != OLD_DRIVER:
        raise RuntimeError("The USB interface must initially use rtl8xxxu")
    if not Path("/sys/module/8188eu").is_dir() or not (USB_DRIVERS / NEW_DRIVER / "bind").exists():
        raise RuntimeError("Load the verified 8188eu module before running this trial")
    for option in ("rtw_power_mgnt", "rtw_enusbss", "rtw_ips_mode"):
        if (Path("/sys/module/8188eu/parameters") / option).read_text().strip() != "0":
            raise RuntimeError("Expected 8188eu parameter " + option + "=0")
    old_autoconnect = command(["nmcli", "-g", "GENERAL.AUTOCONNECT", "device",
                               "show", args.usb_interface_name]).stdout.strip()
    if old_autoconnect not in ("yes", "no"):
        raise RuntimeError("Cannot capture the USB device's runtime autoconnect flag")
    old_state = command(["nmcli", "-g", "GENERAL.STATE", "device", "show",
                         args.usb_interface_name]).stdout.strip()
    if 40 <= int(old_state.split()[0]) <= 100:
        raise RuntimeError("The USB adapter must already be disconnected for this trial")
    lab = Path(tempfile.mkdtemp(prefix="rtl8188eus-trial-",
                                dir=Path(args.work_parent).resolve()))
    lab.chmod(0o700)
    state = {"usb_interface": usb_interface, "old_autoconnect": old_autoconnect}
    (lab / "state.json").write_text(json.dumps(state) + "\n")
    rollback = lab / "rollback_usb.py"
    rollback.write_text(ROLLBACK_PROGRAM)
    rollback.chmod(0o600)
    unit = "rtl8188eus-rollback-" + uuid.uuid4().hex[:12]
    timer = unit + ".timer"
    print("Rollback script:", rollback, flush=True)
    print("Rollback log:", lab / "rollback.log", flush=True)
    command(["systemd-run", "--unit=" + unit, "--on-active=45min",
             "--timer-property=AccuracySec=1s", "--property=Type=oneshot",
             "--property=TimeoutStartSec=60s", "--collect",
             str(Path(sys.executable).resolve()), str(rollback)])
    try:
        command(["systemctl", "is-active", "--quiet", timer])
        print("45-minute USB rollback timer:", timer, flush=True)
        check_ssh_route(client)
        (USB_DRIVERS / OLD_DRIVER / "unbind").write_text(usb_interface + "\n")
        (USB_DRIVERS / NEW_DRIVER / "bind").write_text(usb_interface + "\n")
        if bound_driver(usb_path) != NEW_DRIVER:
            raise RuntimeError("The USB interface did not bind to 8188eu")
        if shutil.which("udevadm"):
            command(["udevadm", "settle", "--timeout=10"], timeout=12)
        interface = wait_for_usb_interface(usb_path)
        interface = suppress_usb_autoconnect(usb_path)
        phy = (Path("/sys/class/net") / interface / "phy80211").resolve(strict=True).name
        if not re.fullmatch(r"phy\d+", phy):
            raise RuntimeError("Unexpected USB wiphy name")
        info = command(["iw", "phy", phy, "info"]).stdout
        modes = []
        in_modes = False
        for line in info.splitlines():
            if line.strip() == "Supported interface modes:":
                in_modes = True
            elif in_modes:
                match = re.fullmatch(r"\s*\*\s*(.+?)\s*", line)
                if not match:
                    break
                modes.append(match[1])
        if "AP" not in modes:
            raise RuntimeError("The USB wiphy does not advertise AP support: " + repr(modes))
        check_ssh_route(client)
        print("USB interface:", interface, "driver:", NEW_DRIVER, "wiphy:", phy)
        print("Supported interface modes:", ", ".join(modes))
        print("AP supported: yes; no AP was started")
        print("wlan0 remains", SSH_ADDRESS, "and carries the SSH client route")
        print("Rollback timer remains active:", timer)
        print("Immediate USB rollback: python3", rollback)
    except BaseException:
        print("Trial failed; restoring only the USB adapter now", flush=True)
        try:
            result = subprocess.run([sys.executable, str(rollback)], env=ENV, timeout=70)
            if result.returncode:
                raise RuntimeError("Rollback exited with status " + str(result.returncode))
            command(["systemctl", "stop", timer], check=False)
        except Exception as error:
            print("USB rollback error:", error, file=sys.stderr)
            print("USB rollback needs attention; see", lab / "rollback.log", file=sys.stderr)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR:", error, file=sys.stderr)
        raise SystemExit(1)
