# Константы, SQL и зависимости

Содержимое получено статически, код не импортирован. Литералы показывают параметры данной версии, не фактическое состояние устройства.

## versions/prepared-media-audio-v1/app.py

```python
UPLOAD_FOLDER = '/mnt/usb_disk/karaoke_media'
```

```python
POSTER_FOLDER = '/mnt/usb_disk/posters'
```

```python
FONSOUND_FOLDER = '/mnt/usb_disk/fonsound'
```

```python
BGM_SETTINGS_FILE = '/root/karaoke/.bgm_settings.json'
```

```python
DB_DIR = "/data/karaoke/db"
```

```python
DB_NAME = os.path.join(DB_DIR, "karaoke.db")
```

```python
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
```

```python
POSTER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
```

**Импорты:** `flask`, `flask_socketio`, `functools`, `glob`, `hashlib`, `ipaddress`, `json`, `karaoke_audio_output`, `karaoke_media_optimizer`, `karaoke_quarantine`, `karaoke_youtube_manager`, `logging`, `os`, `platform`, `poster_auto`, `re`, `shutil`, `signal`, `socket`, `sqlite3`, `subprocess`, `threading`, `time`, `wifi`.

**Строки SQL, встречающиеся в файле:**

```sql
CREATE TABLE IF NOT EXISTS songs (id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT NOT NULL, title TEXT NOT NULL, file TEXT NOT NULL UNIQUE, plays INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY AUTOINCREMENT, song_id INTEGER NOT NULL, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (song_id) REFERENCES songs(id));
SELECT id, file FROM songs;
SELECT file, COUNT(*) as cnt, MIN(id) as keep_id FROM songs GROUP BY file HAVING cnt > 1;
SELECT artist, SUM(plays) AS total_plays FROM songs GROUP BY artist ORDER BY total_plays DESC, artist LIMIT 30;
SELECT * FROM songs ORDER BY plays DESC, artist, title;
UPDATE songs SET plays = plays + 1 WHERE file = ?;
INSERT INTO queue (song_id) VALUES (?);
SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file
        FROM queue q
        JOIN songs s ON q.song_id = s.id
        ORDER BY q.added_at ASC, q.id ASC;
SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file
        FROM queue q
        JOIN songs s ON q.song_id = s.id
        ORDER BY q.added_at ASC, q.id ASC
        LIMIT 1;
DELETE FROM queue WHERE id = ?;
SELECT id FROM queue ORDER BY added_at ASC, id ASC;
DELETE FROM queue;
SELECT q.id AS queue_id, s.file
        FROM queue q
        JOIN songs s ON q.song_id = s.id
        ORDER BY q.added_at ASC, q.id ASC
        LIMIT 1;
DELETE FROM songs WHERE file = ? AND id != ?;
SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file FROM queue q JOIN songs s ON q.song_id = s.id ORDER BY q.added_at ASC, q.id ASC;
UPDATE queue SET added_at = ? WHERE id = ?;
INSERT OR REPLACE INTO songs (artist, title, file, plays) VALUES (?, ?, ?, 0);
SELECT id FROM songs WHERE file = ?;
DELETE FROM queue WHERE song_id = ?;
DELETE FROM songs WHERE id = ?;
SELECT artist FROM songs WHERE id=?;
DELETE FROM queue WHERE id=?;
SELECT q.id FROM queue q JOIN songs s ON q.song_id = s.id WHERE s.file = ?;
SELECT DISTINCT artist FROM songs WHERE artist != '' ORDER BY artist;
SELECT 1 FROM songs WHERE artist = ? LIMIT 1;
INSERT INTO songs (artist,title,file,plays) VALUES(?,?,?,0);
SELECT q.id AS queue_id, s.file FROM queue q
                              JOIN songs s ON q.song_id=s.id
                              ORDER BY q.added_at, q.id LIMIT 1;
SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file FROM queue q JOIN songs s ON q.song_id=s.id ORDER BY q.added_at, q.id;
SELECT artist, title FROM songs WHERE file=? LIMIT 1;
SELECT artist,title FROM songs WHERE file=?;
UPDATE songs SET artist=?,title=? WHERE file=?
```

## versions/prepared-media-audio-v1/karaoke_media_optimizer.py

```python
ACTIVE = {'scanning', 'repairing'}
```

```python
EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov'}
```

**Импорты:** `contextlib`, `copy`, `flask`, `fractions`, `hashlib`, `json`, `os`, `pathlib`, `re`, `shutil`, `sqlite3`, `subprocess`, `threading`, `time`, `unicodedata`, `uuid`.

**Строки SQL, встречающиеся в файле:**

