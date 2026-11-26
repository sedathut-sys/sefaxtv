const Hls=globalThis.Hls;
import {FrameGate} from './frame-gate.mjs';
const $=id=>document.getElementById(id),host=$('host'),status=$('status');
const URL='https://api-tv38.yayin.com.tr/birguntv/index.m3u8';
let active=null;
function state(s){status.dataset.state=s;status.textContent=({idle:'Hazır',connecting:'Bağlanıyor',ready:'Yayın bildirimi alındı, kare kanıtı bekleniyor',manual:'Oynatıcının Play düğmesini kullan',playing:'Görüntü kareleri ilerliyor','continuous-frames':'30 saniye görüntü ilerlemesi doğrulandı','not-live':'Canlı HLS doğrulanmadı','rate-limited':'İstek sınırı; durduruldu',error:'Oynatma başarısız',unsupported:'Tarayıcı desteklemiyor',stalled:'Görüntü ilerlemesi kesildi'})[s]||s;}
function stop(s='idle'){const a=active;active=null;if(a){clearInterval(a.timer);if(a.cb!==null)a.v.cancelVideoFrameCallback?.(a.cb);a.h?.destroy();a.v.pause();a.v.removeAttribute('src');a.v.load();a.v.remove();}state(s);}
function start(){
 if(active)return;
 const v=document.createElement('video');v.controls=true;v.muted=true;v.playsInline=true;v.preload='none';
 if(typeof v.requestVideoFrameCallback!=='function'||!Hls.isSupported()){state('unsupported');return;}
 const a={v,h:null,cb:null,timer:null,live:false,gate:new FrameGate(),last:performance.now(),lastSample:-Infinity,printed:false};active=a;host.append(v);state('connecting');
 const live=()=>active===a;
 const h=new Hls({enableWorker:true,lowLatencyMode:false,maxBufferLength:15,backBufferLength:10,manifestLoadPolicy:{default:{maxTimeToFirstByteMs:10000,maxLoadTimeMs:15000,timeoutRetry:null,errorRetry:null}},playlistLoadPolicy:{default:{maxTimeToFirstByteMs:10000,maxLoadTimeMs:15000,timeoutRetry:null,errorRetry:null}},fragLoadPolicy:{default:{maxTimeToFirstByteMs:10000,maxLoadTimeMs:15000,timeoutRetry:null,errorRetry:null}}});a.h=h;
 h.on(Hls.Events.ERROR,(_,d)=>{if(!live())return;const code=d?.response?.code;if(code===429){stop('rate-limited');return;}if(d.fatal)stop('error');});
 h.on(Hls.Events.LEVEL_LOADED,(_,d)=>{if(!live())return;if(d.details?.live!==true){stop('not-live');return;}a.live=true;});
 h.on(Hls.Events.MANIFEST_PARSED,()=>{if(!live())return;state('ready');v.play().catch(()=>{if(live())state('manual');});});
 v.addEventListener('error',()=>{if(live())stop('error');});
 for(const name of ['pause','seeking','waiting','ended'])v.addEventListener(name,()=>{if(live()){a.gate.reset();a.printed=false;state('stalled');}});
 function frame(t,m){
  if(!live())return;
  if(t-a.lastSample>=480){
   a.lastSample=t;const valid=a.live&&!document.hidden&&!v.paused&&!v.seeking&&!v.ended&&v.readyState>=2&&v.videoWidth>0&&v.videoHeight>0;
   if(a.gate.sample({t,p:m.mediaTime,n:m.presentedFrames,valid})){
    a.last=t;const r=a.gate.result();state('playing');
    if(r.seconds>=30&&r.mediaSeconds>=27&&r.intervals>=30&&r.frames>=30){state('continuous-frames');if(!a.printed){a.printed=true;console.log('SEFA-HLS '+JSON.stringify({...r,live:a.live,width:v.videoWidth,height:v.videoHeight}));}}
   }else if(!valid||a.gate.count===0){a.printed=false;if(status.dataset.state==='playing'||status.dataset.state==='continuous-frames')state('ready');}
  }
  if(live())a.cb=v.requestVideoFrameCallback(frame);
 }
 a.cb=v.requestVideoFrameCallback(frame);
 a.timer=setInterval(()=>{if(!live())return;if(performance.now()-a.last>25000)stop('error');},500);
 h.attachMedia(v);h.on(Hls.Events.MEDIA_ATTACHED,()=>{if(live())h.loadSource(URL);});
}
if(Hls&&Hls.version==='1.6.13'){$('start').disabled=false;state('idle');}else{state('Oynatıcı kütüphanesi yüklenemedi veya sürüm uyuşmuyor.');} $('start').onclick=start;$('stop').onclick=()=>stop();document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});window.addEventListener('pagehide',()=>stop());
