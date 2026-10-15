#!/usr/bin/python3
"""Select 8188eu for the single 0bda:8179 USB adapter; leave NM profiles alone."""
import fcntl
import hashlib
from pathlib import Path
import platform
import subprocess
import sys

RELEASE = "6.6.44-current-sunxi64"
MODULE_SHA256 = "d1c545d580901e3bd85504d7c970a729383aaf75b3217724a4940c3b4e353bc3"
USB_BUS = Path("/sys/bus/usb/devices")
DRIVERS = Path("/sys/bus/usb/drivers")
OLD, NEW = "rtl8xxxu", "8188eu"


def run(*arguments):
    subprocess.run(arguments, check=True, timeout=20)


def identity(path):
    return tuple((path.parent / name).read_text().strip().lower()
                 for name in ("idVendor", "idProduct"))


def target():
    matches = []
    for link in USB_BUS.glob("*:*"):
        try:
            path = link.resolve(strict=True)
            if identity(path) == ("0bda", "8179"):
                matches.append(path)
        except FileNotFoundError:
            continue  # A device may disappear while sysfs is being enumerated.
    if len(matches) > 1:
        raise RuntimeError("Multiple 0bda:8179 USB interfaces; refusing an ambiguous switch")
    return matches[0] if matches else None


def driver(path):
    try:
        return (path / "driver").resolve(strict=True).name
    except FileNotFoundError:
        return None


def bind(path, name):
    if identity(path) != ("0bda", "8179"):
        raise RuntimeError("USB identity changed")
    (DRIVERS / name / "bind").write_text(path.name + "\n")


def unbind(path, name):
    if identity(path) != ("0bda", "8179") or driver(path) != name:
        raise RuntimeError("USB identity or driver changed before unbind")
    (DRIVERS / name / "unbind").write_text(path.name + "\n")


def report(path):
    run("udevadm", "settle", "--timeout=10")
    interfaces = sorted(item.name for item in (path / "net").glob("*"))
    if driver(path) != NEW or len(interfaces) != 1:
        raise RuntimeError("8188eu did not expose exactly one USB network interface")
    print("USB", path.name, "uses", NEW, "on", interfaces[0], flush=True)


def restore_old(path):
    if identity(path) != ("0bda", "8179"):
        raise RuntimeError("USB identity changed during rollback")
    if driver(path) == OLD:
        return
    if driver(path) not in (None, NEW):
        raise RuntimeError("Unexpected USB driver during rollback")
    run("modprobe", OLD)  # Ensure the fallback exists before detaching anything.
    if driver(path) == NEW:
        unbind(path, NEW)
    # Vendor disconnect can reset the USB device and restore binding itself.
    if driver(path) is None:
        try:
            bind(path, OLD)
        except OSError:
            if driver(path) != OLD:
                raise
    if driver(path) != OLD:
        raise RuntimeError("USB rollback did not restore rtl8xxxu")
    print("USB restored to rtl8xxxu", flush=True)


def main():
    if platform.machine() != "aarch64" or platform.release() != RELEASE:
        raise RuntimeError("Requires ARM64 kernel " + RELEASE + "; no USB changes made")
    with Path("/run/lock/rtl8188eu-bind.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = target()
        if path is None:
            print("No 0bda:8179 USB interface present; no action", flush=True)
            return
        current = driver(path)
        if current == NEW:
            report(path)
            return
        if current not in (None, OLD):
            raise RuntimeError("Unexpected USB driver: " + repr(current))
        module = Path("/lib/modules") / RELEASE / "updates/drivers/net/wireless/8188eu.ko"
        with module.open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() != MODULE_SHA256:
                raise RuntimeError("Installed module checksum differs; old binding preserved")
        run("modprobe", NEW)  # Loading failure must leave the old binding intact.
        try:
            current = driver(path)
            if current == OLD:
                unbind(path, OLD)
            elif current not in (None, NEW):
                raise RuntimeError("USB driver changed unexpectedly")
            if driver(path) is None:
                bind(path, NEW)
            report(path)
        except BaseException:
            try:
                restore_old(path)
            except Exception as error:
                print("USB rollback failed:", error, file=sys.stderr, flush=True)
            raise


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR:", error, file=sys.stderr, flush=True)
        raise SystemExit(1)
