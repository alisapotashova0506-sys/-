# Справочник функций Python

Сгенерирован AST-анализом сохранённых файлов. Номера строк относятся именно к указанному снимку. Описание из docstring/аннотации, затем статически найденные вызовы; это не доказательство выполнения ветви и не полный runtime call graph. Вложенные callbacks перечислены с областями видимости. Полный код — по пути и в едином документе.

## versions/prepared-media-audio-v1/app.py

### load_bgm_settings()

Источник: `versions/prepared-media-audio-v1/app.py:41`; тело до строки 47.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `json.load`, `open`.

### save_bgm_settings()

Источник: `versions/prepared-media-audio-v1/app.py:54`; тело до строки 60.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `json.dump`, `open`.

### bgm_get_tracks()

Источник: `versions/prepared-media-audio-v1/app.py:62`; тело до строки 65.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `f.endswith`, `os.listdir`, `os.path.exists`, `sorted`.

### bgm_start()

Источник: `versions/prepared-media-audio-v1/app.py:67`; тело до строки 87.

Создаёт плейлист MP3 и отдельный mpv для фоновой музыки.

Статические вызовы (включая вложенные callbacks): `audio_output.player_args`, `bgm_get_tracks`, `bgm_stop`, `open`, `os.path.abspath`, `os.path.join`, `os.remove`, `pf.write`, `str`, `subprocess.Popen`.

### bgm_stop()

Источник: `versions/prepared-media-audio-v1/app.py:89`; тело до строки 106.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `bgm_process.terminate`, `bgm_process.wait`, `os.remove`, `subprocess.run`.

### bgm_set_volume(vol)

Источник: `versions/prepared-media-audio-v1/app.py:108`; тело до строки 126.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `_sock.socket`, `bgm_start`, `encode`, `int`, `s.close`, `s.connect`, `s.recv`, `s.sendall`, `s.settimeout`, `save_bgm_settings`, `str`.

### video_set_volume(vol)

Источник: `versions/prepared-media-audio-v1/app.py:128`; тело до строки 143.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `_sock.socket`, `cmd.encode`, `int`, `s.close`, `s.connect`, `s.recv`, `s.sendall`, `s.settimeout`, `save_bgm_settings`, `str`.

### _maintenance_player_active()

Источник: `versions/prepared-media-audio-v1/app.py:157`; тело до строки 167.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `audio_output.ipc`, `get`, `globals`, `os.path.exists`.

### _media_changed()

Источник: `versions/prepared-media-audio-v1/app.py:169`; тело до строки 171.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `broadcast_state`, `socketio.emit`.

### _media_refresh_guard(function)

Источник: `versions/prepared-media-audio-v1/app.py:177`; тело до строки 188.

Не допускает refresh во время восстановления/repair.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `function`, `media_optimizer.load`, `wraps`.

### _media_refresh_guard.guarded(*args, **kwargs)

Источник: `versions/prepared-media-audio-v1/app.py:179`; тело до строки 187.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `wraps(function)`.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `function`, `media_optimizer.load`, `wraps`.

### _media_play_guard(function)

Источник: `versions/prepared-media-audio-v1/app.py:190`; тело до строки 201.

Согласует старт видео с maintenance и блокировкой аудио.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `audio_output.wait_ready`, `function`, `platform.system`, `wraps`.

### _media_play_guard.guarded(*args, **kwargs)

Источник: `versions/prepared-media-audio-v1/app.py:192`; тело до строки 200.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `wraps(function)`.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `audio_output.wait_ready`, `function`, `platform.system`, `wraps`.

### _audio_start_guard(function)

Источник: `versions/prepared-media-audio-v1/app.py:203`; тело до строки 211.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `audio_output.wait_ready`, `function`, `get`, `globals`, `wraps`.

### _audio_start_guard.guarded(*args, **kwargs)

Источник: `versions/prepared-media-audio-v1/app.py:205`; тело до строки 210.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `wraps(function)`.

Статические вызовы (включая вложенные callbacks): `audio_output.wait_ready`, `function`, `get`, `globals`, `wraps`.

### _media_queue_guard(function)

Источник: `versions/prepared-media-audio-v1/app.py:213`; тело до строки 220.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `function`, `wraps`.

### _media_queue_guard.guarded(*args, **kwargs)

Источник: `versions/prepared-media-audio-v1/app.py:215`; тело до строки 219.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `wraps(function)`.

Статические вызовы (включая вложенные callbacks): `function`, `wraps`.

### get_db()

Источник: `versions/prepared-media-audio-v1/app.py:236`; тело до строки 239.

Открывает рабочую SQLite-базу, включает Row для доступа по имени.

Статические вызовы (включая вложенные callbacks): `sqlite3.connect`.

### init_db()

Источник: `versions/prepared-media-audio-v1/app.py:241`; тело до строки 248.

Создаёт таблицы songs/queue при отсутствии.

Статические вызовы (включая вложенные callbacks): `c.execute`, `conn.close`, `conn.commit`, `conn.cursor`, `get_db`, `logger.info`.

### get_network_status()

Источник: `versions/prepared-media-audio-v1/app.py:250`; тело до строки 256.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `state.get`, `wifi_network.read_status`.

### allowed_file(filename)

Источник: `versions/prepared-media-audio-v1/app.py:259`; тело до строки 266.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `filename.rsplit`, `len`, `lower`.

### parse_filename(filename)

Источник: `versions/prepared-media-audio-v1/app.py:268`; тело до строки 276.

Разбирает «исполнитель - название» с legacy fallback.

Статические вызовы (включая вложенные callbacks): `name.split`, `os.path.splitext`, `strip`.

### find_poster(artist)

Источник: `versions/prepared-media-audio-v1/app.py:278`; тело до строки 291.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `artist.replace`, `os.path.exists`, `os.path.join`, `search_names.add`.

### safe_filename(filename)

Источник: `versions/prepared-media-audio-v1/app.py:293`; тело до строки 299.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `re.sub`.

### file_hash_quick(path, chunk_size=1024 * 1024)

Источник: `versions/prepared-media-audio-v1/app.py:301`; тело до строки 315.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `f.read`, `f.seek`, `h.hexdigest`, `h.update`, `hashlib.md5`, `max`, `open`, `os.path.getsize`, `str`.

### refresh_database()

Источник: `versions/prepared-media-audio-v1/app.py:318`; тело до строки 360.

Сверяет плоский каталог с songs/queue, требует mount и maintenance guard.

Декораторы: `_media_refresh_guard`.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `allowed_file`, `c.execute`, `c.fetchall`, `conn.close`, `conn.commit`, `conn.cursor`, `fetchone`, `get_db`, `logger.error`, `logger.info`, `os.listdir`, `os.path.exists`, `os.path.isdir`, `os.path.isfile`, `os.path.ismount`, `os.path.join`, `parse_filename`, `quarantine_mentions`.

### find_player()

Источник: `versions/prepared-media-audio-v1/app.py:362`; тело до строки 372.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `platform.system`, `subprocess.run`.

### kill_existing_players()

Источник: `versions/prepared-media-audio-v1/app.py:374`; тело до строки 380.

Останавливаем только караоке mpv, не затрагивая BGM.

Статические вызовы (включая вложенные callbacks): `os.path.exists`, `range`, `send_mpv_command`, `time.sleep`.

### get_media_stats()

Источник: `versions/prepared-media-audio-v1/app.py:386`; тело до строки 423.

Подсчитывает количество файлов и общий размер в папках медиа

Статические вызовы (включая вложенные callbacks): `os.listdir`, `os.path.exists`, `os.path.getsize`, `os.path.isfile`, `os.path.join`.

### play_video_file(path)

Источник: `versions/prepared-media-audio-v1/app.py:434`; тело до строки 501.

IPC loadfile в существующий mpv либо запуск wrapper; обрабатывает завершение.

Декораторы: `_media_play_guard`.

Статические вызовы (включая вложенные callbacks): `_advance_queue_after_end`, `_player_state.update`, `app.app_context`, `cmd.encode`, `find_player`, `json.dumps`, `logger.exception`, `os.environ.copy`, `os.path.exists`, `os.remove`, `os.startfile`, `p.wait`, `platform.system`, `s.close`, `s.connect`, `s.recv`, `s.sendall`, `s.settimeout`, `socket.socket`, `socketio.emit`, `start`, `subprocess.Popen`, `subprocess.run`, `threading.Thread`, `vol_cmd.encode`.

