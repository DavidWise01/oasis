import assert from 'node:assert/strict';
import {PHOTONS,LITERAL,TOTAL,state,indexOf,advance,audit} from './p338_three_photons.mjs';
assert.equal(LITERAL,'{{jane::pink::patricia::purple::toph::green::}}');
assert.deepEqual(PHOTONS.map(x=>x.color),['pink','purple','green']);
for(let i=0;i<TOTAL;i++){const s=state(i),a=audit(i);assert.equal(indexOf(s.hop,s.step),i);assert.equal(s.root,0);assert.equal(s.carriers.length,3);assert.equal(a.anglesSeparated,true);assert.equal(a.rootPinned,true);assert.equal(state(advance(i,1)).index,(i+1)%TOTAL);}
assert.deepEqual([0,360,720,1080].map(x=>state(x).carriers[0].sheet),[-1,1,-1,1]);
assert.throws(()=>state(1440));assert.equal(advance(0,-1),1439);
console.log(JSON.stringify({status:'PASS',slots:TOTAL,carrierChecks:3*TOTAL,colors:PHOTONS.map(p=>p.color)}));
