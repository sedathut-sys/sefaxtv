import {Hls} from './hls.mjs';
import {captureLoop} from './capture.mjs';
const $=id=>document.getElementById(id),v=$('v');
let ready=false,started=false,stopped=false,h=null,stream=null,active=false;
function canStart(){$('capture').disabled=!ready||started||stopped||!$('consent').checked;}
$('consent').onchange=canStart;
async function tick(){
 if(stopped)return;
 try{
  const r=await fetch('./status.json',{cache:'no-store'});if(!r.ok)return;
  const s=await r.json();ready=s.ready;canStart();
  $('status').textContent=({loading:'Modeller hazırlanıyor',ready:'Yayın sekmesini seçebilirsin',playing:'Dublaj hazırlanıyor / oynatılabilir',finished:'Kısa oturum tamamlandı',failed:'İşlem başarısız'})[s.state]||s.state;
  $('stats').textContent='Alınan: '+s.received+' · Türkçe: '+s.rows.filter(x=>x.mode==='dub').length+' / '+s.rows.length+' · Orijinal: '+s.rows.filter(x=>x.mode==='original').length+(s.error?' · '+s.error:'');
  $('play').disabled=!s.rows.length||active;
 }catch{}
}
const timer=setInterval(tick,500);tick();
$('capture').onclick=async()=>{
 if(!ready||started||stopped||!$('consent').checked)return;
 started=true;canStart();
 try{
  stream=await navigator.mediaDevices.getDisplayMedia({video:{displaySurface:'browser',width:{ideal:640},height:{ideal:360},frameRate:{ideal:25,max:25}},audio:{suppressLocalAudioPlayback:true},selfBrowserSurface:'exclude',systemAudio:'exclude',surfaceSwitching:'exclude'});
  if(stopped){stream.getTracks().forEach(t=>t.stop());return;}
  if(stream.getVideoTracks()[0]?.getSettings().displaySurface!=='browser'||!stream.getAudioTracks().length)throw Error('Yalnız sekme ve sekme sesi seçilmeli.');
  await captureLoop(stream,{stopped:()=>stopped,onClip:x=>{$('result').textContent='Kayıt parçası '+(x.index+1)+' · geçiş boşluğu '+Math.round(x.gap)+' ms';}});
  $('result').textContent='Sekme paylaşımı tamamlandı.';
 }catch(e){stream?.getTracks().forEach(t=>t.stop());$('result').textContent=String(e.message||e);await fetch('./finish',{method:'POST'}).catch(()=>{});}
};
$('play').onclick=()=>{if(active||stopped)return;if(!Hls.isSupported()){$('result').textContent='HLS desteklenmiyor';return;}active=true;h=new Hls({startPosition:0,lowLatencyMode:false,maxBufferLength:30});
 h.on(Hls.Events.MEDIA_ATTACHED,()=>h.loadSource('./live.m3u8'));
 h.on(Hls.Events.MANIFEST_PARSED,()=>{v.muted=false;v.play().catch(()=>{$('result').textContent='Oynatıcıdaki Play düğmesine bas';});});
 h.on(Hls.Events.ERROR,(_,d)=>{if(d.fatal){h?.destroy();h=null;active=false;v.pause();$('result').textContent='Oynatma hatası';}});h.attachMedia(v);};
function stop(){if(stopped)return;stopped=true;clearInterval(timer);stream?.getTracks().forEach(t=>t.stop());h?.destroy();h=null;v.pause();v.removeAttribute('src');v.load();$('capture').disabled=true;$('play').disabled=true;$('status').textContent='Durduruldu';fetch('./stop',{method:'POST',keepalive:true}).catch(()=>{});}
$('stop').onclick=stop;window.addEventListener('pagehide',stop);
