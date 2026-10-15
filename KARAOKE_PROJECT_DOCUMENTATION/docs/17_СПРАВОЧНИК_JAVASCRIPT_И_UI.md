# Справочник JavaScript и элементов интерфейса

Статический текстовый индекс: именованные function объявления, присваивания arrow callbacks и id элементов. Не заменяет полноценный JS parser; анонимные функции привязаны к окружающему исходнику. Строки относятся к Python-файлу для встроенного HTML и к HTML для отдельных страниц.

## versions/prepared-media-audio-v1/app.py

### Именованные функции

- Строка 1391: `fetchSync(u,o)`.
- Строка 1393: `fetch(url, opts)`.
- Строка 1399: `Chain(val, err)`.
- Строка 1409: `escapeHtml(str)`.
- Строка 1415: `scanWiFi()`.
- Строка 1418: `selectWiFi(ssid)`.
- Строка 1421: `connectWiFi()`.
- Строка 1424: `loadWiFiStatus()`.
- Строка 1441: `switchTab(tab, context)`.
- Строка 1453: `scrollSlider(delta)`.
- Строка 1454: `loadPosters()`.
- Строка 1471: `filterByArtist(artist)`.
- Строка 1475: `searchSongs()`.
- Строка 1485: `searchSongsLegacy()`.
- Строка 1521: `playSong(file)`.
- Строка 1532: `playFromQueue()`.
- Строка 1542: `addToQueue(songId, btn)`.
- Строка 1549: `loadQueue()`.
- Строка 1576: `moveQueue(queueId, direction)`.
- Строка 1580: `removeFromQueue(queueId)`.
- Строка 1584: `clearQueue()`.
- Строка 1589: `uploadFiles(url, input, statusId)`.
- Строка 1598: `uploadNext()`.
- Строка 1660: `handleVideo(input)`.
- Строка 1664: `handlePoster(input)`.
- Строка 1669: `handleBgm(input)`.
- Строка 1689: `updateWifiStatus()`.
- Строка 1698: `pauseBgm()`.
- Строка 1699: `resumeBgm()`.
- Строка 1700: `toggleBgm()`.
- Строка 1704: `setBgmVolume(val)`.
- Строка 1709: `setVideoVolume(val)`.
- Строка 1718: `fmSwitchTab(type)`.
- Строка 1726: `fmSearch()`.
- Строка 1734: `fmLoadList(clear)`.
- Строка 1751: `fmLoadMore()`.
- Строка 1752: `fmDelete(btn)`.
- Строка 1776: `audioOutputRequest(value)`.
- Строка 1784: `done(message, data)`.
- Строка 1811: `toggleAudioOutput()`.
- Строка 1815: `loadBgmTracks()`.
- Строка 1845: `loadSettings()`.
- Строка 1854: `formatHDD()`.
- Строка 1874: `refreshDB()`.
- Строка 1884: `stopVideo()`.
- Строка 1891: `pauseVideo()`.
- Строка 1894: `nextVideo()`.
- Строка 1905: `posterApiRequest(url, opts)`.
- Строка 1930: `posterScanMissing()`.
- Строка 1945: `posterSearchImages()`.
- Строка 1974: `posterDownloadImage(artist, url, button)`.
- Строка 2028: `renderQueueSync(queue)`.
- Строка 2045: `searchSongsSync()`.
- Строка 2150: `oskShow(inputId, label)`.
- Строка 2192: `oskHide()`.
- Строка 2197: `oskUpdatePreview()`.
- Строка 2204: `oskRenderKeys()`.
- Строка 2251: `oskType(ch)`.
- Строка 2263: `oskBackspace()`.
- Строка 2270: `oskEnter()`.
- Строка 2281: `oskToggleShift()`.
- Строка 2286: `oskToggleLang()`.
- Строка 2297: `updateStats()`.
- Строка 2353: `hideKaraokeControlQr()`.
- Строка 2361: `updateKaraokeControlQr(state)`.
- Строка 2400: `openKaraokeWifiSetup()`.
- Строка 2405: `closeKaraokeWifiSetup()`.
- Строка 2415: `checkKaraokeWifi()`.

### DOM id

