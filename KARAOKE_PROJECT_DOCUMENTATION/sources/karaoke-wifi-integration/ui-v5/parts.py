"""UI fragments for a home-network control QR in the header."""
CSS = '''
    /* KARAOKE_CONTROL_QR_V5 */
    .karaoke-header { position: relative; flex: 0 0 auto; padding: 1px 0; }
    .karaoke-header .top-right-tools { font: 14px/1 sans-serif; letter-spacing: normal; }
    .karaoke-header .icon-btn svg { display: block; }
    .karaoke-header.control-qr-visible { min-height: 310px; }
    .karaoke-header.control-qr-visible h1 { margin-right: 470px; padding-top: 65px; }
    #karaoke-control-qr {
      display: none; position: absolute; top: 58px; right: 20px; z-index: 90;
      width: 440px; box-sizing: border-box; padding: 12px;
      border: 1px solid #475569; border-radius: 12px; background: #0f172a;
      color: #fff; font: 14px/1.4 sans-serif; letter-spacing: normal;
    }
    #karaoke-control-qr .control-qr-row { display: table; table-layout: fixed; width: 100%; }
    #karaoke-control-qr .control-qr-picture { display: table-cell; width: 222px; vertical-align: middle; }
    #karaoke-control-qr img { display: block; width: 222px; height: 222px; background: #fff; image-rendering: pixelated; }
    #karaoke-control-qr .control-qr-copy { display: table-cell; padding-left: 12px; vertical-align: middle; }
    #karaoke-control-qr strong { display: block; margin-bottom: 8px; font-size: 16px; }
    #karaoke-control-qr .control-qr-manual { display: block; margin-top: 12px; color: #cbd5e1; font-size: 12px; }
    #karaoke-control-qr-address { display: block; margin-top: 4px; color: #93c5fd; font-size: 12px; overflow-wrap: anywhere; }
    @media (max-height: 800px) {
      .karaoke-header.control-qr-visible { min-height: 274px; }
      .karaoke-header.control-qr-visible h1 { margin-right: 430px; padding-top: 45px; }
      #karaoke-control-qr { width: 400px; }
      #karaoke-control-qr .control-qr-picture { width: 185px; }
      #karaoke-control-qr img { width: 185px; height: 185px; }
    }
    @media (min-width: 821px) and (max-width: 1400px) {
      .karaoke-header.control-qr-visible h1 { font-size: 90px; letter-spacing: 8px; }
    }
    @media (min-width: 821px) and (max-width: 1000px) {
      .karaoke-header.control-qr-visible h1 { font-size: 64px; letter-spacing: 5px; }
    }
    @media (max-width: 820px) {
      #karaoke-control-qr { display: none !important; }
      .karaoke-header.control-qr-visible { min-height: 0; }
      .karaoke-header.control-qr-visible h1 { margin-right: 0; padding-top: 0; }
    }
'''

HTML = '''    <!-- KARAOKE_CONTROL_QR_V5 -->
    <div id="karaoke-control-qr" role="region" aria-label="Управление караоке с телефона">
      <div class="control-qr-row">
        <div class="control-qr-picture"><img id="karaoke-control-qr-image" width="222" height="222" alt="QR-код страницы управления караоке"></div>
        <div class="control-qr-copy">
          <strong>Управление с телефона</strong>
          <span>Для управления наведите камеру телефона на QR-код и перейдите по ссылке.</span>
          <span class="control-qr-manual">Или наберите в браузере:</span>
          <span id="karaoke-control-qr-address"></span>
        </div>
      </div>
    </div>
'''

