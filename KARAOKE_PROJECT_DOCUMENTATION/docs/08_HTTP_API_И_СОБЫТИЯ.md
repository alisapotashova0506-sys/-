# HTTP API и события

Полный перечень маршрутов с исходными строками приведён в автосправочнике 14. Здесь описаны основные контракты. Маршруты YouTube и карантина неполны, потому что файлы внешних blueprint отсутствуют. Страница основного приложения содержит старые и новые участки JavaScript; название функции в UI не гарантирует, что существует отдельная одноимённая Flask route.

## Wi-Fi

| Метод / URL | Вход | Выход / назначение |
|---|---|---|
| GET /api/karaoke-wifi-monitor | Нет | Полный status, controller_ok, busy, setup_url |
| GET /api/network_status | Нет | status, ip, ssid для старого UI |
| GET /api/wifi/status | Нет | connection, ip, connected, ap_active |
| GET /api/wifi/scan | Нет | networks: ssid, signal, security, in_use |
| POST /api/wifi/connect | JSON ssid,password | 202 ok,job_id; 400/403/409/503 при отказе |
| POST /api/wifi/portal-connect | Тот же JSON | Дополнительно требует активную AP |
| GET /api/wifi/job/<job_id> | 32 HEX job_id | type,status,message,ssid,ip,updated_at без пароля |
| POST /api/wifi/reset | {"confirmed":true} | 202 job_id либо отказ |
| GET /wifi/setup | Нет | Страница настройки |
| GET /wifi/setup-qr.png | Нет | PNG статического URL |
| GET /wifi/control-qr.png?ip=<ожидаемый ip> | query ip необязателен | PNG и X-Control-URL; 409 если адрес/статус устарел |

Статусы Wi-Fi job: queued, connecting, success, failed. У job status — состояние операции, а у monitor mode — состояние контроллера: это разные поля.

## Караоке и очередь

/play POST {file}; /search GET ?q=; /top_artists GET; /increment GET ?file=; /queue/add POST {song_id}; /queue/list GET; /queue/next GET; /queue/remove/<queue_id> DELETE; /queue/move POST {queue_id,direction:-1|1}; /queue/clear POST. /api/stop, /api/pause, /api/next — старые управляющие GET endpoints.

/queue/next извлекает элемент из очереди и возвращает song; /api/next — отдельная команда управления плеером. Их нельзя считать двумя названиями одной операции. Некоторые старые endpoints при ошибках возвращают JSON с error и HTTP 200; клиент должен проверять тело, а не только статус.

Файлы: /upload POST multipart file, /refresh_after_upload POST, /upload_poster POST, /upload_bgm POST, /api/files/list GET, /api/files/delete POST, /settings/refresh_db POST. /api/format_hdd POST — существующая разрушительная операция очистки; не использовать как проверку исправности. Точные поля файлового API смотрите в функции по ссылке справочника, прежде чем писать клиент.

Звук/BGM: /api/bgm/start, stop, volume, toggle, status; /api/video/volume. Здесь старые GET изменяют состояние; это не образец REST для нового внешнего сервиса.

## Новые endpoints подготовленного пакета

| Метод / URL | Вход | Выход |
|---|---|---|
| GET /video-optimization | Нет | HTML интерфейс |
| GET /api/media-optimizer/status | Нет | ok, job или null |
| POST /api/media-optimizer/scan | Нет | 202 ok,job_id |
| POST /api/media-optimizer/apply | job_id,actions,confirmed:true | 202 ok,job_id |
| POST /api/media-optimizer/cancel | Нет | ok; запрос остановки текущей работы |
| GET /api/audio/output | Нет | ok,mode,analog_only,available,players,verified,error |
| POST /api/audio/output | {"analog_only":true|false} | Тот же status либо 400/409 |

Примеры status row для оптимизации: id, name, size, issues[{kind,message}], proposed_name, video{width,height,fps,codec}, duplicates[file_id], possible_duplicates[names], can_transcode. Внутренние поля с префиксом '_' из публичного статуса исключаются. status.job содержит id,state,stage,current,total,processed,message,rows,results,error,cancel_requested.

## Socket.IO

Сервер принимает connect/disconnect и search_sync, рассылает обновления состояния/очереди, plays_update, song_started, song_ended и db_update. Автосправочник содержит все строковые события emit/on, найденные статически. UI может обновляться по Socket.IO и отдельным периодическим HTTP; устаревший браузер после обновления надо перезагрузить.

## Граница доступа

Wi-Fi mutations имеют проверку peer address. Это не общая аутентификация всего приложения: в основном Flask-коде нет единой авторизации пользователей для всех действий. Flask-SocketIO настроен с cors_allowed_origins='*'. Документация не утверждает, что приложение безопасно публиковать в интернете. Развёртывание в доверенной локальной сети и сетевую доступность надо рассматривать отдельно от наличия QR.
