# Offline QR and captive-portal support

`updated/wifi/captive.py` uses only Python's standard library. The controller
imports `CaptivePortal` from `captive`, creates it once, and calls `start()` only
while the USB setup AP owns `192.168.100.1`. `start()` returns a boolean and is
idempotent; `last_error` reports an occupied port or unavailable address. `stop()`
releases the port without touching NetworkManager, USB drivers, host DNS,
firewall rules, or unrelated HTTP servers. It can also be repeated safely.
`running` reports its listener thread; `bound_port` exists for isolated tests.

Defaults: `bind_address="192.168.100.1"`, `port=80`,
`target_url="http://192.168.100.1:8080/wifi/setup"`. It refuses wildcard binds.
All GET and HEAD requests produce a non-cacheable HTTP 302 to the setup URL.
This handles Android `/generate_204`, Apple `/hotspot-detect.html`, Windows
`/connecttest.txt` and `/ncsi.txt`, plus other HTTP paths. It does not intercept
HTTPS or serve files. Another listener's port is never taken over.

## NetworkManager's shared DNS

NetworkManager **1.42.4** sources were read directly:

- https://github.com/NetworkManager/NetworkManager/blob/1.42.4/src/core/dnsmasq/nm-dnsmasq-manager.c
- line 23: `#define CONFDIR NMCONFDIR "/dnsmasq-shared.d"`.
- line 135: `--conf-file=/dev/null`; the regular system dnsmasq configuration is
  deliberately not loaded by this shared-mode process.
- lines 139–140: `--bind-interfaces`, `--except-interface=lo`.
- line 151: `--listen-address=` is the shared interface's IPv4 address.
- lines 205–207: if that directory exists, append `--conf-dir=` plus CONFDIR.

For Debian's standard NMCONFDIR `/etc/NetworkManager`, the install destination is
`/etc/NetworkManager/dnsmasq-shared.d/karaoke-setup.conf`. Create the directory and
copy `karaoke-setup.conf` **before the next setup-AP activation**, which starts a
fresh shared dnsmasq. A global NetworkManager restart is unnecessary.

This is scoped to NetworkManager's **shared** DNS processes, not normal upstream
Wi-Fi DNS or `/etc/resolv.conf`. It applies to all shared profiles on the box;
the karaoke controller must own the only active shared AP while this file is
installed. Do not overwrite other files in that directory. The installer should
back up a same-name preexisting file and restore/remove only its own file on
rollback.

`address=/#/192.168.100.1` is the documented all-domain answer. `local=/#/` avoids
upstream AAAA/other record queries introduced by dnsmasq 2.86 and keeps setup
usable without Internet. dnsmasq 2.90 documentation confirms both behaviours:
https://github.com/imp/dnsmasq/blob/v2.90/man/dnsmasq.8 (lines 573–600).

No global DNS service or firewall mutation is needed. Shared-mode DHCP's
default gateway and DNS address remain the setup AP address. A phone using
mandatory private DNS, VPN, another network, or different connectivity detection
may not display a captive popup automatically.

## QR asset and device behaviour

`updated/wifi/setup-qr.png` is a static 296×296 PNG with an 8-pixel module and
4-module quiet zone. Generated offline with pinned `qrcode==8.2`, error correction
M, version 3. Its complete payload is:

```
http://192.168.100.1:8080/wifi/setup
```

It was independently decoded from the PNG with
`opencv-python-headless==4.12.0.88` and matched the exact payload. Generator and
decoder run only in the cloud build workspace, not on the box; the device needs
no QR dependency or Internet image service.

The latest two-step flow explicitly tells the user to first join KARAOKE
manually using password 12345678, then scan this URL QR to open Wi-Fi setup.
The QR now contains the page URL, not a network-join payload. The optional
captive popup may open setup as soon as the phone joins; otherwise the URL QR
and printed address work independently of captive detection.

The new PNG is 775 bytes, SHA256
`5f7a2c3b9f4281fbba4560da80d737bed5f4a7bb94abc1f424b171d834978671`.
It was independently decoded with OpenCV to the exact setup URL. The device
requires no QR generation package. V4 deployment/phone confirmation is pending.

## Validation

```
python3 -m unittest discover -s captive-support -p 'test_captive.py' -v
```

Seven tests passed: probe/unknown path redirects, HEAD body handling, repeated
start/stop and release of the port, occupied-port no-steal, unsupported methods,
12 concurrent probes, rejected wildcard bind and header injection. Tests bind
only loopback on a random unprivileged port.

The config also passed `dnsmasq --test` using Debian bookworm
`dnsmasq-base=2.90-4~deb12u2`, extracted into `/tmp`; no package was installed and
host services remained unchanged. Two real DNS tests passed with that binary
listening only on a random unprivileged loopback port: all Android/Apple/Windows
probe hostnames resolve to 192.168.100.1 and AAAA receives offline NOERROR/NODATA.
Reproduce with an available binary:

```
DNSMASQ_BINARY=/path/to/dnsmasq python3 -m unittest discover \
  -s captive-support -p 'test_dnsmasq.py' -v
```

These tests verify software behaviour, not a physical phone's popup or actual
USB Wi-Fi performance; those need the user's on-device trial after installation.
