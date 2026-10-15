"""Install UI/code only. Scanning and corrections require later user actions."""
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path('/root/karaoke')
WRAPPER = Path('/usr/local/bin/play_karaoke.sh')
DB = Path('/data/karaoke/db/karaoke.db')
MARKER = ROOT / '.media-audio-installing'
SERVICE = 'karaoke-server.service'
sys.dont_write_bytecode = True


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(*args):
    subprocess.run(args, check=True, timeout=60)


def restart():
    if subprocess.check_output(['systemctl', 'show', SERVICE, '--property=ExecStartPre', '--value'], text=True).strip():
        raise RuntimeError('Старый init-скрипт не отключён; перезапуск запрещён.')
    run('systemctl', 'restart', SERVICE)


def atomic(path, data, mode):
    fd, name = tempfile.mkstemp(prefix='.feature-stage-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def get(path):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open('http://127.0.0.1:8080' + path, timeout=8) as response:
        return response.read()


def player_idle():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(3)
            client.connect('/tmp/mpvsocket')
            client.sendall(b'{"command":["get_property","idle-active"],"request_id":72}\n')
            with client.makefile('r') as stream:
                for _ in range(40):
                    value = json.loads(stream.readline())
                    if value.get('request_id') == 72:
                        if value.get('error') == 'success' and value.get('data') is True:
                            return
                        raise RuntimeError('Остановите песню перед обновлением (кнопка «Стоп»).')
    except (FileNotFoundError, ConnectionRefusedError):
        return
    raise RuntimeError('Не подтверждена остановка видеоплеера.')


def unchanged(manifest):
    for name, expected in manifest['unchanged'].items():
        path = ROOT / name
        if path.is_symlink() or sha(path.read_bytes()) != expected:
            raise RuntimeError('Неожиданно изменился файл: ' + name)


def health(manifest):
    page = get('/')
    if b'audio-output-toggle' not in page or b'/video-optimization' not in page or b'KARAOKE_CONTROL_QR_V5' not in page:
        raise RuntimeError('Не подтверждена новая главная страница.')
    if b'KARAOKE_MEDIA_OPTIMIZER_UI_V1' not in get('/video-optimization'):
        raise RuntimeError('Не подтверждена страница оптимизации.')
    report = json.loads(get('/api/media-optimizer/status'))
    audio = json.loads(get('/api/audio/output'))
    wifi = json.loads(get('/api/karaoke-wifi-monitor'))
    if not report.get('ok') or not audio.get('ok') or not audio.get('available') or not wifi.get('controller_ok'):
        raise RuntimeError('Не подтверждены новые API/состояние Wi-Fi.')
    unchanged(manifest)


def media_idle():
    storage = Path('/mnt/usb_disk/.karaoke-optimization')
    if not storage.exists():
        return
    if (storage / 'current.json').exists():
        record = json.loads((storage / 'current.json').read_text())
        import re
        if not re.fullmatch('[0-9a-f]{32}', record['id']):
            raise RuntimeError('Неизвестный журнал медиатеки.')
        report = storage / record['id'] / 'report.json'
        value = json.loads(report.read_text())
        if value['state'] in {'scanning', 'repairing'}:
            raise RuntimeError('Остановите обработку медиатеки и дождитесь завершения.')
        for path in report.parent.glob('action-*/journal.json'):
            if json.loads(path.read_text())['phase'] in {'prepared', 'committed'}:
                raise RuntimeError('Сначала завершите восстановление медиатеки перезапуском сервера.')


def restore(folder, manifest):
    atomic(ROOT / 'app.py', (folder / 'app.py').read_bytes(), (folder / 'app.py').stat().st_mode & 0o777)
    atomic(WRAPPER, (folder / 'play_karaoke.sh').read_bytes(), (folder / 'play_karaoke.sh').stat().st_mode & 0o777)
    for name in manifest['files']:
        (ROOT / name).unlink(missing_ok=True)
    os.sync()
    restart()
    print('Приложение и прежний запуск плеера восстановлены. Медиатека и база не заменялись.', flush=True)


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Выполните от root в SSH приставки.')
    kit = Path(__file__).resolve().parent
    rollback = len(sys.argv) == 3 and sys.argv[1] == '--rollback'
    if rollback:
        kit = Path(sys.argv[2])
    manifest = json.loads((kit / 'manifest.json').read_text())
    if set(manifest['files']) != {'karaoke_media_optimizer.py', 'karaoke_audio_output.py', 'media_optimizer.html'}:
        raise RuntimeError('Неожиданный список файлов.')
    for path in (ROOT, ROOT / 'app.py', ROOT / 'wifi', WRAPPER):
        if path.is_symlink():
            raise RuntimeError('Неожиданная ссылка: ' + str(path))
    unchanged(manifest)
    if rollback:
        if sha((ROOT / 'app.py').read_bytes()) not in {manifest['app_after'], manifest['app_before']}:
            raise RuntimeError('Приложение уже изменено; старый откат не применён.')
        if sha((kit / 'app.py').read_bytes()) != manifest['app_before']:
            raise RuntimeError('Не совпала проверка резервной копии.')
    elif sha((ROOT / 'app.py').read_bytes()) == manifest['app_after']:
        for name, expected in manifest['files'].items():
            if sha((ROOT / name).read_bytes()) != expected:
                raise RuntimeError('Установленный комплект неполон: ' + name)
        wrapper = WRAPPER.read_bytes()
        if b'karaoke_audio_output.py --device' not in wrapper or b'--audio-device="$AUDIO_DEVICE"' not in wrapper:
            raise RuntimeError('Запуск плеера отличается от установленного варианта.')
        health(manifest)
        print('MEDIA AUDIO ALREADY INSTALLED; обновите страницу ТВ.', flush=True)
        return
    elif sha((ROOT / 'app.py').read_bytes()) != manifest['app_before']:
        raise RuntimeError('app.py отличается от проверенной версии. Изменения не внесены.')
    player_idle()
    if subprocess.check_output(['systemctl', 'show', SERVICE, '--property=ExecStartPre', '--value'], text=True).strip():
        raise RuntimeError('Не подтверждено отключение старого init-скрипта.')
    run('systemctl', 'is-active', '--quiet', SERVICE)
    sys.path.insert(0, str(ROOT))
    network = importlib.import_module('wifi.network')
    with network.admission_lock():
        if network.read_status().get('busy', True) or network.operation_busy():
            raise RuntimeError('Дождитесь завершения настройки Wi-Fi.')
        MARKER.touch(mode=0o600)
        try:
            media_idle()
            if rollback:
                restore(kit, manifest)
                return
            if not os.path.ismount('/mnt/usb_disk'):
                raise RuntimeError('Подключите HDD перед обновлением.')
            for name in manifest['files']:
                if (ROOT / name).exists() or (ROOT / name).is_symlink():
                    raise RuntimeError('Новый путь уже занят: ' + name)
            data = {}
            for name, expected in manifest['files'].items():
                data[name] = (kit / name).read_bytes()
                if sha(data[name]) != expected:
                    raise RuntimeError('Повреждён комплект: ' + name)
                if name.endswith('.py'):
                    ast.parse(data[name], feature_version=(3, 11))
            from parts import patch, patch_wrapper
            app = patch((ROOT / 'app.py').read_bytes())
            wrapper = patch_wrapper(WRAPPER.read_bytes())
            if sha(app) != manifest['app_after']:
                raise RuntimeError('Не совпала проверка нового приложения.')
            ast.parse(app, feature_version=(3, 11))
            subprocess.run(['bash', '-n'], input=wrapper, check=True, timeout=5)
            for executable in ('ffmpeg', 'ffprobe'):
                if not shutil.which(executable):
                    raise RuntimeError('Не найден ' + executable)
            if 'libx264' not in subprocess.check_output(['ffmpeg', '-hide_banner', '-encoders'], stderr=subprocess.DEVNULL, text=True):
                raise RuntimeError('В ffmpeg не найден libx264.')
            folder = Path(tempfile.mkdtemp(prefix='karaoke-media-audio-backup-', dir='/root'))
            folder.chmod(0o700)
            shutil.copy2(ROOT / 'app.py', folder / 'app.py')
            shutil.copy2(WRAPPER, folder / 'play_karaoke.sh')
            shutil.copy2(__file__, folder / 'rollback.py')
            shutil.copy2(kit / 'manifest.json', folder / 'manifest.json')
            with sqlite3.connect(DB.as_uri() + '?mode=ro', uri=True) as source:
                with sqlite3.connect(folder / 'karaoke-preupdate.db') as target:
                    source.backup(target)
                    if target.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                        raise RuntimeError('Не подтверждена резервная копия базы.')
            os.sync()
            print('BACKUP:', folder, flush=True)
            print('ROLLBACK: python3', folder / 'rollback.py', '--rollback', folder, flush=True)
            try:
                for name, value in data.items():
                    atomic(ROOT / name, value, 0o644)
                atomic(WRAPPER, wrapper, WRAPPER.stat().st_mode & 0o777)
                atomic(ROOT / 'app.py', app, (ROOT / 'app.py').stat().st_mode & 0o777)
                restart()
                last = None
                for _ in range(25):
                    try:
                        health(manifest)
                        os.sync()
                        print('MEDIA AUDIO INSTALLED', flush=True)
                        print('Обновите страницу ТВ (F5). Проверка и исправление запускаются в настройках.', flush=True)
                        return
                    except (OSError, ValueError, RuntimeError) as exc:
                        last = exc
                        time.sleep(1)
                raise RuntimeError('Не прошла проверка запуска: ' + str(last))
            except BaseException:
                restore(folder, manifest)
                raise
        finally:
            MARKER.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
