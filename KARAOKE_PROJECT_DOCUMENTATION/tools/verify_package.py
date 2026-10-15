"""Read-only package verification. Never imports or starts the karaoke application."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import warnings

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf-8'))
errors = []
checked = 0
for relative, metadata in manifest['files'].items():
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        errors.append('Unsafe manifest path: ' + relative)
        continue
    path = root / p
    if path.is_symlink() or not path.is_file():
        errors.append('Missing or symlink: ' + relative)
        continue
    data = path.read_bytes()
    if len(data) != metadata['size'] or hashlib.sha256(data).hexdigest() != metadata['sha256']:
        errors.append('Changed: ' + relative)
    if path.suffix == '.py':
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', SyntaxWarning)
                ast.parse(data, filename=relative)
        except SyntaxError as exc:
            errors.append('Python syntax: ' + str(exc))
    checked += 1
versions = {
    'versions/device-confirmed-v5/app.py': '8731353016f544c7f46cbf96e0d45dce7f6c52c1239d5777f92ff7f2abf441ba',
    'versions/prepared-media-audio-v1/app.py': '54fb907fd6eb0ed108863ce747c61e496bbb198850ac65bc140ff54eaaaea29d',
}
for name, expected in versions.items():
    path = root / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append('Version mismatch: ' + name)
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('OK:', checked, 'files match SHA256/size; Python parses; V5 and prepared versions identified.')
print('This checks the archive, not device installation, audible sound, or physical Wi-Fi.')