- Строка 1192: `karaoke-wifi-setup-indicator`.
- Строка 1197: `karaoke-wifi-setup-open`.
- Строка 1199: `karaoke-wifi-dialog`.
- Строка 1203: `karaoke-wifi-frame`.
- Строка 1207: `karaoke-header`.
- Строка 1210: `wifi-icon`.
- Строка 1218: `settings-btn`.
- Строка 1226: `karaoke-control-qr`.
- Строка 1228: `karaoke-control-qr-image`.
- Строка 1233: `karaoke-control-qr-address`.
- Строка 1241: `poster-slider`.
- Строка 1246: `search`.
- Строка 1251: `song-list`.
- Строка 1258: `queue-list`.
- Строка 1268: `now-playing`.
- Строка 1269: `settingsModal`.
- Строка 1274: `stat-songs`.
- Строка 1275: `stat-posters`.
- Строка 1276: `stat-size`.
- Строка 1277: `stat-total`.
- Строка 1289: `wifi-current`.
- Строка 1296: `tab-video-settings`.
- Строка 1297: `tab-poster-settings`.
- Строка 1298: `tab-bgm-settings`.
- Строка 1300: `video-upload-settings`.
- Строка 1302: `video-input-settings`.
- Строка 1305: `poster-upload-settings`.
- Строка 1307: `poster-input-settings`.
- Строка 1310: `bgm-upload-settings`.
- Строка 1312: `bgm-input-settings`.
- Строка 1314: `bgm-upload-status`.
- Строка 1316: `status-settings`.
- Строка 1318: `auto-posters-area`.
- Строка 1322: `poster-auto-status`.
- Строка 1323: `poster-auto-artist`.
- Строка 1325: `poster-auto-results`.
- Строка 1332: `bgm-toggle`.
- Строка 1338: `bgm-vol-label`.
- Строка 1340: `bgm-volume`.
- Строка 1346: `video-vol-label`.
- Строка 1348: `video-volume`.
- Строка 1350: `audio-output-area`.
- Строка 1352: `audio-output-status`.
- Строка 1353: `audio-output-toggle`.
- Строка 1359: `fm-tab-video`.
- Строка 1360: `fm-tab-poster`.
- Строка 1361: `fm-tab-bgm`.
- Строка 1363: `fm-search`.
- Строка 1364: `fm-list`.
- Строка 1366: `fm-more-btn`.
- Строка 1371: `net-status-text`.
- Строка 1372: `net-ip-text`.
- Строка 1373: `net-ssid-text`.
- Строка 1613: `ubar-`.
- Строка 1614: `uprog-`.
- Строка 2333: `osk-overlay`.
- Строка 2334: `osk-bar`.
- Строка 2336: `osk-target-name`.
- Строка 2337: `osk-input-preview`.
- Строка 2340: `osk-lang-btn`.
- Строка 2341: `osk-close`.
- Строка 2344: `osk-keys`.
## versions/prepared-media-audio-v1/media_optimizer.html

### Именованные функции

- Строка 128: `el(id)`.
- Строка 129: `text(node, value)`.
- Строка 130: `show(node, visible)`.
- Строка 131: `empty(node)`.
- Строка 132: `node(tag, value, cls)`.
- Строка 138: `hasOwn(obj, key)`.
- Строка 139: `rowMap()`.
- Строка 144: `selected(row)`.
- Строка 149: `busy()`.
- Строка 150: `mutable()`.
- Строка 151: `problem(row)`.
- Строка 152: `formatIssue(row)`.
- Строка 157: `bytes(size)`.
- Строка 161: `issueText(row)`.
- Строка 166: `setError(message)`.
- Строка 167: `request(method, path, body, callback)`.
- Строка 169: `finish(error, data)`.
- Строка 185: `actions(validate)`.
- Строка 212: `updateSelection()`.
- Строка 218: `clearReview()`.
- Строка 219: `addCheck(parent, label, checked, disabled, change)`.
- Строка 226: `renderRow(row, map)`.
- Строка 275: `renderRows()`.
- Строка 287: `renderResults()`.
- Строка 300: `renderStatus(force)`.
- Строка 325: `poll()`.
- Строка 337: `command(path, payload)`.

### DOM id

- Строка 69: `status-title`.
- Строка 70: `job-message`.
- Строка 71: `current`.
- Строка 72: `progress-wrap`.
- Строка 72: `progress-fill`.
- Строка 73: `progress-text`.
- Строка 74: `cancel-note`.
- Строка 76: `scan`.
- Строка 77: `cancel`.
- Строка 78: `retry`.
- Строка 82: `error`.
- Строка 84: `report`.
- Строка 85: `report-title`.
- Строка 86: `report-summary`.
- Строка 89: `filter`.
- Строка 90: `show-all`.
- Строка 93: `review`.
- Строка 94: `clear`.
- Строка 95: `selection-count`.
- Строка 97: `files`.
- Строка 99: `previous`.
- Строка 100: `page-label`.
- Строка 101: `next`.
- Строка 105: `review-panel`.
- Строка 106: `review-title`.
- Строка 107: `review-summary`.
- Строка 108: `review-files`.
- Строка 111: `apply`.
- Строка 112: `back-to-report`.
- Строка 116: `results-panel`.
- Строка 118: `results`.
## versions/prepared-media-audio-v1/wifi/setup.html

### Именованные функции

- Строка 69: `api(method, url, data, done, timeout)`.
- Строка 90: `setStatus(message, kind)`.
- Строка 96: `setBusy(busy)`.
- Строка 102: `loadNetworks()`.
- Строка 132: `loadStatus()`.
- Строка 152: `pollJob(jobId)`.
- Строка 194: `startJob(url, payload)`.
- Строка 215: `connectWifi()`.
- Строка 226: `resetWifi()`.
- Строка 231: `togglePassword()`.
- Строка 237: `keyboardInsert(text)`.
- Строка 244: `keyboardBackspace()`.
- Строка 252: `renderKeyboard()`.
- Строка 272: `control(label, callback)`.
- Строка 282: `toggleKeyboard()`.

### DOM id

- Строка 38: `connect-form`.
- Строка 40: `ssid`.
- Строка 41: `scanBtn`.
- Строка 43: `manualSsid`.
- Строка 45: `password`.
- Строка 46: `showPassword`.
- Строка 47: `keyboard-toggle`.
- Строка 48: `keyboard`.
- Строка 49: `connectBtn`.
- Строка 51: `status`.
- Строка 56: `resetBtn`.
