import assert from 'node:assert/strict';
import {packTokens,unpackTokens,bindOBS,recoverOBS,transform,addressView,capacities,CHUNK_BYTES} from './obs-token-bus-v1.2.mjs';
import {LETTERS,CODE,PASSES} from './frozen/dual5-floor-v0.7/dual5.mjs';
import {O,B,S,encode,decode,mirror} from './obs-core-v1.1.mjs';
let checks=0;let packets=0;let fragments=0;
function ok(x,msg){assert.ok(x,msg);checks++;}
function eq(x,y,msg){assert.deepEqual(x,y,msg);checks++;}
function throws(fn,msg){assert.throws(fn,undefined,msg);checks++;}
function checkTokens(t){
  const cells=packTokens(t);fragments+=cells.length;
  eq(unpackTokens(cells),t,'OBS direct token recovery');
  const packet=bindOBS(t);eq(recoverOBS(packet),t,'twin-rail recovery');
  eq(transform(transform(t),true),t,'frozen floor forward inverse');
  eq(transform(transform(t.slice().reverse(),true),false).reverse(),t,'frozen floor mirrored inverse');
  eq(packet.floor.code,CODE,'instruction literal');
  eq(packet.floor.passes,PASSES,'five passes');
  packets++;
}
const specials=['@','∑','∞','{','}','|',';',':','🔥','💎','+','-','.','!','?','\u{1F9CA}'];
checkTokens([]);checkTokens(['0']);checkTokens(LETTERS);checkTokens([...LETTERS,...specials,'0','1','10','999']);
for(const t of [...LETTERS,...specials,'0','1','12345678901234567890']){
  const d=addressView(t);eq(d.kind,t==='0'||/^\d/.test(t)?'number':LETTERS.includes(t)?'letter':'special');
  eq(d.addresses.length,d.fragments);
  for(const [i,c] of d.cells.entries()){
    const a=BigInt(d.addresses[i]);const round=decode(a);
    eq(round,{o:BigInt(c.o),b:BigInt(c.b),s:BigInt(c.s)});
    eq(mirror(mirror(round)),round);
  }
}
// Hard framing boundaries, arbitrary-precision numeric strings, UTF-8 multi-byte symbols.
for(const len of [1,2,10,40,1024,1244,1245,1246,2490,2500,5000,9000]){
  const number='9'.repeat(len);
  checkTokens([number,'∞','AaaA',number]);
  const parts=packTokens([number]);eq(unpackTokens(parts),[number]);
  ok(parts.length===Math.ceil(len/CHUNK_BYTES));
}
// Deterministic seeded packets exercise repeated token kinds / fragment resets.
let seed=0xC0FFEE;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
for(let i=0;i<360;i++){
  const n=rnd()%29,arr=[];
  for(let j=0;j<n;j++){
    const kind=rnd()%3;
    arr.push(kind===0?LETTERS[rnd()%26]:kind===1?String(rnd())+(rnd()%2?'9999':''):specials[rnd()%specials.length]);
  }
  checkTokens(arr);
}
// Empty packets and typed framing integrity with malformed input.
throws(()=>packTokens(['Hello']),'reject untyped text');
throws(()=>packTokens(['001']),'reject noncanonical numeric');
throws(()=>packTokens(['-1']),'negative number not a numeric token'); // -1 would require two tokens
throws(()=>packTokens(['a']),'lowercase word is not canonical');
throws(()=>packTokens(['💎💎']),'multiple symbols are not one token');
throws(()=>unpackTokens([{o:'28',b:'0',s:'257'}]),'reserved kind');
throws(()=>unpackTokens([{o:'26',b:'1',s:'257'}]),'no first fragment');
throws(()=>unpackTokens([{o:'26',b:'0',s:'1'}]),'no empty seed payload');
throws(()=>unpackTokens([{o:'26',b:'0',s:'256'}]),'seed sentinel missing');
throws(()=>unpackTokens([{o:'26',b:'0',s:'0257'}]),'no leading zero coordinates');
throws(()=>unpackTokens([{o:'26',b:'0',s:'257',extra:'a'}]),'no silent extra fields');
throws(()=>unpackTokens([{o:O.toString(),b:'0',s:'257'}]),'o upper bound');
throws(()=>unpackTokens([{o:'26',b:B.toString(),s:'257'}]),'b upper bound');
throws(()=>unpackTokens([{o:'26',b:'0',s:S.toString()}]),'s upper bound');
const x=bindOBS(['AaaA','42','∞','ZzzZ']);
const swapped=structuredClone(x);swapped.rails.negative.reverse();throws(()=>recoverOBS(swapped),'negative order tamper');
const broken=structuredClone(x);broken.rails.positive[0].b='12';throws(()=>recoverOBS(broken),'fragment index mismatch');
const altered=structuredClone(x);altered.floor.code='UUDDLRLRBASZ';throws(()=>recoverOBS(altered),'floor literal mismatch');
const cross=structuredClone(x);cross.sourceLength=3;throws(()=>recoverOBS(cross),'length mismatch');
// Values near exact huge bound remain codec-valid for generic OBS addresses.
const hi=encode(O-1n,B-1n,S-1n);eq(hi.toString().length,3210);eq(decode(hi),{o:O-1n,b:B-1n,s:S-1n});
const cap=capacities();eq(cap.maxFragmentBytes,1245);eq(cap.steps,120);
const result={status:'PASS',version:'OBS/token-bus-v1.2',assertions:checks,packets,fragments,
 canonicalLetterFamilies:26,specialSample:specials.length,maxNumericDigitsTested:9000,
 obsAddressDigits:3210,floor:'UUDDLRLRBASS × 5 per rail',
 hardwareQuantumDemonstrated:false,witnessRequired:false};
console.log(JSON.stringify(result,null,2));
