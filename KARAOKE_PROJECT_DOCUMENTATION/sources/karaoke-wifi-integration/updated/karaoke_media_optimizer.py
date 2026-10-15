"""Reviewed video maintenance. Originals and crash journals stay on the HDD."""
from contextlib import closing
from fractions import Fraction
from pathlib import Path
import copy
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import threading
import time
import unicodedata
import uuid

ACTIVE = {'scanning', 'repairing'}
EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov'}


class Cancelled(Exception):
    pass


def safe_name(name):
    if (not isinstance(name, str) or not name.strip() or name != name.strip()
            or name in {'.', '..'} or name.startswith('.') or
            any(ord(c) < 32 or c in '/\\:*?"<>|' for c in name)
            or len(os.fsencode(name)) > 240):
        raise ValueError('Недопустимое имя файла.')
    return name


def names(name):
    stem = Path(name).stem
    # A spaced separator preserves hyphens in AC-DC and similar artist names.
    parts = re.split(r'\s+[-–—]\s+', stem, maxsplit=1)
    if len(parts) != 2:
        return None
    artist, title = (' '.join(part.split()) for part in parts)
    if not artist or not title:
        return None
    return artist, title


def identity(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Файл отсутствует или является ссылкой.')
    st = path.stat()
    return [st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns]


def digest(path, cancelled=lambda: False):
    before = identity(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while True:
            if cancelled():
                raise Cancelled()
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    if identity(path) != before:
        raise RuntimeError('Файл изменился во время чтения.')
    return h.hexdigest()


def rate(value):
    try:
        result = Fraction(str(value))
        return result if result > 0 else None
    except (ValueError, ZeroDivisionError):
        return None


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def probe(path):
    proc = subprocess.run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                           '-show_streams', '-show_format', '-of', 'json', str(path)],
                          capture_output=True, timeout=45)
    if proc.returncode:
        raise RuntimeError('ffprobe: ' + proc.stderr.decode(errors='replace')[-800:])
    data = json.loads(proc.stdout)
    streams = data.get('streams', [])
    videos = [s for s in streams if s.get('codec_type') == 'video'
              and not s.get('disposition', {}).get('attached_pic')]
    if not videos:
        raise RuntimeError('Не обнаружена видеодорожка.')
    v = videos[0]
    avg, nominal = rate(v.get('avg_frame_rate')), rate(v.get('r_frame_rate'))
    fps = max([x for x in (avg, nominal) if x] or [Fraction(0)])
    # Read presentation timestamps too: a header average can hide VFR bursts.
    cadence_unknown = False
    if 0 < fps <= 24:
        packets = subprocess.run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                                 '-select_streams', str(v['index']), '-show_entries',
                                 'packet=pts_time', '-of', 'csv=p=0', str(path)],
                                capture_output=True, timeout=90)
        try:
            stamps = sorted(set(float(line.split(',')[0]) for line in
                                packets.stdout.decode().splitlines() if line.strip()))
            tick = float(rate(v.get('time_base')) or Fraction(1, 1000000))
            if packets.returncode or len(stamps) < 2:
                cadence_unknown = True
            elif min(b - a for a, b in zip(stamps, stamps[1:])) < 1 / 24 - tick - 0.000001:
                fps = max(float(fps), 1 / min(b - a for a, b in zip(stamps, stamps[1:])))
        except (ValueError, ZeroDivisionError):
            cadence_unknown = True
    rotation = float(v.get('tags', {}).get('rotate', 0))
    for item in v.get('side_data_list', []):
        rotation = float(item.get('rotation', rotation))
    try:
        duration = float(data.get('format', {}).get('duration') or v.get('duration') or 0)
    except (ValueError, TypeError):
        duration = 0
    return {'width': int(v.get('width', 0)), 'height': int(v.get('height', 0)),
            'fps': round(float(fps), 5), 'codec': v.get('codec_name', '?'),
            'pix_fmt': v.get('pix_fmt'), 'sar': v.get('sample_aspect_ratio', '1:1'),
            'rotation': rotation, 'duration': duration, 'streams': streams,
            'cadence_unknown': cadence_unknown,
            'interlaced': v.get('field_order') not in (None, 'unknown', 'progressive'),
            'can_transcode': len(videos) == 1 and
                sum(s.get('codec_type') == 'video' for s in streams) == 1 and
                all(s.get('codec_type') in {'video', 'audio', 'subtitle', 'attachment'} for s in streams)}


