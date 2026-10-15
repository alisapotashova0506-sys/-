"""Create three independently checked SSH paste blocks; only part three installs."""
import ast
import base64
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
archive = (HERE / 'karaoke-wifi-update.tar.xz').read_bytes()
expected = '868abf1a5736c622848da8ad7fe48fe0ad94449319db1e08258175acb2d950a3'
assert hashlib.sha256(archive).hexdigest() == expected
encoded = base64.b85encode(archive).decode()
pieces = [encoded[0:10000], encoded[10000:20000], encoded[20000:]]
records = []
for index, piece in enumerate(pieces, 1):
    raw = base64.b85decode(piece)
    digest = hashlib.sha256(raw).hexdigest()
    lines = '\n'.join(piece[i:i+100] for i in range(0, len(piece), 100))
    header = '''import base64
import hashlib
import os
from pathlib import Path

ssh = os.environ.get('SSH_CONNECTION', '')
if os.geteuid() != 0 or len(ssh.split()) != 4 or ssh.split()[2] != '192.168.1.102':
    raise RuntimeError('Выполните блок в SSH root@192.168.1.102.')

encoded = r"""
'''
    footer = f'''\n"""
data = base64.b85decode(''.join(encoded.split()))
if hashlib.sha256(data).hexdigest() != '{digest}':
    raise RuntimeError('Часть {index} повреждена при вставке. Повторите этот блок.')
folder = Path('/root/karaoke-wifi-transfer-868abf1a')
folder.mkdir(mode=0o700, exist_ok=True)
folder.chmod(0o700)
target = folder / 'part{index}.bin'
target.write_bytes(data)
target.chmod(0o600)
print('Часть {index}/3 принята: {len(raw)} байт.', flush=True)
'''
    if index == 3:
        bootstrap = (HERE / 'inline_bootstrap.template.py').read_text()
        # Reuse the tested unpacker/runner, supplying the joined complete archive.
        remainder = bootstrap[bootstrap.index('def unpack(parent):'):]
        footer += '''
import io
import subprocess
import tarfile
import tempfile
import time

parts = [folder / ('part' + str(n) + '.bin') for n in (1, 2, 3)]
if not all(part.is_file() for part in parts):
    raise RuntimeError('Переданы не все части. Установка не начата.')
data = b''.join(part.read_bytes() for part in parts)
encoded = base64.b85encode(data).decode('ascii')
'''
        footer += remainder
    source = header + lines + footer
    ast.parse(source)
    output = HERE / ('paste-part-' + str(index) + '.sh')
    output.write_text("python3 - <<'PY'\n" + source + '\nPY\n')
    records.append(dict(part=index, bytes=len(raw), sha256=digest, command=str(output)))
assert b''.join(base64.b85decode(piece) for piece in pieces) == archive
print(records)
