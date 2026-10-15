import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import time
import unittest
from unittest import mock

from flask import Flask

PROJECT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / 'updated' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


media = load('karaoke_media_optimizer')
audio = load('karaoke_audio_output')


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.mount = Path(self.temp.name)
        self.root = self.mount / 'karaoke_media'
        self.root.mkdir()
        self.db = self.mount / 'karaoke.db'
        with sqlite3.connect(self.db) as db:
            db.executescript('CREATE TABLE songs(id INTEGER PRIMARY KEY,artist TEXT,title TEXT,file TEXT UNIQUE,plays INTEGER DEFAULT 0);'
                             'CREATE TABLE queue(id INTEGER PRIMARY KEY,song_id INTEGER);')
        self.m = media.MediaOptimizer(self.root, self.db, self.mount)
        patcher = mock.patch.object(media.os.path, 'ismount', side_effect=lambda p: Path(p) == self.mount)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.changes = []
        self.m.changed = lambda: self.changes.append(True)

    def add(self, name, data=b'video', plays=7):
        p = self.root / name
        p.write_bytes(data)
        with sqlite3.connect(self.db) as db:
            db.execute('INSERT INTO songs(artist,title,file,plays) VALUES(?,?,?,?)', ('Artist', 'Song', name, plays))
        return p

    def fake_probe(self, path):
        return dict(width=640, height=360, fps=30, codec='h264', pix_fmt='yuv420p', sar='1:1',
                    rotation=0, duration=1, streams=[{'index': 0, 'codec_type': 'video'}],
                    can_transcode=True, interlaced=False, cadence_unknown=False)

    def scan(self):
        with mock.patch.object(media, 'probe', side_effect=self.fake_probe):
            self.m.start_scan()
            self.m.thread.join(10)
        self.assertEqual(self.m.job['state'], 'ready', self.m.job)
        return self.m.job['rows']

    def apply(self, actions):
        self.m.apply(self.m.job['id'], actions, True)
        self.m.thread.join(20)
        self.assertFalse(self.m.thread.is_alive())
        return self.m.job['results']

    def test_scan_is_readonly_and_finds_exact_not_name_duplicates(self):
        p = self.add('AC-DC - One.mp4', b'abcdef')
        self.add('Other - Two.mp4', b'abcdef')
        self.add('AC-DC - One.mkv', b'differv')
        before = self.db.read_bytes()
        rows = self.scan()
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual(p.read_bytes(), b'abcdef')
        self.assertEqual(len(next(r for r in rows if r['name'] == p.name)['duplicates']), 1)
        self.assertEqual(media.names('AC-DC - One.mp4'), ('AC-DC', 'One'))
        self.assertTrue(any(r['possible_duplicates'] for r in rows))
        self.assertTrue(all(any(i['kind'] == 'resolution' for i in r['issues']) for r in rows))

    def test_rename_preserves_song_id_plays_and_independent_backup(self):
        p = self.add('Artist - Song.mp4')
        row = self.scan()[0]
        result = self.apply([dict(file_id=row['id'], rename_to='AC-DC - New.mp4')])[0]
        self.assertEqual(result['status'], 'done', result)
        self.assertFalse(p.exists())
        target = self.root / 'AC-DC - New.mp4'
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT id,artist,title,plays,file FROM songs').fetchone(),
                             (1, 'AC-DC', 'New', 7, target.name))
        backup = Path(result['backup'])
        self.assertNotEqual(backup.stat().st_ino, target.stat().st_ino)
        target.write_bytes(b'new upload')
        self.assertEqual(backup.read_bytes(), b'video')

    def test_duplicate_moves_only_reviewed_copy_and_keeps_plays(self):
        self.add('Artist - A.mp4')
        self.add('Artist - B.mp4', plays=11)
        with sqlite3.connect(self.db) as db:
            db.executemany('INSERT INTO queue(id,song_id) VALUES(?,?)', [(10,1),(11,2)])
        a, b = self.scan()
        result = self.apply([dict(file_id=a['id'], duplicate_keep=b['id'])])[0]
        self.assertEqual(result['status'], 'done', result)
        self.assertFalse((self.root / a['name']).exists())
        self.assertEqual(Path(result['backup']).read_bytes(), b'video')
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT file,plays FROM songs').fetchall(), [(b['name'], 18)])
            self.assertEqual(db.execute('SELECT id,song_id FROM queue ORDER BY id').fetchall(), [(10,2),(11,2)])

    def test_stale_source_is_not_touched(self):
        path = self.add('Artist - Song.mp4')
        row = self.scan()[0]
        path.write_bytes(b'changed')
        result = self.apply([dict(file_id=row['id'], rename_to='Artist - New.mp4')])[0]
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(path.read_bytes(), b'changed')
        self.assertFalse((self.root / 'Artist - New.mp4').exists())

    def test_duplicate_rollback_restores_queue_and_both_play_counts(self):
        self.add('Artist - A.mp4', plays=7)
        self.add('Artist - B.mp4', plays=11)
        with sqlite3.connect(self.db) as db:
            db.executemany('INSERT INTO queue(id,song_id) VALUES(?,?)', [(10,1),(11,2)])
        a,b = self.scan()
        original_write = self.m.write_json
        failed = []
        def write(path,value):
            if path.name == 'journal.json' and value['phase'] == 'committed' and not failed:
                failed.append(True)
                raise OSError('power interruption')
            return original_write(path,value)
        with mock.patch.object(self.m,'write_json',side_effect=write):
            result = self.apply([dict(file_id=a['id'],duplicate_keep=b['id'])])[0]
        self.assertEqual(result['status'],'failed')
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT id,plays FROM songs ORDER BY id').fetchall(),[(1,7),(2,11)])
            self.assertEqual(db.execute('SELECT id,song_id FROM queue ORDER BY id').fetchall(),[(10,1),(11,2)])

    def test_collision_and_traversal_rejected_before_repair(self):
        self.add('Artist - Song.mp4')
        self.add('Artist - Other.mp4', b'other')
        rows = self.scan()
        song = next(r for r in rows if r['name'] == 'Artist - Song.mp4')
        for target in ('../Artist - New.mp4', 'Artist - Other.mp4', 'No separator.mp4'):
            with self.assertRaises((ValueError, RuntimeError)):
                self.m.apply(self.m.job['id'], [dict(file_id=song['id'], rename_to=target)], True)
        self.assertEqual(self.m.job['state'], 'ready')

    def test_playback_rejects_repair_and_stopped_queue_survives_rename(self):
        self.add('Artist - Song.mp4')
        row = self.scan()[0]
        action = dict(file_id=row['id'], rename_to='Artist - Other.mp4')
        self.m.is_playing = lambda: True
        with self.assertRaisesRegex(RuntimeError, 'воспроизведение'):
            self.m.apply(self.m.job['id'], [action], True)
        self.m.is_playing = lambda: False
        with sqlite3.connect(self.db) as db:
            db.execute('INSERT INTO queue(song_id) VALUES(1)')
        result = self.apply([action])[0]
        self.assertEqual(result['status'], 'done', result)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT song_id FROM queue').fetchall(), [(1,)])

    def test_missing_mount_never_creates_backup_directory(self):
        with mock.patch.object(media.os.path, 'ismount', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'HDD'):
                self.m.start_scan()
        self.assertFalse(self.m.storage.exists())

    def test_symlink_report_does_not_touch_target(self):
        outside = self.mount / 'outside'
        outside.write_bytes(b'keep')
        (self.root / 'Artist - Link.mp4').symlink_to(outside)
        rows = self.scan()
        self.assertTrue(any(x['kind'] == 'read' for x in rows[0]['issues']))
        self.assertEqual(outside.read_bytes(), b'keep')

    def test_failure_after_db_commit_restores_both_file_and_database(self):
        path = self.add('Artist - Song.mp4')
        row = self.scan()[0]
        original_write = self.m.write_json
        failed = []
        def write(p, value):
            if p.name == 'journal.json' and value['phase'] == 'committed' and not failed:
                failed.append(True)
                raise OSError('disk interrupted')
            return original_write(p, value)
        with mock.patch.object(self.m, 'write_json', side_effect=write):
            result = self.apply([dict(file_id=row['id'], rename_to='Artist - Other.mp4')])[0]
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(path.read_bytes(), b'video')
        self.assertFalse((self.root / 'Artist - Other.mp4').exists())
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT id,file,plays FROM songs').fetchall(), [(1, path.name, 7)])

    def test_crash_recovery_precedes_refresh_and_restores_metadata(self):
        source = self.add('Artist - Song.mp4')
        row = self.scan()[0]
        folder = self.m.storage / self.m.job['id'] / 'action-crash'
        folder.mkdir()
        shutil.copyfile(source, folder / 'original')
        target = self.root / 'Artist - Other.mp4'
        source.rename(target)
        with sqlite3.connect(self.db) as db:
            db.execute('UPDATE songs SET file=?,title=?', (target.name, 'Other'))
        entry = dict(phase='prepared', source=source.name, target=target.name, keeper=None,
                     old_sha=media.digest(target), new_sha=media.digest(target), inserted_id=None,
                     songs=[dict(id=1, artist='Artist', title='Song', file=source.name, plays=7)])
        self.m.write_json(folder / 'journal.json', entry)
        self.m.job['state'] = 'repairing'
        self.m.persist()
        restored = media.MediaOptimizer(self.root, self.db, self.mount)
        restored.load()
        self.assertEqual(restored.job['state'], 'failed')
        self.assertEqual(source.read_bytes(), b'video')
        self.assertFalse(target.exists())
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT file FROM songs').fetchone()[0], source.name)

    def test_real_ffmpeg_fullhd_24fps_keeps_both_audio_tracks(self):
        source = self.root / 'Artist - Song.mkv'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=160x90:r=30:d=0.6',
                        '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.6',
                        '-f', 'lavfi', '-i', 'sine=frequency=880:duration=0.6',
                        '-map', '0:v', '-map', '1:a', '-map', '2:a', '-c:v', 'libx264',
                        '-threads', '1', '-c:a', 'pcm_s16le', str(source)], check=True, timeout=20)
        before = source.read_bytes()
        self.m.load()
        folder = self.m.storage / 'encode-test'
        folder.mkdir()
        out = folder / 'converted.mkv'
        info = media.probe(source)
        result = self.m.encode(source, out, info)
        self.assertEqual((result['width'], result['height'], result['fps']), (1920, 1080, 24))
        self.assertEqual(sum(s['codec_type'] == 'audio' for s in result['streams']), 2)
        self.assertEqual(source.read_bytes(), before)

    def test_http_confirm_requires_literal_true_and_status_hides_identity(self):
        self.add('Artist - Song.mp4')
        row = self.scan()[0]
        app = Flask(__name__)
        app.register_blueprint(media.create_blueprint(self.m))
        client = app.test_client()
        body = client.get('/api/media-optimizer/status').json
        self.assertNotIn('_identity', body['job']['rows'][0])
        response = client.post('/api/media-optimizer/apply', json={'job_id': self.m.job['id'],
            'confirmed': 'true', 'actions': [dict(file_id=row['id'], rename_to='Artist - New.mp4')]})
        self.assertEqual(response.status_code, 400)

    def test_vfr_burst_is_found_even_when_headers_say_24fps(self):
        data = {'streams': [dict(index=0, codec_type='video', width=1920, height=1080,
                                avg_frame_rate='24/1', r_frame_rate='24/1', time_base='1/1000')],
                'format': {'duration': '1'}}
        outputs = [subprocess.CompletedProcess([], 0, json.dumps(data).encode(), b''),
                   subprocess.CompletedProcess([], 0, b'0.000\n0.020\n0.060\n', b'')]
        with mock.patch.object(media.subprocess, 'run', side_effect=outputs):
            self.assertEqual(media.probe(self.root / 'unused.mp4')['fps'], 50)

    def test_cancel_during_conversion_leaves_original_and_db(self):
        source = self.add('Artist - Song.mp4')
        row = self.scan()[0]
        started = threading.Event()
        def encoding(*args):
            started.set()
            while True:
                self.m.check_cancel()
                time.sleep(0.01)
        with mock.patch.object(self.m, 'encode', side_effect=encoding):
            self.m.apply(self.m.job['id'], [dict(file_id=row['id'], transcode=True)], True)
            self.assertTrue(started.wait(2))
            self.m.cancel()
            self.m.thread.join(5)
        self.assertEqual(self.m.job['state'], 'cancelled')
        self.assertEqual(source.read_bytes(), b'video')
        self.assertFalse((self.root / 'Artist - Song.mkv').exists())

    def test_real_subtitles_and_font_attachment_survive_conversion(self):
        self.m.load()
        folder = self.m.storage / 'subtitles-test'
        folder.mkdir()
        srt = folder / 'lyrics.srt'
        srt.write_text('1\n00:00:00,000 --> 00:00:00,500\nКараоке текст\n', encoding='utf-8')
        font = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.assertTrue(font.is_file())
        source, output = folder / 'source.mkv', folder / 'output.mkv'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=160x90:r=25:d=0.6',
                        '-i', str(srt), '-map', '0:v', '-map', '1:s', '-c:v', 'libx264', '-threads', '1',
                        '-c:s', 'ass', '-attach', str(font), '-metadata:s:t', 'mimetype=application/x-truetype-font',
                        str(source)], check=True, timeout=20)
        result = self.m.encode(source, output, media.probe(source))
        self.assertEqual([s['codec_name'] for s in result['streams'] if s['codec_type'] == 'subtitle'], ['ass'])
        self.assertEqual(sum(s['codec_type'] == 'attachment' for s in result['streams']), 1)
        extracted = folder / 'font.ttf'
        subprocess.run(['ffmpeg', '-v', 'error', '-dump_attachment:t:0', str(extracted),
                        '-i', str(output), '-t', '0', '-f', 'null', '-'], check=True, timeout=15)
        self.assertEqual(extracted.read_bytes(), font.read_bytes())


class AudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.settings = Path(self.temp.name) / 'audio.json'
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(audio, 'SETTINGS', self.settings).start()
        mock.patch.object(audio, 'cards', return_value={'audiocodec', 'HDMI'}).start()
        mock.patch.object(audio.os.path, 'exists', side_effect=lambda p: str(p) in audio.SOCKETS).start()
        self.devices = {p: audio.DEVICES['hdmi'] for p in audio.SOCKETS}
        self.fail_second = False
        def ipc(path, command):
            if command[0] == 'set_property':
                self.devices[path] = command[2]
                if self.fail_second and path == audio.SOCKETS[1] and command[2] == audio.DEVICES['analog']:
                    raise RuntimeError('ALSA busy')
                return None
            return {'audio-device': self.devices[path], 'idle-active': False,
                    'current-ao': 'alsa', 'audio-out-params': {'samplerate': 48000}}[command[1]]
        mock.patch.object(audio, 'ipc', side_effect=ipc).start()

    def test_both_players_switch_and_future_launch_persists(self):
        result = audio.set_analog_only(True)
        self.assertTrue(result['analog_only'])
        self.assertTrue(result['verified'])
        self.assertEqual(set(self.devices.values()), {audio.DEVICES['analog']})
        self.assertIn('--audio-device=' + audio.DEVICES['analog'], audio.player_args())
        self.assertFalse(audio.set_analog_only(False)['analog_only'])

    def test_partial_switch_failure_restores_both_players_and_does_not_save(self):
        self.fail_second = True
        with self.assertRaisesRegex(RuntimeError, 'ALSA busy'):
            audio.set_analog_only(True)
        self.assertEqual(set(self.devices.values()), {audio.DEVICES['hdmi']})
        self.assertFalse(self.settings.exists())

    def test_save_failure_restores_players(self):
        with mock.patch.object(audio, 'save_mode', side_effect=OSError('disk')):
            with self.assertRaises(OSError):
                audio.set_analog_only(True)
        self.assertEqual(set(self.devices.values()), {audio.DEVICES['hdmi']})

    def test_missing_card_and_nonboolean_request_cannot_change_audio(self):
        with mock.patch.object(audio, 'cards', return_value={'HDMI'}):
            with self.assertRaises(RuntimeError):
                audio.set_analog_only(True)
        app = Flask(__name__)
        app.register_blueprint(audio.create_blueprint())
        response = app.test_client().post('/api/audio/output', json={'analog_only': 'false'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(self.devices.values()), {audio.DEVICES['hdmi']})


if __name__ == '__main__':
    unittest.main()