### play_video_file._wait_and_notify(p, generation)

Источник: `versions/prepared-media-audio-v1/app.py:485`; тело до строки 500.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `_advance_queue_after_end`, `_player_state.update`, `app.app_context`, `logger.exception`, `os.remove`, `p.wait`, `socketio.emit`.

### broadcast_state(event='state_update')

Источник: `versions/prepared-media-audio-v1/app.py:504`; тело до строки 516.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `c.execute`, `c.fetchall`, `conn.close`, `conn.cursor`, `get_db`, `logger.error`, `queue.append`, `socketio.emit`.

### _media_request_guard()

Источник: `versions/prepared-media-audio-v1/app.py:2452`; тело до строки 2479.

Блокирует изменения во время установки/repair и удерживает maintenance lock на запрос.

Декораторы: `app.before_request`.

Статические вызовы (включая вложенные callbacks): `jsonify`, `media_optimizer.load`, `media_optimizer.lock.acquire`, `media_optimizer.lock.release`, `os.path.getmtime`, `split`, `str`, `time.time`.

### _media_release_guard(error=None)

Источник: `versions/prepared-media-audio-v1/app.py:2482`; тело до строки 2484.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.teardown_request`.

Статические вызовы (включая вложенные callbacks): `g.pop`, `media_optimizer.lock.release`.

### poster_manager_page()

Источник: `versions/prepared-media-audio-v1/app.py:2488`; тело до строки 2489.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/poster-manager')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `send_from_directory`.

### index()

Источник: `versions/prepared-media-audio-v1/app.py:2492`; тело до строки 2493.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `render_template_string`.

### top_artists()

Источник: `versions/prepared-media-audio-v1/app.py:2496`; тело до строки 2507.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/top_artists')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `artists.append`, `c.execute`, `c.fetchall`, `conn.close`, `conn.cursor`, `find_poster`, `get_db`, `jsonify`, `quarantine_blocked`.

### search()

Источник: `versions/prepared-media-audio-v1/app.py:2510`; тело до строки 2531.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/search')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `artist.lower`, `c.execute`, `c.fetchall`, `conn.close`, `conn.cursor`, `get_db`, `jsonify`, `lower`, `quarantine_mentions`, `request.args.get`, `songs.append`, `strip`, `title.lower`.

### play()

Источник: `versions/prepared-media-audio-v1/app.py:2534`; тело до строки 2551.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/play', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `announce_song`, `app.route`, `isinstance`, `jsonify`, `os.path.basename`, `os.path.exists`, `os.path.join`, `parse_filename`, `play_video_file`, `quarantine_mentions`, `request.json.get`, `str`.

### increment()

Источник: `versions/prepared-media-audio-v1/app.py:2554`; тело до строки 2564.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/increment')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `c.execute`, `conn.close`, `conn.commit`, `conn.cursor`, `get_db`, `jsonify`, `request.args.get`, `socketio.emit`.

### queue_add()

Источник: `versions/prepared-media-audio-v1/app.py:2567`; тело до строки 2581.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/queue/add', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `c.execute`, `conn.close`, `conn.commit`, `conn.cursor`, `fetchone`, `get_db`, `jsonify`, `quarantine_blocked`, `request.json.get`.

### queue_list()

Источник: `versions/prepared-media-audio-v1/app.py:2584`; тело до строки 2608.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/queue/list')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `c.execute`, `c.fetchall`, `conn.close`, `conn.cursor`, `get_db`, `jsonify`, `queue.append`.

### queue_next()

Источник: `versions/prepared-media-audio-v1/app.py:2611`; тело до строки 2630.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/queue/next')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `c.execute`, `c.fetchone`, `conn.close`, `conn.commit`, `conn.cursor`, `get_db`, `jsonify`, `socketio.emit`.

### queue_remove(queue_id)

Источник: `versions/prepared-media-audio-v1/app.py:2633`; тело до строки 2640.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/queue/remove/<int:queue_id>', methods=['DELETE'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `c.execute`, `conn.close`, `conn.commit`, `conn.cursor`, `get_db`, `jsonify`.

### queue_move()

Источник: `versions/prepared-media-audio-v1/app.py:2643`; тело до строки 2673.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/queue/move', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `c.execute`, `c.fetchall`, `conn.close`, `conn.commit`, `conn.cursor`, `data.get`, `enumerate`, `format`, `get_db`, `jsonify`, `len`, `request.get_json`.

### queue_clear()

Источник: `versions/prepared-media-audio-v1/app.py:2676`; тело до строки 2683.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/queue/clear', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `c.execute`, `conn.close`, `conn.commit`, `conn.cursor`, `get_db`, `jsonify`.

### send_mpv_command(command)

Источник: `versions/prepared-media-audio-v1/app.py:2685`; тело до строки 2714.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `cmd.encode`, `json.dumps`, `os.path.exists`, `os.remove`, `s.close`, `s.connect`, `s.recv`, `s.sendall`, `s.settimeout`, `sock_mod.socket`, `subprocess.run`.

### api_stop()

Источник: `versions/prepared-media-audio-v1/app.py:2717`; тело до строки 2732.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/stop')`.

Статические вызовы (включая вложенные callbacks): `_player_state.update`, `app.route`, `jsonify`, `logger.warning`, `os.remove`, `send_mpv_command`, `socketio.emit`, `time.sleep`.

### api_pause()

Источник: `versions/prepared-media-audio-v1/app.py:2735`; тело до строки 2740.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/pause')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `jsonify`, `send_mpv_command`, `socketio.emit`.

### _advance_queue_after_end()

Источник: `versions/prepared-media-audio-v1/app.py:2743`; тело до строки 2759.

Продвигает очередь после завершения песни с maintenance guard.

Декораторы: `_media_queue_guard`.

Статические вызовы (включая вложенные callbacks): `announce_song`, `broadcast_state`, `conn.close`, `conn.commit`, `conn.execute`, `fetchone`, `get_db`, `os.path.isfile`, `os.path.join`, `play_video_file`.

### api_next()

Источник: `versions/prepared-media-audio-v1/app.py:2762`; тело до строки 2788.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/next')`.

Статические вызовы (включая вложенные callbacks): `announce_song`, `app.route`, `broadcast_state`, `c.execute`, `c.fetchone`, `conn.close`, `conn.commit`, `conn.cursor`, `get_db`, `jsonify`, `os.path.exists`, `os.path.join`, `play_video_file`, `send_mpv_command`.

### upload()

Источник: `versions/prepared-media-audio-v1/app.py:2791`; тело до строки 2825.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/upload', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `_time.time`, `allowed_file`, `app.route`, `c.execute`, `conn.close`, `conn.commit`, `conn.cursor`, `file.save`, `get_db`, `jsonify`, `logger.info`, `os.path.getsize`, `os.path.join`, `parse_filename`, `quarantine_mentions`, `safe_filename`, `socketio.emit`, `str`.

### refresh_after_upload()

Источник: `versions/prepared-media-audio-v1/app.py:2828`; тело до строки 2830.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/refresh_after_upload', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `jsonify`, `refresh_database`.

### upload_poster()

Источник: `versions/prepared-media-audio-v1/app.py:2833`; тело до строки 2858.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/upload_poster', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `ext.lower`, `file.save`, `file_hash_quick`, `jsonify`, `logger.info`, `lstrip`, `name.strip`, `os.path.exists`, `os.path.join`, `os.path.splitext`, `os.remove`, `safe_filename`, `socketio.emit`.

### fonsound_list()

Источник: `versions/prepared-media-audio-v1/app.py:2861`; тело до строки 2865.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/fonsound_list')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `endswith`, `f.lower`, `jsonify`, `os.listdir`, `os.path.exists`, `sorted`.

### serve_fonsound(filename)

Источник: `versions/prepared-media-audio-v1/app.py:2868`; тело до строки 2869.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/fonsound/<path:filename>')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `send_from_directory`.

### api_bgm_start()

Источник: `versions/prepared-media-audio-v1/app.py:2873`; тело до строки 2875.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/bgm/start')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `bgm_get_tracks`, `bgm_start`, `jsonify`, `len`.

