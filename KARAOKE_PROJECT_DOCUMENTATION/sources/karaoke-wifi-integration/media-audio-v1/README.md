# Video maintenance and analog audio output

Prepared against the user-confirmed V5 application. Device installation is
pending; `paste-update.sh` carries the entire verified kit inside one SSH paste.
No artifact download or new package installation is required. Stop the current
song before installing; only karaoke-server is restarted. The existing Wi-Fi
controller, QR cards, driver, zapret and bgutil remain unchanged.

## Requested behaviour

Settings now link to `/video-optimization`. Scanning is read-only and runs in
the background: filename structure, dimensions, rotation, pixel aspect,
interlacing, nominal/average rate and presentation timestamps are inspected.
Equal-size candidates are compared using complete SHA256. Matching artist/title
alone is labelled a possible version, not an exact duplicate.

No corrections are selected by default. The user edits names, selects format
changes or chooses the exact copy to keep, then reviews and confirms. Every
converted video becomes 1920x1080 including upscaling, aspect preserved with
padding, H.264/yuv420p at 24fps in MKV. All audio tracks, subtitles, chapters and
font attachments are mapped. MP4 mov_text subtitles become ASS to retain
supported styling. Unsupported complex track layouts are reported for manual
review rather than silently dropping tracks.

Originals and temporary output are stored exclusively on the mounted HDD under
`/mnt/usb_disk/.karaoke-optimization`, outside the indexed library. Source
identities and hashes are rechecked, collisions rejected, output probed and
track counts checked before replacement. Independent source backups, durable
journals and SQLite snapshots recover interrupted commits before library
refresh. Existing song IDs/play counts survive renames. Removing a duplicate
merges its play count and redirects queued requests to the retained song;
queue positions remain. Playback and library mutations are blocked during
repairs. Cancellation preserves already completed corrections.

Audio diagnostics supplied by the user establish card `audiocodec` (analog),
card `HDMI`, both PCM device0, analog LINEOUT enabled. The original wrapper and
ALSA defaults send audio only to HDMI. A settings button now routes both mpv
instances to analog only, or restores HDMI. Stable ALSA card IDs and the
standard dmix PCM allow both players to share the chosen card. No global ALSA
configuration or mixer values change. IPC verifies the chosen device and active
output; partial failures restore both players. Selection is stored separately
in `.audio_output.json` and used by future launches and the wrapper.

## Deployment and recovery

The installer verifies source/unchanged-file hashes, effective disabled
ExecStartPre and idle video, backs up the application, wrapper and consistent
SQLite database, stages new modules then atomically replaces the application.
A temporary marker prevents new edits during installation. Failed health checks
restore code automatically. The printed standalone rollback also handles a
partially completed installation. Code rollback deliberately does not replace
the live database or undo user-confirmed media repairs. Per-file originals and
recovery journals remain on HDD for those operations.

After `MEDIA AUDIO INSTALLED`, refresh the TV page (F5), open settings, and
verify the report and analog sound physically. Cloud tests cannot establish
audible output on the device. Large-library scan and full-library transcoding
have not been run on the device; conversion can take a long time.

## Validation

32 feature/integration/installer tests pass, including actual FFmpeg upscaling,
FPS conversion, two audio tracks, ASS subtitles and byte-identical font
attachment preservation; queue/count preservation; interrupted transactions;
stale files, collisions, cancellation and missing HDD; audio partial-failure
rollback. Existing 12 route tests and the three QR/UI JavaScript harnesses pass.
Real Chromium exercises explicit selection/review/apply, visible server errors,
cancel, phone layout and both sound-button directions. Full app.py is never
imported in cloud tests because it starts media services.

```sh
PYTHONPATH=/tmp/karaoke-wifi-flask-test python3 -m unittest discover -s media-audio-tests -p 'test_*.py' -v
python3 media-audio-tests/check_browser.py
python3 media-audio-v1/package.py
```
