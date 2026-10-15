"""Exercise V5 installation and rollback in temporary trees; never import app.py."""
from contextlib import contextmanager, ExitStack, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
UPDATED = PROJECT / 'updated'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARTS = load_module('control_qr_install_test_parts', HERE / 'parts.py')


class Installation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='control-qr-install-test-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / 'karaoke'
        self.kit = self.base / 'kit'
        self.backups = self.base / 'backups'
        for directory in (self.root / 'wifi', self.kit, self.backups):
            directory.mkdir(parents=True)
        self.before = (HERE / 'app-before.py').read_bytes()
        self.after = PARTS.patch(self.before)
        (self.root / 'app.py').write_bytes(self.before)
        for relative in ('wifi/__init__.py', 'wifi/network.py', 'wifi/setup-qr.png'):
            shutil.copy2(UPDATED / relative, self.root / relative)
        (self.root / 'karaoke.db').write_bytes(b'never modify the database')
        (self.root / 'unrelated.txt').write_bytes(b'preserve unrelated files')
        additions = [UPDATED / 'wifi/control_qr.py'] + sorted(
            path for path in (UPDATED / 'wifi/vendor').rglob('*')
            if path.is_file() and '__pycache__' not in path.parts)
        self.new_files = {}
        for source in additions:
            relative = source.relative_to(UPDATED).as_posix()
            target = self.kit / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            self.new_files[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
        self.manifest = {'app_after': hashlib.sha256(self.after).hexdigest(),
                         'new_files': self.new_files}
        (self.kit / 'manifest.json').write_text(json.dumps(self.manifest))
        shutil.copy2(HERE / 'install_on_x96q.py', self.kit / 'install_on_x96q.py')
        self.installer = load_module('control_qr_installer_under_test',
                                     self.kit / 'install_on_x96q.py')
        self.installer.ROOT = self.root
        self.network = types.SimpleNamespace(read_status=lambda: {'busy': False},
                                             operation_busy=lambda: False)
        self.locked = False

        @contextmanager
        def admission_lock():
            self.assertFalse(self.locked)
            self.locked = True
            try:
                yield
            finally:
                self.locked = False
        self.network.admission_lock = admission_lock
        self.commands = []
        self.restart_apps = []
        self.state = {'controller_ok': True, 'connected': True, 'ip': '192.168.1.102'}
        self.initial = self.snapshot()
        original_mkdtemp = tempfile.mkdtemp

        def redirect_backup(*args, **kwargs):
            self.assertEqual(kwargs.pop('dir'), '/root')
            return original_mkdtemp(*args, dir=self.backups, **kwargs)

        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        patches = (
            mock.patch.object(self.installer.os, 'geteuid', return_value=0),
            mock.patch.object(self.installer.os, 'sync'),
            mock.patch.object(self.installer.subprocess, 'check_output', return_value=''),
            mock.patch.object(self.installer.tempfile, 'mkdtemp', side_effect=redirect_backup),
            mock.patch.object(self.installer.time, 'sleep'),
            mock.patch.object(self.installer, 'network_module', return_value=self.network),
            mock.patch.object(self.installer, 'run', side_effect=self.run_command),
            mock.patch.object(self.installer, 'http_get', side_effect=self.http_get),
            mock.patch.dict(sys.modules, {'parts': PARTS}),
            mock.patch.object(sys, 'argv', ['install_on_x96q.py']),
            redirect_stdout(io.StringIO()),
        )
        self.mocks = [self.stack.enter_context(patch) for patch in patches]

    def snapshot(self):
        return {path.relative_to(self.root).as_posix():
                (path.read_bytes(), path.stat().st_mode & 0o777)
                for path in self.root.rglob('*') if path.is_file()}

    def run_command(self, *args):
        self.commands.append(args)
        if args == ('systemctl', 'restart', self.installer.SERVICE):
            self.assertTrue(self.locked, 'Restart must hold the admission lock')
            self.restart_apps.append((self.root / 'app.py').read_bytes())
        elif args == ('systemctl', 'is-active', '--quiet', self.installer.SERVICE):
            pass
        elif args[:4] == (sys.executable, '-I', '-S', '-B'):
            # Execute the actual isolated import/PNG probe against the temp tree.
            subprocess.run(args, check=True, timeout=20, capture_output=True)
        else:
            self.fail('Unexpected external command: ' + repr(args))

    def http_get(self, path):
        if path == '/':
            return 200, {}, self.after
        if path == '/api/karaoke-wifi-monitor':
            return 200, {}, json.dumps(self.state).encode()
        if path.startswith('/wifi/control-qr.png'):
            if not self.state.get('connected'):
                return 409, {'Cache-Control': 'no-store'}, b'{}'
            address = self.state['ip']
            image = b'\x89PNG\r\n\x1a\n' + b'\0' * 8 + struct.pack('>II', 222, 222)
            return 200, {'X-Control-URL': 'http://' + address + ':8080/',
                         'Cache-Control': 'no-store, max-age=0'}, image
        if path == '/wifi/setup-qr.png?v=4':
            return 200, {}, (self.root / 'wifi/setup-qr.png').read_bytes()
        self.fail('Unexpected health request: ' + path)

    def check_preflight_failure(self, message):
        tree = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, message):
            self.installer.main()
        self.assertEqual(self.snapshot(), tree)
        self.assertFalse(list(self.backups.iterdir()))
        self.assertFalse(self.restart_apps)

    def check_rolled_back(self):
        self.assertEqual(self.snapshot(), self.initial)
        self.assertFalse((self.root / 'wifi/vendor').exists())
        backup = list(self.backups.iterdir())
        self.assertEqual(len(backup), 1)
        self.assertEqual((backup[0] / 'app.py').read_bytes(), self.before)
        self.assertTrue((backup[0] / 'rollback.py').is_file())
        self.assertEqual(self.restart_apps[-1], self.before)

    def test_success_adds_only_manifest_files_and_restarts_only_app(self):
        self.installer.main()
        tree = self.snapshot()
        self.assertEqual(tree['app.py'][0], self.after)
        self.assertEqual(set(tree), set(self.initial) | set(self.new_files))
        for relative, original in self.initial.items():
            if relative != 'app.py':
                self.assertEqual(tree[relative], original, relative)
        for relative, digest in self.new_files.items():
            self.assertEqual(hashlib.sha256(tree[relative][0]).hexdigest(), digest)
            self.assertEqual(tree[relative][1], 0o644)
        self.assertEqual(self.restart_apps, [self.after])
        self.assertEqual((self.root / 'wifi/vendor').stat().st_mode & 0o777, 0o755)
        self.assertEqual((self.root / 'wifi/vendor/qrcode').stat().st_mode & 0o777, 0o755)

    def test_repeat_checks_files_and_health_without_restart(self):
        self.installer.main()
        before = self.snapshot()
        self.commands.clear()
        self.restart_apps.clear()
        self.installer.main()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.commands)
        self.assertEqual(len(list(self.backups.iterdir())), 1)

    def test_repeat_rejects_missing_helper(self):
        self.installer.main()
        (self.root / 'wifi/control_qr.py').write_bytes(b'corrupt')
        self.restart_apps.clear()
        with self.assertRaisesRegex(RuntimeError, 'неполон'):
            self.installer.main()
        self.assertFalse(self.restart_apps)

    def test_wrong_app_hash_does_not_mutate_or_restart(self):
        (self.root / 'app.py').write_bytes(b'# unexpected version\n')
        self.check_preflight_failure('app.py отличается')

    def test_old_init_script_does_not_mutate_or_restart(self):
        with mock.patch.object(self.installer.subprocess, 'check_output',
                               return_value='{ path=/root/karaoke/init_karaoke.sh; }'):
            self.check_preflight_failure('init-скрипт')

    def test_corrupt_unchanged_config_does_not_mutate_or_restart(self):
        (self.root / 'wifi/network.py').write_bytes(b'# changed\n')
        self.check_preflight_failure('неизменяемого файла')

    def test_existing_vendor_directory_is_not_overwritten(self):
        (self.root / 'wifi/vendor').mkdir()
        (self.root / 'wifi/vendor/other.py').write_bytes(b'# preserve\n')
        self.check_preflight_failure('пути уже существуют')

    def test_corrupt_kit_helper_does_not_mutate_or_restart(self):
        (self.kit / 'wifi/control_qr.py').write_bytes(b'# corrupt\n')
        self.check_preflight_failure('Повреждён файл комплекта')

    def test_busy_job_does_not_mutate_or_restart(self):
        self.network.read_status = lambda: {'busy': True}
        self.check_preflight_failure('настройка Wi-Fi')

    def test_busy_operation_does_not_mutate_or_restart(self):
        self.network.operation_busy = lambda: True
        self.check_preflight_failure('настройка Wi-Fi')

    def test_locked_admission_does_not_mutate_or_restart(self):
        @contextmanager
        def busy_lock():
            raise RuntimeError('admission lock busy')
            yield
        self.network.admission_lock = busy_lock
        self.check_preflight_failure('admission lock busy')

    def test_partial_helper_write_failure_rolls_back_without_new_app(self):
        real_write = self.installer.atomic_write
        writes = 0

        def fail_second_addition(path, data, mode=0o644):
            nonlocal writes
            if path != self.root / 'app.py':
                writes += 1
                if writes == 2:
                    raise OSError('simulated disk full')
            real_write(path, data, mode)

        with mock.patch.object(self.installer, 'atomic_write', side_effect=fail_second_addition):
            with self.assertRaisesRegex(OSError, 'disk full'):
                self.installer.main()
        self.check_rolled_back()
        self.assertEqual(self.restart_apps, [self.before])

    def test_failed_import_probe_rolls_back_before_app_replacement(self):
        def fail_probe(*args):
            if args[0] == sys.executable:
                raise subprocess.CalledProcessError(1, args)
            self.run_command(*args)

        with mock.patch.object(self.installer, 'run', side_effect=fail_probe):
            with self.assertRaises(subprocess.CalledProcessError):
                self.installer.main()
        self.check_rolled_back()
        self.assertEqual(self.restart_apps, [self.before])

    def test_restart_failure_restores_app_and_restarts_old_version(self):
        failed = False

        def fail_first_restart(*args):
            nonlocal failed
            self.run_command(*args)
            if args == ('systemctl', 'restart', self.installer.SERVICE) and not failed:
                failed = True
                raise subprocess.CalledProcessError(1, args)

        with mock.patch.object(self.installer, 'run', side_effect=fail_first_restart):
            with self.assertRaises(subprocess.CalledProcessError):
                self.installer.main()
        self.check_rolled_back()
        self.assertEqual(self.restart_apps, [self.after, self.before])

    def test_wrong_served_html_restores_app_and_removes_additions(self):
        def bad_html(path):
            return (200, {}, b'old page remote-info') if path == '/' else self.http_get(path)

        with mock.patch.object(self.installer, 'http_get', side_effect=bad_html):
            with self.assertRaisesRegex(RuntimeError, 'Проверка после запуска'):
                self.installer.main()
        self.check_rolled_back()
        self.assertEqual(self.restart_apps, [self.after, self.before])

    def test_wrong_served_qr_url_restores_app_and_removes_additions(self):
        def bad_qr(path):
            code, headers, body = self.http_get(path)
            if path.startswith('/wifi/control-qr.png'):
                headers['X-Control-URL'] = 'http://192.168.1.99:8080/'
            return code, headers, body

        with mock.patch.object(self.installer, 'http_get', side_effect=bad_qr):
            with self.assertRaisesRegex(RuntimeError, 'Проверка после запуска'):
                self.installer.main()
        self.check_rolled_back()

    def test_disconnected_state_requires_409_and_can_install(self):
        self.state.update(connected=False, ip='')
        self.installer.main()
        self.assertEqual(self.restart_apps, [self.after])

    def test_standalone_rollback_restores_original_tree(self):
        self.installer.main()
        backup = next(self.backups.iterdir())
        with mock.patch.object(sys, 'argv', ['rollback.py', '--rollback', str(backup)]):
            self.installer.main()
        self.check_rolled_back()
        self.assertEqual(self.restart_apps, [self.after, self.before])


if __name__ == '__main__':
    unittest.main()