class MediaOptimizer:
    def __init__(self, root, db_path, mount_root='/mnt/usb_disk', is_playing=lambda: False,
                 changed=lambda: None):
        self.root, self.db_path, self.mount = Path(root), Path(db_path), Path(mount_root)
        self.storage = self.mount / '.karaoke-optimization'
        self.lock = threading.RLock()
        self.is_playing, self.changed = is_playing, changed
        self.job, self.thread = None, None
        self.cancel_event = threading.Event()
        self.loaded = False
        self.recovery_error = ''

    @property
    def repairing(self):
        return bool(self.job and self.job['state'] == 'repairing')

    def check_mount(self):
        if (not os.path.ismount(self.mount) or self.mount.is_symlink() or
                self.root.is_symlink() or not self.root.is_dir() or
                self.root.resolve().parent != self.mount.resolve() or
                self.root.stat().st_dev != self.mount.stat().st_dev):
            raise RuntimeError('HDD не подключён. Медиатека не изменена.')
        if self.storage.is_symlink():
            raise RuntimeError('Неожиданная ссылка вместо резервной папки.')

    def write_json(self, path, data):
        self.check_mount()
        temporary = path.with_name(path.name + '.new')
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def connect(self):
        conn = sqlite3.connect(self.db_path.as_uri() + '?mode=rw', uri=True, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def path(self, name):
        if not isinstance(name, str) or not name or name in {'.', '..'} or '/' in name or '\0' in name:
            raise ValueError('Недопустимый путь.')
        return self.root / name

    def load(self):
        if self.loaded:
            return
        self.check_mount()
        if self.recovery_error:
            raise RuntimeError(self.recovery_error)
        if self.storage.exists() and not (self.storage / '.owner').exists() and any(self.storage.iterdir()):
            raise RuntimeError('Резервная папка занята посторонними файлами.')
        self.storage.mkdir(mode=0o700, exist_ok=True)
        (self.storage / '.owner').write_text('karaoke-media-optimizer-v1\n')
        current = self.storage / 'current.json'
        if current.exists():
            record = json.loads(current.read_text())
            if not re.fullmatch(r'[0-9a-f]{32}', record['id']):
                raise RuntimeError('Повреждён журнал обработки.')
            folder = self.storage / record['id']
            self.job = json.loads((folder / 'report.json').read_text())
            # Recover BEFORE the application's initial library refresh.
            for journal in sorted(folder.glob('action-*/journal.json')):
                entry = json.loads(journal.read_text())
                if entry['phase'] == 'prepared':
                    self.undo(journal.parent, entry)
                elif entry['phase'] == 'committed':
                    self.finalize(journal.parent, entry)
            if self.job['state'] in ACTIVE:
                self.job.update(state='failed', error='Обработка прервана перезапуском. '
                                'Незавершённые изменения отменены; запустите проверку заново.')
                self.persist()
        self.loaded = True

    def persist(self):
        if self.job:
            self.write_json(self.storage / self.job['id'] / 'report.json', self.job)

    def status(self):
        with self.lock:
            self.load()
            result = copy.deepcopy(self.job)
            if result:
                for row in result['rows']:
                    for key in list(row):
                        if key.startswith('_'):
                            del row[key]
            return result

    def progress(self, **changes):
        with self.lock:
            self.job.update(changes)
            self.persist()

    def check_cancel(self):
        if self.cancel_event.is_set():
            raise Cancelled()

    def launch(self, target):
        def worker():
            try:
                target()
            except Cancelled:
                self.progress(state='cancelled', message='Обработка остановлена.')
            except Exception as exc:
                try:
                    self.progress(state='failed', error=str(exc), message='Обработка не завершена.')
                except (OSError, RuntimeError):
                    self.job.update(state='failed', error=str(exc))
        self.cancel_event.clear()
        self.thread = threading.Thread(target=worker, daemon=True, name='media-optimizer')
        self.thread.start()

    def start_scan(self):
        with self.lock:
            self.load()
            self.check_mount()
            if self.job and self.job['state'] in ACTIVE:
                raise RuntimeError('Обработка уже идёт.')
            if not shutil.which('ffprobe'):
                raise RuntimeError('На приставке не найден ffprobe.')
            job_id = uuid.uuid4().hex
            (self.storage / job_id).mkdir(mode=0o700)
            self.job = dict(id=job_id, state='scanning', stage='probe', current='', total=0,
                            processed=0, message='Проверяем параметры видео…', rows=[],
                            results=[], error='', cancel_requested=False)
            self.persist()
            self.write_json(self.storage / 'current.json', {'id': job_id})
            self.launch(self.scan)
            return job_id

    def scan(self):
        self.check_mount()
        entries = sorted((p for p in self.root.iterdir() if p.is_file() or p.is_symlink()),
                         key=lambda p: p.name.casefold())
        self.progress(total=len(entries))
        rows, sizes = [], {}
        for index, path in enumerate(entries):
            self.check_cancel()
            self.check_mount()
            row = dict(id='f' + str(index), name=path.name, size=0, issues=[],
                       proposed_name=path.name, video=None, duplicates=[],
                       possible_duplicates=[], can_transcode=False)
            issue = lambda kind, message: row['issues'].append(dict(kind=kind, message=message))
            self.progress(current=path.name, processed=index)
            try:
                row['_identity'] = identity(path)
                row['size'] = row['_identity'][2]
                sizes.setdefault(row['size'], []).append(row)
                pair = names(path.name)
                if pair:
                    row['proposed_name'] = ' - '.join(pair) + path.suffix.lower()
                    if row['proposed_name'] != path.name:
                        issue('name', 'Название можно привести к виду «Исполнитель - Название».')
                else:
                    issue('name', 'Не выделены исполнитель и название. Укажите имя вручную.')
                try:
                    safe_name(path.name)
                except ValueError:
                    issue('name', 'В названии есть недопустимые или лишние символы.')
                info = probe(path)
                if identity(path) != row['_identity']:
                    raise RuntimeError('Файл изменился во время проверки.')
                row['_probe'] = info
                row['video'] = {k: info[k] for k in ('width', 'height', 'fps', 'codec')}
                row['can_transcode'] = info['can_transcode']
                if info['width'] != 1920 or info['height'] != 1080 or info['rotation'] % 360:
                    issue('resolution', f"Разрешение {info['width']}×{info['height']}; требуется 1920×1080.")
                if info['fps'] <= 0 or info['fps'] > 24:
                    issue('fps', f"Частота {info['fps'] or 'неизвестна'} кадров/с; требуется не более 24.")
                elif info['cadence_unknown']:
                    issue('fps', 'Не удалось подтвердить частоту по меткам кадров; предлагается фиксированные 24 FPS.')
                if (info['sar'] not in ('1:1', '0:1', 'N/A') or info['interlaced']):
                    issue('codec', 'Нестандартные пропорции пикселя или чересстрочное видео.')
                if path.suffix.lower() not in EXTENSIONS:
                    issue('codec', 'Расширение не поддерживается медиатекой; предлагается MKV.')
                if (any(s.get('codec_name') == 'mov_text' for s in info['streams']) and
                        any(x['kind'] in {'resolution', 'fps', 'codec'} for x in row['issues'])):
                    issue('notice', 'Текстовые MP4-субтитры будут переведены в ASS с сохранением поддерживаемого оформления.')
                if not row['can_transcode'] and any(x['kind'] in {'resolution', 'fps', 'codec'} for x in row['issues']):
                    issue('manual', 'Сложный набор дорожек: автоматическое преобразование отключено, чтобы их сохранить.')
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
                issue('read', str(exc))
            rows.append(row)
            self.progress(rows=rows, processed=index + 1, current=path.name)
        self.progress(stage='hash', processed=0, message='Сравниваем полное содержимое возможных копий…')
        groups = [r for group in sizes.values() if len(group) > 1 for r in group]
        by_hash = {}
        for index, row in enumerate(groups):
            self.check_cancel()
            try:
                path = self.path(row['name'])
                if identity(path) != row['_identity']:
                    raise RuntimeError('Файл изменился. Нужна новая проверка.')
                row['_sha'] = digest(path, self.cancel_event.is_set)
                by_hash.setdefault(row['_sha'], []).append(row)
            except (OSError, ValueError, RuntimeError) as exc:
                row['issues'].append(dict(kind='read', message=str(exc)))
            self.progress(current=row['name'], processed=index + 1, total=len(groups))
        for group in by_hash.values():
            if len(group) > 1:
                for row in group:
                    row['duplicates'] = [other['id'] for other in group if other is not row]
                    row['issues'].append(dict(kind='duplicate', message='Найдены точные копии: полные SHA256 совпали.'))
        similar = {}
        for row in rows:
            pair = names(row['name'])
            if pair:
                key = unicodedata.normalize('NFKC', ' - '.join(pair)).casefold()
                similar.setdefault(key, []).append(row)
        for group in similar.values():
            if len(group) > 1:
                for row in group:
                    row['possible_duplicates'] = [r['name'] for r in group if r is not row and r['id'] not in row['duplicates']]
                    if row['possible_duplicates']:
                        row['issues'].append(dict(kind='similar', message='Похожие названия: возможно, разные версии песни.'))
        self.progress(rows=rows, state='ready', stage='ready', total=len(rows),
                      processed=len(rows), current='', message='Проверка завершена. Выберите исправления.')

    def cancel(self):
        self.cancel_event.set()
        with self.lock:
            if self.job and self.job['state'] in ACTIVE:
                self.cancel_event.set()
                self.job['cancel_requested'] = True
                self.persist()

    def idle(self):
        if self.is_playing():
            raise RuntimeError('Остановите воспроизведение перед исправлением.')

    def apply(self, job_id, actions, confirmed):
        with self.lock:
            self.load()
            self.check_mount()
            if not self.job or self.job['id'] != job_id or self.job['state'] != 'ready':
                raise RuntimeError('Нужна завершённая актуальная проверка.')
            if confirmed is not True or not isinstance(actions, list) or not actions:
                raise ValueError('Выберите и подтвердите исправления.')
            self.idle()
            rows = {r['id']: r for r in self.job['rows']}
            selected, seen, targets = [], set(), set()
            for action in actions:
                if not isinstance(action, dict) or set(action) - {'file_id', 'rename_to', 'transcode', 'duplicate_keep'}:
                    raise ValueError('Неизвестное исправление.')
                row = rows.get(action.get('file_id'))
                if row is None or row['id'] in seen or '_identity' not in row:
                    raise ValueError('Файл не найден в отчёте или выбран повторно.')
                seen.add(row['id'])
                if action.get('duplicate_keep'):
                    if set(action) != {'file_id', 'duplicate_keep'} or action['duplicate_keep'] not in row['duplicates']:
                        raise ValueError('Не подтверждена точная копия.')
                else:
                    if not action.get('transcode') and 'rename_to' not in action:
                        raise ValueError('Не выбрано исправление.')
                    if 'transcode' in action and action['transcode'] is not True:
                        raise ValueError('Некорректный выбор преобразования.')
                    target = safe_name(action.get('rename_to', row['name']))
                    if not names(target):
                        raise ValueError('Имя должно иметь вид «Исполнитель - Название.ext».')
                    if action.get('transcode'):
                        if not row['can_transcode'] or not shutil.which('ffmpeg'):
                            raise RuntimeError('Этот файл не может быть преобразован автоматически.')
                        target = Path(target).stem + '.mkv'
                    elif Path(target).suffix.lower() != Path(row['name']).suffix.lower():
                        raise ValueError('Расширение меняется только при преобразовании видео.')
                    if Path(target).suffix.lower() not in EXTENSIONS:
                        raise ValueError('Используйте расширение MP4, MKV, AVI или MOV.')
                    if target in targets or (target != row['name'] and (self.root / target).exists()):
                        raise RuntimeError('Имя уже занято: ' + target)
                    if target == row['name'] and not action.get('transcode'):
                        raise ValueError('Новое имя совпадает с прежним.')
                    targets.add(target)
                    action = dict(action, _target=target)
                selected.append(copy.deepcopy(action))
            removed = {a['file_id'] for a in selected if a.get('duplicate_keep')}
            changed = {a['file_id'] for a in selected}
            if any(a.get('duplicate_keep') in changed for a in selected):
                raise ValueError('Оставляемую копию нельзя изменять в том же запуске.')
            self.progress(state='repairing', stage='repair', total=len(selected), processed=0,
                          message='Исправляем выбранные файлы…', error='', results=[])
            self.launch(lambda: self.repair(selected))
            return self.job['id']

    def check_row(self, row):
        self.check_mount()
        path = self.path(row['name'])
        if identity(path) != row['_identity']:
            raise RuntimeError('Файл изменился после проверки. Запустите проверку заново.')
        value = digest(path, self.cancel_event.is_set)
        if row.get('_sha') and value != row['_sha']:
            raise RuntimeError('Содержимое файла изменилось после проверки.')
        return path, value

    def encode(self, source, destination, info):
        if shutil.disk_usage(self.mount).free < max(256 * 1024 * 1024, source.stat().st_size * 2):
            raise RuntimeError('Недостаточно свободного места на HDD для временного видео и резерва.')
        filters = []
        if info['interlaced']:
            filters.append('yadif')
        filters += ["scale=w='trunc(iw*sar/2)*2':h=ih", 'setsar=1',
                    'scale=1920:1080:force_original_aspect_ratio=decrease:force_divisible_by=2',
                    'pad=1920:1080:(ow-iw)/2:(oh-ih)/2', 'setsar=1', 'fps=24']
        command = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-n',
                   '-protocol_whitelist', 'file,pipe', '-i', str(source), '-map', '0',
                   '-map_metadata', '0', '-map_chapters', '0', '-c', 'copy', '-c:v', 'libx264',
                   '-preset', 'veryfast', '-crf', '20', '-threads', '2', '-pix_fmt', 'yuv420p',
                   '-vf', ','.join(filters), '-metadata:s:v:0', 'rotate=0']
        subtitle = 0
        for stream in info['streams']:
            if stream.get('codec_type') == 'subtitle':
                if stream.get('codec_name') == 'mov_text':
                    command += ['-c:s:' + str(subtitle), 'ass']
                subtitle += 1
        command += [str(destination)]
        command[-1:-1] = ['-progress', str(destination.parent / 'progress.txt'), '-nostats']
        if shutil.which('nice'):
            command = ['nice', '-n', '10'] + command
        with (destination.parent / 'ffmpeg.log').open('wb') as log:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=log,
                                       start_new_session=True)
            started = time.monotonic()
            last_progress = started
            try:
                while process.poll() is None:
                    self.check_cancel()
                    self.check_mount()
                    if shutil.disk_usage(self.mount).free < 64 * 1024 * 1024:
                        raise RuntimeError('Мало свободного места на HDD. Исходник сохранён.')
                    if time.monotonic() - started > 12 * 3600:
                        raise RuntimeError('Превышено время преобразования одного файла.')
                    if self.job and info['duration'] and time.monotonic() - last_progress >= 2:
                        last_progress = time.monotonic()
                        progress_file = destination.parent / 'progress.txt'
                        if progress_file.exists():
                            with progress_file.open('rb') as stream:
                                stream.seek(max(0, progress_file.stat().st_size - 4096))
                                times = re.findall(rb'out_time_us=(\d+)', stream.read())
                            if times:
                                percent = min(99, int(int(times[-1]) / 1000000 / info['duration'] * 100))
                                self.progress(stage='encoding', message='Преобразование текущего файла: ' + str(percent) + '%.')
                    time.sleep(0.2)
                if process.returncode:
                    with (destination.parent / 'ffmpeg.log').open('rb') as stream:
                        stream.seek(max(0, stream.seek(0, 2) - 1200))
                        raise RuntimeError('FFmpeg: ' + stream.read().decode(errors='replace'))
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
        result = probe(destination)
        if (result['width'], result['height']) != (1920, 1080) or not 0 < result['fps'] <= 24.001 or result['codec'] != 'h264':
            raise RuntimeError('Результат преобразования не соответствует Full HD / 24 FPS.')
        for kind in ('audio', 'subtitle', 'attachment'):
            if sum(s.get('codec_type') == kind for s in result['streams']) != sum(s.get('codec_type') == kind for s in info['streams']):
                raise RuntimeError('Не сохранены все дорожки/вложения. Исходник оставлен.')
        if info['duration'] and abs(result['duration'] - info['duration']) > 1:
            raise RuntimeError('Длительность изменилась больше чем на секунду. Исходник оставлен.')
        return result

    def finalize(self, folder, entry, verify=True):
        self.check_mount()
        source = self.path(entry['source'])
        target = self.path(entry.get('target') or entry['keeper'])
        if not target.exists() or (verify and digest(target) != entry['new_sha']):
            raise RuntimeError('Требуется восстановление из резерва: ' + str(folder))
        if source != target and source.exists():
            if (digest(source) != entry['old_sha'] if verify else identity(source) != entry['old_identity']):
                raise RuntimeError('Исходный файл изменён извне; удаление отменено.')
            source.unlink()
        sync_directory(self.root)
        entry['phase'] = 'done'
        self.write_json(folder / 'journal.json', entry)

    def undo(self, folder, entry):
        self.check_mount()
        source, backup = self.path(entry['source']), folder / 'original'
        target = self.path(entry['target']) if entry.get('target') else None
        if not backup.exists() or digest(backup) != entry['old_sha']:
            raise RuntimeError('Требуется ручное восстановление: резервная копия не подтверждена: ' + str(folder))
        for path in (source, target):
            if path and path.exists() and digest(path) not in {entry['old_sha'], entry.get('new_sha')}:
                raise RuntimeError('Файл изменён извне; автоматический откат остановлен: ' + path.name)
        with closing(self.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            snapshots = entry['songs']
            if entry.get('inserted_id'):
                db.execute('DELETE FROM songs WHERE id=?', (entry['inserted_id'],))
            for row in snapshots:
                db.execute('INSERT OR REPLACE INTO songs(id,artist,title,file,plays) VALUES(?,?,?,?,?)',
                           tuple(row[k] for k in ('id', 'artist', 'title', 'file', 'plays')))
            for row in entry.get('queue', []):
                db.execute('UPDATE queue SET song_id=? WHERE id=?', (row['song_id'], row['id']))
            if target and target != source and target.exists():
                target.unlink()
            temporary = folder / 'restore'
            temporary.unlink(missing_ok=True)
            shutil.copyfile(backup, temporary)
            with temporary.open('rb') as stream:
                os.fsync(stream.fileno())
            os.replace(temporary, source)
            sync_directory(self.root)
            sync_directory(folder)
            db.commit()
        entry['phase'] = 'rolled_back'
        self.write_json(folder / 'journal.json', entry)

    def commit(self, row, action, folder, source_sha, encoded=None):
        self.idle()
        source, current_sha = self.check_row(row)
        if current_sha != source_sha:
            raise RuntimeError('Файл изменился во время преобразования.')
        rows = {r['id']: r for r in self.job['rows']}
        keeper = None
        if action.get('duplicate_keep'):
            keeper, keeper_sha = self.check_row(rows[action['duplicate_keep']])
            if source_sha != keeper_sha:
                raise RuntimeError('Копии больше не совпадают.')
        target = self.path(action['_target']) if not keeper else None
        if target and target != source and target.exists():
            raise RuntimeError('Новое имя занято другим файлом.')
        backup = folder / 'original'
        if shutil.disk_usage(self.mount).free < source.stat().st_size + 64 * 1024 * 1024:
            raise RuntimeError('Недостаточно места на HDD для резервной копии.')
        # A separate copy remains intact even if a later upload overwrites
        # the newly named file in place. A hardlink would not protect it.
        with source.open('rb') as src, backup.open('xb') as dst:
            while True:
                self.check_cancel()
                block = src.read(1024 * 1024)
                if not block:
                    break
                dst.write(block)
            dst.flush()
            os.fsync(dst.fileno())
        if identity(source) != row['_identity'] or digest(backup) != source_sha:
            raise RuntimeError('Файл изменился при создании резерва.')
        entry = dict(phase='prepared', source=source.name,
                     target=target.name if target else None, old_sha=source_sha,
                     keeper=keeper.name if keeper else None,
                     new_sha=digest(encoded) if encoded else source_sha, old_identity=row['_identity'],
                     songs=[], queue=[], inserted_id=None)
        with self.lock:
            if identity(source) != row['_identity'] or (target and target != source and target.exists()):
                raise RuntimeError('Файл или новое имя изменились во время подготовки.')
            with closing(self.connect()) as db:
                db.execute('BEGIN IMMEDIATE')
                old_song = db.execute('SELECT * FROM songs WHERE file=?', (source.name,)).fetchone()
                keep_song = db.execute('SELECT * FROM songs WHERE file=?', (keeper.name,)).fetchone() if keeper else None
                entry['songs'] = [dict(r) for r in (old_song, keep_song) if r]
                if keeper and old_song:
                    entry['queue'] = [dict(r) for r in db.execute('SELECT id,song_id FROM queue WHERE song_id=?', (old_song['id'],))]
                self.write_json(folder / 'journal.json', entry)
                try:
                    if keeper:
                        if old_song:
                            if keep_song is None:
                                raise RuntimeError('Оставляемая копия не добавлена в медиатеку.')
                            db.execute('UPDATE songs SET plays=plays+? WHERE id=?', (old_song['plays'], keep_song['id']))
                            db.execute('UPDATE queue SET song_id=? WHERE song_id=?', (keep_song['id'], old_song['id']))
                            db.execute('DELETE FROM songs WHERE id=?', (old_song['id'],))
                    else:
                        artist, title = names(target.name)
                        if old_song:
                            db.execute('UPDATE songs SET file=?,artist=?,title=? WHERE id=?',
                                       (target.name, artist, title, old_song['id']))
                        else:
                            cursor = db.execute('INSERT INTO songs(artist,title,file,plays) VALUES(?,?,?,0)',
                                                (artist, title, target.name))
                            entry['inserted_id'] = cursor.lastrowid
                            self.write_json(folder / 'journal.json', entry)
                        if target == source:
                            if encoded is None:
                                raise RuntimeError('Нет нового видео для замены.')
                            os.replace(encoded, target)
                        else:
                            os.link(encoded or source, target)
                        with target.open('rb') as stream:
                            os.fsync(stream.fileno())
                        sync_directory(self.root)
                        sync_directory(folder)
                    db.commit()
                    # If interrupted before this durable marker, recovery restores
                    # both SQLite metadata and the independent original backup.
                    entry['phase'] = 'committed'
                    self.write_json(folder / 'journal.json', entry)
                    self.finalize(folder, entry, verify=False)
                    os.sync()
                except BaseException:
                    db.rollback()
                    try:
                        self.undo(folder, entry)
                    except Exception as exc:
                        self.recovery_error = 'Нужно восстановление медиатеки после подключения HDD: ' + str(folder) + ': ' + str(exc)
                        raise RuntimeError(self.recovery_error) from exc
                    raise
            return dict(file_id=row['id'], name=row['name'], status='done',
                        new_name=target.name if target else keeper.name,
                        backup=str(backup), message='Исправлено. Исходник сохранён.' if target else 'Точная копия перенесена в резерв.')

    def repair(self, actions):
        rows = {r['id']: r for r in self.job['rows']}
        for index, action in enumerate(actions):
            self.check_cancel()
            row = rows[action['file_id']]
            self.progress(current=row['name'], processed=index)
            folder = self.storage / self.job['id'] / ('action-' + str(index))
            self.check_mount()
            folder.mkdir(mode=0o700)
            encoded = folder / 'converted.mkv'
            try:
                source, source_sha = self.check_row(row)
                if action.get('transcode'):
                    self.encode(source, encoded, row['_probe'])
                result = self.commit(row, action, folder, source_sha,
                                     encoded if action.get('transcode') else None)
            except Cancelled:
                raise
            except Exception as exc:
                if self.recovery_error:
                    raise
                result = dict(file_id=row['id'], name=row['name'], status='failed', error=str(exc))
            finally:
                if encoded.exists():
                    encoded.unlink()
            with self.lock:
                self.job['results'].append(result)
                self.persist()
            try:
                self.changed()
            except Exception:
                pass
        failures = sum(r['status'] == 'failed' for r in self.job['results'])
        self.progress(state='done', stage='done', current='', processed=len(actions),
                      message='Обработка завершена. Ошибок: ' + str(failures) + '. Для повторного выбора запустите проверку заново.')


def create_blueprint(manager):
    from flask import Blueprint, jsonify, request, send_from_directory
    bp = Blueprint('media_optimizer', __name__)

    @bp.route('/video-optimization')
    def page():
        return send_from_directory(Path(__file__).parent, 'media_optimizer.html')

    def call(operation):
        try:
            return operation()
        except (ValueError, TypeError, KeyError) as exc:
            return jsonify(ok=False, error=str(exc)), 400
        except (RuntimeError, OSError, sqlite3.Error) as exc:
            return jsonify(ok=False, error=str(exc)), 409

    @bp.route('/api/media-optimizer/status')
    def status():
        return call(lambda: jsonify(ok=True, job=manager.status()))

    @bp.route('/api/media-optimizer/scan', methods=['POST'])
    def scan():
        return call(lambda: (jsonify(ok=True, job_id=manager.start_scan()), 202))

    @bp.route('/api/media-optimizer/cancel', methods=['POST'])
    def cancel():
        return call(lambda: (manager.cancel(), jsonify(ok=True))[1])

    @bp.route('/api/media-optimizer/apply', methods=['POST'])
    def apply():
        def operation():
            body = request.get_json(silent=True)
            if not isinstance(body, dict):
                raise ValueError('Нужен JSON с выбранными исправлениями.')
            return jsonify(ok=True, job_id=manager.apply(body.get('job_id'), body.get('actions'), body.get('confirmed'))), 202
        return call(operation)
    return bp
