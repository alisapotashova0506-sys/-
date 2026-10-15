const fs=require('fs');const vm=require('vm');const assert=require('assert');
const app=fs.readFileSync(__dirname+'/../updated/app.py','utf8');
const source=app.slice(app.indexOf('  /* KARAOKE_CONTROL_QR_V5 */', app.indexOf('<script>'))).split('  </script>')[0];
const indicator={style:{},onclick:null};
const setupButton={onclick:null};
const frame={src:'',getAttribute(){return this.src}};
const dialog={style:{}};
const elements={'karaoke-wifi-setup-indicator':indicator,'karaoke-wifi-setup-open':setupButton,'karaoke-wifi-frame':frame,'karaoke-wifi-dialog':dialog};
const pending=[];let tick;
class XHR{open(method,url,async){assert.strictEqual(async,true);assert.strictEqual(url,'/api/karaoke-wifi-monitor')}
 send(){pending.push(this)} reply(data){this.status=200;this.responseText=JSON.stringify(data);this.onload();this.onloadend()}}
const ctx={document:{getElementById:id=>elements[id]},XMLHttpRequest:XHR,JSON,
 setInterval:fn=>{tick=fn},loadWiFiStatus:()=>{}};
vm.createContext(ctx);vm.runInContext(source,ctx);
function reply(data,expected){assert.strictEqual(pending.length,1);pending.shift().reply(data);assert.strictEqual(indicator.style.display,expected)}
reply({setup_needed:false,ap_active:false,connected:false},'none');
tick();tick();assert.strictEqual(pending.length,1,'Only one status request may be pending');
reply({setup_needed:true,ap_active:false,connected:false},'none');
tick();reply({setup_needed:true,ap_active:true,connected:false},'block');
assert.strictEqual(indicator.onclick,null,'The QR card is visible without clicking');
setupButton.onclick();assert.strictEqual(dialog.style.display,'block');assert.strictEqual(frame.src,'/wifi/setup?embedded=1');
ctx.closeKaraokeWifiSetup();assert.strictEqual(dialog.style.display,'none');
frame.src='already-loaded';setupButton.onclick();assert.strictEqual(frame.src,'already-loaded','Reopening must preserve in-flight setup');
tick();reply({setup_needed:true,ap_active:true,connected:true},'none');
console.log('QR indicator and non-navigating overlay tests passed');
