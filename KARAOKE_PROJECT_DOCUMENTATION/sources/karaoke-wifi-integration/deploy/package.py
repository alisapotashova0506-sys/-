"""Build a checksum-guarded device update from the uploaded Wi-Fi snapshot."""
import ast
import base64
import difflib
import gzip
import hashlib
import io
import json
import lzma
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / 'current'
UPDATED = ROOT / 'updated'
KIT = ROOT / 'deploy' / 'kit'
KIT.mkdir(exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(source, target, before=None):
    relative = 'payload/' + target.lstrip('/')
    output = KIT / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output)
    return dict(source=relative, target=target, before=sha(before) if before else None,
                sha256=sha(source), mode=0o644)


files = []
for name in ('monitor.py', 'connect-worker.py', 'setup.html', 'network.py',
             '__init__.py', 'captive.py', 'setup-qr.png'):
    original = CURRENT / 'wifi' / name
    files.append(add(UPDATED / 'wifi' / name, '/root/karaoke/wifi/' + name,
                     original if original.exists() else None))
files.append(add(ROOT / 'deploy/30-usb-fallback.conf',
                 '/etc/systemd/system/karaoke-wifi-monitor.service.d/30-usb-fallback.conf'))
files.append(add(ROOT / 'captive-support/karaoke-setup.conf',
                 '/etc/NetworkManager/dnsmasq-shared.d/99-karaoke-setup.conf'))
patch = ''.join(difflib.unified_diff(
    (CURRENT / 'app.py').read_text().splitlines(keepends=True),
    (UPDATED / 'app.py').read_text().splitlines(keepends=True),
    fromfile='a/app.py', tofile='b/app.py'))
(KIT / 'app.patch').write_text(patch)
manifest = dict(app_before=sha(CURRENT / 'app.py'), app_after=sha(UPDATED / 'app.py'),
                qr_sha256=sha(UPDATED / 'wifi/setup-qr.png'), files=files)
(KIT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
shutil.copyfile(ROOT / 'deploy/install.py', KIT / 'install.py')

# Validate the exact patch that will run on the device, never importing app.py.
check = ROOT / 'deploy/patch-check'
check.mkdir(exist_ok=True)
shutil.copyfile(CURRENT / 'app.py', check / 'app.py')
subprocess.run(['patch', '--batch', '--forward', '-p1', '-d', str(check),
                '-i', str(KIT / 'app.patch')], check=True, capture_output=True)
assert sha(check / 'app.py') == manifest['app_after']
ast.parse((check / 'app.py').read_text())
for entry in files:
    if entry['source'].endswith('.py'):
        ast.parse((KIT / entry['source']).read_text())

stream = io.BytesIO()
with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as archive:
    for path in sorted(KIT.rglob('*')):
        if not path.is_file():
            continue
        info = tarfile.TarInfo(path.relative_to(KIT).as_posix())
        info.size = path.stat().st_size
        info.mode = 0o600
        archive.addfile(info, io.BytesIO(path.read_bytes()))
raw = stream.getvalue()
variants = [('tar.gz', gzip.compress(raw, mtime=0), base64.b64encode, 'base64'),
            ('tar.xz', lzma.compress(raw, preset=9), base64.b85encode, 'base85')]
for extension, data, encode, encoding in variants:
    destination = ROOT / 'deploy' / ('karaoke-wifi-update.' + extension)
    destination.write_bytes(data)
    encoded = encode(data).decode('ascii')
    destination.with_suffix(destination.suffix + '.' + encoding).write_text(
        '\n'.join(encoded[i:i + 100] for i in range(0, len(encoded), 100)) + '\n')
    destination.with_suffix(destination.suffix + '.sha256').write_text(
        hashlib.sha256(data).hexdigest() + '  ' + destination.name + '\n')
    print(destination.name, len(data), 'bytes;', encoding, len(encoded), 'characters;',
          hashlib.sha256(data).hexdigest())
print('Patch round-trip and payload Python AST: passed')
