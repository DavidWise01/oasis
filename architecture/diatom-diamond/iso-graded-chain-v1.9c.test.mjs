import assert from 'node:assert/strict';
import {CANONICAL,SYMBOLS,LEVELS,ARITHMETIC,I42,canonicalize,parse,route,unroute} from './iso-graded-chain-v1.9c.mjs';
let checks=0;
const eq=(a,b)=>{assert.deepEqual(a,b);checks++};
const bad=f=>{assert.throws(f);checks++};
const p=parse(CANONICAL);
eq(canonicalize(CANONICAL.replaceAll(' < ','<').replaceAll(' << ','<<').replaceAll(' <<< ','<<<').replaceAll(' <<<< ','<<<<').replaceAll(' <<<<< ','<<<<<')),CANONICAL);
eq(p.nodes.map(x=>x.glyph),SYMBOLS);eq(p.edges.map(x=>x.depth),LEVELS);
eq(p.identityOccurrences,[0,4]);eq(ARITHMETIC.value,729);eq(I42.length,42);
eq(I42.find(x=>x.id==='i4:2').glyph,'n');
eq(I42.find(x=>x.id==='i6:3').glyph,'0');
eq(I42.find(x=>x.id==='i7:4').glyph,'0');
for(const t of I42)for(let a=0;a<8;a++)for(let b=0;b<8;b++){
 const r=route(t.id,a,b);
 eq(unroute(r),t.id);eq(r.glyph,t.glyph);eq(r.sourceView,a);eq(r.targetView,b);
}
for(const s of ['', '{{i}}',CANONICAL.replace('{{so}}','{{SO}}'),CANONICAL.replace(' << ',' < '),
 CANONICAL.replace('<<<< {{i}}','<<<< {{CcC}}'),CANONICAL.replace('{{CcC}}','{{i}}'),
 CANONICAL+' !', CANONICAL.replace(' < ',' = '),CANONICAL.replace('{{Pp}}','{{pp}}')])
 bad(()=>canonicalize(s));
for(const x of [-1,8,1.5,NaN])bad(()=>route('i4:2',x,0));
for(const x of [-1,8,1.5])bad(()=>route('i4:2',0,x));
bad(()=>route('i9:0',0,0));
const altered={...route('i6:3',2,5),glyph:'x'};bad(()=>unroute(altered));
console.log(JSON.stringify({status:'PASS',checks,identities:42,views:8,viewPairs:2688,links:[1,2,3,4,5],arithmetic:729}));
