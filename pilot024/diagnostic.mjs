import {openChannel,ORIGIN} from './channel-adapter.mjs';
import {ProgressGate} from './progress.mjs';
const $=id=>document.getElementById(id),host=$('host'),status=$('status');
let active=null,serial=0;
function log(kind,data={}){console.log('SEFA017 '+JSON.stringify({t:Math.round(performance.now()),...data,kind}));}
function state(result,proof=false){status.textContent=result;status.dataset.result=result;status.dataset.proof=proof?'yes':'no';}
function stop(result='stopped'){const a=active;active=null;++serial;status.dataset.ready='no';if(a){clearInterval(a.timer);a.channel?.close();a.frame.remove();log('session-ended',{seq:a.seq,result});}state(result);}
function start(mode){
 stop();const seq=++serial,frame=document.createElement('iframe');
 frame.title='Blender Foundation test videosu';frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
 frame.src=ORIGIN+'/videos/embed/pAQiVCgv2CsLg79KKXUoMw?api=1&autoplay='+(mode==='auto'?'1':'0')+'&muted=1&p2p=0';
 const a={seq,frame,loaded:false,gate:new ProgressGate(),channel:null,timer:null,started:performance.now(),deadline:null};active=a;state('starting');log('start',{seq,mode});
 frame.addEventListener('load',()=>{if(active===a){if(a.loaded){stop('unexpected-frame-reload');return;}a.loaded=true;log('iframe-load-not-proof',{seq});}});
 host.append(frame);
 try{a.channel=openChannel({source:frame.contentWindow,trace:(kind,data)=>log(kind,{seq,...data}),emit:d=>{
  if(active!==a||document.hidden||!frame.isConnected)return;
  if(d.kind==='ready-rejected'){stop('ready-rejected');return;}
  if(d.kind==='ready'){status.dataset.ready='yes';state(mode==='auto'?'ready-await-progress':'ready-await-play');if(mode==='auto')a.deadline=performance.now()+20000;log('ready',{seq});return;}
  if(d.kind==='status-change'){log('status-change',{seq,state:d.state});if(d.state!=='playing'){a.gate.reset();state('paused-or-interrupted');}return;}
  const ok=a.gate.sample(d,performance.now());log('status-update',{seq,position:d.position,playbackState:d.playbackState,gate:a.gate.reason});
  if(ok){a.deadline=null;state('provider-progress',true);}else if(a.gate.lastProof===null)state('await-progress');
 }});}catch(e){log('channel-init-error',{seq,name:e?.name||'Error'});stop('ready-not-confirmed');return;}
 a.timer=setInterval(()=>{
  if(active!==a||document.hidden)return;const now=performance.now();
  if(!a.channel.ready&&now-a.started>20000){stop('ready-not-confirmed');return;}
  if(a.gate.lastProof!==null&&now-a.gate.lastProof>8000){a.gate.reset();state('progress-stalled');log('stall',{seq});}
  if(a.deadline!==null&&now>a.deadline&&status.dataset.proof!=='yes')stop('no-sustained-progress');
 },250);
}
$('auto').onclick=()=>start('auto');$('manual').onclick=()=>start('manual');$('stop').onclick=()=>stop();
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)stop('hidden-fresh-selection-required');});
window.addEventListener('pagehide',()=>{if(active)stop();});
