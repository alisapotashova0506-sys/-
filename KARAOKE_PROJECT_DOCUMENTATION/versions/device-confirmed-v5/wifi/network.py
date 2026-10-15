"""Shared, private job API and NetworkManager helpers for Wi-Fi setup."""
import configparser
from contextlib import contextmanager
import fcntl
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

STATE_DIR = Path('/var/lib/karaoke-wifi')
OPERATION_LOCK = Path('/run/karaoke-wifi-connect.lock')
STATION = 'wlan0'
AP_UUID = '67e9bd92-5f2a-4bab-9645-4afe89fcfc97'
AP_SSID = 'KARAOKE'
AP_IP = '192.168.100.1'
SETUP_URL = 'http://192.168.100.1:8080/wifi/setup'
WIFI_QR = SETUP_URL
ENV = dict(os.environ, LC_ALL='C')
FINAL_STATES = {'success', 'failed'}


def prepare_state():
    for directory in (STATE_DIR, STATE_DIR / 'jobs', STATE_DIR / 'requests'):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.chmod(0o700)


def write_json(path, data):
    path = Path(path)
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex)
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'w') as target:
            json.dump(data, target, ensure_ascii=False)
            target.write('\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


@contextmanager
def file_lock(path, blocking=True):
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        yield


def operation_busy():
    try:
        with file_lock(OPERATION_LOCK, blocking=False):
            return False
    except BlockingIOError:
        return True


def boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def valid_job_id(job_id):
    if not isinstance(job_id, str) or not re.fullmatch(r'[a-f0-9]{32}', job_id):
        raise ValueError('Неверный номер операции.')
    return job_id


def read_job(job_id):
    valid_job_id(job_id)
    job = load_json(STATE_DIR / 'jobs' / (job_id + '.json'))
    if not isinstance(job, dict) or job.get('job_id') != job_id:
        raise ValueError('Операция не найдена.')
    # Job records contain no passwords; still return only the public contract.
    keys = ('job_id', 'type', 'status', 'message', 'ssid', 'ip', 'updated_at')
    return {key: job[key] for key in keys if key in job}


def current_job():
    pointer = load_json(STATE_DIR / 'active-job.json', {})
    job_id = pointer.get('job_id', '') if isinstance(pointer, dict) else ''
    if not re.fullmatch(r'[a-f0-9]{32}', job_id):
        return None
    job = load_json(STATE_DIR / 'jobs' / (job_id + '.json'))
    return job if isinstance(job, dict) and job.get('job_id') == job_id else None


def update_job(job_id, **changes):
    path = STATE_DIR / 'jobs' / (valid_job_id(job_id) + '.json')
    job = load_json(path, {})
    job.update(changes, job_id=job_id, updated_at=int(time.time()))
    write_json(path, job)
    return job


def read_status():
    state = load_json(STATE_DIR / 'status.json', {})
    if not isinstance(state, dict):
        state = {}
    state = dict(state)
    state.setdefault('connected', False)
    state.setdefault('network', '')
    state.setdefault('ip', '')
    state.setdefault('mode', 'waiting')
    state.setdefault('ap_active', False)
    state.setdefault('setup_needed', bool(state['ap_active']))
    state.setdefault('seconds_without_wifi', 0)
    state.setdefault('updated_at', 0)
    updated = state['updated_at']
    state['controller_ok'] = (state.get('version') == 2 and not state.get('error')
                              and isinstance(updated, (int, float))
                              and 0 <= time.time() - updated <= 12)
    job = current_job()
    state['busy'] = bool(job and job.get('status') not in FINAL_STATES)
    state.update(ap_ssid=AP_SSID, ap_ip=AP_IP, setup_url=SETUP_URL, wifi_qr=WIFI_QR)
    if not state['controller_ok']:
        state['error'] = 'Контроллер Wi-Fi недоступен. Попробуйте немного позже.'
    return state


@contextmanager
def admission_lock():
    try:
        with file_lock(STATE_DIR / 'admission.lock', blocking=False):
            yield
    except BlockingIOError:
        raise RuntimeError('Настройка или обновление Wi-Fi уже выполняется. Попробуйте немного позже.') from None


def _submit(kind, **private):
    prepare_state()
    with admission_lock():
        if not read_status()['controller_ok']:
            raise RuntimeError('Контроллер Wi-Fi запускается. Попробуйте немного позже.')
        previous = current_job()
        if previous and previous.get('status') not in FINAL_STATES:
            raise RuntimeError('Другая настройка Wi-Fi уже выполняется.')
        job_id = uuid.uuid4().hex
        job = dict(job_id=job_id, type=kind, status='queued', boot_id=boot_id(),
                   message='Операция ожидает выполнения.', updated_at=int(time.time()))
        if kind == 'connect':
            job['ssid'] = private['ssid']
        request_path = STATE_DIR / 'requests' / (job_id + '.json')
        job_path = STATE_DIR / 'jobs' / (job_id + '.json')
        try:
            write_json(request_path, dict(type=kind, **private))
            write_json(job_path, job)
            write_json(STATE_DIR / 'active-job.json', {'job_id': job_id})
        except Exception:
            request_path.unlink(missing_ok=True)
            job_path.unlink(missing_ok=True)
            raise RuntimeError('Не удалось безопасно поставить операцию в очередь.') from None
        return job_id


def submit_connection(ssid, password):
    try:
        ssid_bytes = ssid.encode('utf-8') if isinstance(ssid, str) else b''
        password_bytes = password.encode('utf-8') if isinstance(password, str) else b''
    except UnicodeError:
        raise ValueError('Имя сети или пароль содержит неверные символы.') from None
    if (not isinstance(ssid, str) or not ssid or len(ssid_bytes) > 32
            or any(character in ssid for character in '\x00\r\n')):
        raise ValueError('Укажите имя сети длиной от 1 до 32 байт.')
    if ssid == AP_SSID:
        raise ValueError('KARAOKE — точка настройки приставки. Выберите домашнюю сеть.')
    if not isinstance(password, str) or any(character in password for character in '\x00\r\n'):
        raise ValueError('Неверный пароль Wi-Fi.')
    if password and not (8 <= len(password_bytes) <= 63 or
                         re.fullmatch(r'[a-fA-F0-9]{64}', password)):
        raise ValueError('Пароль WPA должен содержать 8–63 байта; для открытой сети оставьте его пустым.')
    return _submit('connect', ssid=ssid, password=password)


def request_reset(confirmed):
    if confirmed is not True:
        raise ValueError('Подтвердите удаление сохранённых домашних сетей Wi-Fi.')
    return _submit('reset', confirmed=True)


def split_nmcli(line):
    """Split escaped nmcli terse output, preserving colons/backslashes in SSIDs."""
    fields, current, escaped = [], [], False
    for character in line:
        if escaped:
            current.append(character)
            escaped = False
        elif character == '\\':
            escaped = True
        elif character == ':':
            fields.append(''.join(current))
            current = []
        else:
            current.append(character)
    if escaped:
        current.append('\\')
    fields.append(''.join(current))
    return fields


def usb_interface():
    matches = []
    for link in Path('/sys/bus/usb/devices').glob('*:*'):
        try:
            path = link.resolve(strict=True)
            identity = tuple((path.parent / key).read_text().strip().lower()
                             for key in ('idVendor', 'idProduct'))
            if identity == ('0bda', '8179'):
                if (path / 'driver').resolve(strict=True).name != '8188eu':
                    raise RuntimeError('USB-адаптер ожидает драйвер 8188eu.')
                matches.extend(item.name for item in (path / 'net').glob('*'))
        except FileNotFoundError:
            continue
    if len(matches) != 1:
        raise RuntimeError('USB-адаптер точки доступа недоступен.')
    return matches[0]


def profile_saved(profile_uuid):
    for directory in ('/etc/NetworkManager/system-connections',
                      '/usr/lib/NetworkManager/system-connections'):
        for path in Path(directory).glob('*'):
            if not path.is_file():
                continue
            parser = configparser.RawConfigParser(strict=False)
            try:
                parser.read(path)
                if parser.get('connection', 'uuid', fallback='') == profile_uuid:
                    return True
            except (configparser.Error, UnicodeError, OSError):
                continue
    return False


def candidate_uuid(job_id):
    return str(uuid.UUID(valid_job_id(job_id)))


def candidate_name(job_id):
    return 'KARAOKE_HOME_' + valid_job_id(job_id)


def cleanup_candidate(manager, job_id):
    """Delete only the deterministic UUID and full profile ID owned by this job."""
    profile_uuid = candidate_uuid(job_id)
    try:
        if manager.property(profile_uuid, 'connection.id') != candidate_name(job_id):
            return False
    except RuntimeError:
        return False
    manager.run('--wait', '10', 'connection', 'delete', 'uuid', profile_uuid)
    return True


class NetworkManager:
    def __init__(self):
        self.profile_cache = {}

    def run(self, *arguments, timeout=15):
        try:
            result = subprocess.run(('nmcli', *arguments), text=True, capture_output=True,
                                    env=ENV, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            raise RuntimeError('NetworkManager не ответил вовремя.') from None
        if result.returncode:
            raise RuntimeError('Не удалось выполнить операцию Wi-Fi.')
        return result.stdout

    def property(self, profile_uuid, key):
        return self.run('--escape', 'no', '-g', key, 'connection', 'show', 'uuid',
                        profile_uuid).rstrip('\n')

    def profile(self, profile_uuid):
        if profile_uuid not in self.profile_cache:
            self.profile_cache[profile_uuid] = {
                'type': self.property(profile_uuid, 'connection.type'),
                'interface': self.property(profile_uuid, 'connection.interface-name'),
                'mode': self.property(profile_uuid, '802-11-wireless.mode'),
                'ssid': self.property(profile_uuid, '802-11-wireless.ssid'),
            }
        return self.profile_cache[profile_uuid]

    def device(self, interface):
        output = self.run('-t', '--escape', 'no', '-f',
                          'GENERAL.STATE,GENERAL.CON-UUID,IP4.ADDRESS',
                          'device', 'show', interface)
        fields = dict(line.split(':', 1) for line in output.splitlines() if ':' in line)
        addresses = []
        for key, value in fields.items():
            if key.startswith('IP4.ADDRESS'):
                try:
                    address = ipaddress.ip_interface(value).ip
                    if address.version == 4 and not (address.is_link_local or address.is_loopback
                                                     or address.is_unspecified):
                        addresses.append(str(address))
                except ValueError:
                    pass
        return {'active': fields.get('GENERAL.STATE', '').split(' ', 1)[0] == '100',
                'uuid': fields.get('GENERAL.CON-UUID', ''), 'addresses': addresses}

    def station(self, require_saved=True):
        state = self.device(STATION)
        state.update(connected=False, network='', ip='')
        if state['active'] and state['uuid'] and state['uuid'] != AP_UUID:
            profile = self.profile(state['uuid'])
            if (profile['type'] in ('wifi', '802-11-wireless') and
                    profile['mode'] in ('', 'infrastructure') and
                    profile['interface'] in ('', STATION) and state['addresses']):
                state.update(network=profile['ssid'], ip=state['addresses'][0])
                state['connected'] = bool(profile['ssid'] and profile['ssid'] != AP_SSID and
                                          (not require_saved or profile_saved(state['uuid'])))
        return state

    def usb(self):
        interface = usb_interface()
        state = self.device(interface)
        state.update(interface=interface, ap_active=bool(state['active'] and
                     state['uuid'] == AP_UUID and AP_IP in state['addresses']))
        return state

    def ensure_usb_role(self):
        state = self.usb()
        self.run('--wait', '3', 'device', 'set', state['interface'], 'autoconnect', 'no')
        if state['active'] and state['uuid'] != AP_UUID:
            self.run('--wait', '5', 'device', 'disconnect', state['interface'])
            state = self.usb()
        return state

    def start_ap(self):
        state = self.ensure_usb_role()
        if not state['ap_active']:
            self.run('--wait', '25', 'connection', 'up', 'uuid', AP_UUID,
                     'ifname', state['interface'], timeout=30)
        state = self.usb()
        if not state['ap_active']:
            raise RuntimeError('Точка доступа ещё не готова.')
        return state

    def stop_ap(self):
        state = self.usb()
        if state['uuid'] == AP_UUID:
            self.run('--wait', '10', 'connection', 'down', 'uuid', AP_UUID)

    def home_profiles(self):
        output = self.run('-t', '-f', 'UUID,TYPE', 'connection', 'show')
        profiles = []
        for line in output.splitlines():
            fields = split_nmcli(line)
            if len(fields) != 2 or fields[1] not in ('wifi', '802-11-wireless'):
                continue
            profile_uuid = fields[0]
            if profile_uuid == AP_UUID:
                continue
            profile = self.profile(profile_uuid)
            if profile['mode'] in ('', 'infrastructure') and profile['interface'] in ('', STATION):
                profiles.append(profile_uuid)
        return profiles


def scan_networks():
    try:
        with file_lock(OPERATION_LOCK, blocking=False):
            output = NetworkManager().run('-t', '-f', 'SSID,SIGNAL,SECURITY,IN-USE',
                                          'device', 'wifi', 'list', 'ifname', STATION,
                                          '--rescan', 'yes', timeout=20)
    except BlockingIOError:
        raise RuntimeError('Дождитесь завершения подключения перед сканированием.') from None
    networks = {}
    for line in output.splitlines():
        parts = split_nmcli(line)
        if len(parts) != 4 or not parts[0] or parts[0] == AP_SSID:
            continue
        ssid, signal, security, active = parts
        value = {'ssid': ssid, 'signal': int(signal) if signal.isdigit() else 0,
                 'security': security or 'Open', 'in_use': 'yes' if active == '*' else 'no'}
        previous = networks.get(ssid)
        if not previous or (value['in_use'] == 'yes', value['signal']) > (
                previous['in_use'] == 'yes', previous['signal']):
            networks[ssid] = value
    return sorted(networks.values(), key=lambda network: network['signal'], reverse=True)