### api_bgm_stop()

Источник: `versions/prepared-media-audio-v1/app.py:2878`; тело до строки 2880.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/bgm/stop')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `bgm_stop`, `jsonify`.

### api_bgm_volume()

Источник: `versions/prepared-media-audio-v1/app.py:2883`; тело до строки 2886.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/bgm/volume')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `bgm_set_volume`, `int`, `jsonify`, `request.args.get`.

### api_bgm_toggle()

Источник: `versions/prepared-media-audio-v1/app.py:2889`; тело до строки 2897.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/bgm/toggle')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `bgm_start`, `bgm_stop`, `jsonify`, `request.args.get`, `save_bgm_settings`.

### api_bgm_status()

Источник: `versions/prepared-media-audio-v1/app.py:2900`; тело до строки 2907.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/bgm/status')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `bgm_get_tracks`, `jsonify`, `len`.

### api_video_volume()

Источник: `versions/prepared-media-audio-v1/app.py:2910`; тело до строки 2913.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/video/volume')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `int`, `jsonify`, `request.args.get`, `video_set_volume`.

### api_files_list()

Источник: `versions/prepared-media-audio-v1/app.py:2916`; тело до строки 2952.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/files/list')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `c.execute`, `c.fetchone`, `conn.close`, `conn.cursor`, `f.lower`, `f.rsplit`, `files.append`, `files.sort`, `get_db`, `int`, `jsonify`, `len`, `lower`, `os.listdir`, `os.path.isfile`, `os.path.join`, `os.stat`, `request.args.get`, `round`.

### api_files_delete()

Источник: `versions/prepared-media-audio-v1/app.py:2955`; тело до строки 2989.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/files/delete', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `c.execute`, `c.fetchone`, `conn.close`, `conn.commit`, `conn.cursor`, `data.get`, `filename.rsplit`, `get_db`, `jsonify`, `logger.info`, `lower`, `os.path.exists`, `os.path.join`, `os.remove`, `request.get_json`, `socketio.emit`.

### upload_bgm()

Источник: `versions/prepared-media-audio-v1/app.py:2992`; тело до строки 3005.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/upload_bgm', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `ext.lower`, `file.save`, `jsonify`, `logger.info`, `os.path.join`, `os.path.splitext`, `safe_filename`.

### karaoke_wifi_monitor_status()

Источник: `versions/prepared-media-audio-v1/app.py:3010`; тело до строки 3011.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/karaoke-wifi-monitor')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `jsonify`, `wifi_network.read_status`.

### _wifi_control_allowed()

Источник: `versions/prepared-media-audio-v1/app.py:3014`; тело до строки 3026.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `bool`, `ipaddress.ip_address`, `ipaddress.ip_network`, `state.get`, `str`, `wifi_network.read_status`.

### _wifi_job_response(operation)

Источник: `versions/prepared-media-audio-v1/app.py:3029`; тело до строки 3040.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `jsonify`, `logger.exception`, `operation`, `str`.

### _wifi_connect_request(portal_only=False)

Источник: `versions/prepared-media-audio-v1/app.py:3043`; тело до строки 3052.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `_wifi_control_allowed`, `_wifi_job_response`, `data.get`, `get`, `isinstance`, `jsonify`, `request.get_json`, `wifi_network.read_status`, `wifi_network.submit_connection`.

### karaoke_portal_connect()

Источник: `versions/prepared-media-audio-v1/app.py:3056`; тело до строки 3057.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/wifi/portal-connect', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `_wifi_connect_request`, `app.route`.

### karaoke_wifi_job(job_id)

Источник: `versions/prepared-media-audio-v1/app.py:3061`; тело до строки 3067.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/wifi/job/<job_id>')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `jsonify`, `str`, `wifi_network.read_job`.

### karaoke_wifi_reset()

Источник: `versions/prepared-media-audio-v1/app.py:3071`; тело до строки 3078.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/wifi/reset', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `_wifi_control_allowed`, `_wifi_job_response`, `app.route`, `data.get`, `isinstance`, `jsonify`, `request.get_json`, `wifi_network.request_reset`.

### karaoke_wifi_setup_page()

Источник: `versions/prepared-media-audio-v1/app.py:3082`; тело до строки 3083.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/wifi/setup')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `send_from_directory`.

### karaoke_wifi_setup_qr()

Источник: `versions/prepared-media-audio-v1/app.py:3087`; тело до строки 3088.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/wifi/setup-qr.png')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `send_from_directory`.

### karaoke_control_qr()

Источник: `versions/prepared-media-audio-v1/app.py:3092`; тело до строки 3102.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/wifi/control-qr.png')`.

Статические вызовы (включая вложенные callbacks): `Response`, `app.route`, `jsonify`, `request.args.get`, `str`, `wifi_control_qr.control_image`.

### api_network_status()

Источник: `versions/prepared-media-audio-v1/app.py:3106`; тело до строки 3107.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/network_status')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `get_network_status`, `jsonify`.

### settings_info()

Источник: `versions/prepared-media-audio-v1/app.py:3110`; тело до строки 3130.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/settings/info')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `jsonify`, `len`, `os.listdir`, `os.path.isfile`, `os.path.join`, `round`, `shutil.disk_usage`.

### api_format_hdd()

Источник: `versions/prepared-media-audio-v1/app.py:3133`; тело до строки 3167.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/format_hdd', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `d.endswith`, `f.readlines`, `f.writelines`, `glob.glob`, `jsonify`, `lines.append`, `open`, `os.makedirs`, `str`, `subprocess.run`, `usb_disks.append`, `uuid_result.stdout.strip`.

### settings_refresh_db()

Источник: `versions/prepared-media-audio-v1/app.py:3170`; тело до строки 3174.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/settings/refresh_db', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `broadcast_state`, `jsonify`, `refresh_database`, `socketio.emit`.

### poster_missing()

Источник: `versions/prepared-media-audio-v1/app.py:3179`; тело до строки 3185.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/posters/missing')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `conn.close`, `conn.execute`, `fetchall`, `find_poster`, `get_db`, `jsonify`, `len`.

### poster_search()

Источник: `versions/prepared-media-audio-v1/app.py:3188`; тело до строки 3200.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/posters/search')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `isinstance`, `jsonify`, `len`, `logger.warning`, `request.args.get`, `search_all`, `str`, `strip`.

### poster_yandex_preview(token)

Источник: `versions/prepared-media-audio-v1/app.py:3203`; тело до строки 3210.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/posters/yandex-preview/<token>')`.

Статические вызовы (включая вложенные callbacks): `Response`, `app.route`, `logger.warning`, `yandex_preview`.

### poster_download()

Источник: `versions/prepared-media-audio-v1/app.py:3213`; тело до строки 3233.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/posters/download', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `conn.close`, `conn.execute`, `data.get`, `fetchone`, `get_db`, `jsonify`, `len`, `logger.exception`, `request.get_json`, `save`, `socketio.emit`, `str`, `strip`.

### serve_poster(filename)

Источник: `versions/prepared-media-audio-v1/app.py:3236`; тело до строки 3237.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/posters/<path:filename>')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `send_from_directory`.

### current_shared_state()

Источник: `versions/prepared-media-audio-v1/app.py:3244`; тело до строки 3250.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `conn.close`, `conn.execute`, `dict`, `fetchall`, `get_db`.

### announce_song(file)

Источник: `versions/prepared-media-audio-v1/app.py:3252`; тело до строки 3259.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `_player_state.update`, `conn.close`, `conn.execute`, `dict`, `fetchone`, `get_db`, `socketio.emit`.

### ws_connect()

Источник: `versions/prepared-media-audio-v1/app.py:3264`; тело до строки 3266.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `socketio.on('connect')`.

Статические вызовы (включая вложенные callbacks): `current_shared_state`, `emit`, `logger.info`, `socketio.on`.

### ws_disconnect()

Источник: `versions/prepared-media-audio-v1/app.py:3269`; тело до строки 3270.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `socketio.on('disconnect')`.

Статические вызовы (включая вложенные callbacks): `logger.info`, `socketio.on`.

### ws_search_sync(data)

