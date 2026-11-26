import assert from 'node:assert/strict';import {FrameGate} from './frame-gate.mjs';
const g=new FrameGate(),s=(t,p,n,valid=true)=>g.sample({t,p,n,valid});
assert.equal(s(0,0,1),false);assert.equal(s(500,.5,12),false);assert.equal(s(1000,1,24),true);
assert.equal(s(1500,1,24),false);assert.equal(g.count,0);assert.equal(s(2000,2,35),false);assert.equal(s(2500,2.5,48),true);
assert.equal(s(3000,3,60,false),false);assert.equal(g.result(),null);
assert.equal(s(3500,3.5,70),false);assert.equal(s(4000,100,80),false);
g.reset();for(let i=0;i<=60;i++)s(i*500,i/2,1+12*i);assert.equal(g.result().seconds,30);assert.equal(g.result().mediaSeconds,30);assert.equal(g.result().frames,720);assert.equal(g.count,60);
console.log('PASS frame gate continuity, frozen frame, invalid state, jump, 30 seconds');
