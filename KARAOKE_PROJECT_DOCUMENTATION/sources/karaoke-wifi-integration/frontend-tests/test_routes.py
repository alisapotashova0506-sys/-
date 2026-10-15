"""Execute only the Wi-Fi AST nodes; never import app.py and its media startup."""
import ast
import ipaddress
import logging
from pathlib import Path
import unittest
from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parents[1]
WIFI_FUNCTIONS = {
    'get_network_status', 'karaoke_wifi_monitor_status', '_wifi_control_allowed',
    '_wifi_job_response', '_wifi_connect_request', 'karaoke_portal_connect',
    'karaoke_wifi_job', 'karaoke_wifi_reset', 'karaoke_wifi_setup_page',
    'karaoke_wifi_setup_qr', 'api_network_status', 'wifi_scan', 'wifi_connect', 'wifi_status',
}

class Network:
    def __init__(self):
        self.state = {'connected': False, 'ap_active': True, 'setup_needed': True,
                      'network': '', 'ip': '', 'mode': 'setup', 'busy': False}
        self.calls = []
    def read_status(self):
        self.calls.append(('status',))
        return self.state.copy()
    def scan_networks(self):
        self.calls.append(('scan',))
        return [{'ssid': 'Name:with\\slash', 'signal': 80, 'security': 'WPA2', 'in_use': 'no'}]
    def submit_connection(self, ssid, password):
        self.calls.append(('connect', ssid, password))
        if not isinstance(ssid, str) or not isinstance(password, str):
            raise ValueError('Неверные данные')
        return '123abc'
    def read_job(self, job_id):
        self.calls.append(('job', job_id))
        if job_id != '123abc':
            raise ValueError('Задание не найдено')
        return {'job_id': job_id, 'type': 'connect', 'status': 'connecting', 'message': 'Проверяем'}
    def request_reset(self, confirmed):
        self.calls.append(('reset', confirmed))
        if confirmed is not True:
            raise ValueError('Подтвердите сброс')
        return '123abc'

class Routes(unittest.TestCase):
    def setUp(self):
        self.network = Network()
        self.app = Flask(__name__)
        self.app.testing = True
        source = ast.parse((ROOT / 'updated/app.py').read_text())
        nodes = [node for node in source.body if isinstance(node, ast.FunctionDef)
                 and node.name in WIFI_FUNCTIONS]
        namespace = {'app': self.app, 'wifi_network': self.network,
                     'request': request, 'jsonify': jsonify, 'ipaddress': ipaddress,
                     'logger': logging.getLogger('wifi-tests'),
                     'send_from_directory': lambda directory, filename, **kw: jsonify(
                         directory=directory, filename=filename, **kw)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<wifi-only>', 'exec'), namespace)
        self.client = self.app.test_client()
    def post(self, route, data=None, peer='127.0.0.1'):
        return self.client.post(route, json=data, environ_overrides={'REMOTE_ADDR': peer})
    def test_monitor_never_scans_or_connects(self):
        result = self.client.get('/api/karaoke-wifi-monitor')
        self.assertEqual(result.json['mode'], 'setup')
        self.assertEqual(self.network.calls, [('status',)])
    def test_station_ip_and_ssid_are_reported(self):
        self.network.state.update(connected=True, network='Home:Net', ip='192.168.1.102')
        self.assertEqual(self.client.get('/api/wifi/status').json['ip'], '192.168.1.102')
        self.assertEqual(self.client.get('/api/network_status').json,
                         {'status': 'connected', 'ip': '192.168.1.102', 'ssid': 'Home:Net'})
    def test_portal_queues_job_without_stripping_password_or_ssid(self):
        result = self.post('/api/wifi/portal-connect', {'ssid': ' Name: \\ ', 'password': ' pass '}, '192.168.100.23')
        self.assertEqual(result.status_code, 202)
        self.assertEqual(result.json['job_id'], '123abc')
        self.assertIn(('connect', ' Name: \\ ', ' pass '), self.network.calls)
        self.assertNotIn('password', result.json)
    def test_home_lan_and_forwarded_address_cannot_reconfigure(self):
        result = self.client.post('/api/wifi/connect', json={'ssid': 'Home', 'password': ''},
                                  headers={'X-Forwarded-For': '127.0.0.1'},
                                  environ_overrides={'REMOTE_ADDR': '192.168.1.33'})
        self.assertEqual(result.status_code, 403)
        self.assertFalse(any(call[0] == 'connect' for call in self.network.calls))
    def test_tv_browser_may_use_its_own_station_address(self):
        self.network.state.update(connected=True, ip='192.168.1.102')
        self.assertEqual(self.post('/api/wifi/connect', {'ssid': 'Home'}, '192.168.1.102').status_code, 202)
        self.assertEqual(self.post('/api/wifi/connect', {'ssid': 'Home'}, '192.168.1.33').status_code, 403)

    def test_portal_guard_and_local_reconfiguration(self):
        self.network.state['ap_active'] = False
        self.assertEqual(self.post('/api/wifi/portal-connect', {'ssid': 'Home'}).status_code, 409)
        self.assertEqual(self.post('/api/wifi/connect', {'ssid': 'Home'}, '192.168.100.23').status_code, 403)
        self.assertEqual(self.post('/api/wifi/connect', {'ssid': 'Home'}).status_code, 202)
    def test_json_validation(self):
        for data in (['Home'], 'Home', None):
            self.assertEqual(self.post('/api/wifi/connect', data).status_code, 400)
        self.assertEqual(self.post('/api/wifi/connect', {'ssid': 42}).status_code, 400)
    def test_job_polling_and_unknown_job(self):
        self.assertEqual(self.client.get('/api/wifi/job/123abc').json['status'], 'connecting')
        self.assertEqual(self.client.get('/api/wifi/job/missing').status_code, 404)
    def test_reset_requires_post_and_literal_true(self):
        self.assertEqual(self.client.get('/api/wifi/reset').status_code, 405)
        for confirmed in (False, 1, 'true', None):
            self.assertEqual(self.post('/api/wifi/reset', {'confirmed': confirmed}).status_code, 400)
        self.assertEqual(self.post('/api/wifi/reset', {'confirmed': True}).status_code, 202)
        self.assertEqual(self.post('/api/wifi/reset', {'confirmed': True}, '192.168.1.33').status_code, 403)
    def test_scan_preserves_special_ssid(self):
        self.assertEqual(self.client.get('/api/wifi/scan').json['networks'][0]['ssid'], 'Name:with\\slash')
    def test_static_qr_and_setup_routes(self):
        self.assertEqual(self.client.get('/wifi/setup-qr.png').json['filename'], 'setup-qr.png')
        self.assertEqual(self.client.get('/wifi/setup').json['filename'], 'setup.html')
    def test_functions_outside_requested_features_are_unchanged(self):
        originals = ast.parse((ROOT / 'current/app.py').read_text())
        updated = ast.parse((ROOT / 'updated/app.py').read_text())
        actual = {node.name: ast.dump(node) for node in updated.body if isinstance(node, ast.FunctionDef)}
        for node in originals.body:
            if isinstance(node, ast.FunctionDef) and node.name not in WIFI_FUNCTIONS | {'bgm_start', 'parse_filename', 'refresh_database', 'play_video_file', '_advance_queue_after_end'}:
                self.assertEqual(ast.dump(node), actual[node.name], node.name)

if __name__ == '__main__':
    unittest.main()
