# Проект X96Q — переписка и материалы

**Составлено:** 14 октября 2026 г.

> **О полноте:** документ объединяет доступные в текущем контексте сообщения, диагностические выводы и сведения о предшествующих этапах. Это **не дословный экспорт всей истории ChatGPT**: более ранние сообщения доступны только в виде сводки. Для полного дословного архива необходим экспорт исходного чата.

## 1. Исходные сведения о проекте (сводка предыдущих этапов)

- Устройство: X96Q v5.1, Armbian Debian Bookworm, ядро `6.6.44-current-sunxi64`.
- SSH: `root@192.168.1.102` через встроенный Wi-Fi (адрес может меняться).
- Сервер караоке: `karaoke-server.service`; приложение `/root/karaoke/app.py`.
- Менеджер YouTube: `/root/karaoke/karaoke_youtube_manager.py`.
- Страницы: `/root/karaoke/youtube_manager.html`, `/root/karaoke/youtube_search.html`.
- Медиа: `/mnt/usb_disk/karaoke_media`, около 1210 песен.
- Службы `zapret.service`, `bgutil-pot.service` критически важны. **Не останавливать, не перезапускать и не изменять `zapret.service`**: от него зависит YouTube. Не нарушать работу HDD, Wi-Fi и сервера караоке.
- Ранее встроенный драйвер `xradio_wlan` показывал сообщения `missed interrupt`.
- Требование к работе: безопасные блоки SSH-команд, резервные копии перед изменениями и возможность отката.

## 2. Цель проекта точки доступа

1. Дома приставка подключается к сохранённой сети, например `Alisa`, и управляется с телефона через локальную сеть.
2. При отсутствии сохранённой сети более примерно 30 секунд приставка должна включать собственную точку доступа `KARAOKE_SYSTEM`.
3. На экране караоке в левом верхнем углу должен появляться QR-код с надписью «Настроить Wi-Fi».
4. По QR-коду пользователь открывает страницу настройки, выбирает сеть и вводит пароль. При успешном подключении новая сеть сохраняется, временная точка доступа отключается.
5. Без интернета локальная библиотека песен на HDD должна работать, а управление возможно мышкой или телефоном, подключённым к `KARAOKE_SYSTEM`.
6. Сброс Wi-Fi должен требовать подтверждения.

## 3. Обнаружение USB Wi-Fi (из предшествующего диагностического вывода)

- `lsusb`: `0bda:8179 Realtek Semiconductor Corp. RTL8188EUS 802.11n Wireless Network Adapter`.
- Драйвер: `rtl8xxxu`; прошивка `rtlwifi/rtl8188eufw.bin` загружена успешно.
- USB-интерфейс: `wlxf0b040f7f699`, PHY `phy1`.
- Встроенный интерфейс: `wlan0`, PHY `phy0`, драйвер `xradio_wlan`.
- Роутер: `Alisa`, адрес шлюза `192.168.1.1`, канал 9 (2452 МГц).
- USB поддерживает 2,4 ГГц; по текущему драйверу режимы `managed`, `monitor` (без AP).
- Встроенный PHY поддерживает AP, а также заявляет комбинацию managed+AP на одном канале, но стабильность комбинации не проверена.
- В предыдущих журналах наблюдались переподключения USB-SATA моста JMicron `152d:2329`; без отдельного согласования HDD не трогать.

## 4. Диагностика сканирования сети Alisa

**Команда пользователя:**

```bash
echo "===== СКАНИРОВАНИЕ ЧЕРЕЗ USB WI-FI ====="
iw dev wlxf0b040f7f699 scan 2>&1 | grep -E 'SSID:|signal:|freq:' | head -90
echo "===== ПОДДЕРЖИВАЕМЫЕ ЧАСТОТЫ ====="
iw phy phy1 info | grep -A 18 'Frequencies:'
echo "===== ПРОВЕРКА ТЕКУЩЕГО ПОДКЛЮЧЕНИЯ ====="
iw dev wlan0 link
ip route get 1.1.1.1
```

**Ключевые результаты:**

