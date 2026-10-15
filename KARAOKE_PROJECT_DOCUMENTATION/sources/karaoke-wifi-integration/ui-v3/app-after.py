import json
import os
import shutil
import time
import threading

_manual_stop = False
import re
import sqlite3
import hashlib
import logging
import socket
import subprocess
import platform
from flask import Flask, render_template_string, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from wifi import network as wifi_network
import ipaddress




UPLOAD_FOLDER = '/mnt/usb_disk/karaoke_media'
POSTER_FOLDER = '/mnt/usb_disk/posters'
FONSOUND_FOLDER = '/mnt/usb_disk/fonsound'








# === Серверный BGM-плеер (mpv) ===
import subprocess, signal, json as _json
bgm_process = None
bgm_enabled = True
BGM_SETTINGS_FILE = '/root/karaoke/.bgm_settings.json'

def load_bgm_settings():
    try:
        import json
        with open(BGM_SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'volume': 25, 'enabled': True, 'video_volume': 80}

_bgm_settings = load_bgm_settings()
bgm_volume = _bgm_settings.get('volume', 25)
bgm_enabled = _bgm_settings.get('enabled', True)
video_volume = _bgm_settings.get('video_volume', 80)

def save_bgm_settings():
    try:
        import json
        with open(BGM_SETTINGS_FILE, 'w') as f:
            json.dump({'volume': bgm_volume, 'enabled': bgm_enabled, 'video_volume': video_volume}, f)
    except:
        pass

def bgm_get_tracks():
    if not os.path.exists(FONSOUND_FOLDER):
        return []
    return sorted([f for f in os.listdir(FONSOUND_FOLDER) if f.endswith('.mp3')])

