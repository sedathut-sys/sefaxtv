'use strict';
const host=document.getElementById('host'),status=document.getElementById('status');
let session=null,serial=0,api=null;
const ID='Ap-UM1O9RBU';
function state(s,detail=''){status.dataset.state=s;status.textContent=s+(detail?' — '+detail:'');}
function stop(s='idle'){const a=session;session=null;++serial;if(a){clearInterval(a.timer);try{a.player?.destroy();}catch{}}host.replaceChildren();state(s);}
function loadAPI(){if(api)return api;api=new Promise((resolve,reject)=>{
 const timer=setTimeout(()=>reject(Error('api-timeout')),15000);
 window.onYouTubeIframeAPIReady=()=>{clearTimeout(timer);resolve();};
 const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';script.onerror=()=>{clearTimeout(timer);reject(Error('api-error'));};document.head.append(script);
 });return api;}
async function start(){
 if(session)return;const a={seq:++serial,player:null,timer:null,prev:null,first:null,count:0};session=a;state('connecting');
 try{await loadAPI();if(session!==a)return;
 const frame=document.createElement('iframe');frame.id='live-'+a.seq;frame.title='France 24 English resmî YouTube oynatıcısı';frame.allow='autoplay; encrypted-media; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
 frame.src='https://www.youtube.com/embed/'+ID+'?enablejsapi=1&autoplay=0&playsinline=1&origin='+encodeURIComponent(location.origin);
 host.append(frame);
 const live=()=>session===a;
 const clearProof=()=>{a.prev=null;a.first=null;a.count=0;};
 a.player=new YT.Player(frame.id,{events:{
  onReady:e=>{if(!live())return;state('ready');e.target.mute();e.target.playVideo();},
  onAutoplayBlocked:()=>{if(live()){clearProof();state('manual','Oynatıcının Play düğmesini kullan');}},
  onStateChange:e=>{if(!live())return;if(e.data!==1){clearProof();state(e.data===2?'paused':e.data===3?'buffering':'await-playing');}},
  onError:e=>{if(live())stop('player-error-'+Number(e.data));}
 }});
 a.timer=setInterval(()=>{
  if(!live())return;
  try{if(a.player.getPlayerState()!==1){clearProof();return;}
   const p=a.player.getCurrentTime(),t=performance.now();if(!Number.isFinite(p)||p<0){clearProof();return;}
   const prev=a.prev;a.prev={p,t};
   if(!prev){a.first={p,t};a.count=0;return;}
   const dt=(t-prev.t)/1000,dp=p-prev.p;
   if(dt<.15||dt>2.5||dp<.16||dp>dt*2+.25){clearProof();state('await-progress');return;}
   a.count++;if(a.count>=2)state('provider-progress');
   if(a.count>=30&&t-a.first.t>=30000&&p-a.first.p>=27){state('continuous-provider-progress');console.log('SEFA-LIVE '+JSON.stringify({duration:(t-a.first.t)/1000,advance:p-a.first.p,intervals:a.count}));}
  }catch{clearProof();}
 },500);
 }catch{if(session===a)stop('api-unavailable');}
}
document.getElementById('start').onclick=start;document.getElementById('stop').onclick=()=>stop();
document.addEventListener('visibilitychange',()=>{if(document.hidden&&session)stop('hidden-stopped');});window.addEventListener('pagehide',()=>stop());
