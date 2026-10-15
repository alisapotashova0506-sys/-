#!/usr/bin/env python3
"""One AP-policy owner: builtin wlan0 is the client, USB is only a setup AP."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import network as net
from captive import CaptivePortal


class Policy:
    def __init__(self):
        self.missing_since = None
        self.home_since = None
        self.seconds_missing = 0

    def decide(self, now, connected, ap_active, busy=False, grace_until=0):
        if connected:
            self.missing_since = None
            self.seconds_missing = 0
            if self.home_since is None:
                self.home_since = now
            if ap_active and not busy and now >= grace_until and now - self.home_since >= 2:
                return 'stop'
        else:
            self.home_since = None
            if self.missing_since is None:
                self.missing_since = now
            self.seconds_missing = max(0, int(now - self.missing_since))
            if self.seconds_missing >= 30 and not ap_active:
                return 'start'
        return None


class Controller:
    def __init__(self, manager=None, portal=None):
        self.manager = manager or net.NetworkManager()
        self.portal = portal or CaptivePortal()
        self.policy = Policy()
        self.worker = None
        self.last_state = {'connected': False, 'network': '', 'ip': '',
                           'ap_active': False, 'setup_needed': False, 'mode': 'waiting'}

    def fail_job(self, job, message):
        (net.STATE_DIR / 'requests' / (job['job_id'] + '.json')).unlink(missing_ok=True)
        net.update_job(job['job_id'], status='failed', message=message,
                       boot_id=net.boot_id(), grace_until=time.monotonic() + 60)

    def recover_job(self, job):
        self.manager.start_ap()
        if job['type'] == 'connect':
            station = self.manager.station()
            if station['connected'] and station['uuid'] == net.candidate_uuid(job['job_id']):
                if self.manager.property(station['uuid'], 'connection.id') == net.candidate_name(job['job_id']):
                    net.update_job(job['job_id'], status='success', message='Домашняя сеть подключена и сохранена.',
                                   ip=station['ip'], boot_id=net.boot_id(),
                                   grace_until=time.monotonic() + 10)
                    return
            net.cleanup_candidate(self.manager, job['job_id'])
        self.fail_job(job, 'Предыдущая операция была прервана. Точка KARAOKE доступна для повторной настройки.')

    def reconcile(self):
        job = net.current_job()
        if self.worker and self.worker.poll() is not None:
            self.worker = None
        if not job or job.get('status') in net.FINAL_STATES:
            return job
        locked = net.operation_busy()
        if job.get('status') == 'connecting':
            if locked:
                if job.get('boot_id') == net.boot_id() and time.monotonic() > job.get('deadline', float('inf')):
                    # Signal only the exact private worker/job, never a reused unrelated PID.
                    pid = job.get('worker_pid', 0)
                    try:
                        arguments = Path('/proc') / str(pid) / 'cmdline'
                        arguments = arguments.read_bytes().split(b'\0')
                        expected = str(Path(__file__).with_name('connect-worker.py')).encode()
                        if pid > 1 and expected in arguments and job['job_id'].encode() in arguments:
                            os.kill(pid, signal.SIGTERM)
                    except (OSError, TypeError):
                        pass
                return job
            if self.worker is not None:
                return job
            self.recover_job(job)
            return net.current_job()
        if job.get('status') != 'queued' or locked:
            return job
        if job.get('boot_id') != net.boot_id() or time.time() - job.get('updated_at', 0) > 120:
            self.fail_job(job, 'Операция устарела. Отправьте данные сети заново.')
            return net.current_job()
        try:
            # Reset and reconfiguration both get a usable rescue AP before wlan0 changes.
            self.manager.start_ap()
            net.update_job(job['job_id'], status='connecting', message='Запускается настройка Wi-Fi.',
                           deadline=time.monotonic() + 180, boot_id=net.boot_id())
            self.worker = subprocess.Popen(
                [sys.executable, str(Path(__file__).with_name('connect-worker.py')), job['job_id']],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                close_fds=True)
            net.update_job(job['job_id'], worker_pid=self.worker.pid)
        except Exception:
            self.fail_job(job, 'Не удалось подготовить точку KARAOKE. Попробуйте снова.')
        return net.current_job()

    def tick(self):
        error = ''
        try:
            self.manager.ensure_usb_role()
            job = self.reconcile()
            station = self.manager.station()
            usb = self.manager.usb()
            busy = bool((job and job.get('status') not in net.FINAL_STATES) or net.operation_busy())
            grace = (job.get('grace_until', 0) if job and job.get('boot_id') == net.boot_id() else 0)
            decision = self.policy.decide(time.monotonic(), station['connected'], usb['ap_active'], busy, grace)
            if decision == 'start':
                usb = self.manager.start_ap()
            elif decision == 'stop':
                self.manager.stop_ap()
                usb = self.manager.usb()
            self.last_state = dict(connected=station['connected'], network=station['network'],
                                   ip=station['ip'], ap_active=usb['ap_active'], busy=busy,
                                   setup_needed=bool(usb['ap_active'] and not station['connected']),
                                   mode='connecting' if busy else ('connected' if station['connected']
                                         else ('setup' if usb['ap_active'] else 'waiting')),
                                   usb_interface=usb['interface'])
        except Exception:
            # Keep the last observed state; do not publish command stderr or credentials.
            error = 'Не удалось обновить состояние Wi-Fi. Контроллер повторит попытку.'
        if self.last_state['ap_active']:
            if not self.portal.start():
                self.last_state['portal_error'] = 'Автостраница на порту 80 недоступна; используйте ссылку настройки.'
            else:
                self.last_state.pop('portal_error', None)
        else:
            self.portal.stop()
        state = dict(self.last_state, version=2, seconds_without_wifi=self.policy.seconds_missing,
                     updated_at=int(time.time()), error=error)
        net.write_json(net.STATE_DIR / 'status.json', state)
        return state


def main():
    net.prepare_state()
    controller = Controller()
    def stop(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        while True:
            controller.tick()
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        controller.portal.stop()


if __name__ == '__main__':
    main()
