import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, '/root/karaoke/wifi')
import network as net

ssh = os.environ.get('SSH_CONNECTION', '').split()
if os.geteuid() != 0 or len(ssh) != 4 or ssh[2] != '192.168.1.102':
    raise RuntimeError('Нужно SSH-подключение к 192.168.1.102.')
route = subprocess.check_output(['ip', '-j', '-4', 'route', 'get', ssh[0], 'from', ssh[2]], text=True)
routes = json.loads(route)
if not routes or any(item.get('dev') != net.STATION for item in routes):
    raise RuntimeError('Компьютер должен быть подключён к домашней сети.')

restore_source = r'''
__RESTORE_SOURCE__
'''

with net.admission_lock(), net.file_lock(net.OPERATION_LOCK, blocking=False):
    state = net.read_status()
    manager = net.NetworkManager()
    home = manager.station()
    if not state['controller_ok'] or state['busy'] or not home['connected']:
        raise RuntimeError('Контроллер Wi-Fi занят или домашняя сеть не подтверждена. Тест не начат.')
    folder = Path(tempfile.mkdtemp(prefix='karaoke-fallback-test-', dir='/root'))
    folder.chmod(0o700)
    rescue = folder / 'restore.py'
    rescue.write_text(restore_source)
    rescue.chmod(0o600)
    unit = 'karaoke-fallback-rescue-' + str(time.time_ns())
    subprocess.run(['systemd-run', '--unit=' + unit, '--on-active=10min',
                    '--timer-property=AccuracySec=1s', '--property=Type=oneshot',
                    '--property=TimeoutStartSec=240s', '/usr/bin/python3', '-u',
                    str(rescue), home['uuid']], check=True)
    subprocess.run(['systemctl', 'is-active', '--quiet', unit + '.timer'], check=True)
    print('Таймер восстановления готов:', unit + '.timer', flush=True)
    print('Отключаем домашний Wi-Fi. SSH прервётся; ждите KARAOKE около 40 секунд.', flush=True)
    manager.run('--wait', '10', 'device', 'disconnect', net.STATION, timeout=15)
