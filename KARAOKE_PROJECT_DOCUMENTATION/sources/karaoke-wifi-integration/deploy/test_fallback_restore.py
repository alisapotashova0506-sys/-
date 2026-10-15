"""Exercise the recovery timer without importing or calling live NM code."""
import ast
from contextlib import contextmanager, redirect_stdout
import importlib.util
import io
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent


class Scenario:
    def __init__(self, connected=False, job=None, admission_busy=0, operation_busy=0):
        self.connected = connected
        self.job = job
        self.admission_busy = admission_busy
        self.operation_busy = operation_busy
        self.admission_held = False
        self.operation_held = False
        self.clock = 0
        self.sleeps = []
        self.after_sleep = []
        self.commands = []
        self.fail_activation = False
        self.events = []
        self.net = ModuleType('network')
        self.net.STATION = 'wlan0'
        self.net.OPERATION_LOCK = 'mock-operation-lock'
        self.net.FINAL_STATES = {'success', 'failed'}
        self.net.admission_lock = self.admission
        self.net.file_lock = self.operation
        self.net.current_job = self.current_job
        self.net.NetworkManager = lambda: self

    def monotonic(self):
        return self.clock

    def sleep(self, seconds):
        assert not self.admission_held and not self.operation_held
        self.sleeps.append(seconds)
        self.clock += seconds
        if self.after_sleep:
            self.after_sleep.pop(0)()

    @contextmanager
    def admission(self):
        assert not self.admission_held
        if self.admission_busy:
            self.admission_busy -= 1
            raise RuntimeError('Admission is busy')
        self.admission_held = True
        try:
            yield
        finally:
            self.admission_held = False

    @contextmanager
    def operation(self, path, blocking=True):
        assert path == self.net.OPERATION_LOCK and blocking is False
        assert self.admission_held and not self.operation_held
        if self.operation_busy:
            self.operation_busy -= 1
            raise BlockingIOError
        self.operation_held = True
        try:
            yield
        finally:
            self.operation_held = False

    def station(self):
        assert self.admission_held and self.operation_held
        self.events.append('station')
        return {'connected': self.connected, 'uuid': 'different-valid-home'}

    def current_job(self):
        assert self.admission_held and self.operation_held
        self.events.append('job')
        return self.job

    def run(self, *args, **kwargs):
        assert self.admission_held and self.operation_held
        assert not self.job or self.job.get('status') in self.net.FINAL_STATES
        self.commands.append((args, kwargs))
        if args[:3] == ('--wait', '30', 'connection'):
            if self.fail_activation:
                raise RuntimeError('Activation failed')
            self.connected = True


def run_restore(scenario):
    spec = importlib.util.spec_from_file_location('fallback_recovery_under_test',
                                                HERE / 'restore_test_connection.py')
    module = importlib.util.module_from_spec(spec)
    old_path = list(sys.path)
    try:
        with patch.dict(sys.modules, {'network': scenario.net}):
            spec.loader.exec_module(module)
    finally:
        sys.path[:] = old_path
    module.time = scenario
    with redirect_stdout(io.StringIO()) as output:
        module.restore('original-uuid')
    return output.getvalue()


class RestoreTests(unittest.TestCase):
    def test_existing_valid_home_is_preserved_without_mutation(self):
        scenario = Scenario(connected=True)
        output = run_restore(scenario)
        self.assertIn('восстановление не требуется', output)
        self.assertEqual(scenario.commands, [])
        self.assertEqual(scenario.sleeps, [])

    def test_missing_home_restores_autoconnect_and_original_uuid(self):
        scenario = Scenario()
        output = run_restore(scenario)
        self.assertIn('Исходная домашняя сеть восстановлена', output)
        self.assertEqual(scenario.commands, [
            (('device', 'set', 'wlan0', 'autoconnect', 'yes'), {}),
            (('--wait', '30', 'connection', 'up', 'uuid', 'original-uuid',
              'ifname', 'wlan0'), {'timeout': 40}),
        ])
        self.assertTrue(scenario.connected)

    def test_queued_and_connecting_jobs_delay_restore_until_finished(self):
        scenario = Scenario(job={'status': 'queued'})
        scenario.after_sleep = [
            lambda: setattr(scenario, 'job', {'status': 'connecting'}),
            lambda: setattr(scenario, 'job', {'status': 'failed'}),
        ]
        run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5, 5])
        self.assertEqual(len(scenario.commands), 2)

    def test_successful_pending_job_is_preserved(self):
        scenario = Scenario(job={'status': 'connecting'})

        def finished():
            scenario.job = {'status': 'success'}
            scenario.connected = True

        scenario.after_sleep = [finished]
        run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5])
        self.assertEqual(scenario.commands, [])

    def test_queued_job_with_existing_home_is_allowed_to_finish(self):
        scenario = Scenario(connected=True, job={'status': 'queued'})

        def started():
            scenario.connected = False
            scenario.job = {'status': 'connecting'}

        def finished():
            scenario.connected = True
            scenario.job = {'status': 'success'}

        scenario.after_sleep = [started, finished]
        run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5, 5])
        self.assertEqual(scenario.commands, [])

    def test_busy_operation_lock_delays_without_nm_mutation(self):
        scenario = Scenario(operation_busy=2)
        run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5, 5])
        self.assertEqual(len(scenario.commands), 2)

    def test_busy_admission_lock_delays_without_nm_mutation(self):
        scenario = Scenario(admission_busy=1)
        run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5])
        self.assertEqual(len(scenario.commands), 2)

    def test_permanent_worker_busy_times_out_without_changing_network(self):
        scenario = Scenario(job={'status': 'connecting'})
        with self.assertRaisesRegex(RuntimeError, 'Не удалось восстановить'):
            run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5] * 36)
        self.assertEqual(scenario.commands, [])
        self.assertFalse(scenario.admission_held or scenario.operation_held)

    def test_activation_failure_releases_locks_and_retries(self):
        scenario = Scenario()
        scenario.fail_activation = True
        scenario.after_sleep = [lambda: setattr(scenario, 'fail_activation', False)]
        run_restore(scenario)
        self.assertEqual(scenario.sleeps, [5])
        self.assertEqual(len(scenario.commands), 4)
        self.assertTrue(scenario.connected)

    def test_embedded_delivered_helper_matches_tested_file(self):
        shell = (HERE / 'start_fallback_test.sh').read_text()
        python = shell.split("python3 - <<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
        tree = ast.parse(python)
        embedded = next(node.value.value for node in tree.body
                        if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == 'restore_source'
                                for target in node.targets))
        self.assertEqual(embedded.strip(),
                         (HERE / 'restore_test_connection.py').read_text().strip())


if __name__ == '__main__':
    unittest.main()
