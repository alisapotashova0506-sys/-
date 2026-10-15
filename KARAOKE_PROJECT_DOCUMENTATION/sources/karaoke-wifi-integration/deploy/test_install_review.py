"""Isolated installer/rollback review; every system action and absolute path is mocked."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location('installer_under_review', Path(__file__).with_name('install.py'))
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def digest(data):
    return hashlib.sha256(data).hexdigest()


class DriverPath:
    def __truediv__(self, _name):
        return self

    def resolve(self, strict=False):
        return SimpleNamespace(name='8188eu')


class Response:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass

    def read(self):
        return self.data


class DeploymentReviewTests(unittest.TestCase):
    def exercise_install(self, fail_health=False):
        with tempfile.TemporaryDirectory(prefix='karaoke-install-review-') as temporary:
            base = Path(temporary)
            live, kit = base / 'live', base / 'kit'
            live.mkdir()
            kit.mkdir()
            app, module = live / 'app.py', live / 'wifi.py'
            app.write_text('answer = 1\n')
            module.write_text('old = True\n')
            (kit / 'module.py').write_text('new = True\n')
            (kit / 'app.patch').write_text('A fake runner applies this patch only in the temporary stage.')
            qr = b'mocked-qr'
            manifest = {
                'app_before': digest(app.read_bytes()), 'app_after': digest(b'answer = 2\n'),
                'qr_sha256': digest(qr),
                'files': [{'source': 'module.py', 'target': str(module),
                           'sha256': digest((kit / 'module.py').read_bytes()),
                           'before': digest(module.read_bytes()), 'mode': 0o644}],
            }
            (kit / 'manifest.json').write_text(json.dumps(manifest))
            calls = []

            def run(*arguments, **_kwargs):
                calls.append(arguments)
                if arguments[0] == 'patch':
                    stage = Path(arguments[arguments.index('-d') + 1])
                    (stage / 'app.py').write_text('answer = 2\n')
                if arguments[:2] == ('systemctl', 'is-enabled'):
                    return 'enabled' if arguments[2] in (installer.MONITOR, installer.SERVER) else 'disabled'
                if arguments[:3] == ('nmcli', '-g', 'GENERAL.AUTOCONNECT'):
                    return 'yes'
                if arguments[:3] == ('nmcli', '-g', 'GENERAL.CON-UUID'):
                    return installer.AP
                return ''

            def settings(_uuid, key):
                return {'802-11-wireless.ssid': 'KARAOKE',
                        'connection.interface-name': installer.USB,
                        'connection.autoconnect': 'yes'}[key]

            def fake_path(value, *arguments):
                if str(value) == '/sys/class/net':
                    return DriverPath()
                if str(value) == '/run/karaoke-wifi-connect.lock':
                    return base / 'connect.lock'
                if str(value).startswith('/var/lib/karaoke-wifi'):
                    return base / 'state' / str(value).removeprefix('/var/lib/karaoke-wifi').lstrip('/')
                return Path(value, *arguments)

            real_mkdtemp = tempfile.mkdtemp

            def mkdtemp(*arguments, **keywords):
                keywords['dir'] = str(base)
                return real_mkdtemp(*arguments, **keywords)

            def health(_path):
                if fail_health:
                    raise RuntimeError('injected health failure')
                return {'controller_ok': True, 'connected': True, 'ap_active': False,
                        'setup_needed': False, 'network': 'Home', 'ip': '192.168.1.102'}

            output = io.StringIO()
            with contextlib.ExitStack() as stack:
                for name, value in (
                    ('ROOT', live), ('HERE', kit), ('Path', fake_path),
                    ('home_ssh', lambda: None), ('run', run),
                    ('active', lambda unit: unit in (installer.MONITOR, installer.SERVER)),
                    ('connection_setting', settings), ('http_json', health),
                ):
                    stack.enter_context(patch.object(installer, name, value))
                stack.enter_context(patch.object(installer.tempfile, 'mkdtemp', mkdtemp))
                stack.enter_context(patch.object(installer.os, 'sync'))
                opener = SimpleNamespace(open=lambda *_args, **_kwargs: Response(qr))
                stack.enter_context(patch.object(installer.urllib.request, 'build_opener', return_value=opener))
                stack.enter_context(contextlib.redirect_stdout(output))
                if fail_health:
                    with self.assertRaisesRegex(RuntimeError, 'injected health failure'):
                        installer.install()
                else:
                    installer.install()
            self.assertFalse(any(name in ' '.join(call) for call in calls
                                 for name in ('zapret', 'bgutil', 'init_karaoke')))
            if fail_health:
                self.assertEqual(app.read_text(), 'answer = 1\n')
                self.assertEqual(module.read_text(), 'old = True\n')
                self.assertIn('ROLLBACK COMPLETE', output.getvalue())
                self.assertEqual(calls.count(('systemctl', 'restart', installer.SERVER)), 2)
            else:
                self.assertEqual(app.read_text(), 'answer = 2\n')
                self.assertEqual(module.read_text(), 'new = True\n')
                self.assertIn('UPDATE COMPLETE', output.getvalue())
                self.assertEqual(calls.count(('systemctl', 'restart', installer.SERVER)), 1)
            self.assertTrue(list(base.glob('karaoke-wifi-backup-*/rollback.py')))

    def test_complete_deployment(self):
        self.exercise_install()

    def test_failed_health_restores_original_application(self):
        self.exercise_install(fail_health=True)

    def exercise_restore(self, missing_backup=False):
        with tempfile.TemporaryDirectory(prefix='karaoke-restore-review-') as temporary:
            base = Path(temporary)
            backup = base / 'backup'
            (backup / 'files').mkdir(parents=True)
            existing, new = base / 'existing.py', base / 'new.py'
            existing.write_text('updated')
            new.write_text('new')
            original = backup / 'files' / 'original'
            original.write_text('original')
            original.chmod(0o640)
            data = {'files': [{'target': str(existing), 'backup': 'files/original'},
                              {'target': str(new), 'backup': None}],
                    'units': {unit: {'enabled': 'enabled' if unit in (installer.MONITOR, installer.SERVER) else 'disabled',
                                     'active': unit in (installer.MONITOR, installer.SERVER)}
                              for unit in (installer.MONITOR, installer.SERVER, *installer.LEGACY)},
                    'ap_autoconnect': 'yes', 'usb_autoconnect': 'yes', 'ap_was_active': True}
            (backup / 'backup.json').write_text(json.dumps(data))
            if missing_backup:
                original.unlink()
            calls = []
            output = io.StringIO()
            def run(*arguments, **_kwargs):
                calls.append(arguments)
                return ''
            with patch.object(installer, 'run', run), patch.object(installer.os, 'sync'), contextlib.redirect_stdout(output):
                self.assertEqual(installer.restore(backup), not missing_backup)
            self.assertFalse(new.exists())
            self.assertEqual(calls[0], ('systemctl', 'stop', installer.MONITOR))
            self.assertEqual(calls.count(('systemctl', 'restart', installer.SERVER)), 1)
            self.assertIn(('nmcli', '--wait', '35', 'connection', 'up', 'uuid', installer.AP,
                           'ifname', installer.USB), calls)
            if missing_backup:
                self.assertIn('ROLLBACK NEEDS ATTENTION', output.getvalue())
            else:
                self.assertEqual(existing.read_text(), 'original')
                self.assertEqual(existing.stat().st_mode & 0o777, 0o640)
                self.assertIn('ROLLBACK COMPLETE', output.getvalue())

    def test_restore_bytes_modes_new_files_and_ap(self):
        self.exercise_restore()

    def test_restore_continues_after_one_missing_file(self):
        self.exercise_restore(missing_backup=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