```sql
BEGIN IMMEDIATE;
DELETE FROM songs WHERE id=?;
INSERT OR REPLACE INTO songs(id,artist,title,file,plays) VALUES(?,?,?,?,?);
UPDATE queue SET song_id=? WHERE id=?;
SELECT * FROM songs WHERE file=?;
SELECT id,song_id FROM queue WHERE song_id=?;
UPDATE songs SET plays=plays+? WHERE id=?;
UPDATE queue SET song_id=? WHERE song_id=?;
UPDATE songs SET file=?,artist=?,title=? WHERE id=?;
INSERT INTO songs(artist,title,file,plays) VALUES(?,?,?,0)
```

## versions/prepared-media-audio-v1/karaoke_audio_output.py

```python
DEVICES = {'hdmi': 'alsa/dmix:CARD=HDMI,DEV=0',
           'analog': 'alsa/dmix:CARD=audiocodec,DEV=0'}
```

```python
SETTINGS = Path('/root/karaoke/.audio_output.json')
```

```python
SOCKETS = ('/tmp/mpvsocket', '/tmp/bgm_mpvsocket')
```

**Импорты:** `flask`, `json`, `os`, `pathlib`, `socket`, `sys`, `tempfile`, `threading`, `time`.

## versions/prepared-media-audio-v1/wifi/__init__.py

**Импорты:** .

## versions/prepared-media-audio-v1/wifi/auto-manager.py

```python
STATUS = '/var/lib/karaoke-wifi/auto-status.json'
```

```python
LOG = '/var/log/karaoke-wifi-auto.log'
```

```python
AP = 'KARAOKE_SYSTEM'
```

```python
WAIT = 30
```

**Импорты:** `json`, `os`, `subprocess`, `time`.

## versions/prepared-media-audio-v1/wifi/captive.py

**Импорты:** `html`, `http.server`, `ipaddress`, `threading`, `urllib.parse`.

## versions/prepared-media-audio-v1/wifi/connect-worker.py

**Импорты:** `network`, `os`, `signal`, `sys`, `time`.

## versions/prepared-media-audio-v1/wifi/control_qr.py

```python
_CACHE_LOCK = threading.Lock()
```

**Импорты:** `.`, `.vendor.qrcode`, `ipaddress`, `struct`, `threading`, `zlib`.

## versions/prepared-media-audio-v1/wifi/monitor.py

**Импорты:** `captive`, `network`, `os`, `pathlib`, `signal`, `subprocess`, `sys`, `time`.

## versions/prepared-media-audio-v1/wifi/network.py

```python
STATE_DIR = Path('/var/lib/karaoke-wifi')
```

```python
OPERATION_LOCK = Path('/run/karaoke-wifi-connect.lock')
```

```python
STATION = 'wlan0'
```

```python
AP_UUID = '67e9bd92-5f2a-4bab-9645-4afe89fcfc97'
```

```python
AP_SSID = 'KARAOKE'
```

```python
AP_IP = '192.168.100.1'
```

```python
SETUP_URL = 'http://192.168.100.1:8080/wifi/setup'
```

```python
WIFI_QR = SETUP_URL
```

```python
ENV = dict(os.environ, LC_ALL='C')
```

```python
FINAL_STATES = {'success', 'failed'}
```

**Импорты:** `configparser`, `contextlib`, `fcntl`, `ipaddress`, `json`, `os`, `pathlib`, `re`, `subprocess`, `time`, `uuid`.

**Строки SQL, встречающиеся в файле:**

```sql
Delete only the deterministic UUID and full profile ID owned by this job.
```

## sources/rtl8188eus-research/build_for_x96q.py

```python
RELEASE = "6.6.44-current-sunxi64"
```

```python
CONFIG_HASH = "ebc09f1d3dba1ebc61323b0c91cbb95e1ec34f3000a0fbf88bffb724f2083123"
```

```python
INPUTS = [
    ("linux.tar.gz", "https://codeload.github.com/gregkh/linux/tar.gz/refs/tags/v6.6.44",
     "83f258ff86d40ee6c4d67ff78002309bbb824a5d7e0ad1fa793a1e00a7707cd3", "linux-6.6.44"),
    ("armbian.tar.gz", "https://codeload.github.com/sicXnull/armbian-build/tar.gz/de1a1959827c3a274d5b7d52c474e4dd373ae3ef",
     "3a7ca94c7fcb365fc22e80bfef29245c2d1e0037d37a1bcab918d0f54449a6b0", "armbian-build-de1a1959827c3a274d5b7d52c474e4dd373ae3ef"),
    ("driver.tar.gz", "https://codeload.github.com/aircrack-ng/rtl8188eus/tar.gz/af3bf004458f76b7aec33e9ba552cd382ed1f5c3",
     "7789a8d6e5f212e31a92bee1c9da41ceab1173e910503591d02762a0e95e7349", "rtl8188eus-af3bf004458f76b7aec33e9ba552cd382ed1f5c3"),
]
```

