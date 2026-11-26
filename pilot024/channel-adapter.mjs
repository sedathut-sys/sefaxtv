// Isolated LAB page only. Use the provider's JSChannel library, with exact origin and active window.
import {build} from './vendor/channel.mjs';
export const ORIGIN='https://video.blender.org';
let active=null;
const allowed=new Set([ORIGIN,'http://127.0.0.1:18763']);
function shape(e){
 let m;try{m=JSON.parse(e.data);}catch{return null;}
 if(!m||typeof m!=='object'||Array.isArray(m))return null;
 const known=['__ready','ready','playbackStatusUpdate','playbackStatusChange'];
 const method=typeof m.method==='string'?m.method.split('::'):[];
 return {method:method[0]==='peertube'&&known.includes(method[1])?method[1]:'other',paramsType:Array.isArray(m.params)?'array':typeof m.params,hasId:Object.hasOwn(m,'id'),hasResult:Object.hasOwn(m,'result')};
}
window.addEventListener('message',e=>{
 const a=active;
 if(!a||a.closed||e.origin!==a.origin||e.source!==a.source||typeof e.data!=='string'||e.data.length>65536){
  e.stopImmediatePropagation();if(a&&!a.closed)a.rejected++;return;
 }
 if(a.observed++<12)a.trace('wire-shape',shape(e)||{method:'malformed'});
},true);
export function openChannel({source,origin=ORIGIN,emit,trace=()=>{}}){
 if(!allowed.has(origin)||!source||active)throw Error('channel-precondition');
 const a={source,origin,closed:false,ready:false,observed:0,rejected:0,trace,channel:null};active=a;
 const live=()=>active===a&&!a.closed;
 const ready=v=>{if(live()&&v===true&&!a.ready){a.ready=true;emit({kind:'ready'});}};
 function close(){
  if(a.closed)return;a.closed=true;a.ready=false;if(active===a)active=null;
  try{a.channel?.destroy();}catch{}a.source=null;
 }
 try{
  a.channel=build({window:source,origin,scope:'peertube',onReady:()=>{if(live())trace('channel-handshake',{});}});
  a.channel.bind('ready',(_txn,v)=>{if(!live())return;if(v===false){emit({kind:'ready-rejected'});return;}ready(v);});
  a.channel.bind('playbackStatusChange',(_txn,v)=>{if(live()&&a.ready&&['playing','paused','ended','buffering','unstarted'].includes(v))emit({kind:'status-change',state:v});});
  a.channel.bind('playbackStatusUpdate',(_txn,v)=>{if(live()&&a.ready&&v&&Number.isFinite(v.position)&&v.position>=0&&['playing','paused','ended','buffering','unstarted'].includes(v.playbackState))emit({kind:'status-update',position:v.position,playbackState:v.playbackState});});
  a.channel.call({method:'isReady',timeout:15000,success:ready,error:()=>{if(live())trace('ready-query-error',{});}});
  return {close,get ready(){return a.ready;},get rejected(){return a.rejected;}};
 }catch(e){close();throw e;}
}
