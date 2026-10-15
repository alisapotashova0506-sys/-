"""Extract checked textual sources from the single Markdown document into a NEW folder.
Usage: python3 extract_sources.py KARAOKE_DOCUMENTATION.md recovered_project
Never executes extracted files. Non-embedded binary artifacts are not recovered.
"""
import hashlib
import json
from pathlib import Path
import re
import sys


def extract(document, destination):
    if destination.exists():
        raise RuntimeError('Choose a new directory; existing data will not be overwritten.')
    # Clipboard / Windows saving may normalize newlines; sources in this package
    # use LF. Preserve all other source characters and verify their original hash.
    text = document.read_bytes().decode('utf-8-sig').replace('\r\n', '\n')
    pattern = re.compile(r'^<!-- KARAOKE_SOURCE (\{[^\n]+\}) -->\n', re.M)
    entries = []
    for match in pattern.finditer(text):
        meta = json.loads(match.group(1))
        name = meta['path']
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            raise RuntimeError('Unsafe source path: ' + name)
        start = match.end()
        fence_end = text.index('\n', start)
        fence_line = text[start:fence_end]
        fence = re.match(r'^(`{4,})[A-Za-z0-9_-]*$', fence_line)
        if not fence:
            raise RuntimeError('Missing source fence: ' + name)
        finish = text.index('\n' + fence.group(1) + '\n<!-- /KARAOKE_SOURCE -->', fence_end)
        body = text[fence_end + 1:finish]
        if meta['ends_with_newline']:
            body += '\n'
        data = body.encode('utf-8')
        if hashlib.sha256(data).hexdigest() != meta['sha256']:
            raise RuntimeError('Content changed or truncated: ' + name)
        entries.append((path,data,meta.get('mode',0o600)))
    footer = re.search(r'^<!-- KARAOKE_SOURCE_COUNT (\d+) -->$',text,re.M)
    if not entries or not footer or len(entries) != int(footer.group(1)):
        raise RuntimeError('Document incomplete or no source blocks found.')
    if len({str(p) for p,_,_ in entries}) != len(entries):
        raise RuntimeError('Duplicate source paths.')
    destination.mkdir(parents=True)
    for path,data,mode in entries:
        target=destination/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        target.chmod(mode)
    print('Extracted',len(entries),'checked text files to',destination)
    print('Binary images/modules/archives not embedded in this text still require the ZIP or device snapshot.')


if __name__ == '__main__':
    if len(sys.argv)!=3:
        raise SystemExit('Usage: python3 extract_sources.py DOCUMENT.md NEW_DIRECTORY')
    extract(Path(sys.argv[1]),Path(sys.argv[2]))
