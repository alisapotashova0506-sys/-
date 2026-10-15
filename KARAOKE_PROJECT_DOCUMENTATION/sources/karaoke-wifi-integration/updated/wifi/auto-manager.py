#!/usr/bin/env python3

import json
import os
import subprocess
import time

STATUS = '/var/lib/karaoke-wifi/auto-status.json'
LOG = '/var/log/karaoke-wifi-auto.log'

AP = 'KARAOKE_SYSTEM'
WAIT = 30

os.makedirs('/var/lib/karaoke-wifi', exist_ok=True)

def run(args, timeout=20):
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except Exception:
        return None

def connection():
    r = run([
        'nmcli', '-g', 'GENERAL.CONNECTION',
        'device', 'show', 'wlan0'
    ])
    return r.stdout.strip() if r and r.returncode == 0 else ''

def log(message):
    with open(LOG, 'a') as f:
        f.write(
            time.strftime('%Y-%m-%d %H:%M:%S ') +
            message + '\n'
        )

def status(mode, network=''):
    tmp = STATUS + '.tmp'
    with open(tmp, 'w') as f:
        json.dump({
            'mode': mode,
            'network': network,
            'updated_at': int(time.time())
        }, f)
    os.replace(tmp, STATUS)

log('Контроллер запущен')

missing_since = None

while True:
    try:
        network = connection()

        if network and network != AP and network != '--':
            missing_since = None
            status('connected', network)

        elif network == AP:
            missing_since = None
            status('setup', AP)

        else:
            if missing_since is None:
                missing_since = time.monotonic()
                log('Wi-Fi отсутствует. Ожидание 30 секунд')

            elapsed = time.monotonic() - missing_since

            if elapsed >= WAIT:
                log('Запуск KARAOKE_SYSTEM')

                result = run([
                    'nmcli', '-w', '30',
                    'connection', 'up', AP,
                    'ifname', 'wlan0'
                ], 40)

                if result and result.returncode == 0:
                    log('Точка доступа включена')
                    status('setup', AP)
                    missing_since = None
                else:
                    log('Ошибка запуска точки доступа')
                    missing_since = time.monotonic()

        time.sleep(3)

    except Exception as exc:
        log('Ошибка контроллера: ' + str(exc))
        time.sleep(5)