**Импорты:** `argparse`, `gzip`, `hashlib`, `os`, `pathlib`, `platform`, `shutil`, `subprocess`, `tarfile`, `tempfile`, `urllib.request`.

## sources/rtl8188eus-research/trial_bind_usb.py

```python
RELEASE = "6.6.44-current-sunxi64"
```

```python
SSH_ADDRESS = "192.168.1.102"
```

```python
BUILTIN_INTERFACE = "wlan0"
```

```python
OLD_DRIVER = "rtl8xxxu"
```

```python
NEW_DRIVER = "8188eu"
```

```python
USB_DRIVERS = Path("/sys/bus/usb/drivers")
```

```python
ENV = dict(os.environ, LC_ALL="C")
```

```python
ROLLBACK_PROGRAM = r'''"""Restore only the USB interface captured by the trial."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
STATE = json.loads((HERE / "state.json").read_text())

def driver(path):
    try:
        return (path / "driver").resolve(strict=True).name
    except FileNotFoundError:
        return None

def restore():
    path = (Path("/sys/bus/usb/devices") / STATE["usb_interface"]).resolve(strict=True)
    if ((path.parent / "idVendor").read_text().strip().lower(),
            (path.parent / "idProduct").read_text().strip().lower()) != ("0bda", "8179"):
        raise RuntimeError("USB identity changed; refusing to touch another device")
    current = driver(path)
    if current == "8188eu":
        Path("/sys/bus/usb/drivers/8188eu/unbind").write_text(STATE["usb_interface"] + "\n")
    elif current not in (None, "rtl8xxxu"):
        raise RuntimeError("Unexpected USB driver: " + repr(current))
    # Vendor disconnect resets the USB device, which may already restore binding.
    current = driver(path)
    if current is None:
        try:
            Path("/sys/bus/usb/drivers/rtl8xxxu/bind").write_text(STATE["usb_interface"] + "\n")
        except OSError:
            if driver(path) != "rtl8xxxu":
                raise
    if driver(path) != "rtl8xxxu":
        raise RuntimeError("USB did not return to rtl8xxxu")
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        names = sorted(item.name for item in (path / "net").glob("*"))
        if len(names) == 1:
            result = subprocess.run(
                ["nmcli", "--wait", "2", "device", "set", names[0],
                 "autoconnect", STATE["old_autoconnect"]],
                capture_output=True, text=True, timeout=4,
                env=dict(os.environ, LC_ALL="C"))
            if result.returncode == 0:
                print("USB restored:", names[0], "driver rtl8xxxu", flush=True)
                return
        time.sleep(0.1)
    raise RuntimeError("USB driver restored, but its NetworkManager flag was not restored")

with (HERE / "rollback.lock").open("a") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    with (HERE / "rollback.log").open("a", buffering=1) as log:
        try:
            restore()
            log.write("USB rollback completed\n")
        except Exception as error:
            log.write("USB rollback failed: " + repr(error) + "\n")
            raise
'''
```

**Импорты:** `argparse`, `ipaddress`, `json`, `os`, `pathlib`, `platform`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, `time`, `uuid`.

## sources/rtl8188eus-research/permanent/install_on_x96q.py

```python
RELEASE = "6.6.44-current-sunxi64"
```

```python
SHA256 = "d1c545d580901e3bd85504d7c970a729383aaf75b3217724a4940c3b4e353bc3"
```

```python
USB = "wlxf0b040f7f699"
```

```python
PROFILE = "67e9bd92-5f2a-4bab-9645-4afe89fcfc97"
```

```python
TIMER = "rtl8188eus-rollback-ca123d7e5cc7.timer"
```

```python
SOURCE = Path("/root/rtl8188eus-build-xs4977k0/8188eu-test.ko")
```

```python
MODULE = Path("/lib/modules") / RELEASE / "updates/drivers/net/wireless/8188eu.ko"
```

```python
HERE = Path(__file__).resolve().parent
```

```python
ENV = dict(os.environ, LC_ALL="C")
```

