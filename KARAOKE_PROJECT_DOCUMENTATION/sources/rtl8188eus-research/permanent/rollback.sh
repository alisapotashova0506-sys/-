#!/bin/bash
# Run through builtin Wi-Fi SSH or a local console. Removes only this USB setup.
set -eu
systemctl disable --now rtl8188eu-bind.service || true
rm -f -- /etc/udev/rules.d/80-rtl8188eu-bind.rules
udevadm control --reload-rules
nmcli connection delete uuid 67e9bd92-5f2a-4bab-9645-4afe89fcfc97 || true
rm -f -- /etc/systemd/system/rtl8188eu-bind.service
rm -f -- /usr/local/libexec/rtl8188eu-bind.py
rm -f -- /etc/modprobe.d/8188eu-power.conf
rm -f -- /lib/modules/6.6.44-current-sunxi64/updates/drivers/net/wireless/8188eu.ko
depmod -a 6.6.44-current-sunxi64
systemctl daemon-reload
if [ -d /sys/module/8188eu ]; then
  if ! rmmod 8188eu; then
    echo 'Boot files restored. Reboot to return USB to rtl8xxxu.'
    exit 0
  fi
fi
modprobe rtl8xxxu
python3 - <<'PY'
from pathlib import Path
for link in Path('/sys/bus/usb/devices').glob('*:*'):
    try:
        path = link.resolve(strict=True)
        ids = tuple((path.parent / name).read_text().strip() for name in ('idVendor', 'idProduct'))
        if ids != ('0bda', '8179'):
            continue
        current = (path / 'driver').resolve().name if (path / 'driver').exists() else None
        if current is None:
            Path('/sys/bus/usb/drivers/rtl8xxxu/bind').write_text(path.name + '\n')
        elif current != 'rtl8xxxu':
            raise RuntimeError('Unexpected USB driver: ' + current)
        print('USB restored to rtl8xxxu:', path.name)
    except FileNotFoundError:
        continue
PY