Источник: `versions/prepared-media-audio-v1/app.py:3273`; тело до строки 3278.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `socketio.on('search_sync')`.

Статические вызовы (включая вложенные callbacks): `emit`, `get`, `socketio.on`, `str`.

### serve_socket_io()

Источник: `versions/prepared-media-audio-v1/app.py:3282`; тело до строки 3283.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/socket.io.min.js')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `send_from_directory`.

### wifi_scan()

Источник: `versions/prepared-media-audio-v1/app.py:3288`; тело до строки 3295.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/wifi/scan')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `jsonify`, `logger.exception`, `str`, `wifi_network.scan_networks`.

### wifi_connect()

Источник: `versions/prepared-media-audio-v1/app.py:3299`; тело до строки 3300.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/wifi/connect', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `_wifi_connect_request`, `app.route`.

### wifi_status()

Источник: `versions/prepared-media-audio-v1/app.py:3304`; тело до строки 3309.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/wifi/status')`.

Статические вызовы (включая вложенные callbacks): `app.route`, `bool`, `jsonify`, `state.get`, `wifi_network.read_status`.

### bgm_startup_fix()

Источник: `versions/prepared-media-audio-v1/app.py:3312`; тело до строки 3330.

Перезапуск первого трека + установка сохранённой громкости через 3 сек

Статические вызовы (включая вложенные callbacks): `_sock.socket`, `logger.info`, `logger.warning`, `s.close`, `s.connect`, `s.recv`, `s.sendall`, `s.settimeout`, `str`, `time.sleep`, `vol_cmd.encode`.

### get_stats()

Источник: `versions/prepared-media-audio-v1/app.py:3334`; тело до строки 3342.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `app.route('/api/stats', methods=['GET'])`.

Статические вызовы (включая вложенные callbacks): `app.route`, `get_media_stats`, `jsonify`, `round`.

### _media_snapshot()

Источник: `versions/prepared-media-audio-v1/app.py:3348`; тело до строки 3357.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `allowed_file`, `e.is_file`, `e.stat`, `logger.warning`, `os.path.ismount`, `os.scandir`, `sorted`, `tuple`.

### _media_watcher()

Источник: `versions/prepared-media-audio-v1/app.py:3359`; тело до строки 3377.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `_media_snapshot`, `any`, `broadcast_state`, `logger.exception`, `refresh_database`, `result.values`, `socketio.emit`, `time.monotonic`, `time.sleep`.

## versions/prepared-media-audio-v1/karaoke_media_optimizer.py

### Класс Cancelled

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:22`. 

### safe_name(name)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:26`; тело до строки 32.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `any`, `isinstance`, `len`, `name.startswith`, `name.strip`, `ord`, `os.fsencode`.

### names(name)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:35`; тело до строки 44.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `join`, `len`, `part.split`, `re.split`.

### identity(path)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:47`; тело до строки 51.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `path.is_file`, `path.is_symlink`, `path.stat`.

### digest(path, cancelled=lambda: False)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:54`; тело до строки 67.

Полный SHA256 с отменой и проверкой identity до/после чтения.

Статические вызовы (включая вложенные callbacks): `Cancelled`, `RuntimeError`, `cancelled`, `h.hexdigest`, `h.update`, `hashlib.sha256`, `identity`, `path.open`, `stream.read`.

### rate(value)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:70`; тело до строки 75.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Fraction`, `str`.

### sync_directory(path)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:78`; тело до строки 83.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `os.close`, `os.fsync`, `os.open`.

### probe(path)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:86`; тело до строки 133.

ffprobe streams/format/PTS; разрешение, fps, SAR, rotation, поддерживаемость.

Статические вызовы (включая вложенные callbacks): `Fraction`, `RuntimeError`, `all`, `data.get`, `float`, `get`, `int`, `item.get`, `json.loads`, `len`, `line.split`, `line.strip`, `max`, `min`, `packets.stdout.decode`, `proc.stderr.decode`, `rate`, `round`, `s.get`, `set`, `sorted`, `splitlines`, `str`, `subprocess.run`, `sum`, `v.get`, `zip`.

### Класс MediaOptimizer

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:136`. 

### MediaOptimizer.__init__(self, root, db_path, mount_root='/mnt/usb_disk', is_playing=lambda: False, changed=lambda: None)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:137`; тело до строки 146.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `threading.Event`, `threading.RLock`.

### MediaOptimizer.repairing(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:149`; тело до строки 150.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `property`.

Статические вызовы (включая вложенные callbacks): `bool`.

### MediaOptimizer.check_mount(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:152`; тело до строки 159.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `os.path.ismount`, `self.mount.is_symlink`, `self.mount.resolve`, `self.mount.stat`, `self.root.is_dir`, `self.root.is_symlink`, `self.root.resolve`, `self.root.stat`, `self.storage.is_symlink`.

### MediaOptimizer.write_json(self, path, data)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:161`; тело до строки 173.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `json.dump`, `os.close`, `os.fsync`, `os.open`, `os.replace`, `path.with_name`, `self.check_mount`, `stream.fileno`, `stream.flush`, `temporary.open`.

### MediaOptimizer.connect(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:175`; тело до строки 178.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.db_path.as_uri`, `sqlite3.connect`.

### MediaOptimizer.path(self, name)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:180`; тело до строки 183.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `isinstance`.

### MediaOptimizer.load(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:185`; тело до строки 213.

Проверяет HDD, читает job и восстанавливает journals перед refresh.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `any`, `current.exists`, `current.read_text`, `exists`, `folder.glob`, `journal.read_text`, `json.loads`, `re.fullmatch`, `read_text`, `self.check_mount`, `self.finalize`, `self.job.update`, `self.persist`, `self.storage.exists`, `self.storage.iterdir`, `self.storage.mkdir`, `self.undo`, `sorted`, `write_text`.

### MediaOptimizer.persist(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:215`; тело до строки 217.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.write_json`.

### MediaOptimizer.status(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:219`; тело до строки 228.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `copy.deepcopy`, `key.startswith`, `list`, `self.load`.

### MediaOptimizer.progress(self, **changes)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:230`; тело до строки 233.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.job.update`, `self.persist`.

### MediaOptimizer.check_cancel(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:235`; тело до строки 237.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Cancelled`, `self.cancel_event.is_set`.

### MediaOptimizer.launch(self, target)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:239`; тело до строки 252.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.cancel_event.clear`, `self.job.update`, `self.progress`, `self.thread.start`, `str`, `target`, `threading.Thread`.

### MediaOptimizer.launch.worker()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:240`; тело до строки 249.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.job.update`, `self.progress`, `str`, `target`.

### MediaOptimizer.start_scan(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:254`; тело до строки 270.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `dict`, `mkdir`, `self.check_mount`, `self.launch`, `self.load`, `self.persist`, `self.write_json`, `shutil.which`, `uuid.uuid4`.

### MediaOptimizer.scan(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:272`; тело до строки 358.

Проверяет имена и видео, точные/возможные дубли, формирует read-only отчёт.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `any`, `append`, `by_hash.setdefault`, `by_hash.values`, `casefold`, `dict`, `digest`, `enumerate`, `identity`, `issue`, `join`, `len`, `names`, `p.is_file`, `p.is_symlink`, `p.name.casefold`, `path.suffix.lower`, `probe`, `rows.append`, `s.get`, `safe_name`, `self.check_cancel`, `self.check_mount`, `self.path`, `self.progress`, `self.root.iterdir`, `similar.setdefault`, `similar.values`, `sizes.setdefault`, `sizes.values`, `sorted`, `str`, `unicodedata.normalize`.

### MediaOptimizer.cancel(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:360`; тело до строки 366.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.cancel_event.set`, `self.persist`.

### MediaOptimizer.idle(self)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:368`; тело до строки 370.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `self.is_playing`.

### MediaOptimizer.apply(self, job_id, actions, confirmed)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:372`; тело до строки 423.

Проверяет явный выбор/подтверждение и запускает исправление.

Статические вызовы (включая вложенные callbacks): `Path`, `RuntimeError`, `ValueError`, `a.get`, `action.get`, `any`, `copy.deepcopy`, `dict`, `exists`, `isinstance`, `len`, `names`, `rows.get`, `safe_name`, `seen.add`, `selected.append`, `self.check_mount`, `self.idle`, `self.launch`, `self.load`, `self.progress`, `self.repair`, `set`, `shutil.which`, `suffix.lower`, `targets.add`.

