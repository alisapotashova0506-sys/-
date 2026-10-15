#!/usr/bin/env python3
"""Run one controller-owned Wi-Fi job. Never switch wlan0 into AP mode."""
import os
import signal
import sys
import time

import network as net


def finish(job_id, status, message, **extra):
    return net.update_job(job_id, status=status, message=message, boot_id=net.boot_id(),
                          grace_until=time.monotonic() + (60 if status == 'failed' else 10), **extra)


def connect(manager, job_id, request):
    profile_uuid = net.candidate_uuid(job_id)
    saved = False
    try:
        arguments = ['connection', 'add', 'save', 'no', 'type', 'wifi', 'ifname', net.STATION,
                     'con-name', net.candidate_name(job_id), 'connection.uuid', profile_uuid,
                     'connection.autoconnect', 'no', 'ssid', request['ssid'],
                     'wifi.mode', 'infrastructure', 'wifi.hidden', 'yes',
                     'wifi.cloned-mac-address', 'permanent',
                     'ipv4.method', 'auto', 'ipv6.method', 'auto']
        if request['password']:
            arguments.extend(('wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', request['password']))
        manager.run(*arguments)
        net.update_job(job_id, candidate_uuid=profile_uuid,
                       message='Подключаем приставку к выбранной сети. Точка доступа остаётся доступной.')
        manager.run('--wait', '40', 'connection', 'up', 'uuid', profile_uuid,
                    'ifname', net.STATION, timeout=50)
        station = manager.station(require_saved=False)
        if not station['connected'] or station['uuid'] != profile_uuid or not station['ip']:
            raise RuntimeError('Подключение к выбранной сети не подтверждено.')
        # A successful association alone is not success: save credentials first.
        manager.run('connection', 'modify', 'uuid', profile_uuid,
                    'connection.autoconnect', 'yes', 'connection.autoconnect-priority', '50')
        if not net.profile_saved(profile_uuid):
            raise RuntimeError('Не удалось сохранить домашнюю сеть.')
        station = manager.station()
        if not station['connected'] or station['uuid'] != profile_uuid:
            raise RuntimeError('Сохранённое подключение больше не активно.')
        saved = True
        finish(job_id, 'success', 'Домашняя сеть подключена и сохранена. '
               'Переключите телефон на неё; точка доступа отключится через 10 секунд.',
               ip=station['ip'], ssid=request['ssid'])
    finally:
        request.pop('password', None)
        if not saved:
            net.cleanup_candidate(manager, job_id)


def reset(manager, job_id, request):
    if request.get('confirmed') is not True:
        raise ValueError('Сброс Wi-Fi не подтверждён.')
    # Controller has opened the USB AP before starting this worker.
    profiles = manager.home_profiles()
    manager.run('device', 'set', net.STATION, 'autoconnect', 'no')
    try:
        for profile_uuid in profiles:
            manager.run('--wait', '10', 'connection', 'delete', 'uuid', profile_uuid)
        station = manager.device(net.STATION)
        if station['active'] and station['uuid'] in profiles:
            manager.run('--wait', '10', 'device', 'disconnect', net.STATION)
    finally:
        manager.run('device', 'set', net.STATION, 'autoconnect', 'yes')
    finish(job_id, 'success', 'Сохранённые домашние сети удалены. '
           'Подключитесь к KARAOKE и выберите новую сеть.')


def perform(job_id, manager=None):
    net.valid_job_id(job_id)
    manager = manager or net.NetworkManager()
    request_path = net.STATE_DIR / 'requests' / (job_id + '.json')
    with net.file_lock(net.OPERATION_LOCK):
        request = net.load_json(request_path)
        request_path.unlink(missing_ok=True)  # Remove the password before NM operations.
        if not isinstance(request, dict) or request.get('type') not in ('connect', 'reset'):
            raise ValueError('Данные операции недоступны.')
        net.update_job(job_id, status='connecting', message='Выполняется настройка Wi-Fi.',
                       worker_pid=os.getpid(), deadline=time.monotonic() + 180,
                       boot_id=net.boot_id())
        try:
            if not manager.usb()['ap_active']:
                raise RuntimeError('Сначала должна быть доступна точка настройки KARAOKE.')
            if request['type'] == 'connect':
                connect(manager, job_id, request)
            else:
                reset(manager, job_id, request)
        except Exception:
            # Never record raw NM stderr, command arguments or submitted passwords.
            finish(job_id, 'failed', 'Не удалось завершить настройку. Проверьте пароль '
                   'и доступность домашней сети; точка KARAOKE остаётся доступной.')
        finally:
            request.pop('password', None)


def interrupted(signum, frame):
    raise InterruptedError('Wi-Fi worker stopped')


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, interrupted)
    try:
        if len(sys.argv) != 2:
            raise ValueError('job id required')
        perform(sys.argv[1])
    except Exception:
        # Controller reconciles an interrupted job; no sensitive traceback output.
        raise SystemExit(1)