```python
FILES = [
    (HERE / "rtl8188eu-bind.py", Path("/usr/local/libexec/rtl8188eu-bind.py"), 0o755),
    (HERE / "rtl8188eu-bind.service", Path("/etc/systemd/system/rtl8188eu-bind.service"), 0o644),
    (HERE / "8188eu-power.conf", Path("/etc/modprobe.d/8188eu-power.conf"), 0o644),
    (HERE / "80-rtl8188eu-bind.rules", Path("/etc/udev/rules.d/80-rtl8188eu-bind.rules"), 0o644),
    (SOURCE, MODULE, 0o644),
]
```

```python
CHANGES = {
    "connection.id": "KARAOKE_USB_AP",
    "connection.autoconnect": "yes",
    "connection.autoconnect-priority": "100",
    "802-11-wireless.ssid": "KARAOKE",
    "802-11-wireless.cloned-mac-address": "permanent",
    "802-11-wireless-security.psk": "12345678",
    "ipv4.addresses": "192.168.100.1/24",
}
```

**Импорты:** `configparser`, `hashlib`, `json`, `os`, `pathlib`, `platform`, `shutil`, `subprocess`, `tempfile`.

## sources/rtl8188eus-research/permanent/rtl8188eu-bind.py

```python
RELEASE = "6.6.44-current-sunxi64"
```

```python
MODULE_SHA256 = "d1c545d580901e3bd85504d7c970a729383aaf75b3217724a4940c3b4e353bc3"
```

```python
USB_BUS = Path("/sys/bus/usb/devices")
```

```python
DRIVERS = Path("/sys/bus/usb/drivers")
```

**Импорты:** `fcntl`, `hashlib`, `pathlib`, `platform`, `subprocess`, `sys`.

**Строки SQL, встречающиеся в файле:**

```sql
Select 8188eu for the single 0bda:8179 USB adapter; leave NM profiles alone.
```

## sources/karaoke-wifi-integration/media-audio-v1/install.py

```python
ROOT = Path('/root/karaoke')
```

```python
WRAPPER = Path('/usr/local/bin/play_karaoke.sh')
```

```python
DB = Path('/data/karaoke/db/karaoke.db')
```

```python
MARKER = ROOT / '.media-audio-installing'
```

```python
SERVICE = 'karaoke-server.service'
```

**Импорты:** `ast`, `hashlib`, `importlib`, `json`, `os`, `parts`, `pathlib`, `re`, `shutil`, `socket`, `sqlite3`, `subprocess`, `sys`, `tempfile`, `time`, `urllib.request`.

## sources/karaoke-wifi-integration/media-audio-v1/parts.py

```python
BOOTSTRAP = '''
# KARAOKE_MEDIA_AUDIO_V1
from functools import wraps
from flask import g
import karaoke_audio_output as audio_output
from karaoke_media_optimizer import MediaOptimizer, create_blueprint as media_blueprint

def _maintenance_player_active():
    if globals().get('_player_state', {}).get('playing'):
        return True
    if os.path.exists('/tmp/mpvsocket'):
        try:
            return audio_output.ipc('/tmp/mpvsocket', ['get_property', 'idle-active']) is not True
        except (FileNotFoundError, ConnectionRefusedError):
            return False
        except (OSError, ValueError, RuntimeError):
            return True
    return False

def _media_changed():
    socketio.emit('db_update', {'optimized': True})
    broadcast_state('queue_update')

media_optimizer = MediaOptimizer(UPLOAD_FOLDER, DB_NAME,
    is_playing=_maintenance_player_active, changed=_media_changed)
media_optimizer.recovery_error = ''

def _media_refresh_guard(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        with media_optimizer.lock:
            if media_optimizer.recovery_error:
                raise RuntimeError(media_optimizer.recovery_error)
            if not media_optimizer.loaded:
                media_optimizer.load()
            if media_optimizer.repairing:
                return {'added': 0, 'removed': 0, 'duplicates_fixed': 0}
            return function(*args, **kwargs)
    return guarded

def _media_play_guard(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        with media_optimizer.lock:
            if media_optimizer.repairing or media_optimizer.recovery_error:
                raise RuntimeError('Идёт исправление медиатеки. Дождитесь завершения.')
            with audio_output.lock:
                result = function(*args, **kwargs)
                if platform.system() != 'Windows':
                    audio_output.wait_ready('/tmp/mpvsocket')
                return result
    return guarded

def _audio_start_guard(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        with audio_output.lock:
            result = function(*args, **kwargs)
            if globals().get('bgm_process') is not None:
                audio_output.wait_ready('/tmp/bgm_mpvsocket')
            return result
    return guarded

def _media_queue_guard(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        with media_optimizer.lock:
            if media_optimizer.repairing or media_optimizer.recovery_error:
                return None
            return function(*args, **kwargs)
    return guarded

bgm_start = _audio_start_guard(bgm_start)
'''
```

