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
AFTER_APP = 'e168e929236a770953bac8e15aef6288662dccbb5bf6935f237c3b4ab13af642'
AFTER_NET = '3238e2b0601464333a5555c574ff3e9f7bf8e6a0e7e3fbab5820ee1278b3d7ca'
QR_SHA = '5f7a2c3b9f4281fbba4560da80d737bed5f4a7bb94abc1f424b171d834978671'
QR = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAASgAAAEoCAAAAADObDPFAAACzklEQVR42u3aO3bDMAwEQN//0knvRgSw1M+DLomjUMMU+wB8/tRSfRCAAgUKFChQChQoUKBAgQKlQIECBQoUKAUKFChQoECBUqBAgQL1OqhPs75//+i5R58/Ol/qvKBAgQIFChQoUGmo7sF3fX4XNChQoECBAgUK1C6oacCsBs9yMAydFxQoUKBAgQIF6mqo7osefb7790GBAgUKFChQoJ4KNR1Yrp4PFChQoECBAgXqblAp2O4i2msnxaBAgQIFChSo10KlX3T319MgCwoUKFCgQIECNYWaVhe2CrT9PUCBAgUKFChQoMKNu1Tgqw5IpxdyeocTFChQoECBAvXzUMsPDg0mVy9quqgGChQoUKBAgQJ11lyvu8g1Dai7LgQUKFCgQIECBWoXVHfgmAqo3QuYBlpQoECBAgUKFKhdUKnF9+7zuxdUDqagQIECBQoUKFBFqGowSzXoUotm1e+DAgUKFChQoEDtXshfHYC2F7eKC/RVoHJjERQoUKBAgQIFKtS4my7KVwPuNJBeNgAFBQoUKFCgQP0sVPcA08beNIBOLxoUKFCgQIECBWpX464aELsvVl0IuzxwggIFChQoUKBAFRty6UWwVMDsNvZAgQIFChQoUKB2QU0DZzcYVhfJpoEWFChQoECBAgUqNQBNN/K6DbZp0I0HTlCgQIECBQoUqHBNG3fTxtv056BAgQIFChQoUOnA2R1wdl+g+9zTBqCgQIECBQoUKFDNQJYaPHYbeNXzbBuAggIFChQoUKBAhQJcNxBOfy81+AQFChQoUKBAgboKajo4rQ5Up40+UKBAgQIFChSou0J1B6blF2sOUEGBAgUKFChQoO4+AE1dyGoAfeykGBQoUKBAgQL1eKjUQv608VZt4MX+AUCBAgUKFChQoIpQChQoUKBAgQKlQIECBQoUKFAKFChQoECBUqBAgQIFChQoBQoUKFAPrX/n+iWKqfWhhwAAAABJRU5ErkJggg==')
CSS = '    /* KARAOKE_WIFI_SETUP_CARD_V4: show QR immediately, outside any button. */\n    #karaoke-wifi-setup-indicator {\n      display: none; position: fixed; top: 12px; left: 12px; z-index: 8000;\n      width: 272px; box-sizing: border-box; padding: 12px; border-radius: 12px;\n      background: #0f172a; border: 1px solid #60a5fa;\n      box-shadow: 0 4px 18px rgba(0,0,0,0.4); color: white;\n      text-align: center; font: 14px/1.4 sans-serif;\n    }\n    #karaoke-wifi-setup-indicator img {\n      display: block; width: 222px; height: 222px; margin: 0 auto 10px;\n      background: white; image-rendering: pixelated;\n    }\n    #karaoke-wifi-setup-indicator .wifi-label {\n      display: block; font-weight: bold; font-size: 17px;\n    }\n    #karaoke-wifi-setup-indicator .wifi-note {\n      display: block; margin-top: 8px; color: #cbd5e1; font-size: 12px;\n    }\n    #karaoke-wifi-setup-open {\n      display: block; width: 100%; margin-top: 10px; padding: 8px;\n      border: 1px solid #64748b; border-radius: 6px; background: #334155;\n      color: white; font: 13px sans-serif; cursor: pointer;\n    }\n'
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
