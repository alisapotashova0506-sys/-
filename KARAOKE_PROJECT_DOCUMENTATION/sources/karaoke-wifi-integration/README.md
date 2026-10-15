# X96Q: QR and temporary USB setup AP

The USB driver and permanent KARAOKE AP are already installed and were verified
after a real device reboot by the user. This update adds the original requested
onboarding behaviour. The base update was installed successfully on the device:
`UPDATE COMPLETE`, saved home `ZZZZ` at `192.168.1.102`, AP and QR off as expected.
Backup: `/root/karaoke-wifi-backup-9t4n98fz`. Full phone/QR flow is still pending.

The user subsequently confirmed that the automatic top-left setup control
appeared, but did not see the desired QR. `ui-v3/` prepared a small separate UI
patch: ordinary card with explicit 222x222 QR outside a button and the exact
camera/link instruction. It preserves network policy and was visually
confirmed on the TV during the three-minute test. `ui-v3/paste-update.sh` carries its
checked installer directly through SSH, without a downloadable artifact.
The already-delivered base archive and its three transfer parts remain frozen.

Latest requested flow: first manually join **KARAOKE** with **12345678**, then
scan a URL QR to open `http://192.168.100.1:8080/wifi/setup`. `ui-v4/` prepares
this revision, including the updated instruction order, URL PNG and matching
API metadata. It accepts both the V2 and V3 installed app, backs up all three
files and restarts only karaoke-server. The new QR was independently decoded
to the exact URL. Device V4 installation, all three file hashes and served
HTML/API are confirmed. Backup: `/root/karaoke-qr-link-backup-wtq_7b8_`.
The user refreshed the TV page and confirmed that the V4 scenario works.

The next requested revision, `ui-v5/`, is prepared and cloud-tested but not yet
installed on the device. It removes the old remote-control text under the title
and puts a local, dynamic home-control QR below the Wi-Fi/settings icons. The
link is `http://<current home IPv4>:8080/`; the card hides without a confirmed
home connection and on phone-sized screens. The existing left setup card,
setup URL, network controller, driver and media handling are unchanged.
The encoder is vendored with its license and uses only Python's standard
library, so installation needs no package download. PNGs are generated locally.

`ui-v5/paste-update.sh` is the complete SSH paste command. It includes a checked
compressed kit, stages and verifies new helper files before replacing app.py,
creates a private backup with standalone rollback, and restarts only
karaoke-server. Run during a playback pause, then refresh the TV page (F5).
V5 verification: 19 helper/isolated route tests, a JS state/race harness,
18 installer/rollback tests, existing 12 route and 2 UI harnesses; real
Chromium layout at 1920, 1280, 821 and mobile widths. OpenCV independently
decoded native and screen-rendered QR images at 222px and 185px.

## Intended behaviour

- Builtin `wlan0` connects to saved home Wi-Fi. Association with a saved profile
  and usable IPv4 counts as connected; Internet access is not a requirement.
- After 30 seconds without home Wi-Fi, USB `wlxf0b040f7f699` starts the existing
  `KARAOKE_USB_AP` profile: SSID `KARAOKE`, password `12345678`,
  `192.168.100.1/24`. The karaoke screen shows the setup-page URL QR top left.
- First join KARAOKE manually, then scan the QR for
  `http://192.168.100.1:8080/wifi/setup`. Captive HTTP/DNS can also open
  the page automatically on supporting phones; the printed URL is the fallback.
- Selecting a home network creates a separate temporary station profile.
  The USB AP remains up until that exact station profile has IPv4 and is saved.
  Success gives a 10-second response grace before the AP is stopped.
- Incorrect credentials keep the AP available for retry. If an old saved home
  network returns after failure, the AP has a 60-second retry grace.
- A reset requires explicit confirmation. The AP is started before home
  profiles are removed. USB station profiles and AP profiles are excluded.
- Main port-8080 karaoke playback/control remains available offline. Only the
  AP-specific port-80 captive helper redirects requests to Wi-Fi setup.

## What is changed

