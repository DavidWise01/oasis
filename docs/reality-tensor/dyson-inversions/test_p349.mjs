import assert from 'node:assert/strict';
import {scale,address,PRIM} from './p349_prim.mjs';
assert.equal(PRIM,'{{1/8 x 1/8}}^{{n}}');
for(let n=0;n<=32;n++){let s=scale(n);assert.equal(s.denominator,64n**BigInt(n));for(let p=0;p<4;p++)for(let a=0;a<6;a++){let x=address(n,p,a);assert.equal(x.root,0);assert.equal(x.scale.denominator,s.denominator);}}
assert.throws(()=>scale(-1));console.log('PASS 33 scales x 24 carriers/axes = 792 combinations');