### MediaOptimizer.check_row(self, row)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:425`; тело до строки 433.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `digest`, `identity`, `row.get`, `self.check_mount`, `self.path`.

### MediaOptimizer.encode(self, source, destination, info)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:435`; тело до строки 503.

ffmpeg H264 FullHD24, сохранение дорожек, контроль результата/места.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `abs`, `decode`, `filters.append`, `int`, `join`, `max`, `min`, `open`, `probe`, `process.kill`, `process.poll`, `process.terminate`, `process.wait`, `progress_file.exists`, `progress_file.open`, `progress_file.stat`, `re.findall`, `s.get`, `self.check_cancel`, `self.check_mount`, `self.progress`, `shutil.disk_usage`, `shutil.which`, `source.stat`, `str`, `stream.get`, `stream.read`, `stream.seek`, `subprocess.Popen`, `sum`, `time.monotonic`, `time.sleep`.

### MediaOptimizer.finalize(self, folder, entry, verify=True)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:505`; тело до строки 517.

Заканчивает подтверждённую замену, фиксирует done.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `digest`, `entry.get`, `identity`, `self.check_mount`, `self.path`, `self.write_json`, `source.exists`, `source.unlink`, `str`, `sync_directory`, `target.exists`.

### MediaOptimizer.undo(self, folder, entry)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:519`; тело до строки 550.

Восстанавливает затронутые файлы/записи по проверенному журналу.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `backup.exists`, `closing`, `db.commit`, `db.execute`, `digest`, `entry.get`, `os.fsync`, `os.replace`, `path.exists`, `self.check_mount`, `self.connect`, `self.path`, `self.write_json`, `shutil.copyfile`, `str`, `stream.fileno`, `sync_directory`, `target.exists`, `target.unlink`, `temporary.open`, `temporary.unlink`, `tuple`.

### MediaOptimizer.commit(self, row, action, folder, source_sha, encoded=None)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:552`; тело до строки 643.

Оригинал, журнал, согласованная файловая/SQLite транзакция.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `action.get`, `backup.open`, `closing`, `db.commit`, `db.execute`, `db.rollback`, `dict`, `digest`, `dst.fileno`, `dst.flush`, `dst.write`, `fetchone`, `identity`, `names`, `os.fsync`, `os.link`, `os.replace`, `os.sync`, `self.check_cancel`, `self.check_row`, `self.connect`, `self.finalize`, `self.idle`, `self.path`, `self.undo`, `self.write_json`, `shutil.disk_usage`, `source.open`, `source.stat`, `src.read`, `str`, `stream.fileno`, `sync_directory`, `target.exists`, `target.open`.

### MediaOptimizer.repair(self, actions)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:645`; тело до строки 679.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `action.get`, `append`, `dict`, `encoded.exists`, `encoded.unlink`, `enumerate`, `folder.mkdir`, `len`, `self.changed`, `self.check_cancel`, `self.check_mount`, `self.check_row`, `self.commit`, `self.encode`, `self.persist`, `self.progress`, `str`, `sum`.

### create_blueprint(manager)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:682`; тело до строки 718.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Blueprint`, `Path`, `ValueError`, `body.get`, `bp.route`, `call`, `isinstance`, `jsonify`, `manager.apply`, `manager.cancel`, `manager.start_scan`, `manager.status`, `operation`, `request.get_json`, `send_from_directory`, `str`.

### create_blueprint.page()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:687`; тело до строки 688.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/video-optimization')`.

Статические вызовы (включая вложенные callbacks): `Path`, `bp.route`, `send_from_directory`.

### create_blueprint.call(operation)

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:690`; тело до строки 696.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `jsonify`, `operation`, `str`.

### create_blueprint.status()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:699`; тело до строки 700.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/api/media-optimizer/status')`.

Статические вызовы (включая вложенные callbacks): `bp.route`, `call`, `jsonify`, `manager.status`.

### create_blueprint.scan()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:703`; тело до строки 704.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/api/media-optimizer/scan', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `bp.route`, `call`, `jsonify`, `manager.start_scan`.

### create_blueprint.cancel()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:707`; тело до строки 708.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/api/media-optimizer/cancel', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `bp.route`, `call`, `jsonify`, `manager.cancel`.

### create_blueprint.apply()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:711`; тело до строки 717.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/api/media-optimizer/apply', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `ValueError`, `body.get`, `bp.route`, `call`, `isinstance`, `jsonify`, `manager.apply`, `request.get_json`.

### create_blueprint.apply.operation()

Источник: `versions/prepared-media-audio-v1/karaoke_media_optimizer.py:712`; тело до строки 716.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `body.get`, `isinstance`, `jsonify`, `manager.apply`, `request.get_json`.

## versions/prepared-media-audio-v1/karaoke_audio_output.py

### selected_mode()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:19`; тело до строки 26.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `SETTINGS.read_text`, `get`, `json.loads`.

### player_args()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:29`; тело до строки 30.

Аргументы ALSA по сохранённому стабильному ID карты.

Статические вызовы (включая вложенные callbacks): `selected_mode`.

### wait_ready(path, timeout=3)

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:33`; тело до строки 43.

Согласует запуск нового mpv с сохранённым выбором выхода.

Статические вызовы (включая вложенные callbacks): `ipc`, `selected_mode`, `time.monotonic`, `time.sleep`.

### cards()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:46`; тело до строки 47.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `glob`, `p.read_text`, `strip`.

### ipc(path, command)

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:50`; тело до строки 65.

mpv JSON IPC с request_id и контролем ответа.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `client.connect`, `client.makefile`, `client.sendall`, `client.settimeout`, `encode`, `json.dumps`, `json.loads`, `range`, `reader.readline`, `response.get`, `socket.socket`, `str`.

### save_mode(mode)

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:68`; тело до строки 78.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `json.dump`, `os.fdopen`, `os.fsync`, `os.path.exists`, `os.replace`, `os.unlink`, `stream.fileno`, `stream.flush`, `tempfile.mkstemp`.

### status()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:81`; тело до строки 99.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `all`, `cards`, `errors.append`, `ipc`, `issubset`, `join`, `os.path.exists`, `players.append`, `selected_mode`, `str`.

### set_analog_only(value)

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:102`; тело до строки 137.

Переключает оба mpv, проверяет реальные выходы, откатывает частичный отказ.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `ValueError`, `cards`, `changed.append`, `ipc`, `join`, `os.path.exists`, `reversed`, `rollback_errors.append`, `save_mode`, `status`, `str`, `type`.

### create_blueprint()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:140`; тело до строки 162.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Blueprint`, `ValueError`, `bp.route`, `isinstance`, `jsonify`, `request.get_json`, `set`, `set_analog_only`, `status`, `str`.

### create_blueprint.get_output()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:145`; тело до строки 149.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/api/audio/output')`.

Статические вызовы (включая вложенные callbacks): `bp.route`, `jsonify`, `status`, `str`.

### create_blueprint.set_output()

Источник: `versions/prepared-media-audio-v1/karaoke_audio_output.py:152`; тело до строки 161.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `bp.route('/api/audio/output', methods=['POST'])`.

Статические вызовы (включая вложенные callbacks): `ValueError`, `bp.route`, `isinstance`, `jsonify`, `request.get_json`, `set`, `set_analog_only`, `str`.

## versions/prepared-media-audio-v1/wifi/__init__.py

## versions/prepared-media-audio-v1/wifi/auto-manager.py

### run(args, timeout=20)

Источник: `versions/prepared-media-audio-v1/wifi/auto-manager.py:16`; тело до строки 25.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `subprocess.run`.

### connection()

Источник: `versions/prepared-media-audio-v1/wifi/auto-manager.py:27`; тело до строки 32.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `r.stdout.strip`, `run`.

### log(message)

Источник: `versions/prepared-media-audio-v1/wifi/auto-manager.py:34`; тело до строки 39.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `f.write`, `open`, `time.strftime`.

### status(mode, network='')

Источник: `versions/prepared-media-audio-v1/wifi/auto-manager.py:41`; тело до строки 49.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `int`, `json.dump`, `open`, `os.replace`, `time.time`.