- `SSID: Alisa`, `freq: 2452`, `signal: -35.00 dBm` при сканировании USB.
- Частоты USB: 2412–2472 МГц (каналы 1–13), 2484 МГц (канал 14, no IR).
- Встроенный Wi-Fi подключён к `Alisa`, BSSID `50:ff:20:4a:92:4b`, сигнал `-43 dBm`.
- Первоначальный маршрут: `1.1.1.1 via 192.168.1.1 dev wlan0 src 192.168.1.102`.

## 5. Проверка сетевого менеджера

**Выполненная команда:**

```bash
systemctl is-active NetworkManager
systemctl is-active systemd-networkd
systemctl is-active networking
nmcli -f NAME,UUID,TYPE,DEVICE connection show
nmcli device status
nmcli -f GENERAL.CONNECTION,GENERAL.DEVICE,IP4.ADDRESS,IP4.GATEWAY device show wlan0
ip -4 route
ls -la /etc/NetworkManager/system-connections/
ls -la /etc/systemd/network/
```

**Результаты:**

- `NetworkManager`: `active`; `systemd-networkd` и `networking`: `inactive`.
- Профиль `Alisa`, UUID `64825e49-6414-46eb-86e4-e0bc1c1e2145`, интерфейс `wlan0`.
- Другие профили: `KARAOKE_SYSTEM` (UUID `28752177-7ad8-44ec-9a38-0e32a29d42a7`), `ZZZZ`, `Wired connection 1`.
- `wlan0`: `192.168.1.102/24`, шлюз `192.168.1.1`, маршрут по умолчанию с метрикой `600`.
- USB на тот момент `disconnected`.

## 6. Создание профиля Alisa_USB и резервной копии

Пользователь выполнил командный блок с копированием `/etc/NetworkManager/system-connections` и клонированием профиля `Alisa` в `Alisa_USB`. Были заданы:

```bash
nmcli connection clone "Alisa" "Alisa_USB"
nmcli connection modify "Alisa_USB" \
  connection.interface-name "wlxf0b040f7f699" \
  802-11-wireless.ssid "Alisa" \
  connection.autoconnect yes \
  connection.autoconnect-priority 100 \
  ipv4.route-metric 100 \
  ipv6.route-metric 100
nmcli connection modify "Alisa" \
  connection.interface-name "wlan0" \
  connection.autoconnect yes \
  connection.autoconnect-priority 10 \
  ipv4.route-metric 600 \
  ipv6.route-metric 600
```

**Фактический результат:**

- Резервная копия: `/root/network-backup-20261014-213051`.
- Новый профиль: `Alisa_USB`, UUID `f60acacb-58a5-4ef1-b4f5-6e9817c008c8`.
- `Alisa_USB` и `Alisa` включены в автоподключение.
- Сразу после настройки основной маршрут оставался через `wlan0` — USB ещё не активировали.

## 7. Активация USB и первый тест

**Команда:**

```bash
nmcli --wait 25 connection up Alisa_USB ifname wlxf0b040f7f699
nmcli device status
ip -br -4 addr
ip -4 route
ip route get 1.1.1.1
iw dev wlxf0b040f7f699 link
ping -I wlxf0b040f7f699 -c 5 -W 2 1.1.1.1
curl --interface wlxf0b040f7f699 --connect-timeout 10 --max-time 35 -L -sS -o /dev/null \
  -w 'Скорость: %{speed_download} байт/с\nВремя: %{time_total} сек\nHTTP: %{http_code}\n' \
  'https://speed.cloudflare.com/__down?bytes=10000000'
```

**Результаты:**

- `Connection successfully activated`.
- `wlxf0b040f7f699`: `connected`, профиль `Alisa_USB`, IP `192.168.1.50/24`.
- `wlan0`: `connected`, профиль `Alisa`, IP `192.168.1.102/24`.
- Основной маршрут: `default via 192.168.1.1 dev wlxf0b040f7f699 ... metric 100`.
- Резервный маршрут: `default via 192.168.1.1 dev wlan0 ... metric 600`.
- `ip route get 1.1.1.1`: USB с адресом источника `192.168.1.50`.
- USB: SSID `Alisa`, сигнал `-35 dBm`, RX `1.0 MBit/s`, TX `72.2 MBit/s MCS 7 short GI` в момент замера.
- Ping `1.1.1.1` через USB: 5 отправлено, 5 получено, 0% потерь; min/avg/max `5.840/18.316/60.471 ms`.
- Тест Cloudflare: тайм-аут соединения на 443 через 10 секунд, скорость не измерена.
- `karaoke-server.service`, `bgutil-pot.service`, `zapret.service`: `active`.

