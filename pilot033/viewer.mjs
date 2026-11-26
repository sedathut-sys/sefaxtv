import {Hls} from './hls.mjs';
const $=id=>document.getElementById(id),v=$('v');let h=null,stopped=false,active=false;
async function tick(){if(stopped)return;try{
 const r=await fetch('./status.json',{cache:'no-store'});if(!r.ok)return;
 const s=await r.json(),rows=s.rows||[];
 $('status').textContent=({checking:'Kaynak kontrolü', 'loading-models':'Yerel modeller hazırlanıyor',receiving:'Yeni canlı parçalar bekleniyor',playing:'Canlı parçalar işleniyor',finished:'Kısa oturum tamamlandı','source-ended':'Kaynak kesildi',failed:'Kaynak veya işlem başarısız'})[s.state]||s.state;
 $('stats').textContent='Türkçe: '+rows.filter(x=>x.mode==='dub').length+' / '+rows.length+' parça · Orijinal: '+rows.filter(x=>x.mode==='original').length+(s.reason?' · '+s.reason:'');
 $('play').disabled=rows.length<1||active;
}catch{}}
const timer=setInterval(tick,500);tick();
$('play').onclick=()=>{if(stopped||active)return;active=true;$('play').disabled=true;
 if(!Hls.isSupported()){$('status').textContent='Tarayıcı HLS desteklemiyor';active=false;return;}
 h=new Hls({lowLatencyMode:false,startPosition:0,maxBufferLength:20});
 h.on(Hls.Events.MEDIA_ATTACHED,()=>h.loadSource('./live.m3u8'));
 h.on(Hls.Events.MANIFEST_PARSED,()=>{v.muted=false;v.play().catch(()=>{$('status').textContent='Oynatıcıdaki Play düğmesine bas';});});
 h.on(Hls.Events.ERROR,(_,d)=>{if(d.fatal){h?.destroy();h=null;active=false;v.pause();$('status').textContent='Oynatma hatası';}});h.attachMedia(v);
};
function end(){if(stopped)return;stopped=true;clearInterval(timer);h?.destroy();h=null;v.pause();v.removeAttribute('src');v.load();$('play').disabled=true;$('status').textContent='Durduruldu';fetch('./stop',{method:'POST',keepalive:true}).catch(()=>{});}
$('stop').onclick=end;window.addEventListener('pagehide',end);
