import {Bridge,ORIGIN} from './bridge.mjs';
import {ProgressGate} from './progress.mjs';
const $=id=>document.getElementById(id),host=$('host'),status=$('status');
let active=null,serial=0;
function log(kind,data={}){console.log('SEFA017 '+JSON.stringify({t:Math.round(performance.now()),kind,...data}));}
function state(result,proof=false){status.textContent=result;status.dataset.result=result;status.dataset.proof=proof?'yes':'no';}
function stop(result='stopped'){const a=active;active=null;++serial;status.dataset.ready='no';if(a){clearInterval(a.timer);a.bridge?.close();a.frame.remove();log('session-ended',{seq:a.seq,result});}state(result);}
function start(mode){
 stop();const seq=++serial,scope='sefa-'+Array.from(crypto.getRandomValues(new Uint8Array(16)),x=>x.toString(16).padStart(2,'0')).join('');
 const frame=document.createElement('iframe');frame.title='Blender Foundation test videosu';frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
 frame.src=ORIGIN+'/videos/embed/pAQiVCgv2CsLg79KKXUoMw?api=1&autoplay='+(mode==='auto'?'1':'0')+'&muted=1&p2p=0&scope='+scope;
 const a={seq,frame,loaded:false,gate:new ProgressGate(),bridge:null,timer:null,started:performance.now(),deadline:null};active=a;state('starting');log('start',{seq,mode});
 frame.addEventListener('load',()=>{if(active===a){a.loaded=true;log('iframe-load-not-proof',{seq});a.bridge?.ping();}});
 host.append(frame);const source=frame.contentWindow;
 a.bridge=new Bridge({source,scope,send:(m,o)=>{if(active===a&&frame.isConnected)source.postMessage(JSON.stringify(m),o);},emit:d=>{
  if(active!==a||document.hidden||!frame.isConnected)return;
  if(d.kind==='handshake'||d.kind==='not-ready'){log(d.kind,{seq});return;}
  if(d.kind==='ready-rejected'){stop('ready-rejected');return;}
  if(d.kind==='ready'){status.dataset.ready='yes';state(mode==='auto'?'ready-await-progress':'ready-await-play');if(mode==='auto')a.deadline=performance.now()+20000;log('ready',{seq});return;}
  if(d.kind==='status-change'){log('status-change',{seq,state:d.state});if(d.state!=='playing'){a.gate.reset();state('paused-or-interrupted');}return;}
  const ok=a.gate.sample(d,performance.now());log('status-update',{seq,position:d.position,playbackState:d.playbackState,gate:a.gate.reason});
  if(ok)state('provider-progress',true);else if(a.gate.lastProof===null)state('await-progress');
 }});
 a.timer=setInterval(()=>{
  if(active!==a||document.hidden)return;
  const now=performance.now();
  if(a.loaded&&!a.bridge.channel)a.bridge.ping();
  if(!a.bridge.ready&&now-a.started>20000){stop('ready-not-confirmed');return;}
  if(a.gate.lastProof!==null&&now-a.gate.lastProof>8000){a.gate.reset();state('progress-stalled');log('stall',{seq});}
  if(a.deadline!==null&&now>a.deadline&&status.dataset.proof!=='yes')stop('no-sustained-progress');
 },1000);
}
window.addEventListener('message',e=>{if(active&&active.frame.isConnected&&!document.hidden)active.bridge?.receive(e);});
$('auto').onclick=()=>start('auto');$('manual').onclick=()=>start('manual');$('stop').onclick=()=>stop();
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)stop('hidden-fresh-selection-required');});
