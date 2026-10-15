#!/bin/bash
set -u

LOG=/var/log/karaoke-wifi-restore.log

{
    echo "===== $(date -Is) ====="
    echo "Запущено восстановление Wi-Fi."

    nmcli connection down KARAOKE_SYSTEM 2>/dev/null || true

    sleep 2

    if nmcli -w 25 connection up ZZZZ ifname wlan0; then
        echo "Подключение ZZZZ восстановлено."
    else
        echo "Не удалось подключиться к ZZZZ."
        echo "Пробуем автоматическое подключение сохранённых сетей."

        nmcli device set wlan0 autoconnect yes || true
        nmcli device connect wlan0 || true
    fi

    nmcli -f GENERAL.STATE,GENERAL.CONNECTION device show wlan0

    echo "Восстановление завершено."
} >> "$LOG" 2>&1
