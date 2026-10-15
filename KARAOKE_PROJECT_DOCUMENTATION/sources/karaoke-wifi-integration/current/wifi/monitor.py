#!/usr/bin/env python3
import json
import os
import subprocess
import time

STATE_FILE = "/var/lib/karaoke-wifi/status.json"
INTERFACE = "wlan0"
TIMEOUT = 30
INTERVAL = 2

missing_since = None

def get_connection():
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f",
             "GENERAL.STATE,GENERAL.CONNECTION",
             "device", "show", INTERFACE],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        if result.returncode != 0:
            return False, ""

        fields = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key] = value

        connected = fields.get("GENERAL.STATE", "").split()[0] == "100"
        name = fields.get("GENERAL.CONNECTION", "")

        if name == "KARAOKE_SYSTEM":
            connected = False

        return connected, name

    except Exception:
        return False, ""

def save_state(data):
    temporary = STATE_FILE + ".tmp"
    with open(temporary, "w") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(temporary, STATE_FILE)

while True:
    now = time.monotonic()
    connected, network = get_connection()

    if connected:
        missing_since = None
        elapsed = 0
    else:
        if missing_since is None:
            missing_since = now
        elapsed = now - missing_since

    setup_needed = not connected and elapsed >= TIMEOUT

    save_state({
        "connected": connected,
        "network": network if connected else "",
        "seconds_without_wifi": int(elapsed),
        "setup_needed": setup_needed,
        "mode": "monitor_only",
        "updated_at": int(time.time())
    })

    time.sleep(INTERVAL)
