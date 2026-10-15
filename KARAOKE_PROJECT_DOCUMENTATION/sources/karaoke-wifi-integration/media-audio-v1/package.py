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
PROJECT = HERE.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    from parts import patch
    before = (HERE / 'app-before.py').read_bytes()
    after = patch(before)
    assert after == (PROJECT / 'updated/app.py').read_bytes()
    sources = ('karaoke_media_optimizer.py', 'karaoke_audio_output.py', 'media_optimizer.html')
    files = {name: (PROJECT / 'updated' / name).read_bytes() for name in sources}
    manifest = dict(app_before=sha(before), app_after=sha(after),
                    files={name: sha(value) for name, value in files.items()},
                    unchanged={name: sha((PROJECT/'updated'/name).read_bytes()) for name in (
                        'wifi/network.py', 'wifi/setup-qr.png', 'wifi/control_qr.py', 'wifi/setup.html')})
    files.update({'install.py': (HERE / 'install.py').read_bytes(),
                  'parts.py': (HERE / 'parts.py').read_bytes(),
                  'manifest.json': json.dumps(manifest, indent=2).encode()})
    for name, data in files.items():
        if name.endswith('.py'):
            ast.parse(data, feature_version=(3, 11))
    ast.parse(after, feature_version=(3, 11))
    (HERE / 'manifest.json').write_bytes(files['manifest.json'])
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name, data in sorted(files.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode, member.mtime = len(data), 0o600, 0
            archive.addfile(member, io.BytesIO(data))
    payload = lzma.compress(buffer.getvalue(), preset=9)
    (HERE / 'media-audio-v1.tar.xz').write_bytes(payload)
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
folder = Path(tempfile.mkdtemp(prefix='karaoke-media-audio-update-', dir='/root'))
folder.chmod(0o700)
with tarfile.open(fileobj=io.BytesIO(lzma.decompress(data)), mode='r:') as archive:
    for entry in archive:
        name = Path(entry.name)
        if not entry.isfile() or name.is_absolute() or '..' in name.parts or entry.size > 256000:
            raise RuntimeError('Неожиданный файл комплекта.')
        target = folder / name
        target.write_bytes(archive.extractfile(entry).read())
        target.chmod(0o600)
unit = 'karaoke-media-audio-' + str(time.time_ns())
print('Журнал обновления:', unit, flush=True)
result = subprocess.run(['systemd-run', '--unit=' + unit, '--wait', '--collect',
                         '/usr/bin/python3', '-u', str(folder / 'install.py')])
subprocess.run(['journalctl', '-u', unit, '--no-pager', '-o', 'cat'])
raise SystemExit(result.returncode)
PY
'''.replace('PAYLOAD', encoded).replace('CHECKSUM', sha(payload))
    ast.parse(loader.split("python3 - <<'PY'\n", 1)[1].rsplit('\nPY', 1)[0], feature_version=(3, 11))
    (HERE / 'paste-update.sh').write_text(loader)
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(payload)), mode='r:') as archive:
        decoded = {e.name: archive.extractfile(e).read() for e in archive}
    assert decoded == files
    print('App SHA:', sha(after))
    print('Bundle SHA:', sha(payload))
    print('Bundle bytes:', len(payload), 'paste bytes:', len(loader.encode()))


if __name__ == '__main__':
    main()
