#!/bin/bash
# Run manually on the X96Q, never automatically from the documentation package.
# Writes a private snapshot on the mounted HDD; does not restart services or change networks.
set -euo pipefail
if [ "$(id -u)" != 0 ]; then
  echo 'Run in the root SSH session on the X96Q.' >&2
  exit 1
fi
mountpoint -q /mnt/usb_disk || { echo 'HDD is not mounted; stopped.' >&2; exit 1; }
command -v python3 >/dev/null
python3 - <<'PY'
import shutil
if shutil.disk_usage('/mnt/usb_disk').free < 256 * 1024 * 1024:
    raise SystemExit('Need at least 256 MiB free on HDD for this settings/code snapshot.')
PY
snapshot_parent=/mnt/usb_disk/.karaoke-documentation
if [ -L "$snapshot_parent" ]; then
  echo 'Unexpected symlink at snapshot directory.' >&2
  exit 1
fi
mkdir -p "$snapshot_parent"
chmod 700 "$snapshot_parent"
snapshot_dir=$(mktemp -d "$snapshot_parent/snapshot-$(date +%Y%m%d-%H%M%S)-XXXXXX")
chmod 700 "$snapshot_dir"
list="$snapshot_dir/file-list.txt"
: > "$list"
for item in \
  root/karaoke \
  usr/local/bin/play_karaoke.sh \
  usr/local/libexec/rtl8188eu-bind.py \
  etc/systemd/system \
  etc/NetworkManager \
  etc/fstab etc/asound.conf root/.asoundrc \
  etc/modprobe.d etc/modules-load.d etc/udev/rules.d \
  etc/armbian-release \
  boot/armbianEnv.txt boot/boot.cmd boot/boot.scr boot/overlay-user \
  "boot/config-$(uname -r)" \
  "lib/modules/$(uname -r)/updates/drivers/net/wireless/8188eu.ko"
do
  if [ -e "/$item" ] || [ -L "/$item" ]; then
    printf '%s\n' "$item" >> "$list"
  fi
done
# Do not follow symlinks or cross nested mounted media. Explicit exclusions also
# protect the application-only intent if those folders are not mounts later.
tar --one-file-system \
  --exclude='root/karaoke/karaoke_media' \
  --exclude='root/karaoke/posters' \
  --exclude='root/karaoke/fonsound' \
  -czf "$snapshot_dir/files.tar.gz" -C / -T "$list"
python3 - "$snapshot_dir" <<'PY'
from pathlib import Path
import sqlite3
import sys
folder=Path(sys.argv[1])
source=Path('/data/karaoke/db/karaoke.db')
if source.is_file():
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as live:
        with sqlite3.connect(folder/'working-karaoke.db') as backup:
            live.backup(backup)
            if backup.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:
                raise RuntimeError('SQLite integrity check failed')
else:
    (folder/'DB-NOT-FOUND.txt').write_text('Expected /data/karaoke/db/karaoke.db not found. Inspect DB_NAME before restoring.\n')
PY
uname -a > "$snapshot_dir/kernel.txt"
dpkg-query -W -f='${binary:Package}\t${Version}\t${db:Status-Status}\n' > "$snapshot_dir/packages.tsv"
python3 -m pip freeze > "$snapshot_dir/python-packages.txt" 2>&1 || true
findmnt > "$snapshot_dir/mounts.txt"
lsblk -f > "$snapshot_dir/disks.txt"
nmcli device status > "$snapshot_dir/network-devices.txt"
ip -br -4 addr > "$snapshot_dir/addresses.txt"
cat /proc/asound/cards /proc/asound/pcm > "$snapshot_dir/audio.txt" 2>&1 || true
for unit in karaoke-server.service karaoke-wifi-monitor.service rtl8188eu-bind.service bgutil-pot.service zapret.service
do
  systemctl cat "$unit" > "$snapshot_dir/$unit.txt" 2>&1 || true
  systemctl show "$unit" -p Result -p ExecMainStatus -p ExecStart -p ExecStartPre -p WorkingDirectory > "$snapshot_dir/$unit-state.txt" 2>&1 || true
done
journalctl -b -u karaoke-wifi-monitor.service -n 120 --no-pager > "$snapshot_dir/wifi-journal.txt" 2>&1 || true
cat > "$snapshot_dir/READ_ME.txt" <<'TXT'
Private device code/settings snapshot. Contains possible Wi-Fi passwords.
Not a full bootable eMMC image. Does not contain the video/poster/BGM collection
or /opt tools. files.tar.gz may include a raw historical database; the separately
created working-karaoke.db is the consistent backup of the app's expected DB_NAME.
No automatic service/network changes were made by this collector.
Do not restore all system settings blindly onto another box.
TXT
tar -tzf "$snapshot_dir/files.tar.gz" >/dev/null
snapshot_archive="$snapshot_dir.tar.gz"
tar -czf "$snapshot_archive" -C "$snapshot_parent" "$(basename "$snapshot_dir")"
chmod 600 "$snapshot_archive"
tar -tzf "$snapshot_archive" >/dev/null
sha256sum "$snapshot_archive"
printf 'Snapshot saved on HDD: %s\n' "$snapshot_archive"
