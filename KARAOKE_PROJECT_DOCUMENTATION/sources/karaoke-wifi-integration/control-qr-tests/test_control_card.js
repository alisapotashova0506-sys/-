// Exercise the JavaScript actually rendered by Python, including escape decoding.
const assert = require('assert');
const child = require('child_process');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const app = path.join(__dirname, '..', 'updated', 'app.py');
const html = JSON.parse(child.execFileSync('python3', ['-c', `
import ast,json,sys
tree=ast.parse(open(sys.argv[1]).read())
node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HTML' for t in n.targets))
print(json.dumps(ast.literal_eval(node.value)))
`, app], {encoding: 'utf8'}));
const script = html.split('<script>\n  /* KARAOKE_CONTROL_QR_V5 */')[1].split('  </script>')[0];
assert(script, 'Extract the actual control/status JavaScript');
assert(!html.includes('remote-info'), 'Remove the old control banner and all references');

const elements = {};
function element(id) {
  const value = {id, style: {}, className: '', textContent: '', parentNode: null};
  elements[id] = value;
  return value;
}
const header = element('karaoke-header');
header.className = 'karaoke-header';
const card = element('karaoke-control-qr');
const address = element('karaoke-control-qr-address');
const initialImage = element('karaoke-control-qr-image');
const imageParent = {
  replaceChild(next, previous) {
    assert.strictEqual(previous, elements['karaoke-control-qr-image']);
    elements[next.id] = next;
    next.parentNode = this;
    previous.parentNode = null;
  }
};
initialImage.parentNode = imageParent;
const indicator = element('karaoke-wifi-setup-indicator');
element('karaoke-wifi-setup-open');
const frame = element('karaoke-wifi-frame');
frame.getAttribute = function(name) { return this[name] || ''; };
element('karaoke-wifi-dialog');
const images = [];
const pending = [];
let tick;
class XHR {
  open(method, url, async) {
    assert.strictEqual(method, 'GET');
    assert.strictEqual(url, '/api/karaoke-wifi-monitor');
    assert.strictEqual(async, true);
  }
  send() { pending.push(this); }
}
const context = {
  document: {
    getElementById: id => elements[id],
    createElement(tag) {
      assert.strictEqual(tag, 'img');
      const image = {style: {}, parentNode: null};
      images.push(image);
      return image;
    }
  },
  window: {innerWidth: 1920},
  XMLHttpRequest: XHR,
  setInterval(fn, ms) { assert.strictEqual(ms, 3000); tick = fn; },
  JSON, Number, encodeURIComponent,
  loadWiFiStatus() {}
};
vm.createContext(context);
vm.runInContext(script, context);
function home(ip = '192.168.1.102') {
  return {controller_ok: true, connected: true, ip, setup_needed: false, ap_active: false};
}
function complete(state, status = 200) {
  assert.strictEqual(pending.length, 1);
  const request = pending.shift();
  request.status = status;
  request.responseText = typeof state === 'string' ? state : JSON.stringify(state);
  request.onload();
  request.onloadend();
}
function poll(state, status = 200) { tick(); complete(state, status); }
function shown(ip) {
  assert.strictEqual(card.style.display, 'block');
  assert.strictEqual(header.className, 'karaoke-header control-qr-visible');
  assert.strictEqual(address.textContent, 'http://' + ip + ':8080/');
}
function hidden() {
  assert.strictEqual(card.style.display, 'none');
  assert.strictEqual(header.className, 'karaoke-header');
}

complete(home());
shown('192.168.1.102');
assert.strictEqual(images.length, 1);
assert.strictEqual(images[0].src, '/wifi/control-qr.png?ip=192.168.1.102');
assert.strictEqual(images[0].width, 222);
assert.strictEqual(images[0].height, 222);
assert.strictEqual(images[0].onload, undefined, 'Legacy browser visibility does not depend on img.onload');
assert.strictEqual(indicator.style.display, 'none');
tick(); tick();
assert.strictEqual(pending.length, 1, 'Reuse one pending status request');
complete(home());
assert.strictEqual(images.length, 1, 'Unchanged IP does not reload the image');

const oldImage = images[0];
poll(home('10.20.30.40'));
shown('10.20.30.40');
oldImage.onerror();
shown('10.20.30.40');
assert.strictEqual(images.length, 2);
images[1].onerror();
hidden();
poll(home('10.20.30.40'));
shown('10.20.30.40');
assert.strictEqual(images.length, 3, 'Failed image is retried on the next state poll');

const activeImage = images[2];
poll({controller_ok: true, connected: false, setup_needed: true, ap_active: true});
hidden();
assert.strictEqual(indicator.style.display, 'block', 'Existing offline setup card stays available');
activeImage.onerror();
hidden();

for (const bad of [null, {}, home('127.0.0.1'), home('169.254.1.2'), home('0.1.2.3'),
  home('224.1.2.3'), home('192.168.1.999'), home('192.168.1.1<script>'), home('1.2.3'),
  {...home(), controller_ok: false}, {...home(), connected: false}, {...home(), ip: 123}]) {
  poll(home());
  shown('192.168.1.102');
  poll(bad);
  hidden();
}
for (const failure of ['http', 'json', 'network', 'timeout']) {
  poll(home());
  shown('192.168.1.102');
  tick();
  if (failure === 'http') complete(home(), 503);
  else if (failure === 'json') complete('not-json');
  else {
    const request = pending.shift();
    request[failure === 'network' ? 'onerror' : 'ontimeout']();
    request.onloadend();
  }
  hidden();
}
context.window.innerWidth = 390;
poll(home());
hidden();
context.window.innerWidth = 1920;
poll(home());
shown('192.168.1.102');
console.log('Control QR: URL changes, image failure/retry races, disconnects, stale/error states, mobile, and shared polling passed.');
