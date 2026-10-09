import assert from 'node:assert/strict';
import {PRIMES,palette,state,invertIndex,blend,TOTAL} from './p339_color_hierarchy.mjs';
assert.deepEqual(PRIMES.map(x=>x.name),['jane','patricia','toph','icarium']);
assert.equal(blend('#000000','#ffffff'),'#808080');
let checks=0;
for(let k=0;k<TOTAL;k++){const s=state(k);assert.equal(invertIndex(s.hop,s.sector,s.substep),k);assert.equal(s.root,0);
 assert.equal(s.carriers.length,4);for(let i=0;i<4;i++){const p=palette(i);assert.equal(s.carriers[i].prime.name,PRIMES[i].name);
 for(const v of [p.secondary,p.tertiary,p.quaternary])assert.match(v,/^#[0-9a-f]{6}$/);checks++;}
}
assert.throws(()=>state(TOTAL));assert.throws(()=>invertIndex(0,3,0));
console.log(JSON.stringify({status:'PASS',slots:TOTAL,carrierChecks:checks,sectorSteps:120,palettes:PRIMES.map((p,i)=>palette(i))},null,2));
