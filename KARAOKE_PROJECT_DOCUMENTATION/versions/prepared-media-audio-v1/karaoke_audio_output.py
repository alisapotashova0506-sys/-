"""Route both mpv players to a verified ALSA output, without muting analog."""
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time

# The shared mixer allows karaoke and background music on the same output.
DEVICES = {'hdmi': 'alsa/dmix:CARD=HDMI,DEV=0',
           'analog': 'alsa/dmix:CARD=audiocodec,DEV=0'}
SETTINGS = Path('/root/karaoke/.audio_output.json')
SOCKETS = ('/tmp/mpvsocket', '/tmp/bgm_mpvsocket')
lock = threading.RLock()


def selected_mode():
    try:
        value = json.loads(SETTINGS.read_text()).get('mode')
        if value in DEVICES:
            return value
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return 'hdmi'


def player_args():
    return ['--ao=alsa', '--audio-device=' + DEVICES[selected_mode()]]


def wait_ready(path, timeout=3):
    """Serialize startup with output changes until the new player has IPC."""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            if ipc(path, ['get_property', 'audio-device']) != DEVICES[selected_mode()]:
                ipc(path, ['set_property', 'audio-device', DEVICES[selected_mode()]])
            return True
        except (OSError, ValueError, RuntimeError):
            time.sleep(0.05)
    return False


def cards():
    return {p.read_text().strip() for p in Path('/proc/asound').glob('card[0-9]*/id')}


def ipc(path, command):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(4)
        client.connect(str(path))
        client.sendall((json.dumps({'command': command, 'request_id': 817}) + '\n').encode())
        with client.makefile('r', encoding='utf-8') as reader:
            for _ in range(100):
                line = reader.readline()
                if not line:
                    break
                response = json.loads(line)
                if response.get('request_id') == 817:
                    if response.get('error') != 'success':
                        raise RuntimeError('Плеер не переключил звук: ' + str(response.get('error')))
                    return response.get('data')
    raise RuntimeError('Плеер не подтвердил переключение звука.')


def save_mode(mode):
    fd, name = tempfile.mkstemp(prefix='.audio-output-', dir=SETTINGS.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump({'mode': mode}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, SETTINGS)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def status():
    with lock:
        available = cards()
        players, errors = [], []
        for path in SOCKETS:
            if os.path.exists(path):
                try:
                    players.append({'player': 'video' if path == SOCKETS[0] else 'bgm',
                                    'device': ipc(path, ['get_property', 'audio-device'])})
                except (OSError, ValueError, RuntimeError) as exc:
                    errors.append(str(exc))
        mode = selected_mode()
        matching = all(p['device'] == DEVICES[mode] for p in players)
        # Before the first switch the original wrapper uses a numeric ALSA ID.
        if mode == 'hdmi':
            matching = all(p['device'] in (DEVICES['hdmi'], 'alsa/plughw:1,0', 'auto') for p in players)
        return {'ok': True, 'mode': mode, 'analog_only': mode == 'analog',
                'available': {'HDMI', 'audiocodec'}.issubset(available),
                'players': players, 'verified': matching and not errors, 'error': '; '.join(errors)}


def set_analog_only(value):
    if type(value) is not bool:
        raise ValueError('Нужен параметр analog_only: true или false.')
    with lock:
        mode = 'analog' if value else 'hdmi'
        card = 'audiocodec' if value else 'HDMI'
        if card not in cards():
            raise RuntimeError('Звуковой выход не найден: ' + card)
        old, changed = {}, []
        try:
            for path in SOCKETS:
                if not os.path.exists(path):
                    continue
                old[path] = ipc(path, ['get_property', 'audio-device'])
                changed.append(path)
                was_idle = ipc(path, ['get_property', 'idle-active'])
                ipc(path, ['set_property', 'audio-device', DEVICES[mode]])
                if ipc(path, ['get_property', 'audio-device']) != DEVICES[mode]:
                    raise RuntimeError('Плеер не подтвердил выбранный выход.')
                # A property can change while ALSA initialization itself fails.
                # Active audio must still have an actual audio output driver.
                if not was_idle and (ipc(path, ['get_property', 'current-ao']) != 'alsa' or
                                     not ipc(path, ['get_property', 'audio-out-params'])):
                    raise RuntimeError('Звуковой выход плеера не открылся.')
            save_mode(mode)
        except BaseException as error:
            rollback_errors = []
            for path in reversed(changed):
                try:
                    ipc(path, ['set_property', 'audio-device', old[path]])
                except (OSError, ValueError, RuntimeError) as exc:
                    rollback_errors.append(str(exc))
            if rollback_errors:
                raise RuntimeError(str(error) + ' Не удалось вернуть прежний выход: ' + '; '.join(rollback_errors)) from error
            raise
        return status()


def create_blueprint():
    from flask import Blueprint, jsonify, request
    bp = Blueprint('audio_output', __name__)

    @bp.route('/api/audio/output')
    def get_output():
        try:
            return jsonify(status())
        except (OSError, ValueError, RuntimeError) as exc:
            return jsonify(ok=False, error=str(exc)), 409

    @bp.route('/api/audio/output', methods=['POST'])
    def set_output():
        try:
            body = request.get_json(silent=True)
            if not isinstance(body, dict) or set(body) != {'analog_only'}:
                raise ValueError('Нужен параметр analog_only.')
            return jsonify(set_analog_only(body['analog_only']))
        except ValueError as exc:
            return jsonify(ok=False, error=str(exc)), 400
        except (OSError, RuntimeError) as exc:
            return jsonify(ok=False, error=str(exc)), 409
    return bp


if __name__ == '__main__':
    if sys.argv[1:] != ['--device']:
        raise SystemExit('Use --device')
    print(DEVICES[selected_mode()])