```python
REGISTRATION = '''
app.register_blueprint(media_blueprint(media_optimizer))
app.register_blueprint(audio_output.create_blueprint())

@app.before_request
def _media_request_guard():
    mutations = {'play', 'upload', 'api_files_delete', 'refresh_after_upload',
                 'settings_refresh_db', 'queue_add', 'queue_next', 'queue_remove', 'queue_move',
                 'queue_clear', 'api_next', 'api_format_hdd'}
    external = request.method not in ('GET', 'HEAD', 'OPTIONS') and (
        '.' in (request.endpoint or '') and (request.endpoint or '').split('.')[0] not in {'media_optimizer', 'audio_output'})
    changing = request.endpoint in mutations or external or (
        request.method == 'POST' and (request.endpoint or '').split('.')[0] in {'media_optimizer', 'audio_output'})
    try:
        installing = 0 <= time.time() - os.path.getmtime('/root/karaoke/.media-audio-installing') < 300
    except OSError:
        installing = False
    if installing and changing:
        return jsonify({'error': 'Идёт обновление программы. Повторите через несколько секунд.'}), 409
    if request.endpoint not in mutations and not external:
        return None
    media_optimizer.lock.acquire()
    try:
        if not media_optimizer.loaded:
            media_optimizer.load()
    except Exception as exc:
        media_optimizer.lock.release()
        return jsonify({'error': str(exc)}), 409
    if media_optimizer.repairing or media_optimizer.recovery_error:
        media_optimizer.lock.release()
        return jsonify({'error': media_optimizer.recovery_error or
                        'Идёт исправление медиатеки. Дождитесь завершения.'}), 409
    g.media_optimization_lock = True

@app.teardown_request
def _media_release_guard(error=None):
    if g.pop('media_optimization_lock', False):
        media_optimizer.lock.release()
'''
```

```python
AUDIO_HTML = '''      <div class="bgm-section" id="audio-output-area">
        <h3>Вывод звука</h3>
        <p id="audio-output-status" style="color:#cbd5e1">Проверяем выход звука…</p>
        <button class="btn" type="button" id="audio-output-toggle" onclick="toggleAudioOutput()" disabled>Отключить HDMI — только аналоговый выход</button>
        <p style="color:#aaa;font-size:13px">Настройка действует на видео и фоновую музыку.</p>
      </div>
'''
```

```python
AUDIO_JS = '''    /* KARAOKE_AUDIO_OUTPUT_V1 */
    var audioOutputBusy = false, audioOutputState = null;
    function audioOutputRequest(value) {
      if (audioOutputBusy) return;
      audioOutputBusy = true;
      var button = document.getElementById('audio-output-toggle');
      var status = document.getElementById('audio-output-status');
      button.disabled = true;
      var xhr = new XMLHttpRequest();
      var finished = false;
      function done(message, data) {
        if (finished) return;
        finished = true; audioOutputBusy = false;
        if (data) audioOutputState = data;
        if (message) { status.textContent = message; status.style.color = '#f87171'; }
        else {
          status.textContent = data.analog_only ? 'Звук только на аналоговом выходе. HDMI отключён.' : 'Звук на HDMI.';
          if (!data.verified) status.textContent += ' ' + (data.error || 'Выход работающего плеера отличается от сохранённой настройки.');
          status.style.color = data.verified ? '#4ade80' : '#fbbf24';
        }
        button.disabled = !audioOutputState || !audioOutputState.available;
        button.textContent = audioOutputState && audioOutputState.analog_only ? 'Включить звук HDMI' : 'Отключить HDMI — только аналоговый выход';
      }
      xhr.open(value === null ? 'GET' : 'POST', '/api/audio/output', true);
      xhr.timeout = 20000;
      xhr.onload = function() {
        try {
          var data = JSON.parse(xhr.responseText);
          if (xhr.status !== 200 || !data.ok) { done(data.error || 'Не удалось переключить выход.'); return; }
          done(null, data);
        } catch(e) { done('Не удалось прочитать состояние звука.'); }
      };
      xhr.onerror = xhr.ontimeout = function() { done('Нет ответа от приставки. Откройте настройки ещё раз для проверки.'); };
      if (value !== null) xhr.setRequestHeader('Content-Type', 'application/json');
      try { xhr.send(value === null ? null : JSON.stringify({analog_only: value})); }
      catch(e) { done('Не удалось отправить запрос.'); }
    }
    function toggleAudioOutput() {
      if (audioOutputState && !audioOutputBusy) audioOutputRequest(!audioOutputState.analog_only);
    }
'''
```

**Импорты:** .