## versions/prepared-media-audio-v1/wifi/captive.py

### Класс _PortalServer

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:17`. 

### Класс CaptivePortal

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:23`. Idempotent, non-blocking start and graceful stop of an AP-only listener.

### CaptivePortal.__init__(self, bind_address='192.168.100.1', port=80, target_url='http://192.168.100.1:8080/wifi/setup')

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:26`; тело до строки 43.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `any`, `ipaddress.IPv4Address`, `isinstance`, `str`, `threading.Lock`, `urlsplit`.

### CaptivePortal.running(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:46`; тело до строки 48.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `property`.

Статические вызовы (включая вложенные callbacks): `self._thread.is_alive`.

### CaptivePortal.bound_port(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:51`; тело до строки 54.

The actual listener port (useful for port=0 in isolated tests).

Декораторы: `property`.

### CaptivePortal.start(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:56`; тело до строки 122.

Return True while listening, or False with last_error on failure.

Статические вызовы (включая вложенные callbacks): `_PortalServer`, `encode`, `html.escape`, `len`, `self._redirect`, `self._server.server_close`, `self._thread.is_alive`, `self.end_headers`, `self.request.settimeout`, `self.send_header`, `self.send_response`, `self.wfile.write`, `server.server_close`, `setup`, `str`, `super`, `thread.start`, `threading.Thread`, `type`.

### Класс CaptivePortal.start.Handler

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:73`. 

### CaptivePortal.start.Handler.setup(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:76`; тело до строки 78.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.request.settimeout`, `setup`, `super`.

### CaptivePortal.start.Handler._redirect(self, head_only=False)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:80`; тело до строки 94.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `len`, `self.end_headers`, `self.send_header`, `self.send_response`, `self.wfile.write`, `str`.

### CaptivePortal.start.Handler.do_GET(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:96`; тело до строки 97.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self._redirect`.

### CaptivePortal.start.Handler.do_HEAD(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:99`; тело до строки 100.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self._redirect`.

### CaptivePortal.start.Handler.log_message(self, format, *args)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:102`; тело до строки 104.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

### CaptivePortal.stop(self)

Источник: `versions/prepared-media-audio-v1/wifi/captive.py:124`; тело до строки 135.

Stop accepting requests and release the bound port; safe to repeat.

Статические вызовы (включая вложенные callbacks): `server.server_close`, `server.shutdown`, `thread.is_alive`, `thread.join`, `threading.current_thread`.

## versions/prepared-media-audio-v1/wifi/connect-worker.py

### finish(job_id, status, message, **extra)

Источник: `versions/prepared-media-audio-v1/wifi/connect-worker.py:11`; тело до строки 13.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `net.boot_id`, `net.update_job`, `time.monotonic`.

### connect(manager, job_id, request)

Источник: `versions/prepared-media-audio-v1/wifi/connect-worker.py:16`; тело до строки 51.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `arguments.extend`, `finish`, `manager.run`, `manager.station`, `net.candidate_name`, `net.candidate_uuid`, `net.cleanup_candidate`, `net.profile_saved`, `net.update_job`, `request.pop`.

### reset(manager, job_id, request)

Источник: `versions/prepared-media-audio-v1/wifi/connect-worker.py:54`; тело до строки 69.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `finish`, `manager.device`, `manager.home_profiles`, `manager.run`, `request.get`.

### perform(job_id, manager=None)

Источник: `versions/prepared-media-audio-v1/wifi/connect-worker.py:72`; тело до строки 96.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `ValueError`, `connect`, `finish`, `isinstance`, `manager.usb`, `net.NetworkManager`, `net.boot_id`, `net.file_lock`, `net.load_json`, `net.update_job`, `net.valid_job_id`, `os.getpid`, `request.get`, `request.pop`, `request_path.unlink`, `reset`, `time.monotonic`.

### interrupted(signum, frame)

Источник: `versions/prepared-media-audio-v1/wifi/connect-worker.py:99`; тело до строки 100.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `InterruptedError`.

## versions/prepared-media-audio-v1/wifi/control_qr.py

### _invalidate()

Источник: `versions/prepared-media-audio-v1/wifi/control_qr.py:15`; тело до строки 19.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

### control_url(state=None)

Источник: `versions/prepared-media-audio-v1/wifi/control_qr.py:22`; тело до строки 38.

Возвращает URL только при здоровом контроллере и допустимом домашнем IPv4.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `_invalidate`, `int`, `ipaddress.IPv4Address`, `isinstance`, `network.read_status`, `state.get`, `str`.

### _chunk(kind, data)

Источник: `versions/prepared-media-audio-v1/wifi/control_qr.py:41`; тело до строки 43.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `len`, `struct.pack`, `zlib.crc32`.

### _png(url)

Источник: `versions/prepared-media-audio-v1/wifi/control_qr.py:46`; тело до строки 65.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `QRCode`, `_chunk`, `bytes`, `code.add_data`, `code.get_matrix`, `code.make`, `join`, `len`, `range`, `rows.extend`, `struct.pack`, `sum`, `zlib.compress`.

### control_image(state=None, expected_ip=None)

Источник: `versions/prepared-media-audio-v1/wifi/control_qr.py:68`; тело до строки 78.

Генерирует/кэширует PNG по URL; отвергает устаревший expected_ip.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `_png`, `control_url`, `str`.

### get_control_qr(state=None, expected_ip=None)

Источник: `versions/prepared-media-audio-v1/wifi/control_qr.py:81`; тело до строки 82.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `control_image`.

## versions/prepared-media-audio-v1/wifi/monitor.py

### Класс Policy

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:14`. 

### Policy.__init__(self)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:15`; тело до строки 18.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

### Policy.decide(self, now, connected, ap_active, busy=False, grace_until=0)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:20`; тело до строки 35.

Чистая политика 30 с отсутствия, grace и стабильного home подключения.

Статические вызовы (включая вложенные callbacks): `int`, `max`.

### Класс Controller

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:38`. 

### Controller.__init__(self, manager=None, portal=None)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:39`; тело до строки 45.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `CaptivePortal`, `Policy`, `net.NetworkManager`.

### Controller.fail_job(self, job, message)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:47`; тело до строки 50.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `net.boot_id`, `net.update_job`, `time.monotonic`, `unlink`.

### Controller.recover_job(self, job)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:52`; тело до строки 63.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `net.boot_id`, `net.candidate_name`, `net.candidate_uuid`, `net.cleanup_candidate`, `net.update_job`, `self.fail_job`, `self.manager.property`, `self.manager.start_ap`, `self.manager.station`, `time.monotonic`.

### Controller.reconcile(self)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:65`; тело до строки 107.

Согласует job/worker/lock/boot, восстанавливает прерванные операции.

Статические вызовы (включая вложенные callbacks): `Path`, `arguments.read_bytes`, `encode`, `float`, `job.get`, `net.boot_id`, `net.current_job`, `net.operation_busy`, `net.update_job`, `os.kill`, `self.fail_job`, `self.manager.start_ap`, `self.recover_job`, `self.worker.poll`, `split`, `str`, `subprocess.Popen`, `time.monotonic`, `time.time`, `with_name`.

### Controller.tick(self)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:109`; тело до строки 143.

Один цикл роли USB, работы, политики, captive и публикации status.

Статические вызовы (включая вложенные callbacks): `bool`, `dict`, `int`, `job.get`, `net.boot_id`, `net.operation_busy`, `net.write_json`, `self.last_state.pop`, `self.manager.ensure_usb_role`, `self.manager.start_ap`, `self.manager.station`, `self.manager.stop_ap`, `self.manager.usb`, `self.policy.decide`, `self.portal.start`, `self.portal.stop`, `self.reconcile`, `time.monotonic`, `time.time`.

### main()

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:146`; тело до строки 159.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Controller`, `controller.portal.stop`, `controller.tick`, `net.prepare_state`, `signal.signal`, `time.sleep`.

### main.stop(signum, frame)

Источник: `versions/prepared-media-audio-v1/wifi/monitor.py:149`; тело до строки 150.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

## versions/prepared-media-audio-v1/wifi/network.py

### prepare_state()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:26`; тело до строки 29.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `directory.chmod`, `directory.mkdir`.

