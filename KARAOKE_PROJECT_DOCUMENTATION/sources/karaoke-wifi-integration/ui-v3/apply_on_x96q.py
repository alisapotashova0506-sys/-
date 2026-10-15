"""Show the QR as a normal visible card; leave Wi-Fi policy unchanged."""
import ast
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

BEFORE = '85a1765e0896f3725929d61333e989d426b5672b1f82d8a2accc259aed288395'
AFTER = '224d490bd8eeb4ca8f0a65799aeeeeb9f4479e8b4f578c46a629f4fea0fec148'
QR_SHA = '08e0a2fd23a6f83c3e8197d154a4cd9e9b31e6efc22d854b54571734729242df'
CSS = '''    /* KARAOKE_WIFI_SETUP_CARD_V3: show QR immediately, outside any button. */
    #karaoke-wifi-setup-indicator {
      display: none; position: fixed; top: 12px; left: 12px; z-index: 8000;
      width: 272px; box-sizing: border-box; padding: 12px; border-radius: 12px;
      background: #0f172a; border: 1px solid #60a5fa;
      box-shadow: 0 4px 18px rgba(0,0,0,0.4); color: white;
      text-align: center; font: 14px/1.4 sans-serif;
    }
    #karaoke-wifi-setup-indicator img {
      display: block; width: 222px; height: 222px; margin: 0 auto 10px;
      background: white; image-rendering: pixelated;
    }
    #karaoke-wifi-setup-indicator .wifi-label {
      display: block; font-weight: bold; font-size: 17px;
    }
    #karaoke-wifi-setup-indicator .wifi-note {
      display: block; margin-top: 8px; color: #cbd5e1; font-size: 12px;
    }
    #karaoke-wifi-setup-open {
      display: block; width: 100%; margin-top: 10px; padding: 8px;
      border: 1px solid #64748b; border-radius: 6px; background: #334155;
      color: white; font: 13px sans-serif; cursor: pointer;
    }
'''
HTML = '''  <!-- KARAOKE_WIFI_SETUP_CARD_V3 -->
  <div id="karaoke-wifi-setup-indicator" role="region" aria-label="Настройка Wi-Fi по QR-коду">
    <img src="/wifi/setup-qr.png?v=3" width="222" height="222" alt="QR-код подключения к KARAOKE">
    <span class="wifi-label">Для настройки Wi-Fi наведите камеру телефона и перейдите по ссылке.</span>
    <span class="wifi-note">Сеть: KARAOKE · пароль: 12345678</span>
    <span class="wifi-note">Если страница не открылась:<br>192.168.100.1:8080/wifi/setup</span>
    <button id="karaoke-wifi-setup-open" type="button">Открыть настройку мышкой</button>
  </div>
'''


def patch(data):
    if hashlib.sha256(data).hexdigest() != BEFORE:
        raise RuntimeError('app.py отличается от установленной версии. Изменения не внесены.')
    text = data.decode('utf-8')
    start = text.index('    /* KARAOKE_WIFI_SETUP_INDICATOR_V2:')
    end = text.index('    #karaoke-wifi-dialog {', start)
    text = text[:start] + CSS + text[end:]
    start = text.index('  <!-- KARAOKE_WIFI_SETUP_INDICATOR_V2 -->')
    end = text.index('  <div id="karaoke-wifi-dialog"', start)
    text = text[:start] + HTML + text[end:]
    old = '    indicator.onclick = openKaraokeWifiSetup;'
    if text.count(old) != 1:
        raise RuntimeError('Не найдена ожидаемая привязка интерфейса.')
    text = text.replace(old, "    var setupButton = document.getElementById('karaoke-wifi-setup-open');\n"
                            '    if (setupButton) setupButton.onclick = openKaraokeWifiSetup;')
    ast.parse(text)
    result = text.encode('utf-8')
    if hashlib.sha256(result).hexdigest() != AFTER:
        raise RuntimeError('Не совпала контрольная сумма нового интерфейса.')
    return result


def run(*args):
    subprocess.run(args, check=True, timeout=60)


def get(path):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open('http://127.0.0.1:8080' + path, timeout=5) as response:
        return response.read()


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Выполните команду от root.')
    target = Path('/root/karaoke/app.py')
    if target.is_symlink():
        raise RuntimeError('Неожиданная ссылка вместо app.py. Изменения не внесены.')
    current = target.read_bytes()
    if hashlib.sha256(current).hexdigest() == AFTER:
        print('QR CARD ALREADY UPDATED; обновите страницу на телевизоре.', flush=True)
        return
    updated = patch(current)
    pre = subprocess.check_output(['systemctl', 'show', 'karaoke-server.service',
                                   '--property=ExecStartPre', '--value'], text=True).strip()
    if pre:
        raise RuntimeError('Не подтверждено отключение старого init-скрипта. Изменения не внесены.')
    sys.path.insert(0, '/root/karaoke/wifi')
    import network as net
    with net.admission_lock():
        if net.read_status()['busy'] or net.operation_busy():
            raise RuntimeError('Выполняется настройка Wi-Fi. Повторите после её завершения.')
        folder = Path(tempfile.mkdtemp(prefix='karaoke-qr-backup-', dir='/root'))
        folder.chmod(0o700)
        backup = folder / 'app.py'
        shutil.copy2(target, backup)
        os.sync()
        print('BACKUP:', backup, flush=True)
        try:
            stage = folder / 'app-new.py'
            stage.write_bytes(updated)
            stage.chmod(target.stat().st_mode & 0o777)
            os.replace(stage, target)
            run('systemctl', 'restart', 'karaoke-server.service')
            for attempt in range(30):
                try:
                    if (b'KARAOKE_WIFI_SETUP_CARD_V3' in get('/') and
                            hashlib.sha256(get('/wifi/setup-qr.png?v=3')).hexdigest() == QR_SHA):
                        print('QR CARD UPDATED; обновите страницу на телевизоре.', flush=True)
                        return
                except OSError:
                    pass
                time.sleep(1)
            raise RuntimeError('Новый блок QR не подтверждён сервером.')
        except BaseException:
            shutil.copy2(backup, target)
            run('systemctl', 'restart', 'karaoke-server.service')
            print('Прежний интерфейс восстановлен.', flush=True)
            raise


if __name__ == '__main__':
    main()
