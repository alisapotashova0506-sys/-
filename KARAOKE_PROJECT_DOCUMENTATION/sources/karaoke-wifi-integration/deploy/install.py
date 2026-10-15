"""Install QR/fallback Wi-Fi with private backups and a standalone rollback."""
import argparse
import ast
import fcntl
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path('/root/karaoke')
HERE = Path(__file__).resolve().parent
AP = '67e9bd92-5f2a-4bab-9645-4afe89fcfc97'
USB = 'wlxf0b040f7f699'
ENV = dict(os.environ, LC_ALL='C')
MONITOR = 'karaoke-wifi-monitor.service'
SERVER = 'karaoke-server.service'
LEGACY = ('karaoke-wifi-auto.service', 'karaoke-wifi-rescue.timer')


def run(*arguments, check=True, timeout=30):
    result = subprocess.run(arguments, text=True, capture_output=True,
                            env=ENV, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(arguments[0] + ': ' + result.stdout + result.stderr)
    return result.stdout.strip()


def active(unit):
    return run('systemctl', 'is-active', unit, check=False) == 'active'


def connection_setting(uuid, name):
    return run('nmcli', '--escape', 'no', '-g', name,
               'connection', 'show', 'uuid', uuid)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def home_ssh():
    fields = os.environ.get('SSH_CONNECTION', '').split()
    if len(fields) != 4 or fields[2] != '192.168.1.102':
        raise RuntimeError('Connect SSH to 192.168.1.102 from the home Wi-Fi before updating')
    routes = json.loads(run('ip', '-j', '-4', 'route', 'get', fields[0], 'from', fields[2]))
    if not routes or any(item.get('dev') != 'wlan0' for item in routes):
        raise RuntimeError('The SSH computer must be on the home Wi-Fi, not KARAOKE')


def http_json(path):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open('http://127.0.0.1:8080' + path, timeout=4) as response:
        return json.loads(response.read())


def restore(folder):
    data = json.loads((folder / 'backup.json').read_text())
    errors = []
    def attempt(label, operation):
        try:
            operation()
        except Exception as error:
            errors.append(label + ': ' + str(error))
    attempt('stop controller', lambda: run('systemctl', 'stop', MONITOR))
    for item in reversed(data['files']):
        destination = Path(item['target'])
        if item['backup'] is None:
            attempt(str(destination), lambda p=destination: p.unlink(missing_ok=True))
        else:
            def copy_back(target=destination, record=item):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(folder / record['backup'], target)
            attempt(str(destination), copy_back)
    attempt('reload units', lambda: run('systemctl', 'daemon-reload'))
    for unit, state in data['units'].items():
        if state['enabled'] in ('enabled', 'disabled'):
            action = 'enable' if state['enabled'] == 'enabled' else 'disable'
            attempt(unit + ' enable state', lambda u=unit, a=action: run('systemctl', a, u))
    attempt('AP profile', lambda: run('nmcli', 'connection', 'modify', 'uuid', AP,
                                    'connection.autoconnect', data['ap_autoconnect']))
    attempt('USB flag', lambda: run('nmcli', 'device', 'set', USB, 'autoconnect', data['usb_autoconnect']))
    if data['units'][SERVER]['active']:
        attempt('original app restart', lambda: run('systemctl', 'restart', SERVER, timeout=70))
    if data['units'][MONITOR]['active']:
        attempt('original monitor start', lambda: run('systemctl', 'start', MONITOR))
    # Recreate the shared DNS process without this update's DNS snippet.
    if data['ap_was_active']:
        attempt('AP stop', lambda: run('nmcli', '--wait', '15', 'connection', 'down', 'uuid', AP, timeout=20))
        attempt('AP start', lambda: run('nmcli', '--wait', '35', 'connection', 'up', 'uuid', AP,
                                      'ifname', USB, timeout=45))
    for unit in LEGACY:
        if data['units'][unit]['active']:
            attempt(unit + ' start', lambda u=unit: run('systemctl', 'start', u))
    os.sync()
    print('ROLLBACK COMPLETE' if not errors else 'ROLLBACK NEEDS ATTENTION', flush=True)
    for error in errors:
        print(error, flush=True)
    return not errors


def install():
    home_ssh()
    if not active(SERVER):
        raise RuntimeError('The existing karaoke server must be running before the update')
    if run('systemctl', 'show', SERVER, '--property=ExecStartPre', '--value'):
        raise RuntimeError('The existing init-script override is not effective; no service was restarted')
    if (Path('/sys/class/net') / USB / 'device/driver').resolve(strict=True).name != '8188eu':
        raise RuntimeError('USB must use the already tested 8188eu driver')
    if (connection_setting(AP, '802-11-wireless.ssid') != 'KARAOKE'
            or connection_setting(AP, 'connection.interface-name') != USB):
        raise RuntimeError('The tested KARAOKE USB profile differs; stop for review')
    units = run('systemctl', 'list-units', '--state=active,activating',
                '--type=service', '--type=timer', '--plain', '--no-legend', '--no-pager')
    patterns = ('karaoke-ap-*', 'karaoke-final-auto-*', 'karaoke-full-*',
                'karaoke-packet-*', 'karaoke-http-diagnostic.*', 'karaoke-wifi-rescue.*')
    for line in units.splitlines():
        unit = line.split()[0]
        if any(fnmatch.fnmatchcase(unit, pattern) for pattern in patterns):
            raise RuntimeError('An old Wi-Fi test or rescue job is active: ' + unit)
    lock = Path('/run/karaoke-wifi-connect.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise RuntimeError('A Wi-Fi connection is already in progress; retry after it finishes') from None
    lock.close()
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for item in manifest['files']:
        source = HERE / item['source']
        target = Path(item['target'])
        if digest(source) != item['sha256']:
            raise RuntimeError('Update payload differs: ' + item['source'])
        if target.is_symlink():
            raise RuntimeError('Unexpected symlink: ' + str(target))
        expected = item['before']
        if expected is None:
            if target.exists():
                raise RuntimeError('Refusing to overwrite an unexpected file: ' + str(target))
        elif not target.is_file() or digest(target) != expected:
            raise RuntimeError('Current file changed since upload: ' + str(target))
    if digest(ROOT / 'app.py') != manifest['app_before']:
        raise RuntimeError('app.py changed since upload; no update performed')
    folder = Path(tempfile.mkdtemp(prefix='karaoke-wifi-backup-', dir='/root'))
    folder.chmod(0o700)
    stage = folder / 'stage'
    stage.mkdir()
    shutil.copy2(ROOT / 'app.py', stage / 'app.py')
    run('patch', '--batch', '--forward', '-p1', '-d', str(stage), '-i', str(HERE / 'app.patch'))
    if digest(stage / 'app.py') != manifest['app_after']:
        raise RuntimeError('Patched app.py checksum differs')
    ast.parse((stage / 'app.py').read_text())
    for item in manifest['files']:
        if item['source'].endswith('.py'):
            ast.parse((HERE / item['source']).read_text())
    files = [dict(target=str(ROOT / 'app.py'), backup='files/app.py')]
    (folder / 'files').mkdir()
    shutil.copy2(ROOT / 'app.py', folder / 'files/app.py')
    for index, item in enumerate(manifest['files']):
        record = dict(target=item['target'], backup=None)
        if item['before'] is not None:
            record['backup'] = 'files/' + str(index)
            shutil.copy2(item['target'], folder / record['backup'])
        files.append(record)
    data = dict(files=files,
                units={unit: dict(enabled=run('systemctl', 'is-enabled', unit, check=False),
                                  active=active(unit)) for unit in (MONITOR, SERVER, *LEGACY)},
                ap_autoconnect=connection_setting(AP, 'connection.autoconnect'),
                usb_autoconnect=run('nmcli', '-g', 'GENERAL.AUTOCONNECT', 'device', 'show', USB),
                ap_was_active=run('nmcli', '-g', 'GENERAL.CON-UUID', 'device', 'show', USB) == AP)
    if data['usb_autoconnect'] not in ('yes', 'no'):
        raise RuntimeError('Cannot record the USB autoconnect flag')
    (folder / 'backup.json').write_text(json.dumps(data, indent=2) + '\n')
    (folder / 'backup.json').chmod(0o600)
    shutil.copy2(__file__, folder / 'rollback.py')
    (folder / 'rollback.py').chmod(0o700)
    print('BACKUP:', folder, flush=True)
    print('ROLLBACK: python3', folder / 'rollback.py', '--rollback', folder, flush=True)
    os.sync()
    admission_path = Path('/var/lib/karaoke-wifi/admission.lock')
    admission_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    admission = admission_path.open('a')
    try:
        fcntl.flock(admission, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        admission.close()
        raise RuntimeError('A Wi-Fi request is being submitted; no update performed') from None
    try:
        run('systemctl', 'stop', MONITOR)
        for item in manifest['files']:
            target = Path(item['target'])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / item['source'], target)
            target.chmod(item['mode'])
        shutil.copyfile(stage / 'app.py', ROOT / 'app.py')
        (ROOT / 'app.py').chmod(0o644)
        for unit in LEGACY:
            run('systemctl', 'disable', '--now', unit)
        run('nmcli', 'connection', 'modify', 'uuid', AP, 'connection.autoconnect', 'no')
        run('systemctl', 'daemon-reload')
        run('systemctl', 'enable', MONITOR)
        # Existing 20-disable-init.conf stays in place; no init script is run.
        run('systemctl', 'restart', SERVER, timeout=70)
        run('systemctl', 'start', MONITOR)
        deadline = time.monotonic() + 55
        state = {}
        while time.monotonic() < deadline:
            try:
                state = http_json('/api/karaoke-wifi-monitor')
                if (state.get('controller_ok') and state.get('connected')
                        and not state.get('ap_active') and not state.get('setup_needed')):
                    break
            except (OSError, ValueError):
                pass
            time.sleep(1)
        else:
            raise RuntimeError('New controller did not confirm home Wi-Fi / AP off; restoring backup')
        if not active(MONITOR) or not active(SERVER):
            raise RuntimeError('A required karaoke Wi-Fi service is not running')
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open('http://127.0.0.1:8080/wifi/setup-qr.png', timeout=5) as response:
            if hashlib.sha256(response.read()).hexdigest() != manifest['qr_sha256']:
                raise RuntimeError('The served QR image differs')
        os.sync()
        print('UPDATE COMPLETE', flush=True)
        print('Home Wi-Fi:', state.get('network'), 'IP:', state.get('ip'), flush=True)
        print('KARAOKE and QR are now off while home Wi-Fi is connected.', flush=True)
        print('Refresh the karaoke screen once to load the new QR interface.', flush=True)
    except BaseException:
        print('UPDATE FAILED; restoring the previous working configuration', flush=True)
        restore(folder)
        raise
    finally:
        admission.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rollback', type=Path)
    args = parser.parse_args()
    try:
        if os.geteuid() != 0:
            raise RuntimeError('Run as root')
        if args.rollback:
            raise SystemExit(0 if restore(args.rollback) else 1)
        install()
    except Exception as error:
        print('ERROR:', error, flush=True)
        raise SystemExit(1)
