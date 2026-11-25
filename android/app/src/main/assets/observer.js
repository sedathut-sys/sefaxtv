/* SefaXTV 0.12 Android: owned, packaged LAB fixture only. Not for third-party pages. */
(() => {
 'use strict';
 const FIXTURE='https://appassets.androidplatform.net/assets/lab-player.html';
 if(window.top===window||location.href.split('#')[0]!==FIXTURE)return;
 const q=new URLSearchParams(location.hash.slice(1)),seq=Number(q.get('seq')),token=q.get('token'),mode=q.get('mode');
 if(!Number.isSafeInteger(seq)||seq<1||!token||!/^[a-f0-9]{32}$/.test(token)||!['play','stall','ready'].includes(mode))return;
 const send=s=>window.parent.postMessage(JSON.parse(s),'https://appassets.androidplatform.net');
 if(!send)return;
 let counter=0,lastSent=-Infinity,lastMedia=-1;
 const seen=new WeakSet();
 function valid(v){if(!v.isConnected||v.paused||v.ended||v.seeking||v.readyState<2||v.videoWidth<=0||v.videoHeight<=0||document.hidden)return false;
  const r=v.getBoundingClientRect(),st=getComputedStyle(v);return r.width>=100&&r.height>=56&&st.display!=='none'&&st.visibility==='visible'&&Number(st.opacity)>0;}
 function proof(method,mediaTime,delta,frameDelta){const now=performance.now();if(!Number.isFinite(mediaTime)||mediaTime<=lastMedia||now-lastSent<700)return false;
  try{send(JSON.stringify({protocol:'sefaxtv-probe-v1',type:'video:advanced',seq,token,url:location.href,counter:counter+1,method,mediaTime,delta,frameDelta}));counter++;lastMedia=mediaTime;lastSent=now;return true;}catch{return false;}}
 function watch(v){if(!(v instanceof HTMLVideoElement)||seen.has(v))return;seen.add(v);let frameTime=NaN,frameCount=0,time=NaN;
  const reset=()=>{frameTime=time=NaN;frameCount=0;};v.addEventListener('seeking',reset);v.addEventListener('pause',reset);v.addEventListener('emptied',reset);
  const onFrame=(_now,m)=>{if(!v.isConnected)return;
   if(valid(v)&&Number.isFinite(m?.mediaTime)&&Number.isSafeInteger(m?.presentedFrames)){
    if(!Number.isFinite(frameTime)||m.mediaTime<frameTime||m.presentedFrames<frameCount){frameTime=m.mediaTime;frameCount=m.presentedFrames;}
    else if(m.mediaTime-frameTime>=.16&&m.presentedFrames>frameCount&&proof('frames',m.mediaTime,m.mediaTime-frameTime,m.presentedFrames-frameCount)){frameTime=m.mediaTime;frameCount=m.presentedFrames;}
   }else{frameTime=NaN;frameCount=0;}
   v.requestVideoFrameCallback(onFrame);
  };
  if(typeof v.requestVideoFrameCallback==='function')v.requestVideoFrameCallback(onFrame);
  const timer=setInterval(()=>{if(!v.isConnected){clearInterval(timer);return;}if(!valid(v)||!Number.isFinite(v.currentTime)){time=NaN;return;}
   if(!Number.isFinite(time)||v.currentTime<time)time=v.currentTime;else if(v.currentTime-time>=.25&&proof('time',v.currentTime,v.currentTime-time,0))time=v.currentTime;
  },250);
 }
 const scan=()=>document.querySelectorAll('video').forEach(watch);
 function start(){scan();new MutationObserver(scan).observe(document.documentElement,{childList:true,subtree:true});}
 if(document.documentElement)start();else document.addEventListener('DOMContentLoaded',start,{once:true});
})();
