import assert from 'node:assert/strict';
import {frame,compose,inverse,PRIMITIVE} from './p333_spinor_frame.mjs';
assert.equal(PRIMITIVE,'{{ -+- : +-+ }}');
let s=frame(0);for(let i=0;i<100000;i++){const result=compose(s);assert.equal(result.signedNumerator,0);assert.equal(result.completedFrameNumerator/result.denominator,1);s=result.next;}
assert.equal(s.frame,100000);
for(let i=0;i<100000;i++)s=inverse(compose(frame(i)));
assert.deepEqual(s,frame(99999));
assert.deepEqual(inverse(compose(frame(0))),frame(0));
assert.throws(()=>inverse({...compose(frame(0)),events:[]}));
console.log(JSON.stringify({status:'PASS',frames:100000,gravity:-0.5,time:0.5,signedBalance:0,frameUnit:1}));