`current/` is the uploaded source snapshot and remains unchanged. `updated/`
contains application/UI Wi-Fi changes and four backend Python files. Only
manifest-listed production files are installed; backend tests, old auto-manager
and restore helpers are excluded. Old auto-manager and rescue timer stay
disabled. Existing driver, binder, NetworkManager service, init-script override,
zapret, bgutil, database and HDD content are not changed.

The installer requires home-network SSH to `192.168.1.102` with the client route
through `wlan0`. It checks source hashes, verifies the effective disabled
`ExecStartPre`, rejects active old Wi-Fi experiments, stages and checks an
`app.py` patch, writes a private backup and standalone rollback, and prevents
concurrent setup submissions. It restarts **only karaoke-server and the Wi-Fi
monitor**, so apply during a playback pause. It rolls back on failed controller
health or QR checks. After success the existing working home Wi-Fi means AP and
QR are off, as intended. Refresh the TV karaoke page once to load the new UI.

The printed recovery command is:

```
python3 /root/karaoke-wifi-backup-XXXXXX/rollback.py --rollback /root/karaoke-wifi-backup-XXXXXX
```

Use the actual directory printed by the installer. This is separate from the
already-installed USB driver's recovery script and does not remove that driver.

## Cloud validation and reproduction

Production code adds no Python dependencies on the device. Cloud validation
requires Python, Node, patch and Flask for isolated route tests. Existing test
dependencies were retained in `/tmp/karaoke-wifi-flask-test` and the extracted
Debian dnsmasq test binary in `/tmp/karaoke-dnsmasq-test/extracted`.

```
cd /workspace/karaoke-wifi-integration/updated/wifi
python3 -m unittest -v test_network.py
cd /workspace/karaoke-wifi-integration
PYTHONPATH=/tmp/karaoke-wifi-flask-test python3 -m unittest discover -s frontend-tests -p test_routes.py -v
node frontend-tests/test_setup_jobs.js
node frontend-tests/test_indicator.js
python3 -m unittest discover -s captive-support -p test_captive.py -v
LD_LIBRARY_PATH=/tmp/karaoke-dnsmasq-test/extracted/usr/lib/x86_64-linux-gnu DNSMASQ_BINARY=/tmp/karaoke-dnsmasq-test/extracted/usr/sbin/dnsmasq python3 -m unittest discover -s captive-support -p test_dnsmasq.py -v
python3 deploy/package.py
```

Completed: 18 backend safety tests, 12 isolated Flask route tests, two Node
frontend flow harnesses, seven real HTTP helper tests and two real DNS tests.
The QR PNG was independently decoded to the exact Wi-Fi payload. The real
unified patch round-trip and production Python AST parsing pass. Installer
normal and failure/rollback paths were independently checked with isolated
filesystem/mocked system calls. No full `app.py` import or media startup runs
in cloud tests. Hardware radio behaviour and phone popup are still untested
for this update.

`deploy/package.py` produces checksum files beside `karaoke-wifi-update.tar.gz`
and the more compact `tar.xz`/base85 alternative. Repackage after any source
change; the installer checks exact uploaded source and final hashes.

## Remaining device validation

1. Apply from home-network SSH in a playback pause. Expect UPDATE COMPLETE,
   home IPv4 retained, and AP off. Refresh TV page; QR should be hidden.
2. Arm an independent recovery timer for the original home UUID, then
   `nmcli device disconnect wlan0`. This suppresses automatic station retry
   without deleting saved profiles. SSH disconnects; after about 30 seconds
   expect AP plus QR and access through `192.168.100.1`.
3. Scan QR on phone, confirm setup page/manual URL and offline karaoke.
   Try an incorrect password: the AP must remain and retry must work.
4. Connect correct home credentials: target profile saved, success IP shown,
   AP off after grace, QR hidden, home SSH restored. Recovery timer must only
   reconnect the original profile if no saved home IPv4 is active.
5. Reboot with home Wi-Fi present and verify it reconnects with AP/QR off.
   A separate boot without saved SSID in range verifies the boot fallback.

Do not use the reset button as a substitute for the reversible loss-of-Wi-Fi
test. Reset intentionally forgets saved station profiles.
