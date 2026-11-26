// Separate smart-viewer prototype; no production catalogue, no persistent ranking.
export class Controller{
 constructor({drivers,show,clock=()=>performance.now(),limit=3}){Object.assign(this,{drivers,show,clock,limit});this.seq=0;this.active=null;this.queue=[];this.attempts=0;}
 select(sources){this.stop();this.queue=sources.slice(0,this.limit);this.attempts=0;this.next();}
 stop(){this.queue=[];this.close();this.show('idle');}
 close(){const a=this.active;this.active=null;++this.seq;if(a)a.handle?.close();}
 next(){this.close();const source=this.queue.shift();if(!source){this.show('exhausted');return;}
  const driver=this.drivers[source];if(typeof driver!=='function'){this.show('unsupported',source);return;}
  const a={seq:++this.seq,source,started:this.clock(),last:null,handle:null};this.active=a;this.attempts++;this.show('connecting',source);
  const emit=event=>{if(this.active!==a)return;const now=this.clock();
   if(event==='proof'){a.last=now;this.show('playing',source);}
   else if(event==='pause'){this.queue=[];this.close();this.show('paused',source);}
   else if(event==='manual'){this.queue=[];this.show('manual',source);}
   else if(event==='ready'){this.show('ready',source);}
   else if(event==='denied'){this.queue=[];this.close();this.show('denied',source);}
   else if(event==='error'){this.next();}
  };
  try{const h=driver(emit);if(this.active===a)a.handle=h;else h?.close();}catch{if(this.active===a)this.next();}
 }
 tick(){const a=this.active;if(!a)return;const n=this.clock();
  if(a.last!==null&&n-a.last>=8000){this.next();}
  else if(a.last===null&&n-a.started>=22000){this.next();}
 }
}
