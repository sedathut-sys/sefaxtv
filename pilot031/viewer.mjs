import {Hls} from './vendor/hls.mjs';
const v=document.querySelector('#v'),s=document.querySelector('#status');
let h=null,cb=null,active=false;
const data={frames:0,first:null,last:null,live:false,errors:0};
window.proof=data;
function stop(){active=false;if(cb!==null)v.cancelVideoFrameCallback(cb);cb=null;h?.destroy();h=null;v.pause();v.removeAttribute('src');v.load();s.textContent='Durduruldu';}
document.querySelector('#stop').onclick=stop;
document.querySelector('#start').onclick=()=>{
 if(active)return;active=true;v.muted=true;Object.assign(data,{frames:0,first:null,last:null,live:false,errors:0});
 if(!Hls.isSupported()||!v.requestVideoFrameCallback){s.textContent='Desteklenmiyor';active=false;return;}
 h=new Hls({lowLatencyMode:false,liveSyncDurationCount:2,liveMaxLatencyDurationCount:5,startPosition:0,maxBufferLength:20});
 h.on(Hls.Events.LEVEL_LOADED,(_,d)=>{if(d.details.live)data.live=true;});
 h.on(Hls.Events.ERROR,(_,d)=>{if(d.fatal){data.errors++;stop();}});
 h.on(Hls.Events.MEDIA_ATTACHED,()=>h.loadSource('./live.m3u8'));
 h.on(Hls.Events.MANIFEST_PARSED,()=>{v.play().catch(()=>{s.textContent='Play düğmesini kullan';});});
 h.attachMedia(v);
 function frame(t,m){if(!active)return;if(!v.paused&&!v.seeking&&v.readyState>=2){data.frames++;if(data.first===null)data.first=m.mediaTime;data.last=m.mediaTime;s.textContent='Görüntü: '+m.mediaTime.toFixed(1)+' sn';}cb=v.requestVideoFrameCallback(frame);}
 cb=v.requestVideoFrameCallback(frame);
};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)stop();});window.addEventListener('pagehide',stop);
