// Diagnostic only: provider-reported VOD time, not native frames or live acceptance.
export class ProgressGate {
 constructor(){this.reset();}
 reset(){this.prev=null;this.count=0;this.lastProof=null;this.reason='reset';}
 sample(d,now){
  if(!Number.isFinite(now)||!d||d.playbackState!=='playing'||typeof d.position!=='number'||!Number.isFinite(d.position)||d.position<0){
   this.reset();this.reason='not-playing-or-invalid';return false;
  }
  const p=this.prev;this.prev={position:d.position,now};
  if(!p){this.reason='baseline';return false;}
  const dt=(now-p.now)/1000,delta=d.position-p.position;
  if(dt<.15||dt>3||delta<.16||delta>dt*2+.25){
   this.count=0;this.reason='interval-outside-gate';
   if(delta<0||delta>dt*2+.25||dt<=0){this.lastProof=null;}
   return false;
  }
  if(++this.count<2){this.reason='first-interval';return false;}
  this.lastProof=now;this.reason='sustained-progress';return true;
 }
}
export function classify({ready,updates,playing,proof}){
 if(proof)return 'provider-progress';
 if(!ready)return 'ready-not-confirmed';
 if(!updates)return 'no-status-events';
 if(!playing)return 'no-playing-status';
 return 'no-sustained-progress';
}