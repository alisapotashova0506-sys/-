import base64
import hashlib
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import time

encoded = r"""
__ENCODED_ARCHIVE__
"""


def unpack(parent):
    data = base64.b85decode(''.join(encoded.split()))
    expected = '868abf1a5736c622848da8ad7fe48fe0ad94449319db1e08258175acb2d950a3'
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError('Переданные данные повреждены. Установка не начата.')
    folder = Path(tempfile.mkdtemp(prefix='karaoke-wifi-update-', dir=parent))
    folder.chmod(0o700)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:xz') as archive:
        for member in archive.getmembers():
            name = Path(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts:
                raise RuntimeError('Неверный файл в комплекте. Установка не начата.')
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
            target.chmod(0o600)
    return folder


def main():
    ssh = os.environ.get('SSH_CONNECTION', '')
    if os.geteuid() != 0 or len(ssh.split()) != 4 or ssh.split()[2] != '192.168.1.102':
        raise RuntimeError('Выполните команду в SSH root@192.168.1.102.')
    folder = unpack('/root')
    unit = 'karaoke-wifi-update-' + str(time.time_ns())
    print('Комплект проверен:', folder, flush=True)
    print('Журнал установки:', unit, flush=True)
    result = subprocess.run([
        'systemd-run', '--unit=' + unit, '--wait', '--collect',
        '--setenv=SSH_CONNECTION=' + ssh,
        '/usr/bin/python3', '-u', str(folder / 'install.py')])
    subprocess.run(['journalctl', '-u', unit, '--no-pager', '-o', 'cat'])
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