## 8. Повторный тест скорости через оба интерфейса

**Команда:**

```bash
for IFACE in wlxf0b040f7f699 wlan0; do
  echo "===== $IFACE ====="
  iw dev "$IFACE" link | grep -E 'signal:|tx bitrate:|rx bitrate:'
  curl --interface "$IFACE" -4 -L -sS \
    --connect-timeout 8 --max-time 20 -o /dev/null \
    -w 'HTTP: %{http_code}, скорость: %{speed_download} Б/с, время: %{time_total} с\n' \
    'https://proof.ovh.net/files/10Mb.dat'
done
ip route get 1.1.1.1
```

**Результаты:**

- USB: `signal: 0 dBm` (вероятно некорректное показание драйвера), RX `26.0 MBit/s MCS 3`, TX `72.2 MBit/s`.
- Встроенный: сигнал `-40 dBm`, RX `1.0 MBit/s`, TX `65.0 MBit/s`.
- Оба HTTPS-теста `proof.ovh.net` завершились тайм-аутом через 8 секунд (`HTTP 000`).
- Основной маршрут по-прежнему USB.
- TX/RX — скорость Wi-Fi линка, **не измеренная скорость интернета**.

## 9. Диагностика HTTP, HTTPS и DNS

**Команды (смысловой блок):**

```bash
getent ahostsv4 ya.ru | head -3
getent ahostsv4 speed.cloudflare.com | head -3
curl -4 --interface wlxf0b040f7f699 --connect-timeout 6 --max-time 12 -sS -o /dev/null -w 'HTTP: %{http_code}\n' https://ya.ru/
curl -4 --interface wlan0 --connect-timeout 6 --max-time 12 -sS -o /dev/null -w 'HTTP: %{http_code}\n' https://ya.ru/
curl -4 --interface wlxf0b040f7f699 --connect-timeout 6 --max-time 12 -sS -o /dev/null -w 'HTTP: %{http_code}\n' http://neverssl.com/
curl -4 --interface wlan0 --connect-timeout 6 --max-time 12 -sS -o /dev/null -w 'HTTP: %{http_code}\n' http://neverssl.com/
```

**Результаты:**

- DNS разрешает `ya.ru` (`77.88.55.242`) и `speed.cloudflare.com` (`162.159.140.220`).
- Все четыре запроса с принудительным `--interface` завершились тайм-аутом через ~6 секунд (`HTTP 000`).
- Эти тайм-ауты не означают, что общий доступ в интернет отсутствует.

## 10. Последняя диагностика маршрутизации

**Команды:**

```bash
curl -4 --noproxy '*' --connect-timeout 6 --max-time 10 -sS -o /dev/null \
  -w 'HTTP: %{http_code}, время: %{time_total} с\n' https://ya.ru/
timeout 5 bash -c 'echo > /dev/tcp/1.1.1.1/443'
ping -I wlxf0b040f7f699 -c 3 -W 2 192.168.1.1
ping -I wlan0 -c 3 -W 2 192.168.1.1
ip -4 rule show
ip -4 route show table all
for x in all default wlan0 wlxf0b040f7f699; do cat "/proc/sys/net/ipv4/conf/$x/rp_filter"; done
env | grep -i proxy
systemctl is-active karaoke-server.service
systemctl is-active bgutil-pot.service
systemctl is-active zapret.service
ip route get 1.1.1.1
```

**Результаты:**

