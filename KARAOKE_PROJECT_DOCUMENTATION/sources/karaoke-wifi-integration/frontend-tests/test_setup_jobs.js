/* Minimal browser harness exercises real setup.html JS without a running server. */
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const html = fs.readFileSync(__dirname + '/../updated/wifi/setup.html', 'utf8');
const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
function harness() {
  const elements = {};
  function element() { return {value:'', textContent:'', className:'', style:{}, disabled:false,
    children:[], type:'password', appendChild(child){this.children.push(child)},
    setSelectionRange(a,b){this.selectionStart=a;this.selectionEnd=b}}; }
  for (const id of ['status','ssid','scanBtn','connectBtn','resetBtn','password','manualSsid',
    'connect-form','showPassword','keyboard','keyboard-toggle']) elements[id]=element();
  const pending=[]; const timers=[];
  class XHR {
    open(method,url,async){this.method=method;this.url=url;assert.strictEqual(async,true)}
    setRequestHeader(){}
    send(data){this.body=data;pending.push(this)}
    reply(code,body){this.status=code;this.responseText=JSON.stringify(body);this.onload()}
  }
  const window={confirm:()=>true};window.parent=window;
  const ctx={window,document:{getElementById:id=>elements[id],createElement:element},
    XMLHttpRequest:XHR, setTimeout:fn=>timers.push(fn),setInterval:()=>{},
    console,encodeURIComponent,JSON,Error};
  vm.createContext(ctx);vm.runInContext(source,ctx);
  function take(url){const i=pending.findIndex(x=>x.url===url);assert(i>=0,'Missing request '+url);return pending.splice(i,1)[0]}
  take('/api/karaoke-wifi-monitor').reply(200,{ap_active:true,connected:false});
  take('/api/wifi/scan').reply(200,{networks:[]});
  return {ctx,elements,pending,timers,take};
}
{
  const h=harness();h.elements.manualSsid.value=' Home: \\ ';h.elements.password.value=' password ';
  h.ctx.connectWifi();
  const req=h.take('/api/wifi/portal-connect');
  assert.deepStrictEqual(JSON.parse(req.body),{ssid:' Home: \\ ',password:' password '});
  req.reply(202,{ok:true,job_id:'abc'});
  assert.strictEqual(h.elements.connectBtn.disabled,true);
  h.take('/api/wifi/job/abc').reply(200,{status:'connecting',message:'Проверяем пароль'});
  assert.strictEqual(h.elements.connectBtn.disabled,true);
  h.timers.shift()();
  h.take('/api/wifi/job/abc').reply(200,{status:'failed',message:'Неверный пароль'});
  assert.strictEqual(h.elements.connectBtn.disabled,false);
  assert.strictEqual(h.elements.status.textContent,'Неверный пароль');
  h.ctx.loadStatus();h.take('/api/karaoke-wifi-monitor').reply(200,{ap_active:true,connected:false});
  assert.strictEqual(h.elements.status.textContent,'Неверный пароль','Failed message must remain for retry');
  h.elements.password.value='correct-password';h.ctx.connectWifi();
  h.take('/api/wifi/portal-connect').reply(202,{ok:true,job_id:'second'});
  h.take('/api/wifi/job/second').reply(200,{status:'success',type:'connect',ssid:'Home',ip:'192.168.1.102'});
  assert.strictEqual(h.elements.password.value,'');
  assert.match(h.elements.status.textContent,/192\.168\.1\.102:8080/);
  assert.match(h.elements.status.textContent,/Переключите телефон/);
}
{
  const h=harness();h.ctx.window.confirm=()=>false;h.ctx.resetWifi();
  assert.strictEqual(h.pending.length,0,'Cancelled reset must not send any request');
  h.ctx.window.confirm=()=>true;h.ctx.resetWifi();
  assert.deepStrictEqual(JSON.parse(h.take('/api/wifi/reset').body),{confirmed:true});
}
{
  const h=harness();h.ctx.loadStatus();
  h.take('/api/karaoke-wifi-monitor').reply(200,{ap_active:false,connected:true,network:'Saved',ip:'1.2.3.4'});
  h.elements.manualSsid.value='New';h.ctx.connectWifi();
  h.take('/api/wifi/connect').reply(409,{error:'Выполняется другой запрос'});
  assert.strictEqual(h.elements.connectBtn.disabled,false);
  assert.strictEqual(h.elements.status.textContent,'Выполняется другой запрос');
}
console.log('Setup job flow tests passed');
