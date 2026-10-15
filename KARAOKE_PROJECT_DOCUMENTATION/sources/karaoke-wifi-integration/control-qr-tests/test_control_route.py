"""Exercise only the control-QR route AST, never app.py media initialization."""
import ast
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from flask import Flask, jsonify, request
from wifi import control_qr

ROOT = Path(__file__).resolve().parents[1]


class ControlRouteTests(unittest.TestCase):
    def setUp(self):
        self.state = {'controller_ok': True, 'connected': True, 'ip': '192.168.1.102'}
        self.status = mock.patch.object(control_qr.network, 'read_status',
                                        side_effect=lambda: self.state.copy())
        self.status.start()
        self.addCleanup(self.status.stop)
        self.addCleanup(control_qr._invalidate)
        self.app = Flask(__name__)
        self.app.testing = True
        source = ast.parse((ROOT / 'updated/app.py').read_text())
        nodes = [item for item in source.body if isinstance(item, ast.FunctionDef)
                 and item.name == 'karaoke_control_qr']
        self.assertEqual(len(nodes), 1)
        namespace = {'app': self.app, 'request': request, 'jsonify': jsonify,
                     'wifi_control_qr': control_qr}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<control-qr-route-only>',
                     'exec'), namespace)
        self.client = self.app.test_client()

    def test_current_ip_returns_real_png_and_canonical_control_url(self):
        response = self.client.get('/wifi/control-qr.png?ip=192.168.1.102')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')
        self.assertTrue(response.data.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertEqual(response.headers['X-Control-URL'], 'http://192.168.1.102:8080/')
        self.assertIn('no-store', response.headers['Cache-Control'])
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response.data, control_qr.control_image(self.state)[0])

    def test_stale_expected_ip_has_409_and_no_store(self):
        response = self.client.get('/wifi/control-qr.png?ip=192.168.1.50')
        self.assertEqual(response.status_code, 409)
        self.assertIn('Адрес домашней сети изменился', response.json['error'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertNotIn('X-Control-URL', response.headers)

    def test_disconnected_home_has_409_instead_of_stale_image(self):
        self.client.get('/wifi/control-qr.png?ip=192.168.1.102')
        self.state['connected'] = False
        response = self.client.get('/wifi/control-qr.png?ip=192.168.1.102')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertIn('no-store', response.headers['Cache-Control'])

    def test_stale_controller_and_invalid_home_ip_have_409(self):
        for changes in ({'controller_ok': False}, {'ip': '127.0.0.1'},
                        {'ip': '169.254.1.2'}, {'ip': '::1'}):
            with self.subTest(changes=changes):
                previous = self.state.copy()
                self.state.update(changes)
                response = self.client.get('/wifi/control-qr.png')
                self.assertEqual(response.status_code, 409)
                self.assertIn('no-store', response.headers['Cache-Control'])
                self.state = previous

    def test_change_of_home_address_yields_new_qr_and_url(self):
        original = self.client.get('/wifi/control-qr.png?ip=192.168.1.102')
        self.state['ip'] = '10.0.0.22'
        stale = self.client.get('/wifi/control-qr.png?ip=192.168.1.102')
        changed = self.client.get('/wifi/control-qr.png?ip=10.0.0.22')
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.headers['X-Control-URL'], 'http://10.0.0.22:8080/')
        self.assertNotEqual(original.data, changed.data)

    def test_optional_ip_query_uses_current_status(self):
        self.state['ip'] = '100.64.1.2'
        response = self.client.get('/wifi/control-qr.png')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Control-URL'], 'http://100.64.1.2:8080/')

    def test_unsafe_expected_ip_query_cannot_set_response_headers(self):
        response = self.client.get('/wifi/control-qr.png?ip=192.168.1.102%0D%0AX-Test:%20x')
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('X-Test', response.headers)

    def test_head_has_same_type_and_control_url_without_body(self):
        response = self.client.head('/wifi/control-qr.png?ip=192.168.1.102')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')
        self.assertEqual(response.data, b'')
        self.assertEqual(response.headers['X-Control-URL'], 'http://192.168.1.102:8080/')

    def test_helper_generates_without_site_packages(self):
        # -S and -I hide installed qrcode/Pillow/OpenCV; only the vendored encoder
        # and Python standard library are reachable in this clean child process.
        source = (
            'import sys; sys.path.insert(0, ' + repr(str(ROOT / 'updated')) + '); '
            'from wifi.control_qr import control_image; '
            "png,url=control_image({'controller_ok':True,'connected':True,'ip':'192.168.1.102'}); "
            "assert png[:8]==b'\\x89PNG\\r\\n\\x1a\\n'; "
            "assert url=='http://192.168.1.102:8080/'; print('stdlib-only QR generation OK')"
        )
        result = subprocess.run([sys.executable, '-I', '-S', '-c', source],
                                text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('stdlib-only QR generation OK', result.stdout)


if __name__ == '__main__':
    unittest.main()
