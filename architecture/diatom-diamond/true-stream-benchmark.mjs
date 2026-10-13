/** Real Node.js Readable -> Writable stream benchmark, with backpressure from slow consumer.
 * Source tokens are generated lazily; no preallocated source token array.
 * v1.3 frames are each bounded, independent permutations, not one global permutation.
 * No neural-model inference, no Bitcoin encryption, no user data.
 */
import {Readable,Writable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {performance} from 'node:perf_hooks';
import {createHash} from 'node:crypto';
import os from 'node:os';
import {encodeStream,decodeFrame,MAX_TOKENS,MAX_FRAME_BYTES,MAX_TOKEN_BYTES} from './obs-stream-v1.3.mjs';
import {LETTERS} from './frozen/dual5-floor-v0.7/dual5.mjs';
import {digestFrame,verifyDigest,MODES} from './bitcoin-hash.mjs';
export const FRAME_TOKENS=32;
const specials=['∞','💎','@','|'];
export function tokenAt(i){
 switch(i%4){
  case 0:return LETTERS[(i*17+3)%26];
  case 1:return String(BigInt(i+1)*2654435761n)+'99999';
  case 2:return specials[(Math.floor(i/4)*7+1)%4];
  default:return '0';
 }
}
export async function runCase({tokens=10000,delayMs=0,mode='none',sampleMs=20,failAtFrame=-1,highWaterMark=1}={}){
 if(!Number.isSafeInteger(tokens)||tokens<1||tokens>1000000)throw new RangeError('tokens must be 1..1000000');
 if(!Number.isInteger(delayMs)||delayMs<0||delayMs>100)throw new RangeError('delayMs must be 0..100');
 if(!MODES.includes(mode))throw new RangeError('bad hash mode');
 if(!Number.isSafeInteger(highWaterMark)||highWaterMark<1||highWaterMark>16)throw new RangeError('bad highWaterMark');
 let generated=0,consumed=0,frames=0,cells=0,byteCount=0,maxAhead=0,maxSourceQueue=0,maxSinkQueue=0;
 let pauseEvents=0,resumeEvents=0,drainEvents=0;
 let hashedBytes=0,hashChecks=0,firstFrameAt=null,lastFrameAt=null,frameLatencies=[];
 let started=performance.now();const cpuStart=process.cpuUsage();
 const startMem=process.memoryUsage();let maxHeap=startMem.heapUsed,maxRss=startMem.rss;
 const inputHash=createHash('sha256'),outputHash=createHash('sha256');
 async function* source(){
  for(let i=0;i<tokens;i++){
   const token=tokenAt(i);
   inputHash.update(token).update('\0');
   generated++;maxAhead=Math.max(maxAhead,generated-consumed);
   yield token;
  }
 }
 const sourceFrames=(async function*(){
  for await(const frame of encodeStream(source(),{maxTokens:FRAME_TOKENS}))
   yield {frame,checksum:digestFrame(frame,mode)};
 })();
 const stream=Readable.from(sourceFrames,{objectMode:true,highWaterMark});
 stream.on('pause',()=>pauseEvents++);stream.on('resume',()=>resumeEvents++);
 const sink=new Writable({objectMode:true,highWaterMark,write(record,unused,done){
  const {frame,checksum}=record;
  const frameStart=performance.now();
  function consume(){
   try{
    if(failAtFrame>=0&&frames===failAtFrame)throw new Error('injected consumer failure');
    const t=decodeFrame(frame,frames);
    for(const token of t){
     if(token!==tokenAt(consumed))throw new Error('source-to-sink token mismatch at '+consumed);
     outputHash.update(token).update('\0');consumed++;
    }
    byteCount+=frame.bytes;cells+=frame.fragments;frames++;
    if(mode!=='none'){
     if(!checksum||checksum.length!==64||!verifyDigest(frame,checksum,mode))throw new Error('frame digest verification failed');
     hashChecks++;
     hashedBytes+=Buffer.byteLength(JSON.stringify(['OBS/v1.4/frame',frame]));
    } else if(checksum!==null)throw new Error('unexpected checksum with disabled mode');
    const now=performance.now();
    if(firstFrameAt===null)firstFrameAt=now;
    lastFrameAt=now;
    frameLatencies.push(now-frameStart);
    done();
   }catch(e){done(e);}
  }
  if(delayMs>0)setTimeout(consume,delayMs);else consume();
 }});
 sink.on('drain',()=>drainEvents++);
 const sampler=setInterval(()=>{
  const m=process.memoryUsage();maxHeap=Math.max(maxHeap,m.heapUsed);maxRss=Math.max(maxRss,m.rss);
  maxAhead=Math.max(maxAhead,generated-consumed);
  maxSourceQueue=Math.max(maxSourceQueue,stream.readableLength);
  maxSinkQueue=Math.max(maxSinkQueue,sink.writableLength);
 },sampleMs);
 try{await pipeline(stream,sink);}finally{clearInterval(sampler);}
 const elapsedMs=performance.now()-started;
 const cpu=process.cpuUsage(cpuStart);
 const finalMem=process.memoryUsage();maxHeap=Math.max(maxHeap,finalMem.heapUsed);maxRss=Math.max(maxRss,finalMem.rss);
 if(generated!==tokens||consumed!==tokens||inputHash.digest('hex')!==outputHash.digest('hex'))throw new Error('stream end-to-end digest or count mismatch');
 const latencySorted=frameLatencies.sort((a,b)=>a-b);
 const percentile=q=>latencySorted[Math.min(latencySorted.length-1,Math.ceil(latencySorted.length*q)-1)];
 return {tokens,frames,cells,sourceBytes:byteCount,frameLimitTokens:FRAME_TOKENS,hashMode:mode,sinkDelayMs:delayMs,
  elapsedMs,throughputTokensPerSecond:tokens*1000/elapsedMs,throughputFramesPerSecond:frames*1000/elapsedMs,
  throughputSourceMiBPerSecond:byteCount/1048576*1000/elapsedMs,
  cpuMs:(cpu.user+cpu.system)/1000,firstFrameMs:firstFrameAt-started,
  p50SinkCallbackMs:percentile(.5),p95SinkCallbackMs:percentile(.95),
  generated,consumed,readablePauseEvents:pauseEvents,readableResumeEvents:resumeEvents,writableDrainEvents:drainEvents,
  maxGeneratedAheadTokens:maxAhead,maxReadableBufferedFrames:maxSourceQueue,maxWritableBufferedFrames:maxSinkQueue,
  baselineHeapBytes:startMem.heapUsed,maxSampledHeapBytes:maxHeap,sampledHeapGrowthBytes:Math.max(0,maxHeap-startMem.heapUsed),
  baselineRssBytes:startMem.rss,maxSampledRssBytes:maxRss,sampledRssGrowthBytes:Math.max(0,maxRss-startMem.rss),
  hashChecks,hashedBytes,backpressureObserved:pauseEvents>0&&drainEvents>0,
  sourceIsLazy:true,sourceArrayAllocated:false};
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 const args=Object.fromEntries(process.argv.slice(2).map(s=>{const [k,v]=s.split('=');return [k.replace(/^--/,''),v]}));
 const out=await runCase({tokens:Number(args.tokens||10000),delayMs:Number(args.delay||0),mode:args.mode||'none',highWaterMark:Number(args.hwm||1)});
 console.log(JSON.stringify({release:'OBS/true-stream-v1.4',machine:{node:process.version,platform:process.platform,cpu:os.cpus()[0]?.model,parallelism:os.availableParallelism()},case:out},null,2));
}