### write_json(path, data)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:32`; тело до строки 42.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `json.dump`, `os.fdopen`, `os.open`, `os.replace`, `path.with_name`, `target.write`, `temporary.unlink`, `uuid.uuid4`.

### load_json(path, default=None)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:45`; тело до строки 49.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `json.loads`, `read_text`.

### file_lock(path, blocking=True)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:53`; тело до строки 57.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `contextmanager`.

Статические вызовы (включая вложенные callbacks): `fcntl.flock`, `os.fdopen`, `os.open`.

### operation_busy()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:60`; тело до строки 65.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `file_lock`.

### boot_id()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:68`; тело до строки 69.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `read_text`, `strip`.

### valid_job_id(job_id)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:72`; тело до строки 75.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `isinstance`, `re.fullmatch`.

### read_job(job_id)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:78`; тело до строки 85.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `ValueError`, `isinstance`, `job.get`, `load_json`, `valid_job_id`.

### current_job()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:88`; тело до строки 94.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `isinstance`, `job.get`, `load_json`, `pointer.get`, `re.fullmatch`.

### update_job(job_id, **changes)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:97`; тело до строки 102.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `int`, `job.update`, `load_json`, `time.time`, `valid_job_id`, `write_json`.

### read_status()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:105`; тело до строки 127.

Дополняет статус, проверяет heartbeat <=12 с и вычисляет busy.

Статические вызовы (включая вложенные callbacks): `bool`, `current_job`, `dict`, `isinstance`, `job.get`, `load_json`, `state.get`, `state.setdefault`, `state.update`, `time.time`.

### admission_lock()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:131`; тело до строки 136.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Декораторы: `contextmanager`.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `file_lock`.

### _submit(kind, **private)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:139`; тело до строки 162.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `admission_lock`, `boot_id`, `current_job`, `dict`, `int`, `job_path.unlink`, `prepare_state`, `previous.get`, `read_status`, `request_path.unlink`, `time.time`, `uuid.uuid4`, `write_json`.

### submit_connection(ssid, password)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:165`; тело до строки 181.

Проверяет SSID/пароль и создаёт приватную заявку подключения.

Статические вызовы (включая вложенные callbacks): `ValueError`, `_submit`, `any`, `isinstance`, `len`, `password.encode`, `re.fullmatch`, `ssid.encode`.

### request_reset(confirmed)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:184`; тело до строки 187.

Требует explicit confirmed=true, создаёт заявку сброса.

Статические вызовы (включая вложенные callbacks): `ValueError`, `_submit`.

### split_nmcli(line)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:190`; тело до строки 207.

Split escaped nmcli terse output, preserving colons/backslashes in SSIDs.

Статические вызовы (включая вложенные callbacks): `current.append`, `fields.append`, `join`.

### usb_interface()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:210`; тело до строки 225.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `RuntimeError`, `glob`, `len`, `link.resolve`, `lower`, `matches.extend`, `read_text`, `resolve`, `strip`, `tuple`.

### profile_saved(profile_uuid)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:228`; тело до строки 241.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `configparser.RawConfigParser`, `glob`, `parser.get`, `parser.read`, `path.is_file`.

### candidate_uuid(job_id)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:244`; тело до строки 245.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `str`, `uuid.UUID`, `valid_job_id`.

### candidate_name(job_id)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:248`; тело до строки 249.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `valid_job_id`.

### cleanup_candidate(manager, job_id)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:252`; тело до строки 261.

Delete only the deterministic UUID and full profile ID owned by this job.

Статические вызовы (включая вложенные callbacks): `candidate_name`, `candidate_uuid`, `manager.property`, `manager.run`.

### Класс NetworkManager

Источник: `versions/prepared-media-audio-v1/wifi/network.py:264`. 

### NetworkManager.__init__(self)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:265`; тело до строки 266.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

### NetworkManager.run(self, *arguments, timeout=15)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:268`; тело до строки 276.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `subprocess.run`.

### NetworkManager.property(self, profile_uuid, key)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:278`; тело до строки 280.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `rstrip`, `self.run`.

### NetworkManager.profile(self, profile_uuid)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:282`; тело до строки 290.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.property`.

### NetworkManager.device(self, interface)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:292`; тело до строки 308.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `addresses.append`, `dict`, `fields.get`, `fields.items`, `ipaddress.ip_interface`, `key.startswith`, `line.split`, `output.splitlines`, `self.run`, `split`, `str`.

### NetworkManager.station(self, require_saved=True)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:310`; тело до строки 321.

Проверяет сохранённый station profile, активный UUID и IPv4.

Статические вызовы (включая вложенные callbacks): `bool`, `profile_saved`, `self.device`, `self.profile`, `state.update`.

### NetworkManager.usb(self)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:323`; тело до строки 328.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `bool`, `self.device`, `state.update`, `usb_interface`.

### NetworkManager.ensure_usb_role(self)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:330`; тело до строки 336.

Исключает автоматический station-role на USB, не вмешиваясь во wlan0.

Статические вызовы (включая вложенные callbacks): `self.run`, `self.usb`.

### NetworkManager.start_ap(self)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:338`; тело до строки 346.

Активирует только заданный AP UUID на найденном USB.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `self.ensure_usb_role`, `self.run`, `self.usb`.

### NetworkManager.stop_ap(self)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:348`; тело до строки 351.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `self.run`, `self.usb`.

### NetworkManager.home_profiles(self)

Источник: `versions/prepared-media-audio-v1/wifi/network.py:353`; тело до строки 366.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `len`, `output.splitlines`, `profiles.append`, `self.profile`, `self.run`, `split_nmcli`.

### scan_networks()

Источник: `versions/prepared-media-audio-v1/wifi/network.py:369`; тело до строки 389.

Сканирует только wlan0 под operation lock и нормализует список SSID.

Статические вызовы (включая вложенные callbacks): `NetworkManager`, `RuntimeError`, `file_lock`, `int`, `len`, `networks.get`, `networks.values`, `output.splitlines`, `run`, `signal.isdigit`, `sorted`, `split_nmcli`.

## sources/rtl8188eus-research/build_for_x96q.py

### sha(path)

Источник: `sources/rtl8188eus-research/build_for_x96q.py:26`; тело до строки 28.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `hashlib.file_digest`, `hexdigest`, `open`.

### config_values(path)

Источник: `sources/rtl8188eus-research/build_for_x96q.py:31`; тело до строки 39.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `line.endswith`, `line.split`, `line.startswith`, `read_text`, `splitlines`.

### main()

Источник: `sources/rtl8188eus-research/build_for_x96q.py:42`; тело до строки 153.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `RuntimeError`, `archive.open`, `argparse.ArgumentParser`, `cached.is_file`, `compiler_values.update`, `config_values`, `flags.append`, `gzip.decompress`, `lab.chmod`, `line.strip`, `log.flush`, `log.write`, `module.chmod`, `name.startswith`, `open`, `original.get`, `original.keys`, `parser.add_argument`, `parser.parse_args`, `path.is_absolute`, `platform.machine`, `platform.release`, `prepared.get`, `prepared.keys`, `print`, `read_text`, `repr`, `resolve`, `run`, `sha`, `shutil.copyfile`, `shutil.copyfileobj`, `shutil.disk_usage`, `shutil.which`, `split`, `splitlines`, `str`, `strip`, `subprocess.check_output`, `subprocess.run`, `symbol_file.read_bytes`, `tarfile.open`, `tempfile.mkdtemp`, `urllib.request.urlopen`, `with_name`, `write_bytes`.

### main.run(command, cwd=lab)

Источник: `sources/rtl8188eus-research/build_for_x96q.py:66`; тело до строки 69.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `log.flush`, `log.write`, `repr`, `subprocess.run`.

## sources/rtl8188eus-research/trial_bind_usb.py

### command(arguments, *, check=True, timeout=15)

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:30`; тело до строки 36.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `repr`, `subprocess.run`.

### bound_driver(usb_path)

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:39`; тело до строки 43.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `resolve`.

### check_usb_identity(usb_path)

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:46`; тело до строки 49.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `lower`, `read_text`, `strip`.

### check_ssh_route(client)

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:52`; тело до строки 62.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `address.get`, `any`, `command`, `interface.get`, `json.loads`, `route.get`.

