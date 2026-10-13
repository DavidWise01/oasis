import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {encodeStream,decodeStream,makeFrame,decodeFrame,pointForCell,capabilities,MAX_TOKEN_BYTES} from './obs-stream-v1.3.mjs';
import {recoverOBS} from './obs-token-bus-v1.2.mjs';
import {LETTERS} from './frozen/dual5-floor-v0.7/dual5.mjs';
import {CAPACITY,O,B,S} from './obs-core-v1.1.mjs';
let assertions=0,frames=0,fragments=0;
function ok(cond,name){assert.ok(cond,name);assertions++;}
function eq(a,b,name){assert.deepEqual(a,b,name);assertions++;}
function nope(fn,name){assert.throws(fn,undefined,name);assertions++;}
async function rejectAsync(fn,name){await assert.rejects(fn,undefined,name);assertions++;}
const specials=['∞','💎','@','+','|','{','}','∑'];
let seed=0xB00B1E;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
function tokens(count){const arr=[];for(let i=0;i<count;i++){const kind=rnd()%4;arr.push(kind===0?LETTERS[rnd()%26]:kind===1?String(rnd())+String(rnd()):kind===2?specials[rnd()%specials.length]:'0');}return arr;}
async function scenario(input,config={}){
 let seen=0,buffer=[];
 const stream=encodeStream(input,config);
 for await(const f of stream){
  eq(f.sequence,seen,'ordered frame');eq(recoverOBS(f.source).length,f.tokens,'floor internal count');
  const restored=decodeFrame(f,seen,config);eq(restored.length,f.tokens,'frame local decode');
  buffer.push(...restored);seen++;frames++;fragments+=f.fragments;
  for(const c of f.source.rails.positive){const p=pointForCell(c);ok(Object.values(p).every(Number.isFinite),'finite schematic coordinates');}
 }
 eq(buffer,input,'stream exact round trip');
 const direct=[];for await(const t of decodeStream(encodeStream(input,config),config))direct.push(t);
 eq(direct,input,'pipelined stream output identical');
}
for(const n of [0,1,2,3,4,7,15,16,31,32,33,63,64,65,96,127,128,129,257])await scenario(tokens(n),{maxTokens:16});
for(let i=0;i<110;i++)await scenario(tokens(rnd()%68),{maxTokens:1+(rnd()%32),maxBytes:1000+(rnd()%16000)});
for(const n of [1244,1245,1246,2490,3700,4980])await scenario(['9'.repeat(n),'∞','AaaA'],{maxTokens:4,maxBytes:16000});
nope(()=>makeFrame([],0),'empty frame');
nope(()=>makeFrame(['0'],-1),'negative seq');
nope(()=>makeFrame(['9'.repeat(MAX_TOKEN_BYTES+1)],0),'oversized token');
nope(()=>makeFrame(['00'],0),'noncanonical numeric');
nope(()=>makeFrame(['AaaA'],0,{maxTokens:0}),'invalid config');
const f=makeFrame(['AaaA','123456789','∞'],0);
for(const change of [x=>x.sequence=4,x=>x.fragments=999,x=>x.bytes=1,x=>x.tokens=1,x=>x.source.rails.negative.pop(),x=>x.source.rails.positive.reverse(),x=>x.source.rails.positive[0].o='27']){
 const mutated=structuredClone(f);change(mutated);nope(()=>decodeFrame(mutated,0),'corrupt frame rejected');
}
await rejectAsync(async()=>{const out=[];for await(const t of decodeStream([f,structuredClone(f)]))out.push(t);},'duplicate sequence rejected');
await rejectAsync(async()=>{for await(const t of encodeStream(['AaaA','9'.repeat(MAX_TOKEN_BYTES+1)])){}},'stream rejects big input');
const caps=capabilities();eq(caps.globalPacketPermutationEquivalent,false,'honest framing semantics');eq(caps.semanticLLMInference,false,'no fake neural inference');
eq((O*B*S).toString().length,3211,'full dimension exact');
console.log(JSON.stringify({status:'PASS',version:caps.version,assertions,scenarios:19+110+6,frames,fragments,
 maxTokenBytes:MAX_TOKEN_BYTES,maxFrameTokens:caps.frameLimitTokens,maxFrameBytes:caps.frameLimitBytes,
 checks:'exact framed streaming; 2-rail decoding; tamper and range rejection; no witness dependency'},null,2));
