"""Build the inline SSH installer; no download from an artifact server."""
import ast
import base64
import hashlib
import io
import json
import lzma
from pathlib import Path
import tarfile
import textwrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    from parts import patch
    before = (HERE / 'app-before.py').read_bytes()
    after = patch(before)
    assert after == (ROOT / 'updated/app.py').read_bytes()
    files = {'install_on_x96q.py': (HERE / 'install_on_x96q.py').read_bytes(),
             'parts.py': (HERE / 'parts.py').read_bytes(),
             'wifi/control_qr.py': (ROOT / 'updated/wifi/control_qr.py').read_bytes()}
    for path in sorted((ROOT / 'updated/wifi/vendor').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            files[str(path.relative_to(ROOT / 'updated'))] = path.read_bytes()
    manifest = {'version': 5, 'app_before': sha(before), 'app_after': sha(after),
                'new_files': {key: sha(value) for key, value in files.items() if key.startswith('wifi/')}}
    files['manifest.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode()
    for name, data in files.items():
        if name.endswith('.py'):
            ast.parse(data, feature_version=(3, 11))
    (HERE / 'manifest.json').write_bytes(files['manifest.json'])
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), 0o600, 0
            archive.addfile(info, io.BytesIO(data))
    payload = lzma.compress(buffer.getvalue(), preset=9)
    (HERE / 'control-qr-v5.tar.xz').write_bytes(payload)
    encoded = '\n'.join(textwrap.wrap(base64.b64encode(payload).decode(), 100))
    loader = '''python3 - <<'PY'
import base64, hashlib, io, lzma, subprocess, tarfile, tempfile, time
from pathlib import Path
encoded = """
PAYLOAD
"""
data = base64.b64decode(encoded)
if hashlib.sha256(data).hexdigest() != 'CHECKSUM':
    raise RuntimeError('Данные повреждены. Изменения не внесены.')
folder = Path(tempfile.mkdtemp(prefix='karaoke-control-qr-update-', dir='/root'))
folder.chmod(0o700)
with tarfile.open(fileobj=io.BytesIO(lzma.decompress(data)), mode='r:') as archive:
    for entry in archive.getmembers():
        name = Path(entry.name)
        if not entry.isfile() or name.is_absolute() or '..' in name.parts or entry.size > 256000:
            raise RuntimeError('Неожиданный файл комплекта.')
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.extractfile(entry).read())
        target.chmod(0o600)
unit = 'karaoke-control-qr-' + str(time.time_ns())
print('Журнал обновления:', unit, flush=True)
result = subprocess.run(['systemd-run', '--unit=' + unit, '--wait', '--collect',
                         '/usr/bin/python3', '-u', str(folder / 'install_on_x96q.py')])
subprocess.run(['journalctl', '-u', unit, '--no-pager', '-o', 'cat'])
raise SystemExit(result.returncode)
PY
'''.replace('PAYLOAD', encoded).replace('CHECKSUM', sha(payload))
    (HERE / 'paste-update.sh').write_text(loader)
    restored = {}
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(payload)), mode='r:') as archive:
        for entry in archive:
            restored[entry.name] = archive.extractfile(entry).read()
    assert restored == files
    ast.parse(loader.split("python3 - <<'PY'\n", 1)[1].rsplit('\nPY', 1)[0], feature_version=(3, 11))
    print('App SHA256:', sha(after))
    print('Bundle:', len(payload), 'bytes; paste:', len(loader.encode()), 'bytes')
    print('Bundle SHA256:', sha(payload))


if __name__ == '__main__':
    main()
