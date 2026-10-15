#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

# KARAOKE_CONNECT_LOCK_V3
import fcntl

LOCK_PATH = '/run/karaoke-wifi-connect.lock'
lock_fd = os.open(LOCK_PATH, os.O_CREAT | os.O_RDWR, 0o600)

try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print('Другое подключение уже выполняется.')
    sys.exit(1)

JOB = sys.argv[1]
LOG = '/root/karaoke/wifi/connect-result.log'

def run(args, timeout=40):
    try:
        return subprocess.run(
            args, capture_output=True, text=True,
            timeout=timeout
        )
    except Exception as exc:
        return type('Result', (), {
            'returncode': 1,
            'stderr': str(exc)
        })()

def current():
    result = run([
        'nmcli', '-g', 'GENERAL.CONNECTION',
        'device', 'show', 'wlan0'
    ], 10)
    return result.stdout.strip() if hasattr(result, 'stdout') else ''

def log(message):
    with open(LOG, 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n')

try:
    with open(JOB) as f:
        data = json.load(f)
finally:
    try:
        os.unlink(JOB)
    except OSError:
        pass

ssid = data['ssid']
password = data['password']

# Даём браузеру получить ответ до отключения AP.
time.sleep(4)

if current() != 'KARAOKE_SYSTEM':
    log('Отмена: точка доступа уже не активна')
    sys.exit(1)

log('Начало подключения к выбранной сети')

cmd = ['nmcli', '-w', '35', 'device', 'wifi', 'connect', ssid]

if password:
    cmd.extend(['password', password])

cmd.extend(['ifname', 'wlan0'])

result = run(cmd, 45)

# KARAOKE_CONNECT_SAFETY_V2
ip_result = run([
    'nmcli', '-g', 'IP4.ADDRESS',
    'device', 'show', 'wlan0'
], 10)

has_ip = (
    hasattr(ip_result, 'stdout')
    and bool(ip_result.stdout.strip())
)

if result.returncode == 0 and current() == ssid and has_ip:
    log('УСПЕХ: подключение к выбранной сети')
    sys.exit(0)

log('ОШИБКА подключения. Возвращаем точку доступа')

# Не записываем stderr: некоторые сообщения могут содержать
# данные о подключении.
restore = run([
    'nmcli', '-w', '30',
    'connection', 'up', 'KARAOKE_SYSTEM',
    'ifname', 'wlan0'
], 40)

if restore.returncode == 0 and current() == 'KARAOKE_SYSTEM':
    log('Точка доступа KARAOKE_SYSTEM восстановлена')
    sys.exit(1)

log('Не удалось восстановить AP. Пробуем ZZZZ')

run([
    'nmcli', '-w', '25',
    'connection', 'up', 'ZZZZ',
    'ifname', 'wlan0'
], 35)

log('Аварийная попытка возврата завершена')
