"""Real Chromium selection/review/cancel flow; no application import."""
import ast
import importlib.util
import json
from pathlib import Path
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('feature_parts', ROOT / 'media-audio-v1/parts.py')
parts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parts)
rows = [dict(id='f0', name='Артист - Песня.mp4', size=10000,
             issues=[dict(kind='resolution', message='640×360 → 1920×1080')],
             proposed_name='Артист - Песня.mp4', video=dict(width=640, height=360, fps=30, codec='h264'),
             duplicates=[], can_transcode=True)]
job = dict(id='a'*32, state='ready', rows=rows, results=[], processed=1, total=1,
           current='', message='', error='', cancel_requested=False)
requests = []
reject_apply = True
audio = dict(ok=True, available=True, verified=True, analog_only=False)


def route(request):
    global reject_apply
    path = request.request.url.split('karaoke.test')[-1]
    if path == '/video-optimization':
        request.fulfill(body=(ROOT/'updated/media_optimizer.html').read_text(), content_type='text/html')
        return
    if path.startswith('/api/media-optimizer/'):
        operation = path.rsplit('/', 1)[-1]
        if operation == 'status':
            data = dict(ok=True, job=job)
        else:
            payload = request.request.post_data_json
            requests.append((operation, payload))
            if operation == 'apply':
                if reject_apply:
                    reject_apply = False
                    request.fulfill(status=409, body=json.dumps(dict(ok=False, error='Файл изменился. Запустите проверку заново.')), content_type='application/json')
                    return
                job['state'] = 'repairing'
            if operation == 'cancel':
                job['state'] = 'cancelled'
            data = dict(ok=True, job_id=job['id'])
    elif path == '/api/audio/output':
        if request.request.method == 'POST':
            payload = request.request.post_data_json
            requests.append(('audio', payload))
            audio['analog_only'] = payload['analog_only']
        data = audio
    else:
        request.fulfill(status=404, body='')
        return
    request.fulfill(body=json.dumps(data), content_type='application/json')


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport=dict(width=1280, height=720))
    page.route('**/*', route)
    page.goto('http://karaoke.test/video-optimization')
    expect(page.locator('#files .file')).to_have_count(1)
    expect(page.locator('#review')).to_be_disabled()
    assert not requests, 'Opening the report cannot start changes'
    page.get_by_label('Преобразовать: 1920 × 1080, до 24 кадров/с, H.264').check()
    page.locator('#review').click()
    expect(page.locator('#review-panel')).to_be_visible()
    expect(page.locator('#review-files')).to_contain_text('Песня.mkv')
    assert not requests, 'Review cannot start conversion'
    page.locator('#apply').click()
    expect(page.locator('#error')).to_contain_text('Файл изменился')
    page.wait_for_timeout(2300)
    expect(page.locator('#error')).to_contain_text('Файл изменился')
    page.locator('#review').click()
    page.locator('#apply').click()
    page.wait_for_function("document.getElementById('cancel').hidden === false")
    assert requests[1] == ('apply', dict(job_id='a'*32, confirmed=True, actions=[dict(file_id='f0', transcode=True)])), requests
    page.locator('#cancel').click()
    page.wait_for_function("document.getElementById('cancel').hidden === true")
    assert requests[-1][0] == 'cancel'
    job['state'] = 'ready'
    page.set_viewport_size(dict(width=390, height=844))
    page.reload()
    expect(page.locator('#files .file')).to_have_count(1)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.screenshot(path='/tmp/karaoke-media-mobile.png', full_page=True)
    tree = ast.parse((ROOT/'updated/app.py').read_text())
    html = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='HTML' for t in n.targets)))
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S)
    page.set_content(html)
    page.evaluate("document.getElementById('settingsModal').style.display='block'")
    page.add_script_tag(content=parts.AUDIO_JS)
    page.evaluate('audioOutputRequest(null)')
    expect(page.locator('#audio-output-toggle')).to_be_enabled()
    page.locator('#audio-output-toggle').click()
    expect(page.locator('#audio-output-status')).to_contain_text('HDMI отключён')
    assert requests[-1] == ('audio', dict(analog_only=True))
    page.locator('#audio-output-toggle').click()
    expect(page.locator('#audio-output-status')).to_have_text('Звук на HDMI.')
    assert requests[-1] == ('audio', dict(analog_only=False))
    page.screenshot(path='/tmp/karaoke-audio-settings-mobile.png', full_page=True)
    browser.close()
print('Browser passed: explicit review/apply, cancel, mobile layout, HDMI/analog toggle')
