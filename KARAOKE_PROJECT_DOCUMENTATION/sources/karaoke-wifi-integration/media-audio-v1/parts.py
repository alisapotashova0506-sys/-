"""Exact V5 -> media maintenance and independent ALSA routing integration."""
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

AUDIO_HTML = '''      <div class="bgm-section" id="audio-output-area">
        <h3>Вывод звука</h3>
        <p id="audio-output-status" style="color:#cbd5e1">Проверяем выход звука…</p>
        <button class="btn" type="button" id="audio-output-toggle" onclick="toggleAudioOutput()" disabled>Отключить HDMI — только аналоговый выход</button>
        <p style="color:#aaa;font-size:13px">Настройка действует на видео и фоновую музыку.</p>
      </div>
'''

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


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise RuntimeError('Не найдена ожидаемая часть приложения: ' + before[:60])
    return text.replace(before, after, 1)


def patch(data):
    source = data.decode('utf-8')
    source = replace_once(source, "POSTER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}\n",
                         "POSTER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}\n" + BOOTSTRAP)
    source = replace_once(source, "['mpv', '--no-video', '--loop-playlist', '--volume=' + str(bgm_volume),",
                         "['mpv'] + audio_output.player_args() + ['--no-video', '--loop-playlist', '--volume=' + str(bgm_volume),")
    source = replace_once(source, 'def refresh_database():\n', '@_media_refresh_guard\ndef refresh_database():\n')
    source = replace_once(source, 'def play_video_file(path):\n', '@_media_play_guard\ndef play_video_file(path):\n')
    source = replace_once(source, 'def _advance_queue_after_end():\n', '@_media_queue_guard\ndef _advance_queue_after_end():\n')
    source = replace_once(source, "    if '-' in name:\n        parts = name.split('-', 1)",
                         "    if ' - ' in name:\n        parts = name.split(' - ', 1)\n        return parts[0].strip(), parts[1].strip()\n    if '-' in name:\n        parts = name.split('-', 1)")
    source = replace_once(source, "            c.execute('INSERT OR IGNORE INTO songs (artist, title, file, plays) VALUES (?, ?, ?, 0)', (artist, title, fname))\n            if c.rowcount > 0:\n                added += 1",
                         "            existing = c.execute('SELECT artist,title FROM songs WHERE file=?', (fname,)).fetchone()\n            if existing is None:\n                c.execute('INSERT INTO songs (artist,title,file,plays) VALUES(?,?,?,0)', (artist,title,fname))\n                added += 1\n            elif existing['artist'] != artist or existing['title'] != title:\n                c.execute('UPDATE songs SET artist=?,title=? WHERE file=?', (artist,title,fname))")
    source = replace_once(source, '<div style="color:#aaa;margin:10px 0">Медиатека обновляется автоматически.</div>',
                         '<div style="color:#aaa;margin:10px 0">Медиатека обновляется автоматически.</div>\n      <a class="btn" href="/video-optimization" style="display:inline-block;margin:6px;text-decoration:none">Оптимизация видеофайлов</a>')
    source = replace_once(source, '      <div class="bgm-section">\n        <h3>Управление файлами</h3>',
                         AUDIO_HTML + '      <div class="bgm-section">\n        <h3>Управление файлами</h3>')
    source = replace_once(source, '    function loadBgmTracks() {', AUDIO_JS + '\n    function loadBgmTracks() {')
    source = replace_once(source, "      loadSettings();\n      try {", "      loadSettings();\n      audioOutputRequest(null);\n      try {")
    source = replace_once(source, 'app.register_blueprint(quarantine_bp)\n',
                         'app.register_blueprint(quarantine_bp)\n' + REGISTRATION)
    source = replace_once(source, '    quarantine_init()\n    if os.path.ismount',
                         "    quarantine_init()\n    try:\n        with media_optimizer.lock:\n            media_optimizer.load()\n    except Exception as exc:\n        if os.path.ismount('/mnt/usb_disk'):\n            media_optimizer.recovery_error = 'Не завершено восстановление медиатеки: ' + str(exc)\n        logger.error('Media maintenance startup: %s', exc)\n    if os.path.ismount")
    source = replace_once(source, "    if os.path.ismount('/mnt/usb_disk'):\n        refresh_database()",
                         "    if os.path.ismount('/mnt/usb_disk') and not media_optimizer.recovery_error:\n        refresh_database()")
    return source.encode('utf-8')


def patch_wrapper(data):
    source = data.decode('utf-8')
    source = replace_once(source, 'mpv --vo=gpu',
        'AUDIO_DEVICE=$(/usr/bin/python3 /root/karaoke/karaoke_audio_output.py --device) || exit 1\nmpv --vo=gpu')
    source = replace_once(source, '--audio-device=alsa/plughw:1,0', '--audio-device="$AUDIO_DEVICE"')
    return source.encode('utf-8')
