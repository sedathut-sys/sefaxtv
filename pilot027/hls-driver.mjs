import {Hls} from './vendor/hls.mjs';
import {FrameGate} from './frame-gate.mjs';
const URL='https://api-tv38.yayin.com.tr/birguntv/index.m3u8';
export function hlsDriver(host,report,emit){
 const v=document.createElement('video');
 v.controls=true;v.muted=true;v.playsInline=true;v.preload='none';
 if(typeof v.requestVideoFrameCallback!=='function'||!Hls.isSupported()){emit('denied');return {close(){}};}
 let closed=false,h=null,cb=null,live=false,lastSample=-Infinity,printed=false;
 const gate=new FrameGate();
 function close(){if(closed)return;closed=true;if(cb!==null)v.cancelVideoFrameCallback(cb);h?.destroy();v.pause();v.removeAttribute('src');v.load();v.remove();report(null);}
 function fail(kind='error'){if(!closed){close();emit(kind);}}
 host.append(v);
 try{
 h=new Hls({enableWorker:true,lowLatencyMode:false,maxBufferLength:15,backBufferLength:10,manifestLoadPolicy:{default:{maxTimeToFirstByteMs:10000,maxLoadTimeMs:15000,timeoutRetry:null,errorRetry:null}},playlistLoadPolicy:{default:{maxTimeToFirstByteMs:10000,maxLoadTimeMs:15000,timeoutRetry:null,errorRetry:null}},fragLoadPolicy:{default:{maxTimeToFirstByteMs:10000,maxLoadTimeMs:15000,timeoutRetry:null,errorRetry:null}}});
 h.on(Hls.Events.ERROR,(_,d)=>{if(closed)return;const code=d?.response?.code;if([401,403,429].includes(code)){fail('denied');return;}if(d.fatal)fail();});
 h.on(Hls.Events.LEVEL_LOADED,(_,d)=>{if(closed)return;if(d.details?.live!==true){fail('denied');return;}live=true;});
 h.on(Hls.Events.MANIFEST_PARSED,()=>{if(closed)return;emit('ready');v.play().catch(()=>{if(!closed)emit('manual');});});
 v.addEventListener('error',()=>fail());
 v.addEventListener('pause',()=>{if(!closed){gate.reset();printed=false;report(null);emit('manual');}});
 for(const ev of ['seeking','waiting','ended'])v.addEventListener(ev,()=>{if(!closed){gate.reset();printed=false;report(null);}});
 function frame(t,m){
  if(closed)return;
  if(t-lastSample>=480){
   lastSample=t;const valid=live&&!document.hidden&&!v.paused&&!v.seeking&&!v.ended&&v.readyState>=2&&v.videoWidth>0&&v.videoHeight>0;
   if(gate.sample({t,p:m.mediaTime,n:m.presentedFrames,valid})){
    emit('proof');const r={...gate.result(),live,width:v.videoWidth,height:v.videoHeight};report(r);
    if(r.seconds>=30&&r.mediaSeconds>=27&&r.intervals>=30&&r.frames>=30&&!printed){printed=true;console.log('SEFA-HLS '+JSON.stringify(r));}
   }else if(!valid||gate.count===0){printed=false;report(null);}
  }
  if(!closed)cb=v.requestVideoFrameCallback(frame);
 }
 cb=v.requestVideoFrameCallback(frame);
 h.on(Hls.Events.MEDIA_ATTACHED,()=>{if(!closed)h.loadSource(URL);});h.attachMedia(v);
 return {close};
 }catch(e){close();throw e;}
}
