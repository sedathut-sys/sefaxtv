import assert from 'node:assert/strict';import {ProgressGate} from './progress.mjs';
const g=new ProgressGate(),s=(position,now,playbackState='playing')=>g.sample({position,playbackState},now);
assert.equal(s(0,0),false);assert.equal(s(.5,500),false);assert.equal(s(1,1000),true);
assert.equal(s(1,1500),false);assert.equal(s(9,2000),false);assert.equal(s(9.5,2500),false);assert.equal(s(10,3000),true);
assert.equal(s(10.5,3500,'paused'),false);assert.equal(s(11,4000),false);assert.equal(s(11.5,4500),false);assert.equal(s(12,5000),true);
assert.equal(s(12.5,9000),false);assert.equal(s(NaN,9500),false);g.reset();assert.equal(g.lastProof,null);
console.log('PASS 14 progress assertions');
