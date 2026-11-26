// Only actual presented video frame metadata counts; not ready, manifest or media bytes.
export class FrameGate{
 constructor(){this.reset();}
 reset(){this.prev=null;this.first=null;this.count=0;}
 sample({t,p,n,valid}){
  if(!valid||!Number.isFinite(t)||!Number.isFinite(p)||p<0||!Number.isSafeInteger(n)||n<1){this.reset();return false;}
  const cur={t,p,n},prev=this.prev;this.prev=cur;
  if(!prev){this.first=cur;return false;}
  const dt=(t-prev.t)/1000,dp=p-prev.p;
  if(dt<.15||dt>2.5||dp<.12||dp>dt*2+.25||n<=prev.n){this.reset();this.prev=this.first=cur;return false;}
  this.count++;return this.count>=2;
 }
 result(){if(!this.first||!this.prev)return null;return{seconds:(this.prev.t-this.first.t)/1000,mediaSeconds:this.prev.p-this.first.p,frames:this.prev.n-this.first.n,intervals:this.count};}
}
