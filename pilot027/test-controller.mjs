import assert from 'node:assert/strict';import {Controller} from './controller.mjs';
let t=0,closed=[],states=[],emitters=[];
const driver=id=>emit=>{emitters.push(emit);return{close:()=>closed.push(id)}};
const c=new Controller({drivers:{a:driver('a'),b:driver('b'),c:driver('c')},show:(...s)=>states.push(s),clock:()=>t});
c.select(['a','b','c','a']);assert.equal(c.attempts,1);emitters[0]('ready');assert.equal(states.at(-1)[0],'ready');
t=22000;c.tick();assert.equal(c.active.source,'b');assert.deepEqual(closed,['a']);
emitters[0]('proof');assert.equal(states.at(-1)[0],'connecting');
emitters[1]('proof');assert.equal(states.at(-1)[0],'playing');t+=7999;c.tick();assert.equal(c.active.source,'b');
t++;c.tick();assert.equal(c.active.source,'c');emitters[2]('error');assert.equal(states.at(-1)[0],'exhausted');assert.equal(c.attempts,3);
c.select(['a','b']);emitters.at(-1)('denied');assert.equal(states.at(-1)[0],'denied');assert.equal(c.active,null);assert.equal(c.queue.length,0);
c.select(['a','b']);emitters.at(-1)('pause');assert.equal(states.at(-1)[0],'paused');assert.equal(c.active,null);
c.select(['a']);c.stop();emitters.at(-1)('proof');assert.equal(states.at(-1)[0],'idle');
console.log('PASS smart viewer selection, readiness not proof, timeout, stall, bounded fallback, stale event, denial, pause, stop');

c.select(['a','b']);emitters.at(-1)('manual');t+=30000;c.tick();assert.equal(c.active.source,'a');emitters.at(-1)('proof');t+=8000;c.tick();assert.equal(c.active,null);console.log('PASS manual start held without automatic fallback');
