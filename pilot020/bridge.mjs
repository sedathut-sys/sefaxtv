// Experimental narrow JSChannel-compatible read-only PeerTube adapter.
// Source: PeerTube embed API and Mozilla JSChannel wire format. Not an official SDK.
export const ORIGIN='https://video.blender.org';
export function decode(event,source,scope){
 if(!source||event.source!==source||event.origin!==ORIGIN||typeof event.data!=='string'||event.data.length>4096)return null;
 let m;try{m=JSON.parse(event.data);}catch{return null;}
 if(!m||typeof m!=='object'||Array.isArray(m))return null;
 if(Object.hasOwn(m,'method')){
  if(Object.hasOwn(m,'id')||Object.hasOwn(m,'error')||Object.hasOwn(m,'result'))return null;
  if(m.method===scope+'::__ready'&&['ping','pong'].includes(m.params))return {kind:'handshake',value:m.params};
  if(m.method===scope+'::ready')return {kind:'ready-notice'};
  if(m.method===scope+'::playbackStatusUpdate'){
   const d=m.params;
   if(!d||!Number.isFinite(d.position)||d.position<0||!['playing','paused','ended','buffering','unstarted'].includes(d.playbackState))return null;
   return {kind:'status-update',position:d.position,playbackState:d.playbackState};
  }
  if(m.method===scope+'::playbackStatusChange'){
   const state=typeof m.params==='string'?m.params:m.params?.playbackState;
   return typeof state==='string'&&state.length<=32?{kind:'status-change',state}:null;
  }
  return null;
 }
 if(Number.isSafeInteger(m.id)&&m.id>=0&&!Object.hasOwn(m,'error')&&typeof m.result==='boolean')return {kind:'reply',id:m.id,result:m.result};
 return null;
}
export class Bridge{
 constructor({source,scope,send,emit}){this.source=source;this.scope=scope;this.send=send;this.emit=emit;this.closed=false;this.channel=false;this.ready=false;this.id=0;this.pending=null;}
 post(method,params){if(!this.closed)this.send({method:this.scope+'::'+method,params},ORIGIN);}
 ping(){if(!this.channel)this.post('__ready','ping');}
 query(){if(this.closed||!this.channel||this.ready)return;this.pending=++this.id;this.send({id:this.pending,method:this.scope+'::isReady'},ORIGIN);}
 receive(event){
  if(this.closed)return false;
  const d=decode(event,this.source,this.scope);if(!d)return false;
  if(d.kind==='handshake'){
   if(d.value==='ping')this.post('__ready','pong');
   if(!this.channel){this.channel=true;this.query();}
   return true;
  }
  if(!this.channel)return false;
  if(d.kind==='reply'){
   if(d.id!==this.pending)return false;this.pending=null;
   if(d.result===true&&!this.ready){this.ready=true;this.emit({kind:'ready'});}
   return true;
  }
  if(d.kind==='ready-notice'){if(!this.ready)this.query();return true;}
  if(!this.ready)return false;
  this.emit(d);return true;
 }
 close(){this.closed=true;this.ready=false;this.pending=null;this.source=null;}
}
