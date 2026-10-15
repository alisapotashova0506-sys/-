"""Only restore the original saved station if no configuration is in progress."""
import sys
import time

sys.path.insert(0, '/root/karaoke/wifi')
import network as net


def restore(original_uuid):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            with net.admission_lock():
                with net.file_lock(net.OPERATION_LOCK, blocking=False):
                    manager = net.NetworkManager()
                    job = net.current_job()
                    if job and job.get('status') not in net.FINAL_STATES:
                        raise BlockingIOError
                    if manager.station()['connected']:
                        print('Домашняя сеть уже работает; восстановление не требуется.', flush=True)
                        return
                    manager.run('device', 'set', net.STATION, 'autoconnect', 'yes')
                    manager.run('--wait', '30', 'connection', 'up', 'uuid', original_uuid,
                                'ifname', net.STATION, timeout=40)
                    if not manager.station()['connected']:
                        raise RuntimeError('Нет подтверждённого подключения.')
                    print('Исходная домашняя сеть восстановлена.', flush=True)
                    return
        except (RuntimeError, BlockingIOError):
            time.sleep(5)
    raise RuntimeError('Не удалось восстановить домашнюю сеть за время ожидания.')


if __name__ == '__main__':
    restore(sys.argv[1])