### wait_for_usb_interface(usb_path, timeout=12)

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:65`; тело до строки 74.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `glob`, `len`, `repr`, `sorted`, `time.monotonic`, `time.sleep`.

### suppress_usb_autoconnect(usb_path)

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:77`; тело до строки 104.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `command`, `int`, `state_result.stdout.strip`, `state_text.split`, `str`, `time.monotonic`, `time.sleep`, `wait_for_usb_interface`.

### main()

Источник: `sources/rtl8188eus-research/trial_bind_usb.py:171`; тело до строки 275.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `RuntimeError`, `argparse.ArgumentParser`, `bound_driver`, `check_ssh_route`, `check_usb_identity`, `command`, `exists`, `info.splitlines`, `int`, `ipaddress.ip_address`, `is_dir`, `join`, `json.dumps`, `lab.chmod`, `len`, `line.strip`, `modes.append`, `old_state.split`, `os.environ.get`, `os.geteuid`, `parser.add_argument`, `parser.parse_args`, `platform.machine`, `platform.release`, `print`, `re.fullmatch`, `read_text`, `repr`, `resolve`, `rollback.chmod`, `rollback.write_text`, `shutil.which`, `split`, `stdout.strip`, `str`, `strip`, `subprocess.run`, `suppress_usb_autoconnect`, `tempfile.mkdtemp`, `uuid.uuid4`, `wait_for_usb_interface`, `write_text`.

## sources/rtl8188eus-research/permanent/install_on_x96q.py

### run(*args, check=True, timeout=30)

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:39`; тело до строки 44.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `subprocess.run`.

### setting(key, uuid=PROFILE)

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:47`; тело до строки 49.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `run`, `stdout.rstrip`.

### profile_files(uuid)

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:52`; тело до строки 65.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `configparser.RawConfigParser`, `file.is_file`, `found.append`, `glob`, `parser.get`, `parser.read`.

### check_ssh()

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:68`; тело до строки 75.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `any`, `json.loads`, `len`, `os.environ.get`, `route.get`, `run`, `split`.

### modify(values)

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:78`; тело до строки 82.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `arguments.extend`, `run`, `values.items`.

### main()

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:85`; тело до строки 188.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `CHANGES.items`, `MODULE.resolve`, `Path`, `RuntimeError`, `SOURCE.read_bytes`, `a.get`, `action`, `any`, `backup.chmod`, `check_ssh`, `chmod`, `cleanup`, `created.append`, `d.get`, `device.resolve`, `hashlib.sha256`, `hexdigest`, `json.dumps`, `json.loads`, `len`, `modify`, `os.geteuid`, `os.sync`, `path.unlink`, `platform.machine`, `platform.release`, `print`, `profile_files`, `read_text`, `resolve`, `reversed`, `rollback.chmod`, `run`, `selected.resolve`, `setting`, `shutil.copyfile`, `source.is_file`, `stdout.strip`, `str`, `strip`, `target.chmod`, `target.exists`, `target.is_symlink`, `target.parent.mkdir`, `tempfile.mkdtemp`, `tuple`, `write_text`.

### main.cleanup(label, action)

Источник: `sources/rtl8188eus-research/permanent/install_on_x96q.py:172`; тело до строки 176.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `action`, `print`.

## sources/rtl8188eus-research/permanent/rtl8188eu-bind.py

### run(*arguments)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:17`; тело до строки 18.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `subprocess.run`.

### identity(path)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:21`; тело до строки 23.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `lower`, `read_text`, `strip`, `tuple`.

### target()

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:26`; тело до строки 37.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `USB_BUS.glob`, `identity`, `len`, `link.resolve`, `matches.append`.

### driver(path)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:40`; тело до строки 44.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `resolve`.

### bind(path, name)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:47`; тело до строки 50.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `identity`, `write_text`.

### unbind(path, name)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:53`; тело до строки 56.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `driver`, `identity`, `write_text`.

### report(path)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:59`; тело до строки 64.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `driver`, `glob`, `len`, `print`, `run`, `sorted`.

### restore_old(path)

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:67`; тело до строки 86.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `bind`, `driver`, `identity`, `print`, `run`, `unbind`.

### main()

Источник: `sources/rtl8188eus-research/permanent/rtl8188eu-bind.py:89`; тело до строки 123.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `RuntimeError`, `bind`, `driver`, `fcntl.flock`, `hashlib.file_digest`, `hexdigest`, `module.open`, `open`, `platform.machine`, `platform.release`, `print`, `report`, `repr`, `restore_old`, `run`, `target`, `unbind`.

## sources/karaoke-wifi-integration/media-audio-v1/install.py

### sha(data)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:25`; тело до строки 26.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `hashlib.sha256`, `hexdigest`.

### run(*args)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:29`; тело до строки 30.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `subprocess.run`.

### restart()

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:33`; тело до строки 36.

Рестарт только сервера после проверки пустого эффективного ExecStartPre.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `run`, `strip`, `subprocess.check_output`.

### atomic(path, data, mode)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:39`; тело до строки 50.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `os.fchmod`, `os.fdopen`, `os.fsync`, `os.path.exists`, `os.replace`, `os.unlink`, `stream.fileno`, `stream.flush`, `stream.write`, `tempfile.mkstemp`.

### get(path)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:53`; тело до строки 56.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `opener.open`, `response.read`, `urllib.request.ProxyHandler`, `urllib.request.build_opener`.

### player_idle()

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:59`; тело до строки 74.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `client.connect`, `client.makefile`, `client.sendall`, `client.settimeout`, `json.loads`, `range`, `socket.socket`, `stream.readline`, `value.get`.

### unchanged(manifest)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:77`; тело до строки 81.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `items`, `path.is_symlink`, `path.read_bytes`, `sha`.

### health(manifest)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:84`; тело до строки 95.

Установочная проверка HTML/API/карт/Wi-Fi, без старта изменений видео.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `audio.get`, `get`, `json.loads`, `report.get`, `unchanged`, `wifi.get`.

### media_idle()

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:98`; тело до строки 113.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `Path`, `RuntimeError`, `exists`, `json.loads`, `path.read_text`, `re.fullmatch`, `read_text`, `report.parent.glob`, `report.read_text`, `storage.exists`.

### restore(folder, manifest)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:116`; тело до строки 123.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `atomic`, `os.sync`, `print`, `read_bytes`, `restart`, `stat`, `unlink`.

### main()

Источник: `sources/karaoke-wifi-integration/media-audio-v1/install.py:126`; тело до строки 232.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `DB.as_uri`, `MARKER.touch`, `MARKER.unlink`, `Path`, `RuntimeError`, `WRAPPER.read_bytes`, `WRAPPER.stat`, `ast.parse`, `atomic`, `data.items`, `exists`, `fetchall`, `folder.chmod`, `get`, `health`, `importlib.import_module`, `is_symlink`, `items`, `json.loads`, `len`, `media_idle`, `name.endswith`, `network.admission_lock`, `network.operation_busy`, `network.read_status`, `os.geteuid`, `os.path.ismount`, `os.sync`, `patch`, `patch_wrapper`, `path.is_symlink`, `player_idle`, `print`, `range`, `read_bytes`, `read_text`, `resolve`, `restart`, `restore`, `run`, `set`, `sha`, `shutil.copy2`, `shutil.which`, `source.backup`, `sqlite3.connect`, `stat`, `str`, `strip`, `subprocess.check_output`, `subprocess.run`, `sys.path.insert`, `target.execute`, `tempfile.mkdtemp`, `time.sleep`, `unchanged`.

## sources/karaoke-wifi-integration/media-audio-v1/parts.py

### replace_once(text, before, after)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/parts.py:168`; тело до строки 171.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `RuntimeError`, `text.count`, `text.replace`.

### patch(data)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/parts.py:174`; тело до строки 199.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `data.decode`, `replace_once`, `source.encode`.

### patch_wrapper(data)

Источник: `sources/karaoke-wifi-integration/media-audio-v1/parts.py:202`; тело до строки 207.

Реализация приведена в исходнике; назначение определяется именем, контекстом класса и вызываемыми операциями.

Статические вызовы (включая вложенные callbacks): `data.decode`, `replace_once`, `source.encode`.
