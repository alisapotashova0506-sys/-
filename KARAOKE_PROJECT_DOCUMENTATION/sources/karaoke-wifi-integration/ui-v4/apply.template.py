"""Two-step setup: manually join KARAOKE, then scan the setup-page URL."""
import ast
import base64
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
URL = 'http://192.168.100.1:8080/wifi/setup'
BEFORE_APPS = {'85a1765e0896f3725929d61333e989d426b5672b1f82d8a2accc259aed288395',
               '224d490bd8eeb4ca8f0a65799aeeeeb9f4479e8b4f578c46a629f4fea0fec148'}
BEFORE_NET = 'b524ee1adcc3c438631016090b092cad7fb7b1a8ed630535f02f3b3687a73a33'
BEFORE_QR = '08e0a2fd23a6f83c3e8197d154a4cd9e9b31e6efc22d854b54571734729242df'
AFTER_APP = '__AFTER_APP__'
AFTER_NET = '__AFTER_NET__'
QR_SHA = '5f7a2c3b9f4281fbba4560da80d737bed5f4a7bb94abc1f424b171d834978671'
QR = base64.b64decode('__QR_BASE64__')
CSS = __CSS_LITERAL__
HTML = '''  <!-- KARAOKE_WIFI_SETUP_CARD_V4 -->
  <div id="karaoke-wifi-setup-indicator" role="region" aria-label="Настройка Wi-Fi по QR-коду">
    <span class="wifi-label">1. Найдите Wi-Fi KARAOKE<br>и введите пароль 12345678.</span>
    <span class="wifi-label" style="margin:10px 0">2. После подключения наведите камеру телефона на QR-код и настройте Wi-Fi.</span>
    <img src="/wifi/setup-qr.png?v=4" width="222" height="222" alt="QR-код страницы настройки Wi-Fi">
    <span class="wifi-note">Адрес настройки:<br>192.168.100.1:8080/wifi/setup</span>
    <button id="karaoke-wifi-setup-open" type="button">Открыть настройку мышкой</button>
  </div>
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def patch(app, network, qr):
    if sha(app) not in BEFORE_APPS or sha(network) != BEFORE_NET or sha(qr) != BEFORE_QR:
        raise RuntimeError('Текущие файлы отличаются от ожидаемых. Изменения не внесены.')
    text = app.decode('utf-8')
    style_marker = ('    /* KARAOKE_WIFI_SETUP_CARD_V3:' if sha(app).startswith('224d49')
                    else '    /* KARAOKE_WIFI_SETUP_INDICATOR_V2:')
    start = text.index(style_marker)
    end = text.index('    #karaoke-wifi-dialog {', start)
    text = text[:start] + CSS + text[end:]
    marker = ('  <!-- KARAOKE_WIFI_SETUP_CARD_V3 -->' if sha(app).startswith('224d49')
              else '  <!-- KARAOKE_WIFI_SETUP_INDICATOR_V2 -->')
    start = text.index(marker)
    end = text.index('  <div id="karaoke-wifi-dialog"', start)
    text = text[:start] + HTML + text[end:]
    text = text.replace('    indicator.onclick = openKaraokeWifiSetup;',
                        "    var setupButton = document.getElementById('karaoke-wifi-setup-open');\n"
                        '    if (setupButton) setupButton.onclick = openKaraokeWifiSetup;')
    old = "WIFI_QR = 'WIFI:T:WPA;S:KARAOKE;P:12345678;;'"
    net = network.decode('utf-8')
    if net.count(old) != 1:
        raise RuntimeError('Не найдены ожидаемые данные QR.')
    net = net.replace(old, 'WIFI_QR = SETUP_URL')
    ast.parse(text)
    ast.parse(net)
    return {'app.py': text.encode('utf-8'), 'wifi/network.py': net.encode('utf-8'),
            'wifi/setup-qr.png': QR}


def run(*args):
    subprocess.run(args, check=True, timeout=60)


def restart():
    pre = subprocess.check_output(['systemctl', 'show', 'karaoke-server.service',
                                   '--property=ExecStartPre', '--value'], text=True).strip()
    if pre:
        raise RuntimeError('Не подтверждено отключение старого init-скрипта.')
    run('systemctl', 'restart', 'karaoke-server.service')


def get(path):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open('http://127.0.0.1:8080' + path, timeout=5) as response:
        return response.read()


def restore(folder):
    for relative in ('app.py', 'wifi/network.py', 'wifi/setup-qr.png'):
        shutil.copy2(folder / relative, ROOT / relative)
    restart()
    os.sync()
    print('Прежние файлы восстановлены.', flush=True)


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Выполните команду от root.')
    if len(sys.argv) == 3 and sys.argv[1] == '--rollback':
        restore(Path(sys.argv[2]))
        return
    expected = {'app.py': AFTER_APP, 'wifi/network.py': AFTER_NET, 'wifi/setup-qr.png': QR_SHA}
    for relative in expected:
        if (ROOT / relative).is_symlink():
            raise RuntimeError('Неожиданная ссылка вместо файла. Изменения не внесены.')
    current = {relative: (ROOT / relative).read_bytes() for relative in expected}
    if all(sha(current[key]) == value for key, value in expected.items()):
        print('QR LINK ALREADY UPDATED; обновите страницу на телевизоре.', flush=True)
        return
    updated = patch(current['app.py'], current['wifi/network.py'], current['wifi/setup-qr.png'])
    if any(sha(updated[key]) != value for key, value in expected.items()):
        raise RuntimeError('Не совпала контрольная сумма обновления.')
    run('systemctl', 'is-active', '--quiet', 'karaoke-server.service')
    pre = subprocess.check_output(['systemctl', 'show', 'karaoke-server.service',
                                   '--property=ExecStartPre', '--value'], text=True).strip()
    if pre:
        raise RuntimeError('Не подтверждено отключение старого init-скрипта.')
    sys.path.insert(0, str(ROOT / 'wifi'))
    import network as net
    with net.admission_lock():
        if net.read_status()['busy'] or net.operation_busy():
            raise RuntimeError('Выполняется настройка Wi-Fi. Повторите после её завершения.')
        folder = Path(tempfile.mkdtemp(prefix='karaoke-qr-link-backup-', dir='/root'))
        folder.chmod(0o700)
        for relative in current:
            backup = folder / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, backup)
        shutil.copy2(__file__, folder / 'rollback.py')
        os.sync()
        print('BACKUP:', folder, flush=True)
        print('ROLLBACK: python3', folder / 'rollback.py', '--rollback', folder, flush=True)
        try:
            for index, (relative, data) in enumerate(updated.items()):
                target = ROOT / relative
                stage = folder / ('stage-' + str(index))
                stage.write_bytes(data)
                stage.chmod(target.stat().st_mode & 0o777)
                os.replace(stage, target)
            restart()
            for attempt in range(30):
                try:
                    if (b'KARAOKE_WIFI_SETUP_CARD_V4' in get('/') and
                            sha(get('/wifi/setup-qr.png?v=4')) == QR_SHA and
                            json.loads(get('/api/karaoke-wifi-monitor')).get('wifi_qr') == URL):
                        os.sync()
                        print('QR LINK UPDATED; обновите страницу на телевизоре.', flush=True)
                        return
                except (OSError, ValueError):
                    pass
                time.sleep(1)
            raise RuntimeError('Новый QR и инструкция не подтверждены сервером.')
        except BaseException:
            restore(folder)
            raise


if __name__ == '__main__':
    main()
