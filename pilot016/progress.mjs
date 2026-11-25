// Pure diagnostic only; not a production admission or a native video proof.
export class ProgressGate {
 constructor(){this.reset();}
 reset(){this.prev=null;this.count=0;this.lastProof=null;}
 sample(d,now){
  if(!Number.isFinite(now)||!d||d.playbackState!=="playing"||typeof d.position!=="number"||!Number.isFinite(d.position)||d.position<0){this.prev=null;this.count=0;return false;}
  const p=this.prev;this.prev={position:d.position,now};
  if(!p){this.count=0;return false;}
  const dt=(now-p.now)/1000,delta=d.position-p.position;
  if(dt<.15||dt>3||delta<.16||delta>dt*2+.25){this.count=0;return false;}
  if(++this.count<2)return false;
  this.lastProof=now;return true;
 }
}
