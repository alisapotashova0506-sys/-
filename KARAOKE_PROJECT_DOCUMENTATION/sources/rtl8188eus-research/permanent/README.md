# Proposed permanent RTL8188EU selection

These files are prepared locally for review. Nothing here has been installed or
executed on the X96Q. The parent workflow handles installation and persistence of
the already working USB AP profile after the network preferences are confirmed.

The binder selects the only USB interface with ID `0bda:8179`. It deliberately
does not match the network MAC, which NetworkManager may randomize while scanning.
It checks the running kernel, accepts only an unbound interface, `rtl8xxxu`, or
`8188eu`, and serializes its runs with a lock in `/run/lock`. An existing `8188eu`
binding is left in place. Otherwise the installed module checksum and ordinary
`modprobe` must succeed before the old driver is detached. A later failure tries
to restore `rtl8xxxu` for that same interface. No forced loading/unloading occurs.

The binder changes no NetworkManager profiles, device autoconnect flags, IP
settings, firewall rules, regulatory settings, or other adapters. NetworkManager
can automatically activate the separately saved USB AP profile when its device
is recreated. The built-in wlan0 connection remains outside this script.

Proposed installed paths:

| Prepared file | Installed path |
| --- | --- |
| `rtl8188eu-bind.py` | `/usr/local/libexec/rtl8188eu-bind.py` |
| `rtl8188eu-bind.service` | `/etc/systemd/system/rtl8188eu-bind.service` |
| `8188eu-power.conf` | `/etc/modprobe.d/8188eu-power.conf` |
| `80-rtl8188eu-bind.rules` (optional) | `/etc/udev/rules.d/80-rtl8188eu-bind.rules` |

Use the native-built module from
`/root/rtl8188eus-build-xs4977k0/8188eu-test.ko`, installed as
`/lib/modules/6.6.44-current-sunxi64/updates/drivers/net/wireless/8188eu.ko`.
Its SHA256 must be
`d1c545d580901e3bd85504d7c970a729383aaf75b3217724a4940c3b4e353bc3`.
The binder checks this checksum before loading it. Run `depmod` for that release
after installation. No kernel, headers, initramfs, blacklist or softdep changes
are part of this proposal. A different kernel needs a separately rebuilt and
validated module and an updated guard; this module will not be forced into it.

The boot unit runs after NetworkManager. It also handles an old driver already
loaded from initramfs. Enabling the optional udev rule starts the same unit for
USB interface add events, including unplug/replug. It does not run the binder
inside a udev worker. The oneshot unit intentionally has no `RemainAfterExit`, so
a later device-add event can start it again. A successful unit is normally
inactive after its command exits. Without the optional rule, restart the unit
manually after a hotplug if necessary.

Useful operator commands after installation:

```sh
systemctl restart rtl8188eu-bind.service
systemctl show rtl8188eu-bind.service -p Result -p ExecMainStatus
journalctl -u rtl8188eu-bind.service -b --no-pager
```

The installer must verify the module path selected by `modinfo -n 8188eu`,
preserve any pre-existing files at the proposed paths, and validate the unit
before enabling it. Reloading udev rules is needed only if the optional rule is
installed. Keep the trial rollback timer until the module, binder, saved AP
profile and saved built-in client profile have all been checked. Cancel that
timer as the final installation step. Arrange a reboot test separately.

## Rollback and uninstall

Run operator actions through the built-in wlan0 connection. Disable the boot
unit and remove the optional hotplug rule before changing USB binding:

```sh
systemctl disable --now rtl8188eu-bind.service
rm -f /etc/udev/rules.d/80-rtl8188eu-bind.rules
udevadm control --reload-rules
```

Stop only the USB AP profile if desired, using its exact UUID. Leave the built-in
client and the existing `KARAOKE_SYSTEM` profile alone. After checking the current
USB interface name and parent USB ID, restore the original driver. The example
below requires replacing the placeholder with that verified USB interface ID
(such as `1-1:1.0`), not a network-interface name:

```sh
USB_INTERFACE='<verified USB interface ID>'
modprobe rtl8xxxu
printf '%s\n' "$USB_INTERFACE" > /sys/bus/usb/drivers/8188eu/unbind
printf '%s\n' "$USB_INTERFACE" > /sys/bus/usb/drivers/rtl8xxxu/bind
```

The vendor disconnect can reset the USB device. If it has already returned to
`rtl8xxxu`, skip the last bind write. Never unbind an unexpected driver. After
confirming the old binding, remove only files installed by this proposal (or
restore their backups), then rebuild the module index:

```sh
rm -f /etc/systemd/system/rtl8188eu-bind.service
rm -f /usr/local/libexec/rtl8188eu-bind.py
rm -f /etc/modprobe.d/8188eu-power.conf
rm -f /lib/modules/6.6.44-current-sunxi64/updates/drivers/net/wireless/8188eu.ko
depmod -a 6.6.44-current-sunxi64
systemctl daemon-reload
```

No broad driver unload or deletion of the original rtl8xxxu module is needed.
The new module may remain loaded and unbound in RAM until reboot. Any saved USB
AP profile is managed separately; remove only its exact UUID if it is no longer
wanted.
