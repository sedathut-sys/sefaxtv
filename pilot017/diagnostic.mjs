import {ProgressGate,classify} from './progress.mjs';
const ORIGIN='https://video.blender.org', PATH='/videos/embed/pAQiVCgv2CsLg79KKXUoMw';
const $=id=>document.getElementById(id),host=$('host'),status=$('status'),play=$('play');
let active=null,serial=0,records=[];
const stamp=()=>Math.round(performance.now());
function log(kind,data={}){
 const row={t:stamp(),kind,...data};records.push(row);
 if(records.length>250)records.shift();
 $('log').textContent=records.map(r=>JSON.stringify(r)).join('\n');
 console.log('SEFA017 '+JSON.stringify(row));
}
function state(result,proof=false){status.dataset.result=result;status.dataset.proof=proof?'yes':'no';status.textContent=result;}
function stop(result='stopped'){
 ++serial;const a=active;active=null;play.disabled=true;
 if(a){clearInterval(a.timer);for(const [name,fn] of a.listeners){try{a.player?.removeEventListener(name,fn);}catch{}}
  a.frame.remove();log('session-ended',{seq:a.seq,result});}
 state(result);
}
function start(mode){
 stop();records=[];$('log').textContent='';
 const seq=++serial;
 log('start',{seq,mode,sdk:typeof window.PeerTubePlayer,secureContext:isSecureContext});
 if(typeof window.PeerTubePlayer!=='function'){state('sdk-missing');return;}
 const frame=document.createElement('iframe');frame.title='Blender Foundation açık lisanslı test videosu';
 frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
 frame.src=ORIGIN+PATH+'?api=1&autoplay='+(mode==='auto'?'1':'0')+'&muted=1&p2p=0';
 const a={seq,mode,frame,gate:new ProgressGate(),ready:false,updates:0,playing:0,started:performance.now(),deadline:null,proof:false,listeners:[],player:null,timer:null};
 active=a;state('starting');
 const current=()=>active===a&&serial===seq&&frame.isConnected;
 frame.addEventListener('load',()=>{if(current())log('iframe-load-not-proof',{seq});});
 frame.addEventListener('error',()=>{if(current())log('iframe-error-event',{seq});});
 host.append(frame);
 const on=(name,fn)=>{a.listeners.push([name,fn]);a.player.addEventListener(name,fn);};
 try{
  a.player=new window.PeerTubePlayer(frame);
  on('playbackStatusUpdate',d=>{
   if(!current()||document.hidden)return;
   a.updates++;if(d?.playbackState==='playing')a.playing++;
   const now=performance.now(),ok=a.gate.sample(d,now);
   log('status-update',{seq,position:Number.isFinite(d?.position)?d.position:null,playbackState:typeof d?.playbackState==='string'?d.playbackState.slice(0,32):null,gate:a.gate.reason});
   if(ok){a.proof=true;state('provider-progress',true);}
   else if(a.proof&&a.gate.lastProof===null){a.proof=false;a.deadline=now+20000;state('proof-revoked');}
  });
  on('playbackStatusChange',d=>{if(current())log('status-change',{seq,state:typeof d==='string'?d.slice(0,32):typeof d?.playbackState==='string'?d.playbackState.slice(0,32):null});});
  a.player.ready.then(()=>{if(!current())return;a.ready=true;play.disabled=false;log('ready',{seq});if(!a.proof)state(mode==='manual'?'ready-await-play':'ready-await-progress');if(mode==='auto')a.deadline=performance.now()+20000;}).catch(()=>{if(current()){log('ready-rejected',{seq});stop('ready-rejected');}});
  a.timer=setInterval(()=>{
   if(!current()||document.hidden)return;
   const now=performance.now();
   if(a.proof&&a.gate.lastProof!==null&&now-a.gate.lastProof>8000){a.proof=false;a.gate.reset();a.deadline=now+20000;state('progress-stalled');log('stall',{seq});}
   if(!a.ready&&now-a.started>20000){log('timeout',{seq,stage:'ready',updates:a.updates});stop('ready-not-confirmed');return;}
   if(!a.proof&&a.deadline!==null&&now>a.deadline){
    const result=classify(a);log('timeout',{seq,stage:'progress',result,updates:a.updates,playing:a.playing});stop(result);
   }
  },250);
 }catch(e){log('sdk-init-error',{seq,name:e?.name||'Error'});stop('sdk-init-error');}
}
play.onclick=()=>{
 const a=active;if(!a?.ready||!a.frame.isConnected)return;
 const seq=a.seq;a.deadline=performance.now()+20000;log('api-play-request',{seq});
 Promise.resolve().then(()=>a.player.play()).then(()=>{if(active===a)log('api-play-resolved',{seq});}).catch(e=>{if(active===a)log('api-play-rejected',{seq,name:e?.name||'Error'});});
};
$('auto').onclick=()=>start('auto');$('manual').onclick=()=>start('manual');$('stop').onclick=()=>stop();
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)stop('hidden-fresh-selection-required');});