JS = '''  /* KARAOKE_CONTROL_QR_V5 */
  var controlQrKey = '';
  var controlQrGeneration = 0;
  function hideKaraokeControlQr() {
    controlQrKey = '';
    controlQrGeneration++;
    var card = document.getElementById('karaoke-control-qr');
    var header = document.getElementById('karaoke-header');
    if (card) card.style.display = 'none';
    if (header) header.className = 'karaoke-header';
  }
  function updateKaraokeControlQr(state) {
    var card = document.getElementById('karaoke-control-qr');
    var header = document.getElementById('karaoke-header');
    var oldImage = document.getElementById('karaoke-control-qr-image');
    var address = document.getElementById('karaoke-control-qr-address');
    if (!card || !header || !oldImage || !address) return;
    if (!state || state.controller_ok !== true || state.connected !== true ||
        typeof state.ip !== 'string' || (window.innerWidth && window.innerWidth <= 820)) {
      hideKaraokeControlQr(); return;
    }
    var parts = state.ip.split('.');
    var valid = parts.length === 4;
    for (var i = 0; i < parts.length; i++) {
      if (!/^\\d{1,3}$/.test(parts[i]) || Number(parts[i]) > 255) valid = false;
    }
    if (!valid || Number(parts[0]) === 0 || Number(parts[0]) === 127 ||
        Number(parts[0]) >= 224 || (Number(parts[0]) === 169 && Number(parts[1]) === 254)) {
      hideKaraokeControlQr(); return;
    }
    var url = 'http://' + state.ip + ':8080/';
    if (controlQrKey === url) return;
    var generation = ++controlQrGeneration;
    var image = document.createElement('img');
    image.id = 'karaoke-control-qr-image';
    image.width = 222; image.height = 222;
    image.alt = 'QR-код страницы управления караоке';
    image.onerror = function() {
      if (generation !== controlQrGeneration || controlQrKey !== url) return;
      hideKaraokeControlQr();
    };
    oldImage.parentNode.replaceChild(image, oldImage);
    controlQrKey = url;
    address.textContent = url;
    image.src = '/wifi/control-qr.png?ip=' + encodeURIComponent(state.ip);
    header.className = 'karaoke-header control-qr-visible';
    card.style.display = 'block';
  }
'''

ROUTE = '''@app.route('/wifi/control-qr.png')
def karaoke_control_qr():
    from flask import Response
    try:
        png, url = wifi_control_qr.control_image(expected_ip=request.args.get('ip'))
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 409, {'Cache-Control': 'no-store'}
    response = Response(png, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Control-URL'] = url
    return response


'''


def patch(source):
    import re
    text = source.decode('utf-8')
    text = text.replace('from wifi import network as wifi_network\n',
                        'from wifi import network as wifi_network\nfrom wifi import control_qr as wifi_control_qr\n')
    text, count = re.subn(r'^[ \t]*#remote-info(?: b)?\s*\{[^}]*\}\n', '', text, flags=re.M)
    if count != 4:
        raise RuntimeError('Unexpected old remote-info CSS')
    text = text.replace('  </style>\n</head>', CSS + '\n  </style>\n</head>', 1)
    text = text.replace('  <h1>Караоке\n    <div class="top-right-tools">',
                        '  <div id="karaoke-header" class="karaoke-header">\n  <h1>Караоке</h1>\n    <div class="top-right-tools">', 1)
    text = text.replace('    </div>\n  </h1>\n  <div id="remote-info">Загрузка...</div>',
                        '    </div>\n' + HTML + '  </div>', 1)
    start = text.index('    // Показываем IP для удалённого управления\n')
    end = text.index('    loadBgmTracks();', start)
    text = text[:start] + text[end:]
    marker = '  /* KARAOKE_WIFI_SETUP_INDICATOR_V2 */\n'
    text = text.replace(marker, JS + '\n' + marker, 1)
    text = text.replace("        if (xhr.status !== 200) return;\n        try {\n          var state = JSON.parse(xhr.responseText);",
                        "        if (xhr.status !== 200) { hideKaraokeControlQr(); return; }\n        try {\n          var state = JSON.parse(xhr.responseText);\n          updateKaraokeControlQr(state);", 1)
    text = text.replace("        } catch (e) {}\n      };\n      xhr.onloadend = function() { pending = false; };\n      try { xhr.send(null); } catch (e) { pending = false; }",
                        "        } catch (e) { hideKaraokeControlQr(); }\n      };\n      xhr.onerror = xhr.ontimeout = hideKaraokeControlQr;\n      xhr.onloadend = function() { pending = false; };\n      try { xhr.send(null); } catch (e) { pending = false; hideKaraokeControlQr(); }", 1)
    text = text.replace("@app.route('/api/network_status')\n", ROUTE + "@app.route('/api/network_status')\n", 1)
    if 'remote-info' in text:
        raise RuntimeError('Old remote-info reference remains')
    return text.encode('utf-8')
