import ast
from functools import wraps
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock
from flask import Flask, Blueprint, g, request, jsonify

ROOT = Path(__file__).resolve().parents[1]


class Guards(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.manager = SimpleNamespace(lock=threading.RLock(), repairing=False, recovery_error='', loaded=True)
        self.ns = dict(app=self.app, g=g, request=request, jsonify=jsonify, wraps=wraps,
                       media_optimizer=self.manager, os=__import__('os'), time=time)
        names = {'_media_request_guard', '_media_release_guard', '_media_refresh_guard', '_media_queue_guard', 'parse_filename'}
        tree = ast.parse((ROOT / 'updated/app.py').read_text())
        code = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[])
        exec(compile(code, '<app-guards-only>', 'exec'), self.ns)
        self.calls = []
        @self.app.route('/play', methods=['POST'])
        def play():
            self.calls.append('play')
            return jsonify(ok=True)
        @self.app.route('/')
        def read():
            return jsonify(ok=True)
        @self.app.route('/api/audio/output', methods=['POST'], endpoint='audio_output.set_output')
        def output():
            return jsonify(ok=True)
        @self.app.route('/api/media-optimizer/apply', methods=['POST'], endpoint='media_optimizer.apply')
        def apply():
            return jsonify(ok=True)
        bp = Blueprint('different_youtube_name', __name__)
        bp.add_url_rule('/download', 'download', lambda: jsonify(ok=True), methods=['POST'])
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()
        self.marker = mock.patch.object(self.ns['os'].path, 'getmtime', side_effect=FileNotFoundError)
        self.marker.start()
        self.addCleanup(self.marker.stop)

    def test_repairs_block_play_and_download_but_leave_read_audio_available(self):
        self.manager.repairing = True
        self.assertEqual(self.client.post('/play').status_code, 409)
        self.assertEqual(self.client.post('/download').status_code, 409)
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.post('/api/audio/output').status_code, 200)
        self.manager.repairing = False
        self.assertEqual(self.client.post('/play').status_code, 200)
        self.assertEqual(self.calls, ['play'])
        acquired = []
        def check():
            acquired.append(self.manager.lock.acquire(blocking=False))
            if acquired[-1]:
                self.manager.lock.release()
        t = threading.Thread(target=check)
        t.start(); t.join()
        self.assertEqual(acquired, [True], 'teardown must release the request lock')

    def test_update_marker_blocks_new_media_and_audio_changes(self):
        self.marker.stop()
        with mock.patch.object(self.ns['os'].path, 'getmtime', return_value=time.time()):
            for path in ('/play', '/download', '/api/audio/output', '/api/media-optimizer/apply'):
                self.assertEqual(self.client.post(path).status_code, 409, path)
            self.assertEqual(self.client.get('/').status_code, 200)

    def test_watcher_cannot_refresh_during_repair_or_recovery_failure(self):
        calls = []
        function = self.ns['_media_refresh_guard'](lambda: calls.append(True) or {'added': 1})
        self.manager.repairing = True
        self.assertEqual(function()['added'], 0)
        self.assertFalse(calls)
        queue = self.ns['_media_queue_guard'](lambda: calls.append('advance'))
        queue()
        self.assertFalse(calls)
        self.manager.repairing = False
        self.assertEqual(function()['added'], 1)
        self.manager.recovery_error = 'Recover first'
        with self.assertRaisesRegex(RuntimeError, 'Recover first'):
            function()

    def test_filename_parser_preserves_hyphenated_artists_and_legacy_files(self):
        self.assertEqual(self.ns['parse_filename']('AC-DC - Thunder.mp4'), ('AC-DC', 'Thunder'))
        self.assertEqual(self.ns['parse_filename']('Artist-Song.mp4'), ('Artist', 'Song'))


if __name__ == '__main__':
    unittest.main()
