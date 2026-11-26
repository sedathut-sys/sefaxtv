// Read-only JSChannel-compatible PeerTube LAB adapter. Exact origin and active window.
export const ORIGIN='https://video.blender.org';
export function decode(event,source,scope,origin=ORIGIN){
 if(!source||event.source!==source||event.origin!==origin||typeof event.data!=='string'||event.data.length>4096)return null;
 let m;try{m=JSON.parse(event.data);}catch{return null;}
 if(!m||typeof m!=='object'||Array.isArray(m))return null;
 if(Object.hasOwn(m,'method')){
  if(Object.hasOwn(m,'id')||Object.hasOwn(m,'error')||Object.hasOwn(m,'result'))return null;
  if(m.method===scope+'::__ready'&&['ping','pong'].includes(m.params))return {kind:'handshake',value:m.params};
  if(m.method===scope+'::ready'&&typeof m.params==='boolean')return {kind:'ready-notice',result:m.params};
  if(m.method===scope+'::playbackStatusUpdate'){
   const d=m.params;
   if(!d||!Number.isFinite(d.position)||d.position<0||!['playing','paused','ended','buffering','unstarted'].includes(d.playbackState))return null;
   return {kind:'status-update',position:d.position,playbackState:d.playbackState};
  }
  if(m.method===scope+'::playbackStatusChange'&&['playing','paused','ended','buffering','unstarted'].includes(m.params))return {kind:'status-change',state:m.params};
  return null;
 }
 if(Number.isSafeInteger(m.id)&&m.id>=0&&!Object.hasOwn(m,'error')&&typeof m.result==='boolean')return {kind:'reply',id:m.id,result:m.result};
 return null;
}
export class Bridge{
 constructor({source,scope,send,emit,origin=ORIGIN,now=()=>performance.now()}){
  // Alternate origins are only the explicit controlled loopback test fixture.
  if(origin!==ORIGIN&&origin!=='http://127.0.0.1:18763')throw Error('origin-not-allowed');
  this.source=source;this.scope=scope;this.send=send;this.emit=emit;this.origin=origin;this.now=now;
  this.closed=false;this.channel=false;this.ready=false;this.id=0;this.pending=null;this.queried=false;this.pings=0;this.lastPing=-Infinity;
 }
 post(method,params){if(!this.closed)this.send({method:this.scope+'::'+method,params},this.origin);}
 ping(){
  if(this.closed||this.channel||this.pings>=2||this.now()-this.lastPing<3000)return false;
  this.pings++;this.lastPing=this.now();this.post('__ready','ping');return true;
 }
 query(){
  if(this.closed||!this.channel||this.ready||this.queried)return false;
  this.queried=true;this.pending=++this.id;this.send({id:this.pending,method:this.scope+'::isReady'},this.origin);return true;
 }
 markReady(){if(this.ready||this.closed)return;this.ready=true;this.pending=null;this.emit({kind:'ready'});}
 receive(event){
  if(this.closed)return false;
  const d=decode(event,this.source,this.scope,this.origin);if(!d)return false;
  if(d.kind==='handshake'){
   if(this.channel)return false;
   this.channel=true;
   if(d.value==='ping')this.post('__ready','pong');
   this.emit({kind:'handshake'});this.query();return true;
  }
  if(!this.channel)return false;
  if(d.kind==='reply'){
   if(this.pending===null||d.id!==this.pending)return false;
   this.pending=null;if(d.result===true)this.markReady();else this.emit({kind:'not-ready'});return true;
  }
  if(d.kind==='ready-notice'){
   if(d.result===true)this.markReady();else{this.ready=false;this.pending=null;this.emit({kind:'ready-rejected'});}
   return true;
  }
  if(!this.ready)return false;
  this.emit(d);return true;
 }
 close(){this.closed=true;this.ready=false;this.pending=null;this.source=null;}
}