- Обычный HTTPS без принудительного интерфейса: `HTTP 302`, время `0.380055 с` — **интернет работает**.
- TCP к `1.1.1.1:443`: **доступен**.
- Ping шлюза через USB: min/avg/max `1.497/2.809/5.420 ms`, потерь нет.
- Ping шлюза через встроенный: min/avg/max `1.891/37.413/105.673 ms`, потерь нет.
- `ip rule`: только стандартные правила `local`, `main`, `default`.
- Оба интерфейса в подсети `192.168.1.0/24`; основной маршрут через USB (метрика 100), резервный через встроенный (600).
- `rp_filter` на `all`, `default`, `wlan0`, `wlxf0b040f7f699`: `0`.
- В переменных окружения показан `UBUNTU_MENUPROXY=1`.
- Все три службы: `active`.
- Причина тайм-аутов `curl --interface` пока **не установлена**. Предположение о маршрутизации требует проверки, не является диагнозом.

## 11. Проверка возможностей точки доступа

**Команды:**

```bash
iw phy phy0 info | grep -A 18 "Supported interface modes"
iw phy phy0 info | grep -A 18 "valid interface combinations"
iw phy phy1 info | grep -A 18 "Supported interface modes"
iw phy phy1 info | grep -A 18 "valid interface combinations"
command -v hostapd || true
command -v dnsmasq || true
```

**Результаты:**

**Встроенный `phy0`:**

```text
Supported interface modes:
 * IBSS
 * managed
 * AP
 * AP/VLAN
 * monitor
 * mesh point
 * P2P-client
 * P2P-GO
valid interface combinations:
 * #{ managed } <= 1, #{ AP } <= 1, total <= 2, #channels <= 1
 * #{ managed } <= 2, total <= 2, #channels <= 1
 * #{ managed } <= 1, #{ P2P-client, P2P-GO } <= 1, total <= 2, #channels <= 1
```

**USB `phy1`:**

```text
Supported interface modes:
 * managed
 * monitor
```

`hostapd`: не найден в PATH; `dnsmasq`: `/usr/sbin/dnsmasq`.

**Вывод:** USB подходит для приёма Wi-Fi, встроенный адаптер заявляет поддержку точки доступа. Одновременная работа встроенного адаптера как AP и клиента теоретически поддерживается на одном канале, но не испытана. NetworkManager может организовать hotspot без отдельного `hostapd`, однако это тоже нужно проверить безопасно.

## 12. Текущее состояние и следующие действия

**Работает:**

- USB Wi-Fi подключён к `Alisa`, IP `192.168.1.50`, основной маршрут с метрикой 100.
- Встроенный Wi-Fi подключён к `Alisa`, IP `192.168.1.102`, резервный маршрут с метрикой 600.
- Интернет без принудительного выбора интерфейса работает.
- Караоке, `bgutil-pot`, `zapret` активны.
- Сетевые профили сохранены; резервная копия доступна.

**Не проверено / не завершено:**

1. Реальная скорость интернета через USB и встроенный Wi-Fi (принудительные curl-тесты не удались).
2. Фактическое переключение маршрута при физическом отключении USB и обратное восстановление после подключения.
3. Запуск `KARAOKE_SYSTEM` на встроенном Wi-Fi без потери SSH и без вмешательства в USB.
4. Автоматический запуск AP при отсутствии сохранённой сети, QR-код и веб-страница настройки.
5. Сохранение резервирования при одновременной работе AP и клиента (ограничение одного канала).

**Осторожность:** создание точки доступа на `wlan0` может прервать SSH по `192.168.1.102`. Планировать изменение только после подготовки альтернативного доступа через USB (`192.168.1.50`) и безопасного отката. Не трогать `zapret.service`, `bgutil-pot.service`, работающий караоке-сервер и HDD.

## 13. Дополнительный контекст: менеджер загрузок YouTube (сводка)

В предыдущей работе обсуждалась ошибка массовой загрузки `Ошибка — Неверное имя файла или video ID`. Маршрут `/api/youtube/download` валидировал элементы и прекращал всю пачку при одной ошибке; одиночная загрузка работала. Предлагалась правка для пропуска некорректных элементов и удаления суффикса `.mp4` перед нормализацией имени. **Не подтверждено, что правка применена.** Не изменять менеджер без отдельной проверки.

---

**Конец доступной компиляции.** Для полного дословного экспорта всех сообщений и вложений потребуется исходный архив чата. Этот файл не включает двоичные вложения или не предоставленные здесь исходники прошивок, медиа и программы.