def bgm_start():
    global bgm_process
    bgm_stop()
    tracks = bgm_get_tracks()
    if not tracks or not bgm_enabled:
        return
    playlist_file = '/tmp/bgm_playlist.txt'
    fonsound_abs = os.path.abspath(FONSOUND_FOLDER)
    with open(playlist_file, 'w') as pf:
        for t in tracks:
            pf.write(os.path.join(fonsound_abs, t) + '\n')
    try:
        os.remove('/tmp/bgm_mpvsocket')
    except:
        pass
    bgm_process = subprocess.Popen(
        ['mpv', '--no-video', '--loop-playlist', '--volume=' + str(bgm_volume),
         '--playlist=' + playlist_file, '--really-quiet',
         '--input-ipc-server=/tmp/bgm_mpvsocket'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def bgm_stop():
    global bgm_process
    if bgm_process:
        try:
            bgm_process.terminate()
            bgm_process.wait(timeout=3)
        except:
            pass
        bgm_process = None
    # Запасной вариант: убиваем все mpv с нашим плейлистом
    try:
        subprocess.run(['pkill', '-9', '-f', 'bgm_playlist'], capture_output=True, timeout=2)
    except:
        pass
    try:
        os.remove('/tmp/bgm_mpvsocket')
    except:
        pass

def bgm_set_volume(vol):
    global bgm_volume
    bgm_volume = int(vol)
    save_bgm_settings()
    if bgm_process:
        # Пытаемся через IPC-сокет BGM (без перезапуска)
        try:
            import socket as _sock
            s = _sock.socket(_sock.AF_UNIX, _sock.SOCK_STREAM)
            s.settimeout(1)
            s.connect('/tmp/bgm_mpvsocket')
            s.sendall(('{"command":["set_property","volume",' + str(int(vol)) + ']}\n').encode())
            s.recv(1024)
            s.close()
            return
        except:
            pass
        # Запасной вариант: перезапуск с новой громкостью
        bgm_start()

def video_set_volume(vol):
    global video_volume
    video_volume = int(vol)
    save_bgm_settings()
    # Меняем громкость видео-плеера через IPC-сокет
    try:
        import socket as _sock
        s = _sock.socket(_sock.AF_UNIX, _sock.SOCK_STREAM)
        s.settimeout(2)
        s.connect('/tmp/mpvsocket')
        cmd = '{"command":["set_property","volume",' + str(int(vol)) + ']}\n'
        s.sendall(cmd.encode())
        s.recv(1024)
        s.close()
    except Exception:
        pass
import os
DB_DIR = "/data/karaoke/db"
os.makedirs(DB_DIR, exist_ok=True)
DB_NAME = os.path.join(DB_DIR, "karaoke.db")
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
POSTER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(POSTER_FOLDER, exist_ok=True)
os.makedirs(FONSOUND_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS songs (id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT NOT NULL, title TEXT NOT NULL, file TEXT NOT NULL UNIQUE, plays INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY AUTOINCREMENT, song_id INTEGER NOT NULL, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (song_id) REFERENCES songs(id))")
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def get_network_status():
    state = wifi_network.read_status()
    return {
        'status': 'connected' if state.get('connected') else 'disconnected',
        'ip': state.get('ip') or '0.0.0.0',
        'ssid': state.get('network') or 'Нет подключения',
    }


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    parts = filename.rsplit('.', 1)
    if len(parts) < 2:
        return False
    ext = parts[1].lower()
    return ext in ALLOWED_EXTENSIONS

def parse_filename(filename):
    name = os.path.splitext(filename)[0]
    if '-' in name:
        parts = name.split('-', 1)
        return parts[0].strip(), parts[1].strip()
    return "Unknown", name

def find_poster(artist):
    if not artist:
        return None
    search_names = {artist}
    if '_' in artist:
        search_names.add(artist.replace('_', ' '))
    if ' ' in artist:
        search_names.add(artist.replace(' ', '_'))
    for name in search_names:
        for ext in POSTER_EXTENSIONS:
            path = os.path.join(POSTER_FOLDER, name + '.' + ext)
            if os.path.exists(path):
                return name + '.' + ext
    return None

def safe_filename(filename):
    if not filename:
        return ''
    clean = re.sub(r'[/:*?"<>|]', '_', filename)
    if not clean:
        clean = 'file_unknown'
    return clean

def file_hash_quick(path, chunk_size=1024*1024):
    try:
        size = os.path.getsize(path)
        h = hashlib.md5()
        with open(path, 'rb') as f:
            data = f.read(chunk_size)
            if data:
                h.update(data)
            f.seek(max(0, size - chunk_size))
            data = f.read(chunk_size)
            if data:
                h.update(data)
        return h.hexdigest() + '_' + str(size)
    except Exception:
        return ''

def refresh_database():
    if not os.path.ismount('/mnt/usb_disk') or not os.path.isdir(UPLOAD_FOLDER):
        raise RuntimeError('HDD не смонтирован: база не изменена')
    conn = get_db()
    c = conn.cursor()
    added = 0
    removed = 0
    duplicates_fixed = 0
    for fname in os.listdir(UPLOAD_FOLDER):
        if not allowed_file(fname):
            continue
        full_path = os.path.join(UPLOAD_FOLDER, fname)
        if not os.path.isfile(full_path):
            continue
        artist, title = parse_filename(fname)
        if quarantine_mentions(fname):
            continue
        try:
            c.execute('INSERT OR IGNORE INTO songs (artist, title, file, plays) VALUES (?, ?, ?, 0)', (artist, title, fname))
            if c.rowcount > 0:
                added += 1
        except Exception as e:
            logger.error(f"Error adding {fname}: {e}")
    c.execute('SELECT id, file FROM songs')
    rows = c.fetchall()
    for row in rows:
        file_path = os.path.join(UPLOAD_FOLDER, row['file'])
        if not os.path.exists(file_path):
            c.execute('DELETE FROM queue WHERE song_id = ?', (row['id'],))
            c.execute('DELETE FROM songs WHERE id = ?', (row['id'],))
            removed += 1
    c.execute('SELECT file, COUNT(*) as cnt, MIN(id) as keep_id FROM songs GROUP BY file HAVING cnt > 1')
    dup_rows = c.fetchall()
    for row in dup_rows:
        c.execute('DELETE FROM songs WHERE file = ? AND id != ?', (row['file'], row['keep_id']))
        duplicates_fixed += (row['cnt'] - 1)
    conn.commit()
    conn.close()
    logger.info(f'DB refreshed: {added} added, {removed} removed, {duplicates_fixed} duplicates fixed')
    return {'added': added, 'removed': removed, 'duplicates_fixed': duplicates_fixed}

def find_player():
    if platform.system() == "Windows":
        for cmd in ['mpv', 'ffplay']:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, timeout=3)
                return cmd
            except Exception:
                pass
        return None
    else:
        return 'mpv'

def kill_existing_players():
    """Останавливаем только караоке mpv, не затрагивая BGM."""
    send_mpv_command(["quit"])
    for _ in range(10):
        if not os.path.exists('/tmp/mpvsocket'):
            break
        time.sleep(0.05)





def get_media_stats():
    """Подсчитывает количество файлов и общий размер в папках медиа"""
    folders = {
        'tracks': UPLOAD_FOLDER,
        'posters': POSTER_FOLDER,
        'bgm': FONSOUND_FOLDER
    }
    
    stats = {
        'tracks_count': 0,
        'posters_count': 0,
        'total_size_bytes': 0
    }

    # Считаем треки
    if os.path.exists(folders['tracks']):
        for f in os.listdir(folders['tracks']):
            path = os.path.join(folders['tracks'], f)
            if os.path.isfile(path):
                stats['tracks_count'] += 1
                stats['total_size_bytes'] += os.path.getsize(path)

    # Считаем постеры
    if os.path.exists(folders['posters']):
        for f in os.listdir(folders['posters']):
            path = os.path.join(folders['posters'], f)
            if os.path.isfile(path):
                stats['posters_count'] += 1
                stats['total_size_bytes'] += os.path.getsize(path)

    # Считаем фоновую музыку
    if os.path.exists(folders['bgm']):
        for f in os.listdir(folders['bgm']):
            path = os.path.join(folders['bgm'], f)
            if os.path.isfile(path):
                stats['total_size_bytes'] += os.path.getsize(path)

    return stats







_play_generation = [0]

def play_video_file(path):
    _play_generation[0] += 1
    player = find_player()
    if platform.system() == "Windows":
        if player == 'mpv':
            subprocess.run(['mpv', '--fullscreen', '--no-keep-open', path], timeout=None)
        elif player == 'ffplay':
            subprocess.run(['ffplay', '-autoexit', '-fs', path], timeout=None)
        else:
            os.startfile(path)
    else:
        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        env['XAUTHORITY'] = '/root/.Xauthority'
        if player == 'ffplay':
            subprocess.Popen(['ffplay', '-autoexit', path], env=env)
        else:
            # Проверяем — может mpv уже запущен и живой?
            mpv_running = False
            if os.path.exists('/tmp/mpvsocket'):
                try:
                    result = subprocess.run(['pgrep', '-x', 'mpv'], capture_output=True, timeout=2)
                    if result.returncode == 0:
                        import socket, json
                        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        s.settimeout(2)
                        s.connect('/tmp/mpvsocket')
                        cmd = json.dumps({"command": ["loadfile", path]}) + "\n"
                        # Ставим сохранённую громкость
                        vol_cmd = json.dumps({"command": ["set_property", "volume", video_volume]}) + "\n"
                        s.sendall(vol_cmd.encode())
                        try:
                            s.recv(4096)
                        except Exception:
                            pass
                        s.sendall(cmd.encode())
                        try:
                            s.recv(4096)
                        except Exception:
                            pass
                        s.close()
                        mpv_running = True
                    else:
                        os.remove('/tmp/mpvsocket')
                except Exception:
                    mpv_running = False

            if not mpv_running:
                # Первый запуск — запускаем wrapper
                proc = subprocess.Popen(['/usr/local/bin/play_karaoke.sh', path], env=env)
                current_generation = _play_generation[0]
                def _wait_and_notify(p, generation):
                    global _manual_stop
                    p.wait()
                    try:
                        os.remove('/tmp/mpvsocket')
                    except FileNotFoundError:
                        pass
                    if not _manual_stop and generation == _play_generation[0]:
                        _player_state.update(playing=False, paused=False, file='', artist='', title='')
                        socketio.emit('song_ended', {})
                        try:
                            with app.app_context():
                                _advance_queue_after_end()
                        except Exception:
                            logger.exception('Automatic queue advance failed')
                    _manual_stop = False
                threading.Thread(target=_wait_and_notify, args=(proc, current_generation), daemon=True).start()


def broadcast_state(event='state_update'):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file FROM queue q JOIN songs s ON q.song_id = s.id ORDER BY q.added_at ASC, q.id ASC')
        rows = c.fetchall()
        conn.close()
        queue = []
        for r in rows:
            queue.append({'queue_id': r['queue_id'], 'song_id': r['song_id'], 'artist': r['artist'], 'title': r['title'], 'file': r['file']})
        socketio.emit(event, {'queue': queue})
    except Exception as e:
        logger.error(f"broadcast_state error: {e}")


HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Караоке</title>
  <link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
  <style>
    html, body { cursor: pointer !important; }
    body { margin: 0; padding: 0; background: #1a2a40; color: white; font-family: sans-serif; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
    h1 { font-family: 'Pacifico', cursive; font-size: 126px; text-align: center; margin: 8px 0; color: #ff0000; font-weight: bold; text-shadow: 0 0 15px rgba(255,0,0,0.5), 0 0 30px rgba(255,0,0,0.2); letter-spacing: 20px; position: relative; }
    .top-right-tools { position: absolute; right: 20px; top: 15px; display: flex; gap: 15px; align-items: center; z-index: 100; }
    .icon-btn { cursor: pointer; transition: transform 0.2s, color 0.2s; position: relative; }
    .icon-btn:hover { transform: scale(1.15); }
    #settings-btn { color: white; }
    .slider-section { padding: 0 20px 10px; position: relative; }
    .slider-wrap { position: relative; display: flex; align-items: center; gap: 8px; }
    .slider { display: flex; gap: 12px; overflow-x: auto; scroll-behavior: smooth; padding: 8px 4px; scrollbar-width: none; flex: 1; }
    .slider::-webkit-scrollbar { display: none; }
    .poster-card { flex: 0 0 110px; width: 110px; height: 110px; border-radius: 12px; overflow: hidden; cursor: pointer; position: relative; background: rgba(255,255,255,0.1); border: 2px solid transparent; transition: transform 0.2s, border-color 0.2s; }
    .poster-card:hover { transform: scale(1.08); border-color: #4facfe; }
    .poster-card img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .poster-card .poster-name { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.7); padding: 4px 6px; font-size: 11px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .poster-card .poster-plays { position: absolute; top: 4px; right: 4px; background: rgba(0,0,0,0.7); padding: 2px 6px; border-radius: 8px; font-size: 11px; color: #4facfe; }
    .poster-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 36px; color: rgba(255,255,255,0.4); }
    .slider-btn { flex: 0 0 36px; width: 36px; height: 36px; border-radius: 50%; border: none; background: rgba(255,255,255,0.15); color: white; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
    .slider-btn:hover { background: rgba(255,255,255,0.3); }
    .controls { padding: 8px 20px; display: flex; gap: 10px; }
    input[type="text"] { flex: 1; padding: 12px; border-radius: 8px; border: none; background: rgba(255,255,255,0.2); color: white; font-size: 16px; outline: none; }
    input[type="text"]::placeholder { color: rgba(255,255,255,0.5); }
    .main-area { flex: 1; display: flex; gap: 0; overflow: hidden; padding: 10px 20px; }
    .left-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .right-panel { flex: 0 0 480px; display: flex; flex-direction: column; overflow: hidden; margin-left: 10px; background: rgba(0,0,0,0.15); border-radius: 10px; }
    .panel-header { font-size: 18px; font-weight: bold; padding: 10px 14px; color: #4facfe; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
    .list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding: 10px; }
    .item { background: rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 8px; display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 16px; transition: background 0.15s; }
    .item:hover { background: rgba(255,255,255,0.2); }
    .item .play-icon { color: #4facfe; font-size: 16px; flex: 0 0 auto; }
    .artist { font-weight: bold; color: #fff; }
    .dash { color: #4facfe; font-weight: bold; }
    .title { opacity: 0.9; }
    .plays { margin-left: auto; font-size: 13px; color: #aaa; }
    .queue-btn { flex: 0 0 auto; background: rgba(79,172,254,0.2); border: 1px solid #4facfe; color: #4facfe; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 13px; font-weight: bold; transition: background 0.15s; }
    .queue-btn:hover { background: rgba(79,172,254,0.4); }
    .queue-btn.added { background: #10b981; border-color: #10b981; color: white; }
    .hint { padding: 12px; color: #888; text-align: center; }
    .queue-item { background: rgba(255,255,255,0.06); padding: 10px 12px; border-radius: 8px; display: flex; align-items: center; gap: 8px; font-size: 15px; transition: background 0.15s; }
    .queue-item:hover { background: rgba(255,255,255,0.15); }
    .queue-item .q-num { flex: 0 0 24px; width: 24px; height: 24px; border-radius: 50%; background: #4facfe; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; }
    .queue-item .q-text { flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    .queue-item .q-artist { font-weight: bold; }
    .queue-item .q-remove { flex: 0 0 auto; background: rgba(239,68,68,0.2); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; padding: 2px 8px; cursor: pointer; font-size: 13px; transition: background 0.15s; }
    .queue-item .q-remove:hover { background: rgba(239,68,68,0.5); }
    .queue-item .q-move { flex: 0 0 auto; background: rgba(79,172,254,0.15); border: 1px solid rgba(79,172,254,0.4); color: #4facfe; border-radius: 6px; padding: 2px 6px; cursor: pointer; font-size: 14px; line-height: 1; transition: background 0.15s; }
    .queue-item .q-move:hover { background: rgba(79,172,254,0.4); }
    .queue-item .q-move:disabled { opacity: 0.3; cursor: default; }
    .fm-list { max-height: 400px; overflow-y: auto; border-radius: 8px; background: rgba(0,0,0,0.2); }
    .fm-item { display: flex; align-items: center; padding: 8px 10px; border-bottom: 1px solid #333; gap: 10px; }
    .fm-item:hover { background: rgba(255,255,255,0.05); }
    .fm-item-icon { flex: 0 0 28px; font-size: 18px; text-align: center; }
    .fm-item-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
    .fm-item-size { flex: 0 0 55px; font-size: 11px; color: #888; text-align: right; }
    .fm-item-del { flex: 0 0 auto; background: rgba(239,68,68,0.2); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; padding: 4px 8px; cursor: pointer; font-size: 13px; transition: background 0.15s; }
    .fm-item-del:hover { background: rgba(239,68,68,0.5); }
    .fm-queue-badge { flex: 0 0 auto; font-size: 10px; color: #f59e0b; background: rgba(245,158,11,0.15); border-radius: 4px; padding: 2px 6px; }
    .queue-empty { padding: 20px; color: #888; text-align: center; font-size: 14px; }
    .queue-clear-btn { background: rgba(239,68,68,0.15); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 13px; font-weight: bold; }
    .queue-clear-btn:hover { background: rgba(239,68,68,0.3); }
    #remote-info { text-align: center; padding: 6px 12px; background: rgba(79,172,254,0.1); border: 1px solid rgba(79,172,254,0.25); border-radius: 8px; margin: 0 auto 8px; font-size: 15px; color: #8ec5fc; max-width: 600px; }
    #remote-info b { color: #4facfe; }
    #now-playing { position: fixed; bottom: 12px; right: 20px; background: rgba(0,0,0,0.8); padding: 8px 16px; border-radius: 8px; font-size: 14px; color: #4ade80; display: none; z-index: 200; }
    .upload-tabs { display: flex; gap: 10px; justify-content: center; margin-bottom: 12px; }
    .upload-tab { padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; background: rgba(255,255,255,0.1); }
    .upload-tab.active { background: #4facfe; color: white; font-weight: bold; }
    .btn { padding: 12px 20px; background: #4facfe; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
    .btn:hover { background: #3a9cf0; }
    #refresh-btn { background: #10b981; display: block; margin: 0 auto; text-align: center; }
    #refresh-btn:hover { background: #0e9e72; }
    .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); }
    .modal-content { background-color: #1e293b; margin: 5% auto; padding: 25px; border-radius: 12px; width: 520px; max-width: 90%; max-height: 85vh; overflow-y: auto; }
    .close { float: right; font-size: 28px; font-weight: bold; cursor: pointer; color: #aaa; }
    .close:hover { color: #fff; }
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
    .stat-card { background: #334155; padding: 12px; border-radius: 8px; text-align: center; }
    .network-section { margin-top: 20px; padding-top: 20px; border-top: 1px solid #475569; }
    .network-info { display: flex; justify-content: space-between; margin: 8px 0; }
    .ip-addr { font-family: monospace; color: #64b5f6; font-weight: bold; }
    .wifi-settings-area { margin-top: 20px; padding-top: 20px; border-top: 1px solid #333; }
    .wifi-settings-area h3 { margin-top: 0; color: #fff; margin-bottom: 12px; }
    .wifi-current { font-size: 13px; color: #8ec5fc; margin-bottom: 10px; }
    .wifi-list { max-height: 200px; overflow-y: auto; border: 1px solid #333; border-radius: 8px; margin-bottom: 10px; }
    .wifi-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; border-bottom: 1px solid #222; cursor: pointer; }
    .wifi-item:hover { background: rgba(79,172,254,0.1); }
    .wifi-item.active { background: rgba(16,185,129,0.1); }
    .wifi-ssid { font-weight: 500; color: #fff; font-size: 14px; }
    .wifi-info { font-size: 12px; color: #888; }
    .wifi-signal { font-size: 12px; color: #4facfe; min-width: 40px; text-align: right; }
    .wifi-input { width: 100%; padding: 8px 12px; background: #0f172a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; margin-bottom: 8px; box-sizing: border-box; }
    .wifi-btn { padding: 8px 20px; background: #3b82f6; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
    .wifi-btn:hover { background: #2563eb; }
    .wifi-msg { font-size: 13px; margin-top: 8px; padding: 8px; border-radius: 6px; display: none; }
    .wifi-msg.ok { background: rgba(16,185,129,0.1); color: #4ade80; display: block; }
    .wifi-msg.err { background: rgba(239,68,68,0.1); color: #f87171; display: block; }

    .upload-settings-area { margin-top: 20px; padding-top: 20px; border-top: 1px solid #333; }
    .upload-settings-area h3 { margin-top: 0; color: #fff; }
    .upload-btn-wrap { text-align: center; margin-top: 10px; }
    .bgm-section { margin-top: 20px; padding-top: 20px; border-top: 1px solid #475569; }
    .bgm-row { display: flex; align-items: center; justify-content: space-between; margin: 10px 0; }
    .toggle-switch { position: relative; width: 50px; height: 26px; }
    .toggle-switch input { opacity: 0; width: 0; height: 0; }
    .toggle-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #555; border-radius: 26px; transition: 0.3s; }
    .toggle-slider:before { content: ""; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; }
    .toggle-switch input:checked + .toggle-slider { background: #10b981; }
    .toggle-switch input:checked + .toggle-slider:before { transform: translateX(24px); }
    .volume-slider { width: 100%; margin-top: 8px; }
    .player-controls { display: flex; gap: 8px; padding: 10px; border-top: 1px solid rgba(255,255,255,0.1); }
    .ctrl-btn { flex: 1; padding: 10px 6px; border-radius: 8px; border: none; cursor: pointer; font-size: 14px; font-weight: bold; color: white; transition: opacity 0.15s; }
    .ctrl-btn:hover { opacity: 0.85; }
    .stop-btn { background: #ef4444; }
    .pause-btn { background: #f59e0b; }
    .next-btn { background: #4facfe; }

    /* ===== Экранная клавиатура ===== */
    #osk-overlay {
      display: none;
      position: fixed;
      bottom: 12px;
      right: 12px;
      left: auto;
      width: min(720px, calc(100vw - 24px));
      max-width: calc(100vw - 24px);
      box-sizing: border-box;
      border-radius: 12px;
      background: rgba(15,20,35,0.98);
      padding: 8px 10px 14px;
      z-index: 9999;
      box-shadow: 0 -4px 20px rgba(0,0,0,0.5);
      border-top: 2px solid rgba(79,172,254,0.3);
    }
    #osk-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    #osk-target-name { color: #64748b; font-size: 13px; }
    #osk-close { background: rgba(239,68,68,0.2); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; padding: 4px 14px; cursor: pointer; font-size: 14px; }
    #osk-lang-btn { background: rgba(79,172,254,0.2); border: 1px solid #4facfe; color: #4facfe; border-radius: 6px; padding: 4px 14px; cursor: pointer; font-size: 14px; margin-left: 6px; }
    #osk-input-preview { color: #e2e8f0; font-size: 15px; padding: 4px 8px; min-height: 24px; max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .osk-row { display: flex; justify-content: center; gap: 5px; margin-bottom: 5px; }
    .osk-key {
      min-width: 38px; height: 44px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 6px;
      color: #e2e8f0; font-size: 16px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; user-select: none;
      transition: background 0.1s;
      flex: 0 0 auto;
    }
    #osk-overlay .osk-row {
      flex-wrap: nowrap;
    }
    #osk-overlay .osk-key {
      min-width: 0;
      flex-shrink: 1;
    }
    #osk-overlay .osk-key.wide { min-width: 50px; }
    #osk-overlay .osk-key.extra-wide { min-width: 95px; }
    #osk-overlay .osk-key.space { min-width: 120px; }
    .osk-key:active { background: rgba(79,172,254,0.5); }
    .osk-key.wide { min-width: 70px; }
    .osk-key.extra-wide { min-width: 140px; }
    .osk-key.space { min-width: 200px; }
    .osk-key.shift { background: rgba(139,92,246,0.2); border-color: #8b5cf6; }
    .osk-key.shift.active { background: rgba(139,92,246,0.5); }
    .osk-key.special { background: rgba(255,255,255,0.05); font-size: 14px; }
    .osk-key.enter { background: rgba(34,197,94,0.2); border-color: #22c55e; }
    .osk-key.backspace { background: rgba(239,68,68,0.15); border-color: #ef4444; }
  

    /* KARAOKE_KEYBOARD_FULLWIDTH_V2 */

    #osk-overlay .osk-row {
      display: flex !important;
      width: 100% !important;
      justify-content: stretch !important;
      flex-wrap: nowrap !important;
      gap: 5px !important;
    }

    #osk-overlay .osk-row .osk-key {
      flex: 1 1 0px !important;
      width: 0 !important;
      min-width: 0 !important;
      max-width: none !important;
      height: 48px !important;
      box-sizing: border-box !important;
      font-size: 18px !important;
    }

    #osk-overlay .osk-row .osk-key.wide {
      flex-grow: 1.5 !important;
    }

    #osk-overlay .osk-row .osk-key.extra-wide {
      flex-grow: 2 !important;
    }

    #osk-overlay .osk-row .osk-key.space {
      flex-grow: 3 !important;
    }


    /* KARAOKE_KEYBOARD_HEIGHT_V3 */

    #osk-overlay {
      bottom: 24px !important;
      max-height: calc(100vh - 36px);
      overflow-y: auto;
    }

    #osk-overlay .osk-row {
      margin-bottom: 8px !important;
    }

    #osk-overlay .osk-row .osk-key {
      height: 62px !important;
      font-size: 21px !important;
    }

    .footer { flex: 0 0 auto; text-align: center; padding: 6px 0; font-size: 12px; color: rgba(255,255,255,0.4); background: rgba(0,0,0,0.3); }
  
    .upload-status-row { padding: 4px 0; font-size: 13px; display: flex; align-items: center; gap: 6px; }
    .upload-name { color: rgba(255,255,255,0.8); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .upload-progress { color: #4facfe; min-width: 40px; text-align: right; }
    .upload-bar { width: 80px; height: 6px; background: rgba(255,255,255,0.15); border-radius: 3px; overflow: hidden; }
    .upload-bar-fill { height: 100%; background: #4facfe; border-radius: 3px; transition: width 0.3s; width: 0%; }
  
    /* KARAOKE_WIFI_SETUP_CARD_V3: show QR immediately, outside any button. */
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
    #karaoke-wifi-dialog {
      display: none; position: fixed; top: 0; right: 0; bottom: 0; left: 0; z-index: 8100;
      background: rgba(0,0,0,0.8); padding: 12px;
    }
    #karaoke-wifi-dialog .wifi-dialog-content {
      display: flex; flex-direction: column; width: 600px; max-width: 100%;
      height: calc(100vh - 24px); margin: auto; background: #101827;
      border: 1px solid #475569; border-radius: 14px; overflow: hidden;
    }
    #karaoke-wifi-dialog .wifi-dialog-close {
      padding: 12px; background: #334155; color: white; border: 0;
      font: bold 16px sans-serif; cursor: pointer;
    }
    #karaoke-wifi-frame { width: 100%; flex: 1; border: 0; background: #101827; }


    /* ===== KARAOKE_RESPONSIVE_UI_V1 =====
       Тот же дизайн и функции. Меняется только компоновка под размер экрана. */
    /* Планшеты / небольшие ноутбуки */
    @media (max-width: 1180px) {
      *, *::before, *::after { box-sizing: border-box; }
      h1 {
        font-size: clamp(58px, 10vw, 100px);
        letter-spacing: clamp(6px, 1.2vw, 16px);
        margin: 4px 0;
      }

      .main-area {
        padding: 8px 12px;
      }

      .slider-section {
        padding-left: 12px;
        padding-right: 12px;
      }

      .controls {
        padding-left: 12px;
        padding-right: 12px;
      }

      .right-panel {
        flex-basis: 38vw;
        min-width: 330px;
      }

      .poster-card {
        flex-basis: 96px;
        width: 96px;
        height: 96px;
      }
    }

    /* Телефон / планшет в портретной ориентации */
    @media (max-width: 820px) {
      body {
        height: 100vh;
        min-height: 100vh;
        height: 100dvh;
        min-height: 100dvh;
        overflow: hidden;
      }

      h1 {
        font-size: clamp(48px, 13vw, 78px);
        letter-spacing: clamp(3px, 1vw, 8px);
        line-height: 1.08;
        margin: 4px 0 2px;
      }

      .top-right-tools {
        right: 10px;
        top: 8px;
        gap: 12px;
      }

      .top-right-tools svg {
        width: 22px;
        height: 22px;
      }

      #remote-info {
        font-size: 12px;
        padding: 5px 8px;
        margin: 0 10px 5px;
        max-width: none;
      }

      .slider-section {
        padding: 0 8px 5px;
      }

      .slider-wrap {
        gap: 4px;
      }

      .slider {
        gap: 8px;
        padding: 5px 2px;
        -webkit-overflow-scrolling: touch;
      }

      /* На сенсорном экране слайдер листается пальцем */
      .slider-btn {
        display: none;
      }

      .poster-card {
        flex: 0 0 76px;
        width: 76px;
        height: 76px;
        border-radius: 10px;
      }

      .poster-card .poster-name {
        font-size: 9px;
        padding: 3px 4px;
      }

      .poster-card .poster-plays {
        font-size: 9px;
        padding: 2px 5px;
      }

      .controls {
        padding: 5px 8px;
      }

      input[type="text"],
      input[type="password"] {
        min-height: 44px;
        font-size: 16px;
      }

      .main-area {
        padding: 4px 8px 7px;
        flex-direction: column;
        gap: 7px;
        min-height: 0;
      }

      .left-panel {
        flex: 1 1 56%;
        min-height: 0;
        background: rgba(0,0,0,0.08);
        border-radius: 10px;
      }

      .right-panel {
        flex: 1 1 44%;
        min-height: 0;
        width: 100%;
        min-width: 0;
        margin-left: 0;
      }

      .panel-header {
        font-size: 16px;
        padding: 8px 10px;
      }

      .list {
        gap: 5px;
        padding: 7px;
        -webkit-overflow-scrolling: touch;
      }

      .item {
        padding: 9px 10px;
        font-size: 14px;
        gap: 5px;
      }

      .item .plays {
        display: none;
      }

      .queue-btn {
        padding: 6px 9px;
        font-size: 12px;
        min-height: 32px;
      }

      .queue-item {
        padding: 8px;
        font-size: 13px;
        gap: 5px;
      }

      .queue-item .q-num {
        flex-basis: 22px;
        width: 22px;
        height: 22px;
      }

      .queue-item .q-move,
      .queue-item .q-remove {
        min-height: 30px;
        min-width: 30px;
      }

      .player-controls {
        padding: 7px;
        gap: 6px;
      }

      .ctrl-btn {
        padding: 10px 4px;
        font-size: 13px;
        min-height: 42px;
      }

      .modal-content {
        width: calc(100% - 18px);
        max-width: none;
        margin: 9px auto;
        padding: 16px;
        max-height: calc(100vh - 18px);
        max-height: calc(100dvh - 18px);
      }

      .stats-grid {
        grid-template-columns: 1fr 1fr;
      }

      .upload-tabs {
        gap: 5px;
        flex-wrap: wrap;
      }

      .upload-tab {
        padding: 8px 10px;
        font-size: 12px;
      }

      .wifi-btn,
      .btn {
        min-height: 42px;
      }

      #now-playing {
        left: 8px;
        right: 8px;
        bottom: 8px;
        text-align: center;
        font-size: 12px;
      }

      .footer {
        font-size: 10px;
        padding: 3px 0;
      }

      /* На телефоне/планшете используем системную клавиатуру устройства.
         Встроенная экранная клавиатура нужна телевизору/приставке. */
      @media (pointer: coarse) {
        #osk-overlay {
          display: none !important;
        }
      }
    }

    /* Узкий телефон */
    @media (max-width: 540px) {
      h1 {
        font-size: clamp(40px, 12vw, 60px);
      }

      #remote-info {
        display: none;
      }

      .slider-section {
        padding-bottom: 2px;
      }

      .poster-card {
        flex-basis: 66px;
        width: 66px;
        height: 66px;
      }

      .main-area {
        gap: 5px;
      }

      .left-panel {
        flex-basis: 58%;
      }

      .right-panel {
        flex-basis: 42%;
      }

      .item {
        flex-wrap: wrap;
        align-items: center;
        padding: 8px;
      }

      .item .play-icon {
        font-size: 13px;
      }

      .item .artist {
        max-width: calc(100% - 40px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .item .dash {
        display: none;
      }

      .item .title {
        order: 3;
        flex: 1 1 calc(100% - 98px);
        margin-left: 21px;
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .queue-btn {
        order: 4;
        flex: 0 0 auto;
        margin-left: auto;
      }

      .panel-header {
        font-size: 14px;
      }

      .queue-clear-btn {
        padding: 5px 8px;
        font-size: 11px;
        min-height: 30px;
      }

      .queue-item .q-text {
        font-size: 12px;
      }

      .queue-item .q-move {
        padding: 2px 5px;
      }

      .queue-item .q-remove {
        padding: 2px 6px;
      }

      .ctrl-btn {
        font-size: 12px;
      }

      .stats-grid {
        gap: 6px;
      }

      .stat-card {
        padding: 9px 5px;
      }

      .network-info {
        gap: 8px;
        flex-wrap: wrap;
      }
    }

    /* Планшет в альбомной ориентации — привычные две колонки */
    @media (min-width: 821px) and (max-width: 1180px) and (orientation: landscape) {
      .main-area {
        flex-direction: row;
      }

      .right-panel {
        min-width: 320px;
      }
    }

  </style>
</head>
<body>
  <!-- KARAOKE_WIFI_SETUP_CARD_V3 -->
  <div id="karaoke-wifi-setup-indicator" role="region" aria-label="Настройка Wi-Fi по QR-коду">
    <img src="/wifi/setup-qr.png?v=3" width="222" height="222" alt="QR-код подключения к KARAOKE">
    <span class="wifi-label">Для настройки Wi-Fi наведите камеру телефона и перейдите по ссылке.</span>
    <span class="wifi-note">Сеть: KARAOKE · пароль: 12345678</span>
    <span class="wifi-note">Если страница не открылась:<br>192.168.100.1:8080/wifi/setup</span>
    <button id="karaoke-wifi-setup-open" type="button">Открыть настройку мышкой</button>
  </div>
  <div id="karaoke-wifi-dialog" role="dialog" aria-modal="true"
       aria-label="Настройка Wi-Fi">
    <div class="wifi-dialog-content">
      <button type="button" class="wifi-dialog-close" onclick="closeKaraokeWifiSetup()">Закрыть настройку Wi-Fi ×</button>
      <iframe id="karaoke-wifi-frame" title="Подключение приставки к Wi-Fi"></iframe>
    </div>
  </div>

  <h1>Караоке
    <div class="top-right-tools">
      <div id="wifi-icon" class="icon-btn" title="Network Status">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12.55a11 11 0 0 1 14.08 0"></path>
          <path d="M1.42 9a16 16 0 0 1 21.16 0"></path>
          <path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path>
          <line x1="12" y1="20" x2="12.01" y2="20"></line>
        </svg>
      </div>
      <div id="settings-btn" class="icon-btn" title="Settings">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      </div>
    </div>
  </h1>
  <div id="remote-info">Загрузка...</div>
  <div class="slider-section">
    <div class="slider-wrap">
      <button class="slider-btn" onclick="scrollSlider(-300)">&#9664;</button>
      <div class="slider" id="poster-slider"></div>
      <button class="slider-btn" onclick="scrollSlider(300)">&#9654;</button>
    </div>
  </div>
  <div class="controls">
    <input type="text" id="search" placeholder="Поиск артиста или песни..." onclick="oskShow('search', 'Поиск')" oninput="searchSongs()">
  </div>
  <div class="main-area">
    <div class="left-panel">
      <div class="panel-header">Список песен</div>
      <div class="list" id="song-list"></div>
    </div>
    <div class="right-panel">
      <div class="panel-header">
        <span>Очередь</span>
        <button class="queue-clear-btn" onclick="clearQueue()">Очистить</button>
      </div>
      <div class="list" id="queue-list">
        <div class="queue-empty">Очередь пуста</div>
      </div>
      <div class="player-controls">
        <button class="ctrl-btn stop-btn" onclick="stopVideo()">&#9209; Стоп</button>
        <button class="ctrl-btn pause-btn" onclick="pauseVideo()">&#9208; Пауза</button>
        <button class="ctrl-btn next-btn" onclick="nextVideo()">&#9197; Далее</button>
      </div>
    </div>
  </div>
  <div id="now-playing">Идет воспроизведение видео...</div>
  <div id="settingsModal" class="modal">
    <div class="modal-content">
      <span class="close" onclick="document.getElementById('settingsModal').style.display='none'">&times;</span>
      <h2>Настройки</h2>
      <div class="stats-grid">
        <div class="stat-card"><div style="font-size: 2rem; color: #3b82f6;" id="stat-songs">0</div><div>Треков</div></div>
        <div class="stat-card"><div style="font-size: 2rem; color: #f59e0b;" id="stat-posters">0</div><div>Постеров</div></div>
        <div class="stat-card"><div style="font-size: 2rem; color: #10b981;" id="stat-size">0 GB</div><div>Занято</div></div>
        <div class="stat-card"><div style="font-size: 2rem; color: #8b5cf6;" id="stat-total">0 GB</div><div>HDD</div></div>
      </div>
      <hr style="border-color: #333; margin: 20px 0;">
      <div style="color:#aaa;margin:10px 0">Медиатека обновляется автоматически.</div>
      <a class="btn" href="/quarantine" style="display:inline-block;margin:6px;text-decoration:none">🚫 Карантин исполнителей</a>
      <a class="btn" href="/youtube-search" style="display:inline-block;margin:6px;text-decoration:none">🔎 Найти караоке на YouTube</a>
      <a class="btn" href="/youtube-manager" style="display:inline-block;margin:6px;text-decoration:none">▶ Загрузка с YouTube</a>
      <a class="btn" href="/poster-manager" style="display:inline-block;margin:6px;text-decoration:none">▣ Управление постерами</a>

      <div class="wifi-settings-area">
        <h3>Wi-Fi</h3>
        <div class="wifi-current" id="wifi-current">Текущая сеть: ...</div>
        <button class="btn" type="button" onclick="openKaraokeWifiSetup()">Настроить Wi-Fi</button>
      </div>

      <div class="upload-settings-area">
        <h3>Загрузка файлов</h3>
        <div class="upload-tabs">
          <div class="upload-tab active" id="tab-video-settings" onclick="switchTab('video', 'settings')">Загрузить видео</div>
          <div class="upload-tab" id="tab-poster-settings" onclick="switchTab('poster', 'settings')">Загрузить постер</div>
          <div class="upload-tab" id="tab-bgm-settings" onclick="switchTab('bgm', 'settings')">Загрузить музыку</div>
        </div>
        <div id="video-upload-settings">
          <p>Формат имени: Артист - Название.mp4</p>
          <input type="file" multiple id="video-input-settings" accept=".mp4,.mkv,.avi,.mov" style="display:none;" onchange="handleVideo(this)">
          <div class="upload-btn-wrap"><button class="btn" onclick="document.getElementById('video-input-settings').click()">Выбрать видео</button></div>
        </div>
        <div id="poster-upload-settings" style="display:none;">
          <p>Формат имени: Артист.jpg</p>
          <input type="file" multiple id="poster-input-settings" accept=".jpg,.jpeg,.png,.webp" style="display:none;" onchange="handlePoster(this)">
          <div class="upload-btn-wrap"><button class="btn" onclick="document.getElementById('poster-input-settings').click()">Выбрать постер</button></div>
        </div>
        <div id="bgm-upload-settings" style="display:none;">
          <p>Формат: MP3. Будет добавлен в фоновый плейлист.</p>
          <input type="file" multiple id="bgm-input-settings" accept=".mp3" style="display:none;" onchange="handleBgm(this)">
          <div class="upload-btn-wrap"><button class="btn" onclick="document.getElementById('bgm-input-settings').click()">Выбрать MP3</button></div>
          <div id="bgm-upload-status" style="margin-top:8px;"></div>
        </div>
        <div id="status-settings"></div>
      </div>
      <div class="upload-settings-area" id="auto-posters-area">
        <h3>Автоматическая загрузка постеров</h3>
        <p style="color:#aaa">Поиск фотографий исполнителей в Wikimedia Commons. Перед сохранением выберите подходящий снимок.</p>
        <button class="btn" onclick="posterScanMissing()">Найти артистов без постеров</button>
        <div id="poster-auto-status" style="margin:10px 0;color:#9ed9ff"></div>
        <select id="poster-auto-artist" style="max-width:100%;padding:9px;background:#222;color:white;border:1px solid #555;border-radius:7px"></select>
        <button class="btn" onclick="posterSearchImages()">Подобрать изображения</button>
        <div id="poster-auto-results" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px"></div>
      </div>
      <div class="bgm-section">
        <h3>Фоновая музыка</h3>
        <div class="bgm-row">
          <span>Включить фоновую музыку</span>
          <label class="toggle-switch">
            <input type="checkbox" id="bgm-toggle" checked onchange="toggleBgm()">
            <span class="toggle-slider"></span>
          </label>
        </div>
        <div class="bgm-row">
          <span>Громкость</span>
          <span id="bgm-vol-label">25%</span>
        </div>
        <input type="range" class="volume-slider" id="bgm-volume" min="0" max="100" value="25" oninput="setBgmVolume(this.value)">
      </div>
      <div class="bgm-section">
        <h3>Громкость видео</h3>
        <div class="bgm-row">
          <span>Громкость</span>
          <span id="video-vol-label">80%</span>
        </div>
        <input type="range" class="volume-slider" id="video-volume" min="0" max="100" value="80" oninput="setVideoVolume(this.value)">
      </div>
      <div class="bgm-section">
        <h3>Управление файлами</h3>
        <div class="upload-tabs">
          <div class="upload-tab active" id="fm-tab-video" onclick="fmSwitchTab('video')">Видео</div>
          <div class="upload-tab" id="fm-tab-poster" onclick="fmSwitchTab('poster')">Постеры</div>
          <div class="upload-tab" id="fm-tab-bgm" onclick="fmSwitchTab('bgm')">Музыка</div>
        </div>
        <input type="text" id="fm-search" class="wifi-input" placeholder="Поиск..." oninput="fmSearch()" style="margin:8px 0; width:100%; box-sizing:border-box;">
        <div id="fm-list" class="fm-list"></div>
        <div style="text-align:center; padding:8px;">
          <button class="btn" id="fm-more-btn" onclick="fmLoadMore()" style="display:none;">Загрузить еще</button>
        </div>
      </div>
      <div class="network-section">
        <h3>Сеть</h3>
        <div class="network-info"><span>Статус:</span> <span id="net-status-text" style="font-weight:bold;">...</span></div>
        <div class="network-info"><span>IP:</span> <span id="net-ip-text" class="ip-addr">0.0.0.0</span></div>
        <div class="network-info"><span>SSID:</span> <span id="net-ssid-text">Unknown</span></div>
      </div>
    </div>
  </div>
  <script>
    // --- ES5 Polyfills for old WebKit (surf) ---
    if (!String.prototype.includes) { String.prototype.includes = function(s, i) { return this.indexOf(s, i||0) !== -1; }; }
    if (!String.prototype.repeat) { String.prototype.repeat = function(n) { var r = ''; for (var i = 0; i < n; i++) r += this; return r; }; }
    if (!String.prototype.startsWith) { String.prototype.startsWith = function(s, i) { return this.indexOf(s, i||0) === (i||0); }; }
    if (!String.prototype.endsWith) { String.prototype.endsWith = function(s) { return this.indexOf(s, this.length - s.length) !== -1; }; }
    if (!Array.prototype.includes) { Array.prototype.includes = function(v) { return this.indexOf(v) !== -1; }; }
    if (!Array.prototype.find) { Array.prototype.find = function(f) { for (var i = 0; i < this.length; i++) if (f(this[i], i, this)) return this[i]; return undefined; }; }
    if (!Array.prototype.findIndex) { Array.prototype.findIndex = function(f) { for (var i = 0; i < this.length; i++) if (f(this[i], i, this)) return i; return -1; }; }
    if (!Array.from) { Array.from = function(a) { var r = []; for (var i = 0; i < a.length; i++) r.push(a[i]); return r; }; }
    // --- End polyfills ---



function fetchSync(u,o){var x=new XMLHttpRequest();x.open((o&&o.method)||"GET",u,false);if(o&&o.headers)for(var k in o.headers)x.setRequestHeader(k,o.headers[k]);x.send(o&&o.body||null);try{return JSON.parse(x.responseText)}catch(e){return x.responseText}}

    function fetch(url, opts) {
      var x = new XMLHttpRequest();
      x.open((opts && opts.method) || 'GET', url, false);
      if (opts && opts.headers) for (var k in opts.headers) x.setRequestHeader(k, opts.headers[k]);
      x.send(opts && opts.body || null);
      var resp = { json: function() { try { return JSON.parse(x.responseText); } catch(e) { return {}; } }, text: function() { return x.responseText; }, status: x.status };
      function Chain(val, err) {
        this.then = function(cb) { if (err) return this; try { return new Chain(cb(val), false); } catch(e) { return new Chain(e, true); } };
        this.catch = function(cb) { if (err) { try { return new Chain(cb(val), false); } catch(e2) { return new Chain(e2, true); } } return this; };
      }
      return new Chain(resp, false);
    }
    var videoPlaying = false;
    var bgmEnabled = true;
    var bgmVolume = 25;

    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
    }

      // ===== WiFi =====
      function scanWiFi() {
        openKaraokeWifiSetup();
      }
      function selectWiFi(ssid) {
        openKaraokeWifiSetup();
      }
      function connectWiFi() {
        openKaraokeWifiSetup();
      }
      function loadWiFiStatus() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/wifi/status', true);
        xhr.timeout = 4000;
        xhr.onload = function() {
          if (xhr.status !== 200) return;
          try {
            var state = JSON.parse(xhr.responseText);
            document.getElementById('wifi-current').textContent = state.connection
              ? 'Текущая сеть: ' + state.connection + (state.ip ? ' (' + state.ip + ')' : '')
              : 'Домашняя сеть не подключена';
          } catch (e) {}
        };
        try { xhr.send(null); } catch (e) {}
      }
      loadWiFiStatus();

    function switchTab(tab, context) {
      var names = ['video', 'poster', 'bgm'];
      for (var i = 0; i < names.length; i++) {
        var name = names[i];
        var button = document.getElementById('tab-' + name + '-settings');
        var panel = document.getElementById(name + '-upload-settings');
        if (button) button.classList.toggle('active', tab === name);
        if (panel) panel.style.display = tab === name ? 'block' : 'none';
      }
      var status = document.getElementById('status-settings');
      if (status) status.innerHTML = '';
    }
    function scrollSlider(delta) { document.getElementById('poster-slider').scrollBy({ left: delta, behavior: 'smooth' }); }
    function loadPosters() {
      var res = fetchSync('/top_artists');
      var artists = res;
      var slider = document.getElementById('poster-slider');
      slider.innerHTML = '';
      artists.forEach(function(a) {
        var card = document.createElement('div');
        card.className = 'poster-card';
        card.onclick = function() { return filterByArtist(a.artist); };
        if (a.poster) {
          card.innerHTML = '<img src="/posters/' + encodeURIComponent(a.poster) + '" alt="' + escapeHtml(a.artist) + '">' + '<div class="poster-plays">' + a.total_plays + '</div>' + '<div class="poster-name">' + escapeHtml(a.artist) + '</div>';
        } else {
          card.innerHTML = '<div class="poster-placeholder">&#127908;</div>' + '<div class="poster-plays">' + a.total_plays + '</div>' + '<div class="poster-name">' + escapeHtml(a.artist) + '</div>';
        }
        slider.appendChild(card);
      });
    }
    function filterByArtist(artist) { document.getElementById('search').value = artist; searchSongs(); }
    var menuSearchTimer = null;
    var menuSearchRequest = 0;

    function searchSongs() {
      var q = document.getElementById('search').value;
      if (socket && socket.connected) socket.emit('search_sync', {q:q});
      clearTimeout(menuSearchTimer);
      menuSearchTimer = setTimeout(function() {
        searchSongsSync();
      }, 250);
      return;
    }

    function searchSongsLegacy() {
      var q = document.getElementById('search').value;
      if (socket && socket.connected) socket.emit('search_sync', {q:q});
      var list = document.getElementById('song-list');
      list.innerHTML = '<div class="hint">...</div>';
      try {
        var res = fetchSync('/search?q=' + encodeURIComponent(q));
        var songs = res;
        list.innerHTML = '';
        if (songs.length === 0) { list.innerHTML = `<div class="hint">Ничего не найдено. <a href="/youtube-search?q=${encodeURIComponent(q)}">Найти караоке на YouTube и скачать</a></div>`; return; }
        songs.sort(function(a, b) {
          var an = (a.artist || '').toLowerCase();
          var bn = (b.artist || '').toLowerCase();
          if (an < bn) return -1;
          if (an > bn) return 1;
          var at = (a.title || '').toLowerCase();
          var bt = (b.title || '').toLowerCase();
          if (at < bt) return -1;
          if (at > bt) return 1;
          return 0;
        });
        songs.forEach(function(s) {
          var el = document.createElement('div');
          el.className = 'item';
          el.innerHTML = 
            '<span class="play-icon">&#9654;</span>' +
            '<span class="artist">' + escapeHtml(s.artist) + '</span>' +
            '<span class="dash"> \u2014 </span>' +
            '<span class="title">' + escapeHtml(s.title) + '</span>' +
            '<span class="plays">' + s.plays + '</span>' +
            '<button class="queue-btn" onclick="event.stopPropagation(); addToQueue(' + s.id + ', this)">\u271A В очередь</button>';
          el.onclick = function() { return playSong(s.file); };
          list.appendChild(el);
        });
      } catch (e) { list.innerHTML = '<div class="hint" style="color:#ff5a5a;">Error</div>'; }
    }
    function playSong(file) {
      videoPlaying = true;
      pauseBgm();
      document.getElementById('now-playing').style.display = 'block';
      try {
        fetchSync('/play', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({file: file}) });
      } catch (e) {}
      fetchSync('/increment?file=' + encodeURIComponent(file));
      searchSongs();
      loadPosters();
    }
    function playFromQueue() {
      var res = fetchSync('/queue/next');
      var data = res;
      loadQueue();
      if (data.song) {
        playSong(data.song.file);
      } else {
        resumeBgm();
      }
    }
    function addToQueue(songId, btn) {
      fetchSync('/queue/add', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({song_id: songId}) });
      btn.classList.add('added');
      btn.innerText = '\u2714 В очереди';
      setTimeout(function() { btn.classList.remove('added'); btn.innerText = '\u271A В очередь'; }, 1500);
      loadQueue();
    }
    function loadQueue() {
      try {
        var dbg = document.getElementById('debug-log');
        if (dbg) dbg.textContent = 'loadQueue ' + new Date().toLocaleTimeString();
        var res = fetchSync('/queue/list?_t=' + Date.now());
        var queue = res;
        if (dbg) dbg.textContent += ' got ' + queue.length + ' items';
      var container = document.getElementById('queue-list');
      container.innerHTML = '';
      if (queue.length === 0) {
        container.innerHTML = '<div class="queue-empty">Очередь пуста</div>';
        return;
      }
      queue.forEach(function(q, i) {
        var el = document.createElement('div');
        el.className = 'queue-item';
        el.innerHTML = 
          '<div class="q-num">' + (i + 1) + '</div>' +
          '<div class="q-text"><span class="q-artist">' + escapeHtml(q.artist) + '</span> \u2014 ' + escapeHtml(q.title) + '</div>' +
          '<button class="q-move" onclick="event.stopPropagation(); moveQueue(' + q.queue_id + ', -1)"' + (i === 0 ? ' disabled' : '') + '>\u25B2</button>' +
          '<button class="q-move" onclick="event.stopPropagation(); moveQueue(' + q.queue_id + ', 1)"' + (i === queue.length - 1 ? ' disabled' : '') + '>\u25BC</button>' +
          '<button class="q-remove" onclick="event.stopPropagation(); removeFromQueue(' + q.queue_id + ')">\u2715</button>';
        el.onclick = function() { return playSong(q.file); };
        container.appendChild(el);
      });
      } catch(e) {}
    }
    function moveQueue(queueId, direction) {
      fetchSync('/queue/move', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({queue_id: queueId, direction: direction}) });
      loadQueue();
    }
    function removeFromQueue(queueId) {
      fetchSync('/queue/remove/' + queueId, { method: 'DELETE' });
      loadQueue();
    }
    function clearQueue() {
      fetchSync('/queue/clear', { method: 'POST' });
      loadQueue();
    }

    function uploadFiles(url, input, statusId) {
      var files = input.files;
      if (!files || files.length === 0) return;
      var status = document.getElementById(statusId);
      if (!status) return;
      status.innerHTML = '';
      var total = files.length;
      var idx = 0;

      function uploadNext() {
        if (idx >= total) {
          input.value = '';
          fetch('/refresh_after_upload', { method: 'POST' }).then(function() {
            searchSongs(); loadPosters(); loadSettings(); loadBgmTracks();
          });
          return;
        }
        var file = files[idx];
        var cur = idx;
        idx++;

        var row = document.createElement('div');
        row.className = 'upload-status-row';
        row.innerHTML = '<span class="upload-name">' + escapeHtml(file.name) + '</span>' +
          '<div class="upload-bar"><div class="upload-bar-fill" id="ubar-' + cur + '"></div></div>' +
          '<span class="upload-progress" id="uprog-' + cur + '">0%</span>';
        status.appendChild(row);

        var formData = new FormData();
        formData.append('file', file);

        var x = new XMLHttpRequest();
        x.open('POST', url, true);

        x.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            var pct = Math.round(e.loaded / e.total * 100);
            var bar = document.getElementById('ubar-' + cur);
            var lbl = document.getElementById('uprog-' + cur);
            if (bar) bar.style.width = pct + '%';
            if (lbl) lbl.textContent = pct + '%';
          }
        };

        x.onload = function() {
          var lbl = document.getElementById('uprog-' + cur);
          try {
            var data = JSON.parse(x.responseText);
            if (data.error) {
              if (lbl) lbl.innerHTML = '<span style="color:#f87171;">\u2717</span>';
              row.querySelector('.upload-name').innerHTML += ' <span style="color:#f87171;">' + data.error + '</span>';
            } else {
              if (lbl) lbl.innerHTML = '<span style="color:#4ade80;">\u2713</span>';
            }
          } catch(e) {
            if (lbl) lbl.innerHTML = '<span style="color:#f87171;">\u2717</span>';
          }
          uploadNext();
        };

        x.onerror = function() {
          var lbl = document.getElementById('uprog-' + cur);
          if (lbl) lbl.innerHTML = '<span style="color:#f87171;">\u2717</span>';
          uploadNext();
        };

        x.send(formData);
      }
      uploadNext();
    }

    function handleVideo(input) {
      var statusId = input.id.indexOf('settings') !== -1 ? 'status-settings' : 'status';
      uploadFiles('/upload', input, statusId);
    }
    function handlePoster(input) {
      var statusId = input.id.indexOf('settings') !== -1 ? 'status-settings' : 'status';
      uploadFiles('/upload_poster', input, statusId);
    }

    function handleBgm(input) {
      var file = input.files[0];
      if (!file) return;
      var status = document.getElementById('bgm-upload-status');
      status.innerHTML = '<span style="color:#4facfe;">Загрузка...</span>';
      var formData = new FormData();
      formData.append('file', file);
      fetch('/upload_bgm', { method: 'POST', body: formData }).then(function(r) { return r.json(); }).then(function(data) {
        if (data.error) {
          status.innerHTML = '<span style="color:#f87171;">' + data.error + '</span>';
        } else {
          status.innerHTML = '<span style="color:#4ade80;">\u2713 ' + data.filename + ' добавлен</span>';
          loadBgmTracks();
        }
      }).catch(function(e) {
        status.innerHTML = '<span style="color:#f87171;">Ошибка загрузки</span>';
      });
      input.value = '';
    }

    function updateWifiStatus() {
      try {
        var res = fetchSync('/api/network_status');
        var data = res;
        var icon = document.getElementById('wifi-icon');
        if (data.status === 'connected') { icon.style.color = '#4ade80'; icon.title = data.ssid + ' / ' + data.ip; }
        else { icon.style.color = '#ef4444'; icon.title = 'No network'; }
      } catch (e) {}
    }
    function pauseBgm() { fetchSync('/api/bgm/stop?_t=' + Date.now()); }
    function resumeBgm() { if (bgmEnabled && !videoPlaying) { fetchSync('/api/bgm/start'); } }
    function toggleBgm() {
      bgmEnabled = document.getElementById('bgm-toggle').checked;
      fetchSync('/api/bgm/toggle?enabled=' + bgmEnabled);
    }
    function setBgmVolume(val) {
      bgmVolume = parseInt(val);
      document.getElementById('bgm-vol-label').textContent = val + '%';
      fetchSync('/api/bgm/volume?vol=' + val);
    }
    function setVideoVolume(val) {
      document.getElementById('video-vol-label').textContent = val + '%';
      fetchSync('/api/video/volume?vol=' + val);
    }
    var fmType = 'video';
    var fmPage = 1;
    var fmPerPage = 50;
    var fmSearchQ = '';
    var fmSearchTimer;
    function fmSwitchTab(type) {
      fmType = type; fmPage = 1;
      document.querySelectorAll('[id^="fm-tab-"]').forEach(function(t) { t.classList.remove('active'); });
      document.getElementById('fm-tab-' + type).classList.add('active');
      document.getElementById('fm-search').value = '';
      fmSearchQ = '';
      fmLoadList(true);
    }
    function fmSearch() {
      clearTimeout(fmSearchTimer);
      fmSearchTimer = setTimeout(function() {
        fmSearchQ = document.getElementById('fm-search').value.toLowerCase();
        fmPage = 1;
        fmLoadList(true);
      }, 300);
    }
    function fmLoadList(clear) {
      fetch('/api/files/list?type=' + fmType + '&page=' + fmPage + '&per_page=' + fmPerPage + '&q=' + encodeURIComponent(fmSearchQ))
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data.error) { document.getElementById('fm-list').innerHTML = '<div style="padding:10px;color:#f87171;">' + data.error + '</div>'; return; }
          if (clear) document.getElementById('fm-list').innerHTML = '';
          var icon = fmType === 'video' ? '▶' : fmType === 'poster' ? '■' : '♫';
          var html = '';
          data.files.forEach(function(f) {
            var queueBadge = f.in_queue ? '<span class="fm-queue-badge">\u0432 \u043e\u0447\u0435\u0440\u0435\u0434\u0438</span>' : '';
            html += '<div class="fm-item" data-name="' + encodeURIComponent(f.name) + '"><span class="fm-item-icon">' + icon + '</span><span class="fm-item-name">' + f.name + '</span>' + queueBadge + '<span class="fm-item-size">' + (f.size < 1048576 ? Math.max(1, Math.round(f.size / 1024)) + ' КБ' : (f.size / 1048576).toFixed(1) + ' МБ') + '</span><button class="fm-item-del" onclick="fmDelete(this)">\u2715</button></div>';
          });
          document.getElementById('fm-list').insertAdjacentHTML('beforeend', html);
          document.getElementById('fm-more-btn').style.display = (data.page < data.pages) ? '' : 'none';
        })
        .catch(function(e) { document.getElementById('fm-list').innerHTML = '<div style="padding:10px;color:#f87171;">\u041e\u0448\u0438\u0431\u043a\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438</div>'; });
    }
    function fmLoadMore() { fmPage++; fmLoadList(false); }
    function fmDelete(btn) {
      var item = btn.closest('.fm-item');
      var name = decodeURIComponent(item.dataset.name);
      if (!confirm('\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0444\u0430\u0439\u043b: ' + name + '?')) return;
      fetch('/api/files/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: fmType, name: name})
      })
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data.ok) {
            fmPage = 1; fmLoadList(true);
            fetch('/settings/info').then(function(r) { return r.json(); }).then(function(d) {
              document.getElementById('stat-songs').textContent = d.song_count;
              document.getElementById('stat-posters').textContent = d.poster_count;
              document.getElementById('stat-size').textContent = (d.disk_used_mb < 1024 ? d.disk_used_mb + ' MB' : d.disk_used_gb.toFixed(2) + ' GB');
              document.getElementById('stat-total').textContent = d.disk_total_gb + ' GB';
            });
          } else { alert('\u041e\u0448\u0438\u0431\u043a\u0430: ' + (data.error || 'unknown')); }
        });
    }
    function loadBgmTracks() {
      try {
        var res = fetchSync('/api/bgm/status');
        var data = res;
        document.getElementById('bgm-toggle').checked = data.enabled;
        document.getElementById('bgm-volume').value = data.volume;
        document.getElementById('bgm-vol-label').textContent = data.volume + '%';
        bgmEnabled = data.enabled;
        bgmVolume = data.volume;
        if (data.video_volume !== undefined) {
          document.getElementById('video-volume').value = data.video_volume;
          document.getElementById('video-vol-label').textContent = data.video_volume + '%';
        }
      } catch (e) {}
    }
    updateWifiStatus(); setInterval(updateWifiStatus, 10000);
    document.getElementById('settings-btn').addEventListener('click', function() {
      document.getElementById('settingsModal').style.display = 'block';
      fmSwitchTab('video');
      loadWiFiStatus();
      loadSettings();
      try {
        var res = fetchSync('/api/network_status'); var data = res;
        document.getElementById('net-status-text').innerText = data.status === 'connected' ? 'OK' : 'OFF';
        document.getElementById('net-ip-text').innerText = data.ip;
        document.getElementById('net-ssid-text').innerText = data.ssid;
        document.getElementById('net-status-text').style.color = data.status === 'connected' ? '#4ade80' : '#ef4444';
      } catch (e) {}
    });
    function loadSettings() {
      try {
        var res = fetchSync('/settings/info'); var data = res;
        document.getElementById('stat-songs').textContent = data.song_count;
        document.getElementById('stat-posters').textContent = data.poster_count;
        document.getElementById('stat-size').textContent = (data.disk_used_mb < 1024 ? data.disk_used_mb + ' MB' : data.disk_used_gb.toFixed(2) + ' GB');
        document.getElementById('stat-total').textContent = data.disk_total_gb + ' GB';
      } catch (e) {}
    }
    function formatHDD() {
      if (!confirm('ВНИМАНИЕ! Все данные на HDD будут удалены! Продолжить?')) return;
      if (!confirm('Точно? Это действие необратимо!')) return;
      document.getElementById('format-hdd-btn').textContent = 'Форматирование...';
      document.getElementById('format-hdd-btn').disabled = true;
      try {
        var res = fetchSync('/api/format_hdd', { method: 'POST' });
        var data = res;
        if (data.ok) {
          alert('HDD отформатирован!');
          loadSettings();
        } else {
          alert('Ошибка: ' + (data.error || 'unknown'));
        }
      } catch (e) {
        alert('Ошибка: ' + e.message);
      }
      document.getElementById('format-hdd-btn').textContent = 'Форматировать HDD';
      document.getElementById('format-hdd-btn').disabled = false;
    }
    function refreshDB() {
      var btn = document.getElementById('refresh-btn'); var orig = btn.innerText;
      btn.innerText = '...'; btn.disabled = true;
      try {
        var res = fetchSync('/settings/refresh_db', { method: 'POST' }); var data = res;
        alert('OK: +' + data.added + ' -' + data.removed + ' dup:' + data.duplicates_fixed);
        searchSongs(); loadPosters(); loadSettings();
      } catch (e) { alert('Error'); }
      finally { btn.innerText = orig; btn.disabled = false; }
    }
    function stopVideo() {
      fetchSync('/api/stop?_t=' + Date.now());
      videoPlaying = false;
      document.getElementById('now-playing').style.display = 'none';
      resumeBgm();
      loadQueue();
    }
    function pauseVideo() {
      fetchSync('/api/pause?_t=' + Date.now());
    }
    function nextVideo() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/next?_t=' + Date.now(), true);
      xhr.onload = function() { loadQueue(); };
      xhr.send();
    }
    // Показываем IP для удалённого управления
    fetch('/api/network_status').then(function(r) { return r.json(); }).then(function(d) {
      if (d.status === 'connected' && d.ip) {
        document.getElementById('remote-info').innerHTML = '\u2709\ufe0f Для управления наберите в браузере: <b>http://' + d.ip + ':8080</b>';
      } else {
        document.getElementById('remote-info').innerHTML = '\u2709\ufe0f Для управления наберите в браузере: <b>http://IP-ПРИСТАВКИ:8080</b>';
      }
    }).catch(function() {
      document.getElementById('remote-info').innerHTML = '\u2709\ufe0f Для управления наберите в браузере: <b>http://IP-ПРИСТАВКИ:8080</b>';
    });
    loadBgmTracks();
    loadPosters();
    searchSongs();
    loadQueue();
    // Независимый HTTP-клиент: старый интерфейс переопределяет window.fetch.
    function posterApiRequest(url, opts) {
      return new Promise(function(resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open((opts && opts.method) || 'GET', url, true);
        xhr.timeout = 20000;
        if (opts && opts.headers) {
          for (var key in opts.headers) {
            if (Object.prototype.hasOwnProperty.call(opts.headers, key)) xhr.setRequestHeader(key, opts.headers[key]);
          }
        }
        xhr.onload = function() {
          var data;
          try { data = JSON.parse(xhr.responseText); }
          catch (e) { reject(new Error('Некорректный ответ сервера')); return; }
          if (xhr.status < 200 || xhr.status >= 300) {
            reject(new Error(data.error || 'HTTP ' + xhr.status)); return;
          }
          resolve(data);
        };
        xhr.onerror = function() { reject(new Error('Нет соединения с сервером')); };
        xhr.ontimeout = function() { reject(new Error('Время ожидания истекло')); };
        xhr.send((opts && opts.body) || null);
      });
    }
    // Поиск и подтверждение постеров. Скачивание начинается только после выбора.
    async function posterScanMissing() {
      const status = document.getElementById('poster-auto-status');
      const select = document.getElementById('poster-auto-artist');
      status.textContent = 'Проверяем медиатеку...';
      try {
        const data = await posterApiRequest('/api/posters/missing');
        select.replaceChildren();
        data.missing.forEach(name => {
          const option = document.createElement('option');
          option.value = name; option.textContent = name;
          select.appendChild(option);
        });
        status.textContent = `Исполнителей: ${data.total}. Без постеров: ${data.missing_count}.`;
      } catch (err) { status.textContent = err.message; }
    }
    async function posterSearchImages() {
      const artist = document.getElementById('poster-auto-artist').value;
      const status = document.getElementById('poster-auto-status');
      const results = document.getElementById('poster-auto-results');
      results.replaceChildren();
      if (!artist) { status.textContent = 'Сначала найдите артистов без постеров.'; return; }
      status.textContent = `Ищем изображения: ${artist}...`;
      try {
        const data = await posterApiRequest('/api/posters/search?artist=' + encodeURIComponent(artist));
        status.textContent = data.candidates.length ? `Найдено вариантов: ${data.candidates.length}. Проверьте, что на фото нужный артист.` : 'Wikimedia Commons не вернула подходящих изображений. Можно загрузить постер вручную во вкладке «Загрузить постер».';
        data.candidates.forEach(item => {
          const card = document.createElement('div');
          card.style.cssText = 'width:140px;background:#242424;border-radius:9px;padding:8px';
          const img = document.createElement('img');
          img.src = item.preview; img.alt = item.title;
          img.style.cssText = 'width:124px;height:124px;object-fit:cover;border-radius:7px';
          const license = document.createElement('div');
          license.textContent = item.license || 'Лицензия не указана';
          license.style.cssText = 'font-size:11px;color:#aaa;min-height:30px';
          const link = document.createElement('a');
          link.href = item.description_url; link.target = '_blank'; link.rel = 'noopener noreferrer';
          link.textContent = 'Источник и лицензия'; link.style.cssText = 'font-size:11px;color:#9ed9ff;display:block';
          const button = document.createElement('button');
          button.className = 'btn'; button.textContent = 'Сохранить';
          button.onclick = () => posterDownloadImage(artist, item.url, button);
          card.append(img, license, link, button); results.appendChild(card);
        });
      } catch (err) { status.textContent = err.message; }
    }
    async function posterDownloadImage(artist, url, button) {
      const status = document.getElementById('poster-auto-status');
      button.disabled = true; button.textContent = 'Загрузка...';
      try {
        const data = await posterApiRequest('/api/posters/download', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({artist,url})});
        status.textContent = 'Постер сохранён: ' + data.filename;
        button.textContent = 'Готово';
        if (typeof loadPosters === 'function') loadPosters();
      } catch (err) { status.textContent = err.message; button.textContent = 'Повторить'; button.disabled = false; }
    }
  </script>

  <script src="/socket.io.min.js"></script>
  <script>

    var socket = null;
    try {
      socket = io();
      socket.on('connect', function() { console.log('WS connected'); });
      socket.on('full_state', function(data) {
        if (!data) return;
        if (data.queue) renderQueueSync(data.queue);
        if (data.search !== undefined) { document.getElementById('search').value = data.search; searchSongsSync(); }
        if (data.player) {
          videoPlaying = !!data.player.playing;
          var np = document.getElementById('now-playing');
          np.style.display = videoPlaying ? 'block' : 'none';
          if (videoPlaying) np.textContent = 'Играет: ' + (data.player.artist || '') + ' — ' + (data.player.title || '') + (data.player.paused ? ' (пауза)' : '');
        }
      });
      socket.on('disconnect', function() { console.log('WS disconnected'); });
      socket.on('queue_update', function(data) { if (data && data.queue) { renderQueueSync(data.queue); } });
      socket.on('search_sync', function(data) { if (data && data.q !== undefined) { document.getElementById('search').value = data.q; searchSongsSync(); } });
      socket.on('song_started', function(data) {
        document.getElementById('now-playing').textContent = '\u0418\u0433\u0440\u0430\u0435\u0442: ' + (data.artist || '') + ' \u2014 ' + (data.title || '');
        document.getElementById('now-playing').style.display = 'block';
        videoPlaying = true;
      });
      socket.on('song_ended', function(data) {
        videoPlaying = false; document.getElementById('now-playing').style.display = 'none';
      });
      socket.on('song_stopped', function(data) {
        document.getElementById('now-playing').style.display = 'none';
        videoPlaying = false;
      });
      socket.on('db_update', function(data) { searchSongsSync(); loadPosters(); loadSettings(); });
      socket.on('posters_update', function(data) { loadPosters(); });
      socket.on('plays_update', function(data) { searchSongsSync(); loadPosters(); });
      socket.on('player_cmd', function(data) {
        if (data.cmd === 'pause') { var np = document.getElementById('now-playing'); np.textContent = np.textContent.replace(/ \(пауза\)$/, ''); if (data.paused) np.textContent += ' (пауза)'; }
        if (data.cmd === 'stop') { videoPlaying = false; document.getElementById('now-playing').style.display = 'none'; }
      });
    } catch(e) { console.log('Socket.IO init error:', e); }

    function renderQueueSync(queue) {
      var container = document.getElementById('queue-list');
      container.innerHTML = '';
      if (!queue || queue.length === 0) { container.innerHTML = '<div class="queue-empty">\u041e\u0447\u0435\u0440\u0435\u0434\u044c \u043f\u0443\u0441\u0442\u0430</div>'; return; }
      queue.forEach(function(q, i) {
        var el = document.createElement('div');
        el.className = 'queue-item';
        el.innerHTML = '<div class="q-num">' + (i + 1) + '</div>' +
          '<div class="q-text"><span class="q-artist">' + escapeHtml(q.artist) + '</span> \u2014 ' + escapeHtml(q.title) + '</div>' +
          '<button class="q-move" onclick="event.stopPropagation(); moveQueue(' + q.queue_id + ', -1)"' + (i === 0 ? ' disabled' : '') + '>\u25B2</button>' +
          '<button class="q-move" onclick="event.stopPropagation(); moveQueue(' + q.queue_id + ', 1)"' + (i === queue.length - 1 ? ' disabled' : '') + '>\u25BC</button>' +
          '<button class="q-remove" onclick="event.stopPropagation(); removeFromQueue(' + q.queue_id + ')">\u2715</button>';
        el.onclick = function() { return playSong(q.file); };
        container.appendChild(el);
      });
    }

    function searchSongsSync() {
      var q = document.getElementById('search').value;
      var requestId = ++menuSearchRequest;

      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/search?q=' + encodeURIComponent(q), true);

      xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4 || requestId !== menuSearchRequest) return;

        var list = document.getElementById('song-list');
        if (xhr.status !== 200) {
          list.innerHTML = '<div class="hint">Ошибка поиска</div>';
          return;
        }

        var songs;
        try {
          songs = JSON.parse(xhr.responseText);
        } catch (e) {
          return;
        }

        list.innerHTML = '';

        if (!songs.length) {
          list.innerHTML =
            '<div class="hint">Ничего не найдено. ' +
            '<a href="/youtube-search?q=' + encodeURIComponent(q) +
            '">Найти караоке на YouTube и скачать</a></div>';
          return;
        }

        songs.sort(function(a, b) {
          var an = (a.artist || '').toLowerCase();
          var bn = (b.artist || '').toLowerCase();
          if (an < bn) return -1;
          if (an > bn) return 1;

          var at = (a.title || '').toLowerCase();
          var bt = (b.title || '').toLowerCase();
          return at < bt ? -1 : at > bt ? 1 : 0;
        });

        var fragment = document.createDocumentFragment();

        songs.forEach(function(song) {
          var el = document.createElement('div');
          el.className = 'item';

          el.innerHTML =
            '<span class="play-icon">&#9654;</span>' +
            '<span class="artist">' + escapeHtml(song.artist) + '</span>' +
            '<span class="dash"> — </span>' +
            '<span class="title">' + escapeHtml(song.title) + '</span>' +
            '<span class="plays">' + song.plays + '</span>' +
            '<button class="queue-btn" onclick="event.stopPropagation(); addToQueue(' +
            song.id + ', this)">✚ В очередь</button>';

          el.onclick = function() { playSong(song.file); };
          fragment.appendChild(el);
        });

        list.appendChild(fragment);
      };

      xhr.send();
    }

    document.addEventListener('DOMContentLoaded', function() {
      var searchInput = document.getElementById('search');
      if (searchInput) {

      }
    });

    // ===== Экранная клавиатура =====
    var oskTarget = null;
    var oskLang = 'ru';
    var oskShift = false;
    var oskLayouts = {
      ru: [
        ['й','ц','у','к','е','н','г','ш','щ','з','х','ъ'],
        ['ф','ы','в','а','п','р','о','л','д','ж','э'],
        ['я','ч','с','м','и','т','ь','б','ю'],
      ],
      en: [
        ['q','w','e','r','t','y','u','i','o','p','[',']'],
        ['a','s','d','f','g','h','j','k','l',';','#'],
        ['z','x','c','v','b','n','m',',','.','/'],
      ]
    };
    var oskShiftLayouts = {
      ru: [
        ['Й','Ц','У','К','Е','Н','Г','Ш','Щ','З','Х','Ъ'],
        ['Ф','Ы','В','А','П','Р','О','Л','Д','Ж','Э'],
        ['Я','Ч','С','М','И','Т','Ь','Б','Ю'],
      ],
      en: [
        ['Q','W','E','R','T','Y','U','I','O','P','{','}'],
        ['A','S','D','F','G','H','J','K','L',':','~'],
        ['Z','X','C','V','B','N','M','<','>','?'],
      ]
    };

    function oskShow(inputId, label) {
      /* KARAOKE_RESPONSIVE_NATIVE_KEYBOARD_V1 */
      if (window.matchMedia &&
          window.matchMedia('(max-width: 820px)').matches &&
          window.matchMedia('(pointer: coarse)').matches) {
        var nativeTarget = document.getElementById(inputId);
        if (nativeTarget) nativeTarget.focus();
        return;
      }

      oskTarget = document.getElementById(inputId);
      if (!oskTarget) return;
      document.getElementById('osk-target-name').textContent = label || 'Ввод текста';
      var overlay = document.getElementById('osk-overlay');
      overlay.style.display = 'block';
      overlay.style.position = 'fixed';
      overlay.style.bottom = 'auto';
      var rect = oskTarget.getBoundingClientRect();
      var height = overlay.getBoundingClientRect().height;
      if (rect.bottom + height > window.innerHeight) {
        window.scrollBy(0, rect.bottom + height - window.innerHeight + 12);
        rect = oskTarget.getBoundingClientRect();
      }
      overlay.style.top = Math.max(0, rect.bottom + 5) + 'px';
      overlay.style.maxHeight = Math.max(120, window.innerHeight - Math.max(0, rect.bottom + 5) - 8) + 'px';
      overlay.style.overflowY = 'auto';
      oskUpdatePreview();
      oskRenderKeys();
      requestAnimationFrame(function(){
        var rect = oskTarget.getBoundingClientRect();
        var height = Math.min(overlay.scrollHeight, window.innerHeight * 0.65);
        if (rect.bottom + height + 12 > window.innerHeight) {
          var scrollArea = oskTarget.closest('.modal, .content, .panel');
          if (scrollArea && scrollArea.scrollHeight > scrollArea.clientHeight) scrollArea.scrollTop += rect.bottom + height + 12 - window.innerHeight;
          else window.scrollBy(0, rect.bottom + height + 12 - window.innerHeight);
          rect = oskTarget.getBoundingClientRect();
        }
        overlay.style.top = Math.max(0, rect.bottom + 6) + 'px';
        overlay.style.maxHeight = Math.max(120, window.innerHeight - Math.max(0, rect.bottom + 6) - 8) + 'px';
      });
    }

    function oskHide() {
      document.getElementById('osk-overlay').style.display = 'none';
      oskTarget = null;
    }

    function oskUpdatePreview() {
      if (!oskTarget) return;
      var val = oskTarget.value || '';
      if (oskTarget.type === 'password') val = '\u25CF'.repeat(val.length);
      document.getElementById('osk-input-preview').textContent = val;
    }

    function oskRenderKeys() {
      var layout = oskShift ? oskShiftLayouts[oskLang] : oskLayouts[oskLang];
      var shiftClass = oskShift ? " active" : "";
      var html = "";
      var digits = oskShift ? "!@#$%^&*()" : "1234567890";
      html += "<div class='osk-row'>";
      for (var i = 0; i < digits.length; i++) {
        html += "<div class='osk-key' data-key='" + digits[i] + "'>" + digits[i] + "</div>";
      }
      html += "<div class='osk-key backspace' data-key='BACKSPACE'>&#9003;</div>";
      html += "</div>";
      for (var r = 0; r < layout.length; r++) {
        html += "<div class='osk-row'>";
        if (r === 2) {
          html += "<div class='osk-key shift" + shiftClass + "' data-key='SHIFT'>&#8593;</div>";
        }
        for (var c = 0; c < layout[r].length; c++) {
          var ch = layout[r][c];
          html += "<div class='osk-key' data-key='" + ch + "'>" + ch + "</div>";
        }
        if (r === 2) {
          html += "<div class='osk-key shift" + shiftClass + "' data-key='SHIFT'>&#8593;</div>";
        }
        html += "</div>";
      }
      html += "<div class='osk-row'>";
      html += "<div class='osk-key wide special' data-key='-'>-</div>";
      html += "<div class='osk-key wide special' data-key='_'>_</div>";
      html += "<div class='osk-key space' data-key=' '>Пробел</div>";
      html += "<div class='osk-key wide special' data-key='.'><b>.</b></div>";
      html += "<div class='osk-key wide special' data-key='@'>@</div>";
      html += "<div class='osk-key enter' data-key='ENTER'>&#9166;</div>";
      html += "</div>";
      var container = document.getElementById("osk-keys");
      container.innerHTML = html;
      var keys = container.querySelectorAll(".osk-key");
      for (var k = 0; k < keys.length; k++) {
        keys[k].onclick = function() {
          var key = this.getAttribute("data-key");
          if (key === "BACKSPACE") { oskBackspace(); }
          else if (key === "SHIFT") { oskToggleShift(); }
          else if (key === "ENTER") { oskEnter(); }
          else { oskType(key); }
        };
      }
    }

    function oskType(ch) {
      if (!oskTarget) return;
      if (oskShift && oskTarget.type !== 'password') {
        oskTarget.value += ch;
        oskToggleShift();
      } else {
        oskTarget.value += ch;
      }
      oskTarget.dispatchEvent(new Event('input', {bubbles: true}));
      oskUpdatePreview();
    }

    function oskBackspace() {
      if (!oskTarget) return;
      oskTarget.value = oskTarget.value.slice(0, -1);
      oskTarget.dispatchEvent(new Event('input', {bubbles: true}));
      oskUpdatePreview();
    }

    function oskEnter() {
      if (!oskTarget) return;
      if (oskTarget.id === 'wifi-pass-input') {
        connectWiFi();
        oskHide();
      } else {
        oskTarget.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
      }
      oskUpdatePreview();
    }

    function oskToggleShift() {
      oskShift = !oskShift;
      oskRenderKeys();
    }

    function oskToggleLang() {
      oskLang = oskLang === 'ru' ? 'en' : 'ru';
      document.getElementById('osk-lang-btn').textContent = oskLang.toUpperCase();
      oskShift = false;
      oskRenderKeys();
    }


  </script>

<script>
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Обновляем "Треков"
        const tracksEl = document.querySelector('[data-stat="tracks"]');
        if (tracksEl) tracksEl.innerText = data.tracks;
        
        // Обновляем "Постеров"
        const postersEl = document.querySelector('[data-stat="posters"]');
        if (postersEl) postersEl.innerText = data.posters;
        
        // Обновляем "Занято"
        const usedEl = document.querySelector('[data-stat="used_gb"]');
        if (usedEl) {
            usedEl.innerText = (data.used_gb < 1 ? (data.used_gb * 1024).toFixed(1) + ' MB' : data.used_gb.toFixed(2) + ' GB');
            // Меняем цвет в зависимости от заполнения (опционально)
            if (data.used_gb > 200) usedEl.style.color = '#ef4444';
            else usedEl.style.color = '#10b981';
        }
    } catch (error) {
        console.error('Ошибка получения статистики:', error);
    }
}

// Запускаем при загрузке страницы
document.addEventListener('DOMContentLoaded', updateStats);

// Обновляем каждые 5 минут
setInterval(updateStats, 300000);
</script>



  <!-- ===== Экранная клавиатура ===== -->
  <div id="osk-overlay">
    <div id="osk-bar">
      <div style="display:flex; align-items:center; gap:8px;">
        <span id="osk-target-name">Ввод текста</span>
        <span id="osk-input-preview"></span>
      </div>
      <div>
        <button id="osk-lang-btn" onclick="oskToggleLang()">RU</button>
        <button id="osk-close" onclick="oskHide()">&#10006; Закрыть</button>
      </div>
    </div>
    <div id="osk-keys"></div>
  </div>

  <div class="footer">Professional karaoke server. Made by Roman Potashov</div>

  <script>
  /* KARAOKE_WIFI_SETUP_INDICATOR_V2 */
  function openKaraokeWifiSetup() {
    var frame = document.getElementById('karaoke-wifi-frame');
    if (!frame.getAttribute('src')) frame.src = '/wifi/setup?embedded=1';
    document.getElementById('karaoke-wifi-dialog').style.display = 'block';
  }
  function closeKaraokeWifiSetup() {
    document.getElementById('karaoke-wifi-dialog').style.display = 'none';
    loadWiFiStatus();
  }
  (function() {
    var indicator = document.getElementById('karaoke-wifi-setup-indicator');
    var pending = false;
    if (!indicator) return;
    var setupButton = document.getElementById('karaoke-wifi-setup-open');
    if (setupButton) setupButton.onclick = openKaraokeWifiSetup;
    function checkKaraokeWifi() {
      if (pending) return;
      pending = true;
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/karaoke-wifi-monitor', true);
      xhr.timeout = 4000;
      xhr.onload = function() {
        if (xhr.status !== 200) return;
        try {
          var state = JSON.parse(xhr.responseText);
          indicator.style.display = state.setup_needed && state.ap_active && !state.connected
            ? 'block' : 'none';
        } catch (e) {}
      };
      xhr.onloadend = function() { pending = false; };
      try { xhr.send(null); } catch (e) { pending = false; }
    }
    checkKaraokeWifi();
    setInterval(checkKaraokeWifi, 3000);
  })();
  </script>

</body>
</html>"""

# YOUTUBE_MANAGER_X96Q_V1
from karaoke_youtube_manager import bp as youtube_bp
app.register_blueprint(youtube_bp)
from karaoke_quarantine import bp as quarantine_bp, init as quarantine_init, blocked as quarantine_blocked, mentions as quarantine_mentions
app.register_blueprint(quarantine_bp)
app.config['QUARANTINE_PLAYER_STATE'] = lambda: dict(_player_state)

@app.route('/poster-manager')
def poster_manager_page():
    return send_from_directory('/root/karaoke', 'poster_manager.html')

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/top_artists')
def top_artists():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT artist, SUM(plays) AS total_plays FROM songs GROUP BY artist ORDER BY total_plays DESC, artist LIMIT 30')
    artists = []
    for r in c.fetchall():
        if quarantine_blocked(r['artist']):
            continue
        poster = find_poster(r['artist'])
        artists.append({'artist': r['artist'], 'total_plays': r['total_plays'], 'poster': poster})
    conn.close()
    return jsonify(artists)

@app.route('/search')
def search():
    q = request.args.get('q', '').strip().lower()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM songs ORDER BY plays DESC, artist, title')
    rows = c.fetchall()
    conn.close()
    songs = []
    for r in rows:
        artist = r['artist'] or ''
        title = r['title'] or ''

        # Сначала быстрый поиск по названию и исполнителю.
        if q and q not in artist.lower() and q not in title.lower():
            continue

        # Проверка карантина сохраняется для каждого результата.
        if quarantine_mentions(r['file'] or ''):
            continue

        songs.append({'id': r['id'], 'artist': artist, 'title': title, 'file': r['file'], 'plays': r['plays']})
    return jsonify(songs)

@app.route('/play', methods=['POST'])
def play():
    fname = request.json.get('file')
    if not fname:
        return jsonify({'error': 'No file'})
    if not isinstance(fname, str) or os.path.basename(fname) != fname:
        return jsonify({'error': 'Недопустимое имя файла'}), 400
    artist, _ = parse_filename(fname)
    if quarantine_mentions(fname):
        return jsonify({'error': 'Исполнитель в карантине'}), 403
    path = os.path.join(UPLOAD_FOLDER, fname)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'})
    try:
        play_video_file(path)
        announce_song(fname)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/increment')
def increment():
    file = request.args.get('file', '')
    if not file:
        return jsonify({'error': 'No file'})
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE songs SET plays = plays + 1 WHERE file = ?', (file,))
    conn.commit()
    conn.close()
    socketio.emit('plays_update', {'file': file})
    return jsonify({'ok': True})

@app.route('/queue/add', methods=['POST'])
def queue_add():
    song_id = request.json.get('song_id')
    if not song_id:
        return jsonify({'error': 'No song_id'})
    conn = get_db()
    c = conn.cursor()
    song = c.execute('SELECT artist FROM songs WHERE id=?', (song_id,)).fetchone()
    if not song or quarantine_blocked(song['artist']):
        conn.close()
        return jsonify({'error': 'Песня отсутствует или исполнитель в карантине'}), 403
    c.execute('INSERT INTO queue (song_id) VALUES (?)', (song_id,))
    conn.commit()
    conn.close()
    broadcast_state('queue_update')
    return jsonify({'ok': True})

@app.route('/queue/list')
def queue_list():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file
        FROM queue q
        JOIN songs s ON q.song_id = s.id
        ORDER BY q.added_at ASC, q.id ASC
    ''')
    rows = c.fetchall()
    conn.close()
    queue = []
    for r in rows:
        queue.append({
            'queue_id': r['queue_id'],
            'song_id': r['song_id'],
            'artist': r['artist'],
            'title': r['title'],
            'file': r['file']
        })
    resp = jsonify(queue)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/queue/next')
def queue_next():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file
        FROM queue q
        JOIN songs s ON q.song_id = s.id
        ORDER BY q.added_at ASC, q.id ASC
        LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        c.execute('DELETE FROM queue WHERE id = ?', (row['queue_id'],))
        conn.commit()
    conn.close()
    broadcast_state('queue_update')
    if row:
        socketio.emit('song_started', {'file': row['file'], 'artist': row['artist'], 'title': row['title']})
        return jsonify({'song': {'file': row['file'], 'artist': row['artist'], 'title': row['title']}})
    return jsonify({'song': None})

@app.route('/queue/remove/<int:queue_id>', methods=['DELETE'])
def queue_remove(queue_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM queue WHERE id = ?', (queue_id,))
    conn.commit()
    conn.close()
    broadcast_state('queue_update')
    return jsonify({'ok': True})

@app.route('/queue/move', methods=['POST'])
def queue_move():
    data = request.get_json(force=True)
    queue_id = data.get('queue_id')
    direction = data.get('direction', 0)
    if not queue_id or direction not in (-1, 1):
        return jsonify({'error': 'bad params'})
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM queue ORDER BY added_at ASC, id ASC')
    rows = c.fetchall()
    ids = [r['id'] for r in rows]
    idx = None
    for i, rid in enumerate(ids):
        if rid == queue_id:
            idx = i
            break
    if idx is None:
        conn.close()
        return jsonify({'error': 'not in queue'})
    new_idx = idx + direction
    if new_idx < 0 or new_idx >= len(ids):
        conn.close()
        return jsonify({'error': 'out of range'})
    ids[idx], ids[new_idx] = ids[new_idx], ids[idx]
    for i, rid in enumerate(ids):
        ts = '2000-01-01 00:00:00.{:09d}'.format(i)
        c.execute('UPDATE queue SET added_at = ? WHERE id = ?', (ts, rid))
    conn.commit()
    conn.close()
    broadcast_state('queue_update')
    return jsonify({'ok': True})

@app.route('/queue/clear', methods=['POST'])
def queue_clear():
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM queue')
    conn.commit()
    conn.close()
    broadcast_state('queue_update')
    return jsonify({'ok': True})

def send_mpv_command(command):
    if not os.path.exists('/tmp/mpvsocket'):
        return False
    # Проверяем, что mpv реально живой
    try:
        result = subprocess.run(['pgrep', '-x', 'mpv'], capture_output=True, timeout=2)
        if result.returncode != 0:
            os.remove('/tmp/mpvsocket')
            return False
    except Exception:
        pass
    try:
        import socket as sock_mod, json
        s = sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM)
        s.settimeout(2)
        s.connect('/tmp/mpvsocket')
        cmd = json.dumps({"command": command}) + "\n"
        s.sendall(cmd.encode())
        try:
            s.recv(4096)
        except Exception:
            pass
        s.close()
        return True
    except Exception:
        try:
            os.remove('/tmp/mpvsocket')
        except FileNotFoundError:
            pass
        return False

@app.route('/api/stop')
def api_stop():
    global _manual_stop
    _manual_stop = True
    ok = send_mpv_command(["quit"])
    if not ok:
        logger.warning('Караоке mpv не ответил на quit; BGM не трогаем')
    time.sleep(0.5)
    try:
        os.remove('/tmp/mpvsocket')
    except FileNotFoundError:
        pass
    # Фоновый mpv не трогаем: отдельный IPC-сокет /tmp/bgm_mpvsocket.
    _player_state.update(playing=False, paused=False, file='', artist='', title='')
    socketio.emit("song_stopped", {})
    socketio.emit("player_cmd", {"cmd": "stop"})
    return jsonify({'ok': True})

@app.route('/api/pause')
def api_pause():
    ok = send_mpv_command(["cycle", "pause"])
    if ok:
        _player_state["paused"] = not _player_state["paused"]
    socketio.emit("player_cmd", {"cmd": "pause", "paused": _player_state["paused"]})
    return jsonify({'ok': ok})

def _advance_queue_after_end():
    conn = get_db()
    try:
        row = conn.execute('''SELECT q.id AS queue_id, s.file FROM queue q
                              JOIN songs s ON q.song_id=s.id
                              ORDER BY q.added_at, q.id LIMIT 1''').fetchone()
        if row:
            conn.execute('DELETE FROM queue WHERE id=?', (row['queue_id'],))
            conn.commit()
    finally:
        conn.close()
    broadcast_state('queue_update')
    if row:
        path = os.path.join(UPLOAD_FOLDER, row['file'])
        if os.path.isfile(path):
            play_video_file(path)
            announce_song(row['file'])

@app.route('/api/next')
def api_next():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT q.id AS queue_id, s.file
        FROM queue q
        JOIN songs s ON q.song_id = s.id
        ORDER BY q.added_at ASC, q.id ASC
        LIMIT 1
    ''')
    row = c.fetchone()
    if row:
        c.execute('DELETE FROM queue WHERE id = ?', (row['queue_id'],))
        conn.commit()
    conn.close()
    if row:
        path = os.path.join(UPLOAD_FOLDER, row['file'])
        if os.path.exists(path):
            play_video_file(path)
    else:
        global _manual_stop
        _manual_stop = True
        send_mpv_command(["quit"])
    broadcast_state('queue_update')
    if row:
        announce_song(row['file'])
    return jsonify({'ok': True, 'has_next': row is not None})

@app.route('/upload', methods=['POST'])
def upload():
    import time as _time
    t0 = _time.time()
    if 'file' not in request.files:
        return jsonify({'error': 'No file'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'})
    if not allowed_file(file.filename):
        return jsonify({'error': 'Bad extension'})
    safe_name = safe_filename(file.filename)
    upload_artist, _ = parse_filename(safe_name)
    if quarantine_mentions(safe_name):
        return jsonify({'error': 'Исполнитель в карантине'}), 403
    full_path = os.path.join(UPLOAD_FOLDER, safe_name)
    logger.info(f'Upload video: orig="{file.filename}" -> saved="{safe_name}"')
    t1 = _time.time()
    file.save(full_path)
    t2 = _time.time()
    logger.info(f'Upload timing: total_received={t1-t0:.2f}s, save_to_disk={t2-t1:.2f}s, size={os.path.getsize(full_path)//1024}KB')
    artist, title = parse_filename(safe_name)
    if not artist or not title:
        artist = 'Unknown'
        title = safe_name
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT OR REPLACE INTO songs (artist, title, file, plays) VALUES (?, ?, ?, 0)', (artist, title, safe_name))
        conn.commit()
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()
    socketio.emit('db_update', {'added': safe_name})
    return jsonify({'artist': artist, 'title': title, 'file': safe_name})

@app.route('/refresh_after_upload', methods=['POST'])
def refresh_after_upload():
    refresh_database()
    return jsonify({'ok': True})

@app.route('/upload_poster', methods=['POST'])
def upload_poster():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'})
    name, ext = os.path.splitext(file.filename)
    if ext.lower().lstrip('.') not in POSTER_EXTENSIONS:
        return jsonify({'error': 'Bad extension'})
    artist = name.strip()
    if not artist:
        return jsonify({'error': 'No artist name'})
    safe_name = safe_filename(artist + ext)
    full_path = os.path.join(POSTER_FOLDER, safe_name)
    logger.info(f'Upload poster: orig="{file.filename}" -> saved="{safe_name}"')
    if os.path.exists(full_path):
        file.save(full_path + '.tmp')
        existing_hash = file_hash_quick(full_path)
        new_hash = file_hash_quick(full_path + '.tmp')
        os.remove(full_path + '.tmp')
        if existing_hash == new_hash and existing_hash:
            return jsonify({'error': 'Duplicate poster'})
    file.save(full_path)
    artist_name, _ = os.path.splitext(safe_name)
    socketio.emit('posters_update', {'artist': artist_name})
    return jsonify({'artist': artist_name})

@app.route('/fonsound_list')
def fonsound_list():
    files = []
    if os.path.exists(FONSOUND_FOLDER):
        files = sorted([f for f in os.listdir(FONSOUND_FOLDER) if f.lower().endswith('.mp3')])
    return jsonify(files)

@app.route('/fonsound/<path:filename>')
def serve_fonsound(filename):
    return send_from_directory(FONSOUND_FOLDER, filename)


@app.route('/api/bgm/start')
def api_bgm_start():
    bgm_start()
    return jsonify({'ok': True, 'tracks': len(bgm_get_tracks())})

@app.route('/api/bgm/stop')
def api_bgm_stop():
    bgm_stop()
    return jsonify({'ok': True})

@app.route('/api/bgm/volume')
def api_bgm_volume():
    vol = request.args.get('vol', 25)
    bgm_set_volume(int(vol))
    return jsonify({'ok': True, 'volume': bgm_volume})

@app.route('/api/bgm/toggle')
def api_bgm_toggle():
    global bgm_enabled
    bgm_enabled = request.args.get('enabled', 'true') == 'true'
    save_bgm_settings()
    if bgm_enabled:
        bgm_start()
    else:
        bgm_stop()
    return jsonify({'ok': True, 'enabled': bgm_enabled})

@app.route('/api/bgm/status')
def api_bgm_status():
    return jsonify({
        'enabled': bgm_enabled,
        'volume': bgm_volume,
        'playing': bgm_process is not None,
        'tracks': len(bgm_get_tracks()),
        'video_volume': video_volume
    })

@app.route('/api/video/volume')
def api_video_volume():
    vol = request.args.get('vol', '80')
    video_set_volume(int(vol))
    return jsonify({'ok': True, 'volume': video_volume})

@app.route('/api/files/list')
def api_files_list():
    ftype = request.args.get('type', 'video')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = request.args.get('q', '').lower()
    if ftype == 'video':
        folder, exts = UPLOAD_FOLDER, {'mp4', 'avi', 'mkv', 'mov'}
    elif ftype == 'poster':
        folder, exts = POSTER_FOLDER, {'jpg', 'jpeg', 'png', 'webp'}
    elif ftype == 'bgm':
        folder, exts = FONSOUND_FOLDER, {'mp3'}
    else:
        return jsonify({'error': 'bad type'})
    files = []
    for f in os.listdir(folder):
        full = os.path.join(folder, f)
        if not os.path.isfile(full):
            continue
        ext = f.rsplit('.', 1)[-1].lower() if '.' in f else ''
        if ext not in exts:
            continue
        if q and q not in f.lower():
            continue
        st = os.stat(full)
        files.append({'name': f, 'size': st.st_size, 'size_mb': round(st.st_size / 1048576, 1), 'date': int(st.st_mtime)})
    files.sort(key=lambda x: x['name'].lower())
    total = len(files)
    start = (page - 1) * per_page
    page_files = files[start:start + per_page]
    if ftype == 'video':
        conn = get_db()
        c = conn.cursor()
        for f in page_files:
            c.execute("SELECT q.id FROM queue q JOIN songs s ON q.song_id = s.id WHERE s.file = ?", (f['name'],))
            f['in_queue'] = c.fetchone() is not None
        conn.close()
    return jsonify({'files': page_files, 'total': total, 'page': page, 'per_page': per_page, 'pages': (total + per_page - 1) // per_page})

@app.route('/api/files/delete', methods=['POST'])
def api_files_delete():
    data = request.get_json(force=True)
    ftype = data.get('type')
    filename = data.get('name')
    if not filename or '/' in filename or '..' in filename:
        return jsonify({'error': 'bad filename'})
    if ftype == 'video':
        folder, exts = UPLOAD_FOLDER, {'mp4', 'avi', 'mkv', 'mov'}
    elif ftype == 'poster':
        folder, exts = POSTER_FOLDER, {'jpg', 'jpeg', 'png', 'webp'}
    elif ftype == 'bgm':
        folder, exts = FONSOUND_FOLDER, {'mp3'}
    else:
        return jsonify({'error': 'bad type'})
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in exts:
        return jsonify({'error': 'bad extension'})
    full_path = os.path.join(folder, filename)
    if not os.path.exists(full_path):
        return jsonify({'error': 'not found'})
    if ftype == 'video':
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM songs WHERE file = ?", (filename,))
        row = c.fetchone()
        if row:
            c.execute("DELETE FROM queue WHERE song_id = ?", (row['id'],))
            c.execute("DELETE FROM songs WHERE id = ?", (row['id'],))
            conn.commit()
        conn.close()
    os.remove(full_path)
    logger.info('Deleted file: %s/%s' % (folder, filename))
    socketio.emit('posters_update' if ftype == 'poster' else 'db_update', {'deleted': filename})
    if ftype == 'video': broadcast_state('queue_update')
    return jsonify({'ok': True})

@app.route('/upload_bgm', methods=['POST'])
def upload_bgm():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'})
    name, ext = os.path.splitext(file.filename)
    if ext.lower() != '.mp3':
        return jsonify({'error': 'Only MP3 allowed'})
    safe_name = safe_filename(file.filename)
    full_path = os.path.join(FONSOUND_FOLDER, safe_name)
    logger.info(f'Upload BGM: orig="{file.filename}" -> saved="{safe_name}"')
    file.save(full_path)
    return jsonify({'filename': safe_name})


# KARAOKE_WIFI_SETUP_V2: all NetworkManager operations live in wifi.network.
@app.route('/api/karaoke-wifi-monitor')
def karaoke_wifi_monitor_status():
    return jsonify(wifi_network.read_status())


def _wifi_control_allowed():
    # Use the actual peer address, never client-supplied forwarding headers.
    try:
        peer = ipaddress.ip_address(request.remote_addr or '')
    except ValueError:
        return False
    if peer.is_loopback:
        return True
    state = wifi_network.read_status()
    if state.get('connected') and str(peer) == state.get('ip'):
        return True  # TV browser can address this machine by its own station IP.
    return (peer in ipaddress.ip_network('192.168.100.0/24')
            and bool(state.get('ap_active')))


def _wifi_job_response(operation):
    try:
        job_id = operation()
        return jsonify({'ok': True, 'job_id': job_id,
                        'message': 'Запрос принят. Проверяем подключение.'}), 202
    except ValueError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 409
    except Exception:
        logger.exception('Wi-Fi operation could not be started')
        return jsonify({'ok': False, 'error': 'Служба настройки Wi-Fi недоступна'}), 503


def _wifi_connect_request(portal_only=False):
    if not _wifi_control_allowed():
        return jsonify({'ok': False, 'error': 'Настраивайте Wi-Fi с экрана приставки или подключитесь к KARAOKE'}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'ok': False, 'error': 'Неверные данные запроса'}), 400
    if portal_only and not wifi_network.read_status().get('ap_active'):
        return jsonify({'ok': False, 'error': 'Точка KARAOKE сейчас не включена'}), 409
    return _wifi_job_response(lambda: wifi_network.submit_connection(
        data.get('ssid', ''), data.get('password', '')))


@app.route('/api/wifi/portal-connect', methods=['POST'])
def karaoke_portal_connect():
    return _wifi_connect_request(portal_only=True)


@app.route('/api/wifi/job/<job_id>')
def karaoke_wifi_job(job_id):
    try:
        return jsonify(wifi_network.read_job(job_id))
    except ValueError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 409


@app.route('/api/wifi/reset', methods=['POST'])
def karaoke_wifi_reset():
    if not _wifi_control_allowed():
        return jsonify({'ok': False, 'error': 'Сброс доступен с экрана приставки или из сети KARAOKE'}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'ok': False, 'error': 'Нужно подтвердить сброс Wi-Fi'}), 400
    return _wifi_job_response(lambda: wifi_network.request_reset(
        confirmed=data.get('confirmed') is True))


@app.route('/wifi/setup')
def karaoke_wifi_setup_page():
    return send_from_directory('/root/karaoke/wifi', 'setup.html')


@app.route('/wifi/setup-qr.png')
def karaoke_wifi_setup_qr():
    return send_from_directory('/root/karaoke/wifi', 'setup-qr.png', mimetype='image/png')


@app.route('/api/network_status')
def api_network_status():
    return jsonify(get_network_status())

@app.route('/settings/info')
def settings_info():
    media_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    poster_files = [f for f in os.listdir(POSTER_FOLDER) if os.path.isfile(os.path.join(POSTER_FOLDER, f))]
    try:
        du = shutil.disk_usage('/mnt/usb_disk')
        disk_used_gb = round(du.used / (1024**3), 4)
        disk_used_mb = round(du.used / (1024**2), 1)
        disk_total_gb = round(du.total / (1024**3), 1)
    except:
        disk_used_gb = 0
        disk_used_mb = 0
        disk_total_gb = 0
    return jsonify({
        'upload_folder': UPLOAD_FOLDER,
        'poster_folder': POSTER_FOLDER,
        'song_count': len(media_files),
        'poster_count': len(poster_files),
        'disk_used_gb': disk_used_gb,
        'disk_used_mb': disk_used_mb,
        'disk_total_gb': disk_total_gb,
    })

@app.route('/api/format_hdd', methods=['POST'])
def api_format_hdd():
    try:
        import glob
        # Найти USB-диск (не mmcblk)
        usb_disks = []
        for d in glob.glob('/dev/sd*1'):
            if not d.endswith('1'):
                continue
            # Проверить что это не системный диск
            if 'mmcblk' in d:
                continue
            usb_disks.append(d)
        if not usb_disks:
            return jsonify({'error': 'USB HDD not found'})
        disk_part = usb_disks[0]
        subprocess.run(['umount', '/mnt/hdd'], capture_output=True, timeout=10)
        subprocess.run(['mkfs.ext4', '-F', disk_part], capture_output=True, timeout=120)
        subprocess.run(['mount', disk_part, '/mnt/hdd'], capture_output=True, timeout=10)
        os.makedirs('/mnt/hdd/karaoke_media', exist_ok=True)
        os.makedirs('/mnt/hdd/posters', exist_ok=True)
        os.makedirs('/mnt/hdd/fonsound', exist_ok=True)
        # Обновить fstab по UUID
        uuid_result = subprocess.run(['blkid', '-s', 'UUID', '-o', 'value', disk_part], capture_output=True, text=True)
        uuid_val = uuid_result.stdout.strip()
        with open('/etc/fstab', 'r') as f:
            lines = [l for l in f.readlines() if '/mnt/hdd' not in l]
        if uuid_val:
            lines.append(f'UUID={uuid_val} /mnt/hdd ext4 defaults,nofail 0 2\n')
        else:
            lines.append(f'{disk_part} /mnt/hdd ext4 defaults,nofail 0 2\n')
        with open('/etc/fstab', 'w') as f:
            f.writelines(lines)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/settings/refresh_db', methods=['POST'])
def settings_refresh_db():
    res = refresh_database()
    socketio.emit('db_update', res)
    broadcast_state('queue_update')
    return jsonify(res)

# === Автоматическое пополнение постеров (Wikimedia Commons) ===
# Для работы нужен Pillow: python3 -m pip install Pillow
@app.route('/api/posters/missing')
def poster_missing():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT artist FROM songs WHERE artist != '' ORDER BY artist").fetchall()
    conn.close()
    names = [r['artist'] for r in rows]
    missing = [name for name in names if not find_poster(name)]
    return jsonify({'total': len(names), 'missing': missing, 'missing_count': len(missing)})

@app.route('/api/posters/search')
def poster_search():
    artist = request.args.get('artist', '').strip()
    if not artist or len(artist) > 100:
        return jsonify({'error': 'Укажите исполнителя (до 100 символов)'}), 400
    try:
        from poster_auto import search_all
        return jsonify({'artist': artist, **search_all(artist)})
    except Exception as exc:
        from poster_auto import PosterRateLimited
        logger.warning('Поиск постера: %s', exc)
        if isinstance(exc, PosterRateLimited):
            return jsonify({'error': str(exc)}), 429
        return jsonify({'error': 'Источник изображений временно недоступен. Попробуйте позже.'}), 503

@app.route('/api/posters/yandex-preview/<token>')
def poster_yandex_preview(token):
    try:
        from poster_auto import yandex_preview
        from flask import Response
        return Response(yandex_preview(token), mimetype='image/jpeg', headers={'Cache-Control': 'private, max-age=900', 'X-Content-Type-Options':'nosniff'})
    except Exception as exc:
        logger.warning('Миниатюра Яндекс: %s', exc)
        return ('Изображение недоступно', 404)

@app.route('/api/posters/download', methods=['POST'])
def poster_download():
    data = request.get_json(silent=True) or {}
    artist = str(data.get('artist', '')).strip()
    url = str(data.get('url', ''))
    if not artist or len(artist) > 120:
        return jsonify({'error': 'Некорректное имя артиста'}), 400
    conn = get_db()
    known = conn.execute('SELECT 1 FROM songs WHERE artist = ? LIMIT 1', (artist,)).fetchone()
    conn.close()
    if not known:
        return jsonify({'error': 'Исполнитель отсутствует в медиатеке'}), 400
    try:
        from poster_auto import save
        filename = save(artist, url, POSTER_FOLDER, '/mnt/usb_disk', overwrite=False)
        socketio.emit('db_update', {'posters_updated': True})
        return jsonify({'ok': True, 'filename': filename})
    except (ValueError, RuntimeError, FileExistsError) as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        logger.exception('Ошибка сохранения постера: %s', exc)
        return jsonify({'error': 'Ошибка загрузки постера'}), 500

@app.route('/posters/<path:filename>')
def serve_poster(filename):
    return send_from_directory(POSTER_FOLDER, filename)


# === Shared UI state ===
_shared_search = ''
_player_state = {'playing': False, 'paused': False, 'file': '', 'artist': '', 'title': ''}

def current_shared_state():
    conn = get_db()
    try:
        rows = conn.execute('SELECT q.id AS queue_id, s.id AS song_id, s.artist, s.title, s.file FROM queue q JOIN songs s ON q.song_id=s.id ORDER BY q.added_at, q.id').fetchall()
        return {'queue': [dict(r) for r in rows], 'search': _shared_search, 'player': dict(_player_state)}
    finally:
        conn.close()

def announce_song(file):
    conn = get_db()
    try:
        row = conn.execute('SELECT artist, title FROM songs WHERE file=? LIMIT 1', (file,)).fetchone()
    finally:
        conn.close()
    _player_state.update(playing=True, paused=False, file=file, artist=row['artist'] if row else '', title=row['title'] if row else '')
    socketio.emit('song_started', dict(_player_state))

# === WebSocket handlers ===

@socketio.on('connect')
def ws_connect():
    logger.info('WebSocket client connected')
    emit('full_state', current_shared_state())

@socketio.on('disconnect')
def ws_disconnect():
    logger.info('WebSocket client disconnected')

@socketio.on('search_sync')
def ws_search_sync(data):
    
    global _shared_search
    q = str((data or {}).get('q', ''))[:150]
    _shared_search = q
    emit('search_sync', {'q': q}, broadcast=True, include_self=False)


@app.route('/socket.io.min.js')
def serve_socket_io():
    return send_from_directory('/root/karaoke', 'socket.io.min.js')


# ===== WiFi Management API =====
@app.route('/api/wifi/scan')
def wifi_scan():
    try:
        return jsonify({'networks': wifi_network.scan_networks()})
    except (ValueError, RuntimeError) as exc:
        return jsonify({'error': str(exc)}), 409
    except Exception:
        logger.exception('Wi-Fi scan failed')
        return jsonify({'error': 'Не удалось получить список сетей'}), 503


@app.route('/api/wifi/connect', methods=['POST'])
def wifi_connect():
    return _wifi_connect_request()


@app.route('/api/wifi/status')
def wifi_status():
    state = wifi_network.read_status()
    return jsonify({'connection': state.get('network') or '',
                    'ip': state.get('ip') or '',
                    'connected': bool(state.get('connected')),
                    'ap_active': bool(state.get('ap_active'))})


def bgm_startup_fix():
    """Перезапуск первого трека + установка сохранённой громкости через 3 сек"""
    time.sleep(3)
    try:
        import socket as _sock
        s = _sock.socket(_sock.AF_UNIX, _sock.SOCK_STREAM)
        s.settimeout(2)
        s.connect('/tmp/bgm_mpvsocket')
        # Перезапускаем трек с начала
        s.sendall(b'{"command":["set_property","time-pos",0]}\n')
        s.recv(1024)
        # Явно ставим сохранённую громкость
        vol_cmd = '{"command":["set_property","volume",' + str(bgm_volume) + ']}\n'
        s.sendall(vol_cmd.encode())
        s.recv(1024)
        s.close()
        logger.info("BGM track restarted, volume set to " + str(bgm_volume))
    except Exception as e:
        logger.warning("BGM restart failed: " + str(e))


@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = get_media_stats()
    gb_size = stats['total_size_bytes'] / (1024 ** 3)
    
    return jsonify({
        'tracks': stats['tracks_count'],
        'posters': stats['posters_count'],
        'used_gb': round(gb_size, 4)
    })





def _media_snapshot():
    if not os.path.ismount('/mnt/usb_disk'):
        return None
    try:
        return tuple(sorted((e.name, e.stat().st_size, e.stat().st_mtime_ns)
                            for e in os.scandir(UPLOAD_FOLDER)
                            if e.is_file() and allowed_file(e.name)))
    except OSError as exc:
        logger.warning('Media scan unavailable: %s', exc)
        return None

def _media_watcher():
    previous = _media_snapshot()
    pending = None
    while True:
        time.sleep(8)
        current = _media_snapshot()
        if current is None:
            continue  # never erase DB when HDD is absent
        if current != previous:
            previous, pending = current, time.monotonic()
        elif pending is not None and time.monotonic() - pending >= 8:
            pending = None
            try:
                result = refresh_database()
                if any(result.values()):
                    socketio.emit('db_update', result)
                    broadcast_state('queue_update')
            except Exception:
                logger.exception('Automatic media database refresh failed')

if __name__ == '__main__':
    init_db()
    quarantine_init()
    if os.path.ismount('/mnt/usb_disk'):
        refresh_database()
    else:
        logger.warning('HDD is not mounted: skip startup DB refresh')
    threading.Thread(target=_media_watcher, daemon=True).start()
    bgm_start()
    threading.Thread(target=bgm_startup_fix, daemon=True).start()
    logger.info("Server started on http://0.0.0.0:8080")
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
