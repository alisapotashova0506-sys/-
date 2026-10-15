"""Install the home-control QR card; never import the playback application."""
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path('/root/karaoke')
SERVICE = 'karaoke-server.service'
BEFORE = 'e168e929236a770953bac8e15aef6288662dccbb5bf6935f237c3b4ab13af642'
UNCHANGED = {
    'wifi/network.py': '3238e2b0601464333a5555c574ff3e9f7bf8e6a0e7e3fbab5820ee1278b3d7ca',
    'wifi/setup-qr.png': '5f7a2c3b9f4281fbba4560da80d737bed5f4a7bb94abc1f424b171d834978671',
}
sys.dont_write_bytecode = True


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(*args):
    subprocess.run(args, check=True, timeout=60)


def check_restart():
    pre = subprocess.check_output(['systemctl', 'show', SERVICE,
                                   '--property=ExecStartPre', '--value'], text=True).strip()
    if pre:
        raise RuntimeError('Старый init-скрипт не отключён. Изменения не внесены.')


def restart():
    check_restart()
    run('systemctl', 'restart', SERVICE)


def atomic_write(path, data, mode=0o644):
    fd, temporary = tempfile.mkstemp(prefix='.control-qr-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def verify_unchanged():
    for relative, expected in UNCHANGED.items():
        path = ROOT / relative
        if path.is_symlink() or sha(path.read_bytes()) != expected:
            raise RuntimeError('Не совпала проверка неизменяемого файла: ' + relative)


def http_get(path):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        response = opener.open('http://127.0.0.1:8080' + path, timeout=5)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        return response.code, response.headers, response.read()


def health():
    code, _, html = http_get('/')
    if (code != 200 or b'KARAOKE_CONTROL_QR_V5' not in html or b'remote-info' in html
            or b'KARAOKE_WIFI_SETUP_CARD_V4' not in html):
        raise RuntimeError('Новая страница не подтверждена сервером.')
    code, _, body = http_get('/api/karaoke-wifi-monitor')
    state = json.loads(body)
    if code != 200 or state.get('controller_ok') is not True:
        raise RuntimeError('Контроллер Wi-Fi не подтвердил состояние.')
    if state.get('connected') is True:
        address = state['ip']
        code, headers, png = http_get('/wifi/control-qr.png?ip=' + address)
        if (code != 200 or not png.startswith(b'\x89PNG\r\n\x1a\n')
                or struct.unpack('>II', png[16:24]) != (222, 222)
                or headers.get('X-Control-URL') != 'http://' + address + ':8080/'
                or 'no-store' not in headers.get('Cache-Control', '')):
            raise RuntimeError('Новый QR не подтверждён сервером.')
    elif http_get('/wifi/control-qr.png')[0] != 409:
        raise RuntimeError('QR не должен показывать старый адрес без домашней сети.')
    code, _, png = http_get('/wifi/setup-qr.png?v=4')
    if code != 200 or sha(png) != UNCHANGED['wifi/setup-qr.png']:
        raise RuntimeError('Проверка прежнего QR настройки Wi-Fi не пройдена.')
    verify_unchanged()
    return state


def load_manifest(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    for relative in manifest['new_files']:
        path = Path(relative)
        if (path.is_absolute() or '..' in path.parts or
                not (relative == 'wifi/control_qr.py' or relative.startswith('wifi/vendor/'))):
            raise RuntimeError('Неожиданный путь в комплекте.')
    return manifest


def restore(folder, manifest):
    old = folder / 'app.py'
    if sha(old.read_bytes()) != BEFORE:
        raise RuntimeError('Резервная копия не прошла проверку.')
    atomic_write(ROOT / 'app.py', old.read_bytes(), old.stat().st_mode & 0o777)
    for relative in manifest['new_files']:
        (ROOT / relative).unlink(missing_ok=True)
    for relative in ('wifi/vendor/qrcode', 'wifi/vendor'):
        try:
            (ROOT / relative).rmdir()
        except OSError:
            pass
    os.sync()
    restart()
    print('Прежняя версия приложения восстановлена.', flush=True)


def network_module():
    sys.path.insert(0, str(ROOT))
    return importlib.import_module('wifi.network')


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Выполните команду от root.')
    if len(sys.argv) == 3 and sys.argv[1] == '--rollback':
        folder = Path(sys.argv[2])
        manifest = load_manifest(folder)
        check_restart()
        net = network_module()
        with net.admission_lock():
            if net.read_status().get('busy', True) or net.operation_busy():
                raise RuntimeError('Дождитесь завершения настройки Wi-Fi.')
            restore(folder, manifest)
        return
    kit = Path(__file__).resolve().parent
    manifest = load_manifest(kit)
    app = ROOT / 'app.py'
    if ROOT.is_symlink() or (ROOT / 'wifi').is_symlink() or app.is_symlink():
        raise RuntimeError('Неожиданная ссылка вместо каталога/файла приложения.')
    verify_unchanged()
    if sha(app.read_bytes()) == manifest['app_after']:
        for relative, expected in manifest['new_files'].items():
            path = ROOT / relative
            if path.is_symlink() or sha(path.read_bytes()) != expected:
                raise RuntimeError('Установленный комплект неполон: ' + relative)
        health()
        print('CONTROL QR ALREADY INSTALLED; обновите страницу на телевизоре.', flush=True)
        return
    if sha(app.read_bytes()) != BEFORE:
        raise RuntimeError('app.py отличается от проверенной версии. Изменения не внесены.')
    if ((ROOT / 'wifi/control_qr.py').exists() or (ROOT / 'wifi/control_qr.py').is_symlink()
            or (ROOT / 'wifi/vendor').exists() or (ROOT / 'wifi/vendor').is_symlink()):
        raise RuntimeError('Новые пути уже существуют. Изменения не внесены.')
    from parts import patch
    updated = patch(app.read_bytes())
    if sha(updated) != manifest['app_after']:
        raise RuntimeError('Не совпала контрольная сумма нового приложения.')
    ast.parse(updated, feature_version=(3, 11))
    additions = {}
    for relative, expected in manifest['new_files'].items():
        data = (kit / relative).read_bytes()
        if sha(data) != expected:
            raise RuntimeError('Повреждён файл комплекта: ' + relative)
        if relative.endswith('.py'):
            ast.parse(data, feature_version=(3, 11))
        additions[relative] = data
    check_restart()
    run('systemctl', 'is-active', '--quiet', SERVICE)
    net = network_module()
    with net.admission_lock():
        if net.read_status().get('busy', True) or net.operation_busy():
            raise RuntimeError('Выполняется настройка Wi-Fi. Дождитесь завершения.')
        if sha(app.read_bytes()) != BEFORE:
            raise RuntimeError('Приложение изменилось во время подготовки.')
        folder = Path(tempfile.mkdtemp(prefix='karaoke-control-qr-backup-', dir='/root'))
        folder.chmod(0o700)
        shutil.copy2(app, folder / 'app.py')
        shutil.copy2(kit / 'manifest.json', folder / 'manifest.json')
        shutil.copy2(__file__, folder / 'rollback.py')
        os.sync()
        print('BACKUP:', folder, flush=True)
        print('ROLLBACK: python3', folder / 'rollback.py', '--rollback', folder, flush=True)
        try:
            for relative in ('wifi/vendor', 'wifi/vendor/qrcode'):
                (ROOT / relative).mkdir(mode=0o755)
                (ROOT / relative).chmod(0o755)
            for relative, data in additions.items():
                atomic_write(ROOT / relative, data)
            for relative, expected in manifest['new_files'].items():
                if sha((ROOT / relative).read_bytes()) != expected:
                    raise RuntimeError('Не пройдена проверка записанного файла: ' + relative)
            probe = ('import sys;sys.path.insert(0,' + repr(str(ROOT)) + ');'
                     'from wifi.control_qr import control_image;'
                     "p,u=control_image({'controller_ok':True,'connected':True,'ip':'192.168.1.102'});"
                     "assert p[:8]==b'\\x89PNG\\r\\n\\x1a\\n' and u=='http://192.168.1.102:8080/'")
            run(sys.executable, '-I', '-S', '-B', '-c', probe)
            os.sync()
            atomic_write(app, updated, app.stat().st_mode & 0o777)
            restart()
            last_error = None
            for attempt in range(25):
                try:
                    state = health()
                    os.sync()
                    print('CONTROL QR INSTALLED', flush=True)
                    print('Домашний адрес:', 'http://' + state['ip'] + ':8080/'
                          if state.get('connected') else 'ожидает подключения', flush=True)
                    print('Обновите страницу на телевизоре (F5).', flush=True)
                    return
                except (OSError, ValueError, KeyError, struct.error, RuntimeError) as exc:
                    last_error = exc
                    time.sleep(1)
            raise RuntimeError('Проверка после запуска не пройдена: ' + str(last_error))
        except BaseException:
            restore(folder, manifest)
            raise


if __name__ == '__main__':
    main()
