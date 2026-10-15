"""Backend safety tests. All NM operations and device observations are mocked."""
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import network as net
import monitor

spec = importlib.util.spec_from_file_location('wifi_worker_test',
                                              Path(__file__).with_name('connect-worker.py'))
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


class FakeManager:
    def __init__(self):
        self.calls = []
        self.ap = True
        self.created = False
        self.saved = False
        self.active = False
        self.fail_up = False
        self.fail_save = False
        self.wrong_uuid = False
        self.deleted = []
        self.uuid = ''
        self.name = ''

    def run(self, *args, **kwargs):
        self.calls.append(args)
        if args[:2] == ('connection', 'add'):
            self.uuid = args[args.index('connection.uuid') + 1]
            self.name = args[args.index('con-name') + 1]
            self.created = True
        elif 'up' in args:
            if self.fail_up:
                raise RuntimeError('secret password must never reach job output')
            self.active = True
        elif args[:2] == ('connection', 'modify'):
            if self.fail_save:
                raise RuntimeError('save failed')
            self.saved = True
        elif 'delete' in args:
            self.deleted.append(args[-1])
            if args[-1] == self.uuid:
                self.created = self.active = False
        return ''

    def property(self, profile_uuid, key):
        if self.created and profile_uuid == self.uuid and key == 'connection.id':
            return self.name
        raise RuntimeError('not found')

    def usb(self):
        self.calls.append(('usb-observed',))
        return {'ap_active': self.ap, 'interface': 'usb-test', 'uuid': net.AP_UUID}

    def station(self, require_saved=True):
        return {'connected': self.active and (self.saved or not require_saved),
                'uuid': 'unrelated' if self.wrong_uuid else self.uuid,
                'network': ' home:ssid ', 'ip': '192.168.1.23'}

    def device(self, interface):
        return {'active': False, 'uuid': '', 'addresses': []}

    def home_profiles(self):
        return ['home-one', 'home-two']

    def start_ap(self):
        self.calls.append(('start-ap',))
        self.ap = True
        return self.usb()


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        for key, value in (('STATE_DIR', root / 'state'), ('OPERATION_LOCK', root / 'operation.lock')):
            context = patch.object(net, key, value)
            context.start()
            self.addCleanup(context.stop)
        net.prepare_state()
        net.write_json(net.STATE_DIR / 'status.json', {'version': 2, 'updated_at': int(time.time())})

    def test_escaped_ssids_scan_only_station_and_preserve_spaces(self):
        output = ' home\\:ssid :81:WPA2:*\nback\\\\slash:42:WPA2:\n home\\:ssid :20:WPA2:\n'
        with patch.object(net.NetworkManager, 'run', return_value=output) as run:
            networks = net.scan_networks()
        self.assertEqual(networks[0]['ssid'], ' home:ssid ')
        self.assertEqual(networks[1]['ssid'], 'back\\slash')
        self.assertEqual(networks[0]['in_use'], 'yes')
        self.assertIn('wlan0', run.call_args.args)
        self.assertNotIn('usb-test', run.call_args.args)

    def test_jobs_are_private_password_never_public_and_busy_rejected(self):
        job_id = net.submit_connection(' home:ssid ', 'password1')
        private = net.STATE_DIR / 'requests' / (job_id + '.json')
        public = net.STATE_DIR / 'jobs' / (job_id + '.json')
        self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(public.stat().st_mode), 0o600)
        self.assertNotIn('password', json.dumps(net.read_job(job_id)))
        self.assertEqual(net.read_job(job_id)['ssid'], ' home:ssid ')
        with self.assertRaises(RuntimeError):
            net.submit_connection('second', 'password2')

    def test_unhealthy_or_stale_controller_cannot_accept_credentials(self):
        for state in ({'version': 2, 'updated_at': time.time() - 13},
                      {'version': 2, 'updated_at': time.time(), 'error': 'NM unavailable'},
                      {'updated_at': time.time()}):
            net.write_json(net.STATE_DIR / 'status.json', state)
            with self.assertRaises(RuntimeError):
                net.submit_connection('home', 'password1')
            self.assertFalse(list((net.STATE_DIR / 'requests').iterdir()))

    def test_deployment_admission_lock_rejects_without_waiting_or_creating_job(self):
        outcomes = []
        def attempt():
            try:
                outcomes.append(net.submit_connection('home', 'password1'))
            except Exception as error:
                outcomes.append(error)
        with net.file_lock(net.STATE_DIR / 'admission.lock'):
            pending = threading.Thread(target=attempt, daemon=True)
            pending.start()
            pending.join(timeout=1)
            waited_for_update = pending.is_alive()
        pending.join(timeout=1)
        self.assertFalse(waited_for_update, 'A web request must not wait for deployment completion.')
        self.assertEqual(len(outcomes), 1)
        self.assertIsInstance(outcomes[0], RuntimeError)
        self.assertIn('Попробуйте', str(outcomes[0]))
        self.assertFalse(list((net.STATE_DIR / 'requests').iterdir()))
        self.assertFalse(list((net.STATE_DIR / 'jobs').iterdir()))

    def test_strict_confirmation_input_and_unknown_job(self):
        for value in ('true', 1, None, False):
            with self.assertRaises(ValueError):
                net.request_reset(value)
        for ssid, password in (('', ''), ('x' * 33, ''), ('a\n', ''), ('ok', '12345'), ('\ud800', '')):
            with self.assertRaises(ValueError):
                net.submit_connection(ssid, password)
        with self.assertRaises(ValueError):
            net.read_job('../outside')
        with self.assertRaises(ValueError):
            net.submit_connection(net.AP_SSID, '12345678')

    def test_scan_excludes_own_setup_ap(self):
        with patch.object(net.NetworkManager, 'run', return_value='KARAOKE:90:WPA2:\nZZZZ:50:WPA2:\n'):
            self.assertEqual([item['ssid'] for item in net.scan_networks()], ['ZZZZ'])

    def test_worker_success_saves_before_success_and_removes_password(self):
        manager = FakeManager()
        job_id = net.submit_connection(' home:ssid ', 'password1')
        with patch.object(net, 'profile_saved', side_effect=lambda profile: manager.saved):
            worker.perform(job_id, manager)
        job = net.read_job(job_id)
        self.assertEqual(job['status'], 'success')
        self.assertEqual(job['ip'], '192.168.1.23')
        self.assertTrue(manager.saved)
        self.assertEqual(manager.deleted, [])
        self.assertFalse((net.STATE_DIR / 'requests' / (job_id + '.json')).exists())
        self.assertNotIn('password1', (net.STATE_DIR / 'jobs' / (job_id + '.json')).read_text())
        self.assertEqual(manager.calls[0], ('usb-observed',))

    def test_wrong_password_cleans_only_candidate_and_allows_retry(self):
        manager = FakeManager()
        manager.fail_up = True
        job_id = net.submit_connection('first', 'password1')
        worker.perform(job_id, manager)
        self.assertEqual(net.read_job(job_id)['status'], 'failed')
        self.assertEqual(manager.deleted, [net.candidate_uuid(job_id)])
        self.assertTrue(manager.ap)
        self.assertNotIn('secret password', json.dumps(net.read_job(job_id)))
        self.assertNotIn('ip', net.read_job(job_id))
        self.assertNotEqual(net.submit_connection('retry', 'password2'), job_id)

    def test_persist_failure_and_wrong_uuid_are_not_success(self):
        for failure in ('fail_save', 'wrong_uuid'):
            manager = FakeManager()
            setattr(manager, failure, True)
            job_id = net.submit_connection('home', 'password1')
            worker.perform(job_id, manager)
            self.assertEqual(net.read_job(job_id)['status'], 'failed')
            self.assertEqual(manager.deleted, [net.candidate_uuid(job_id)])

    def test_worker_never_changes_station_before_ap_exists(self):
        manager = FakeManager()
        manager.ap = False
        job_id = net.submit_connection('home', 'password1')
        worker.perform(job_id, manager)
        self.assertEqual(net.read_job(job_id)['status'], 'failed')
        self.assertEqual(manager.calls, [('usb-observed',)])

    def test_reset_deletes_home_only_and_handles_already_disconnected(self):
        manager = FakeManager()
        job_id = net.request_reset(True)
        worker.perform(job_id, manager)
        self.assertEqual(net.read_job(job_id)['status'], 'success')
        self.assertEqual(manager.deleted, ['home-one', 'home-two'])
        self.assertNotIn(net.AP_UUID, manager.deleted)
        self.assertIn(('device', 'set', 'wlan0', 'autoconnect', 'yes'), manager.calls)
        self.assertFalse(any('disconnect' in call for call in manager.calls))

    def test_reset_starts_ap_before_worker_launch(self):
        manager = FakeManager()
        manager.ap = False
        controller = monitor.Controller(manager, portal=object())
        job_id = net.request_reset(True)
        fake_process = type('Process', (), {'pid': 12345, 'poll': lambda self: None})()
        def spawn(*args, **kwargs):
            self.assertTrue(manager.ap)
            self.assertIn(('start-ap',), manager.calls)
            self.assertEqual(args[0][-1], job_id)
            return fake_process
        with patch.object(monitor.subprocess, 'Popen', side_effect=spawn):
            controller.reconcile()
        self.assertEqual(net.read_job(job_id)['status'], 'connecting')

    def test_orphan_unsaved_candidate_is_removed_with_ap_available(self):
        manager = FakeManager()
        job_id = net.submit_connection('home', 'password1')
        manager.created = manager.active = True
        manager.uuid, manager.name = net.candidate_uuid(job_id), net.candidate_name(job_id)
        manager.ap = False
        net.update_job(job_id, status='connecting')
        controller = monitor.Controller(manager, portal=object())
        controller.reconcile()
        self.assertTrue(manager.ap)
        self.assertEqual(net.read_job(job_id)['status'], 'failed')
        self.assertEqual(manager.deleted, [manager.uuid])

    def test_orphan_saved_active_candidate_recovers_success(self):
        manager = FakeManager()
        job_id = net.submit_connection('home', 'password1')
        manager.created = manager.active = manager.saved = True
        manager.uuid, manager.name = net.candidate_uuid(job_id), net.candidate_name(job_id)
        net.update_job(job_id, status='connecting')
        monitor.Controller(manager, portal=object()).reconcile()
        self.assertEqual(net.read_job(job_id)['status'], 'success')
        self.assertEqual(manager.deleted, [])

    def test_home_profile_filter_excludes_usb_and_ap(self):
        manager = net.NetworkManager()
        manager.profile_cache = {
            'bound': {'mode': 'infrastructure', 'interface': 'wlan0'},
            'unbound': {'mode': '', 'interface': ''},
            'usb-client': {'mode': 'infrastructure', 'interface': 'usb-test'},
            'builtin-ap': {'mode': 'ap', 'interface': 'wlan0'},
        }
        output = ''.join(profile + ':802-11-wireless\n' for profile in
                         ['bound', 'unbound', 'usb-client', 'builtin-ap', net.AP_UUID])
        with patch.object(manager, 'run', return_value=output):
            self.assertEqual(manager.home_profiles(), ['bound', 'unbound'])

    def test_policy_delays_fallback_and_honors_worker_and_grace(self):
        policy = monitor.Policy()
        self.assertIsNone(policy.decide(0, False, False))
        self.assertIsNone(policy.decide(29, False, False))
        self.assertEqual(policy.decide(30, False, False), 'start')
        self.assertIsNone(policy.decide(31, True, True, busy=True))
        self.assertIsNone(policy.decide(35, True, True, grace_until=41))
        self.assertEqual(policy.decide(41, True, True, grace_until=41), 'stop')
        self.assertIsNone(policy.decide(42, False, False))
        self.assertEqual(policy.decide(72, False, False), 'start')

    def test_policy_wrong_password_keeps_ap_during_retry_grace(self):
        policy = monitor.Policy()
        self.assertIsNone(policy.decide(0, False, True))
        # Previous saved Wi-Fi returns after the attempted password fails.
        self.assertIsNone(policy.decide(5, True, True, grace_until=60))
        self.assertIsNone(policy.decide(59, True, True, grace_until=60))
        self.assertEqual(policy.decide(60, True, True, grace_until=60), 'stop')
        # If no home network is usable, expiration must never remove the rescue AP.
        self.assertIsNone(policy.decide(70, False, True, grace_until=60))
        self.assertIsNone(policy.decide(1000, False, True, grace_until=60))

    def test_station_requires_saved_profile_not_internet(self):
        manager = net.NetworkManager()
        manager.profile_cache['home'] = dict(type='802-11-wireless', interface='wlan0',
                                             mode='infrastructure', ssid='ZZZZ')
        device = dict(active=True, uuid='home', addresses=['192.168.1.102'])
        with patch.object(manager, 'device', return_value=device), patch.object(net, 'profile_saved', return_value=False):
            self.assertFalse(manager.station()['connected'])
        with patch.object(manager, 'device', return_value=dict(device)), patch.object(net, 'profile_saved', return_value=True):
            self.assertTrue(manager.station()['connected'])


if __name__ == '__main__':
    unittest.main()
