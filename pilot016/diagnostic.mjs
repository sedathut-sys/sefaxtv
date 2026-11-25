import {ProgressGate} from './progress.mjs';
const ORIGIN='https://video.blender.org';
const SRC=ORIGIN+'/videos/embed/pAQiVCgv2CsLg79KKXUoMw?api=1&autoplay=1&muted=1&p2p=0';
const host=document.querySelector('#host'),status=document.querySelector('#status');
let serial=0,active=null;
function stop(message='Durduruldu'){
 ++serial;
 if(active){clearInterval(active.timer);try{active.player?.removeEventListener('playbackStatusUpdate',active.cb);}catch{} active.frame.remove();}
 active=null;status.textContent=message;status.dataset.proof='no';
}
document.querySelector('#stop').onclick=()=>stop();
document.querySelector('#start').onclick=()=>{
 stop('Oynatıcı hazırlanıyor');
 if(typeof window.PeerTubePlayer!=='function'){stop('Bilinmiyor: SDK yerel test dosyası eksik');return;}
 const seq=++serial,frame=document.createElement('iframe');
 frame.title='Blender Foundation resmî test videosu';frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';frame.src=SRC;
 const a={seq,frame,gate:new ProgressGate(),started:performance.now(),timer:null,cb:null,player:null};active=a;host.append(frame);
 const current=()=>active===a&&serial===seq&&frame.isConnected;
 try{
  a.player=new window.PeerTubePlayer(frame);
  a.cb=d=>{if(!current()||document.hidden)return;
   if(a.gate.sample(d,performance.now())){status.textContent='Oynatıcı zaman ilerlemesi bildiriyor (VOD tanı kanıtı)';status.dataset.proof='yes';}
   else if(d?.playbackState!=='playing'){status.dataset.proof='no';status.textContent='Bekleniyor: oynatma ilerlemesi yok';a.gate.lastProof=null;}
  };
  a.player.addEventListener('playbackStatusUpdate',a.cb);
  a.player.ready.then(()=>{if(current()&&status.dataset.proof!=='yes')status.textContent='Hazır; zaman ilerlemesi bekleniyor';}).catch(()=>{if(current())stop('Bilinmiyor: sağlayıcı hazır olmadı');});
  a.timer=setInterval(()=>{if(!current())return;if(document.hidden)return;const now=performance.now();if(a.gate.lastProof!==null&&now-a.gate.lastProof>8000){stop('Bilinmiyor: ilerleme durdu');}else if(a.gate.lastProof===null&&now-a.started>20000){stop('Bilinmiyor: 20 sn içinde kanıt yok');}},250);
 }catch{stop('Bilinmiyor: sağlayıcı bağlantısı kurulamadı');}
};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)stop('Sekme gizlendi; taze seçim gerekir');});
