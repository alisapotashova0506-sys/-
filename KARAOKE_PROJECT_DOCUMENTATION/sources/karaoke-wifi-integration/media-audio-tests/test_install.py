from contextlib import contextmanager, ExitStack, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.app = base/'karaoke'
        self.app.mkdir()
        self.kit = base/'kit'
        self.kit.mkdir()
        self.backups = base/'backups'
        self.backups.mkdir()
        self.wrapper = base/'play_karaoke.sh'
        self.wrapper_before = b'#!/bin/bash\n# retain this\nmpv --vo=gpu --ao=alsa --audio-device=alsa/plughw:1,0 "$1"\n'
        self.wrapper.write_bytes(self.wrapper_before)
        self.wrapper.chmod(0o755)
        self.before = (ROOT/'media-audio-v1/app-before.py').read_bytes()
        self.parts = load('test_feature_install_parts', ROOT/'media-audio-v1/parts.py')
        self.after = self.parts.patch(self.before)
        (self.app/'app.py').write_bytes(self.before)
        self.files = {}
        for name in ('karaoke_media_optimizer.py', 'karaoke_audio_output.py', 'media_optimizer.html'):
            data = (ROOT/'updated'/name).read_bytes()
            (self.kit/name).write_bytes(data)
            self.files[name] = hashlib.sha256(data).hexdigest()
        self.manifest = dict(files=self.files, unchanged={},
                             app_before=hashlib.sha256(self.before).hexdigest(),
                             app_after=hashlib.sha256(self.after).hexdigest())
        (self.kit/'manifest.json').write_text(json.dumps(self.manifest))
        shutil.copyfile(ROOT/'media-audio-v1/install.py', self.kit/'install.py')
        self.inst = load('feature_install_under_test', self.kit/'install.py')
        self.inst.ROOT = self.app
        self.inst.WRAPPER = self.wrapper
        self.inst.DB = base/'actual.db'
        self.inst.MARKER = self.app/'.media-audio-installing'
        with sqlite3.connect(self.inst.DB) as db:
            db.executescript('CREATE TABLE songs(id INTEGER PRIMARY KEY,plays INTEGER); INSERT INTO songs VALUES(1,37);')
        self.net = SimpleNamespace(read_status=lambda: {'busy': False}, operation_busy=lambda: False)
        self.locked = False
        @contextmanager
        def lock():
            self.assertFalse(self.locked)
            self.locked = True
            try: yield
            finally: self.locked = False
        self.net.admission_lock = lock
        self.restarts = []
        self.fail_restart = False
        self.fail_health = False
        original_mkdtemp, original_import = tempfile.mkdtemp, self.inst.importlib.import_module
        def command(*args):
            if args == ('systemctl', 'restart', self.inst.SERVICE):
                self.assertTrue(self.locked)
                self.restarts.append((self.app/'app.py').read_bytes())
                if self.fail_restart and len(self.restarts) == 1:
                    raise subprocess.CalledProcessError(1, args)
            elif args != ('systemctl', 'is-active', '--quiet', self.inst.SERVICE):
                self.fail('Unexpected mutation command ' + repr(args))
        def output(args, **kwargs):
            if args[0] == 'systemctl': return ''
            self.assertEqual(args, ['ffmpeg','-hide_banner','-encoders'])
            return 'libx264'
        def health(manifest):
            self.assertEqual((self.app/'app.py').read_bytes(), self.after)
            if self.fail_health: raise RuntimeError('bad health')
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        patches = [
            mock.patch.object(self.inst.os, 'geteuid', return_value=0),
            mock.patch.object(self.inst.os, 'sync'),
            mock.patch.object(self.inst.os.path, 'ismount', return_value=True),
            mock.patch.object(self.inst, 'player_idle'),
            mock.patch.object(self.inst, 'media_idle'),
            mock.patch.object(self.inst, 'health', side_effect=health),
            mock.patch.object(self.inst, 'run', side_effect=command),
            mock.patch.object(self.inst.subprocess, 'check_output', side_effect=output),
            mock.patch.object(self.inst.importlib, 'import_module', side_effect=lambda n: self.net if n=='wifi.network' else original_import(n)),
            mock.patch.object(self.inst.tempfile, 'mkdtemp', side_effect=lambda **kw: original_mkdtemp(prefix=kw['prefix'],dir=self.backups)),
            mock.patch.object(self.inst.time, 'sleep'),
            mock.patch.dict(sys.modules, {'parts': self.parts}),
            mock.patch.object(sys, 'argv', ['install.py']),
            redirect_stdout(io.StringIO())]
        for patch in patches:
            self.stack.enter_context(patch)

    def old_intact(self):
        self.assertEqual((self.app/'app.py').read_bytes(), self.before)
        self.assertEqual(self.wrapper.read_bytes(), self.wrapper_before)
        for name in self.files: self.assertFalse((self.app/name).exists())
        self.assertFalse(self.inst.MARKER.exists())
        with sqlite3.connect(self.inst.DB) as db:
            self.assertEqual(db.execute('SELECT * FROM songs').fetchall(), [(1,37)])

    def test_success_saves_real_consistent_db_and_only_restarts_karaoke(self):
        self.inst.main()
        self.assertEqual(self.restarts, [self.after])
        self.assertIn(b'--audio-device="$AUDIO_DEVICE"', self.wrapper.read_bytes())
        self.assertEqual(self.wrapper.stat().st_mode&0o777, 0o755)
        self.assertFalse(self.inst.MARKER.exists())
        folder = next(self.backups.iterdir())
        with sqlite3.connect(folder/'karaoke-preupdate.db') as db:
            self.assertEqual(db.execute('SELECT * FROM songs').fetchall(), [(1,37)])
        with mock.patch.object(sys,'argv',['rollback.py','--rollback',str(folder)]):
            self.inst.main()
        self.old_intact()

    def test_wrong_app_stops_without_restarts_or_backup(self):
        (self.app/'app.py').write_bytes(b'unexpected user edit')
        with self.assertRaisesRegex(RuntimeError,'app.py'):
            self.inst.main()
        self.assertFalse(self.restarts)
        self.assertFalse(list(self.backups.iterdir()))
        self.assertEqual((self.app/'app.py').read_bytes(), b'unexpected user edit')

    def test_partial_install_can_be_rolled_back_when_app_is_still_old(self):
        folder = self.backups/'interrupted'
        folder.mkdir()
        (folder/'app.py').write_bytes(self.before)
        (folder/'play_karaoke.sh').write_bytes(self.wrapper_before)
        (folder/'manifest.json').write_text(json.dumps(self.manifest))
        for name in self.files:
            shutil.copyfile(self.kit/name, self.app/name)
        self.wrapper.write_bytes(self.parts.patch_wrapper(self.wrapper_before))
        with mock.patch.object(sys,'argv',['rollback.py','--rollback',str(folder)]):
            self.inst.main()
        self.old_intact()

    def test_busy_wifi_does_not_modify_files(self):
        self.net.operation_busy = lambda: True
        with self.assertRaisesRegex(RuntimeError,'Wi-Fi'):
            self.inst.main()
        self.old_intact()
        self.assertFalse(self.restarts)

    def test_bad_wrapper_does_not_modify_application(self):
        self.wrapper.write_bytes(b'#!/bin/bash\nunknown setup\n')
        with self.assertRaisesRegex(RuntimeError,'часть'):
            self.inst.main()
        self.assertEqual((self.app/'app.py').read_bytes(), self.before)
        self.assertFalse(self.restarts)
        self.assertFalse(self.inst.MARKER.exists())

    def test_failed_restart_restores_exact_app_and_wrapper(self):
        self.fail_restart = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.inst.main()
        self.old_intact()
        self.assertEqual(self.restarts, [self.after,self.before])

    def test_bad_health_rolls_back_without_replacing_user_database(self):
        self.fail_health = True
        with self.assertRaisesRegex(RuntimeError,'проверка'):
            self.inst.main()
        self.old_intact()
        self.assertEqual(self.restarts[-1], self.before)

    def test_old_init_script_cannot_run(self):
        with mock.patch.object(self.inst.subprocess,'check_output',return_value='old-init.sh'):
            with self.assertRaisesRegex(RuntimeError,'init'):
                self.inst.main()
        self.old_intact()
        self.assertFalse(self.restarts)


if __name__ == '__main__': unittest.main()
