/** OBS symbolic throughput benchmark, not a neural-model inference benchmark. */
import {performance} from 'node:perf_hooks';
import {createHash} from 'node:crypto';
import os from 'node:os';
import {bindOBS,recoverOBS} from './obs-token-bus-v1.2.mjs';
import {encodeStream,decodeFrame} from './obs-stream-v1.3.mjs';
import {LETTERS} from './frozen/dual5-floor-v0.7/dual5.mjs';
const sizes=[512,2048,8192];
const rounds=5;
const specials=['∞','💎','@','|'];
function makeTokens(n){let seed=0xC0FEE;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};const a=[];for(let i=0;i<n;i++){
 const k=i%4;a.push(k===0?LETTERS[rnd()%26]:k===1?String(rnd())+String(rnd()):k===2?specials[rnd()%specials.length]:'0');
}return a;}
function digestTokens(tokens){const h=createHash('sha256');for(const t of tokens)h.update(Buffer.from(t)).update('\0');return h.digest('hex');}
function pct(a,p){const s=a.slice().sort((x,y)=>x-y);return s[Math.min(s.length-1,Math.ceil(s.length*p)-1)];}
function med(a){return pct(a,.5);}
function mem(){return process.memoryUsage().heapUsed;}
function gc(){if(global.gc)global.gc();}
async function onceLegacy(tokens){
 const start=performance.now();let h0=mem();
 const packet=bindOBS(tokens);const cells=packet.rails.positive.length;let peak=Math.max(h0,mem());
 const recovered=recoverOBS(packet);peak=Math.max(peak,mem());
 if(recovered.length!==tokens.length||digestTokens(recovered)!==digestTokens(tokens))throw Error('legacy recovery mismatch');
 return {ms:performance.now()-start,frames:1,cells,heapDeltaBytes:Math.max(0,peak-h0)};
}
async function onceStream(tokens,limit=32){
 const start=performance.now();const h0=mem();let peak=h0,frames=0,cells=0,count=0;
 const h=createHash('sha256');
 for await(const packet of encodeStream(tokens,{maxTokens:limit})){
  const output=decodeFrame(packet,frames);for(const t of output){h.update(Buffer.from(t)).update('\0');count++;}
  frames++;cells+=packet.fragments;peak=Math.max(peak,mem());
 }
 if(count!==tokens.length||h.digest('hex')!==digestTokens(tokens))throw Error('stream mismatch');
 return {ms:performance.now()-start,frames,cells,heapDeltaBytes:Math.max(0,peak-h0)};
}
const out=[];
for(const n of sizes){
 const tokens=makeTokens(n);const target=digestTokens(tokens);const results={};
 for(const [label,runner] of [['v1.2_full_packet',onceLegacy],['v1.3_framed_32',onceStream]]){
  await runner(tokens);const raw=[];
  for(let j=0;j<rounds;j++){gc();raw.push(await runner(tokens));}
  const ms=raw.map(r=>r.ms),tokensps=raw.map(r=>n/(r.ms/1000)), medianMs=med(ms);
  results[label]={rounds,medianElapsedMs:medianMs,p95ElapsedMs:pct(ms,.95),medianTokensPerSec:med(tokensps),
    medianFramesPerSec:med(raw.map(r=>r.frames/(r.ms/1000))),medianCellsPerSec:med(raw.map(r=>r.cells/(r.ms/1000))),
    frameCount:raw[0].frames,cellCountPerRail:raw[0].cells,
    maxObservedHeapDeltaBytes:Math.max(...raw.map(r=>r.heapDeltaBytes)),
    individualElapsedMs:ms.map(x=>Math.round(x*1e3)/1e3)};
 }
 out.push({tokens:n,results,relativeTokenThroughput:results['v1.3_framed_32'].medianTokensPerSec/results['v1.2_full_packet'].medianTokensPerSec});
 console.error('Completed',n,'tokens');
}
console.log(JSON.stringify({release:'OBS/stream-v1.3',benchmark:'dual OBS symbolic token routing, NOT neural inference',
 node:process.version,cpus:os.availableParallelism(),platform:process.platform,
 clock:'performance.now',measure:'warmup 1 then 5 sequential runs; median and p95 elapsed',
 workload:'alternating 26 canonical letter tokens, 9-20 digit integer tokens, special symbols, and zero; CPU only',
 packetSemantics:'v1.2 applies P to whole packet; v1.3 applies same P independently within bounded 32-token frames; outputs both decode to same source',
 limits:{maxFrameTokens:32,maxFrameUTF8Bytes:32768,maxTokenUTF8Bytes:4980},
 externalInputsRetainedInMemory:true,streamingMemoryClaim:'Only the v1.3 adapter buffers bounded in-flight frames; benchmark source array is preallocated outside the adapter; peak heap sampling approximate',
 results:out},null,2));
