import {performance} from 'node:perf_hooks';
import {createServer,createConnection} from 'node:net';
import {deflateRawSync,inflateRawSync} from 'node:zlib';
import {SOURCE,routeIntoOBS,recoverFromOBS} from './astrophage-field-v2.0.mjs';
import {encodeField,decodeField} from './astrophage-compact-v2.1.mjs';
import {writeFileSync} from 'node:fs';
const legacy=routeIntoOBS(SOURCE),oldRaw=Buffer.from(JSON.stringify(legacy)),oldCompressed=deflateRawSync(oldRaw,{level:6});
const packed=encodeField(SOURCE);const MAX_WIRE=1024*1024,MAX_INFLATE=2*1024*1024;
function restore(mode,data){if(mode==='compact')return decodeField(data);const json=inflateRawSync(data,{maxOutputLength:MAX_INFLATE});return recoverFromOBS(JSON.parse(json.toString('utf8')));}
function median(a){const x=a.slice().sort((u,v)=>u-v);return x[Math.floor(x.length/2)];}
const modes=['compact','legacy'];
let smoke=0;
for(const mode of modes){const raw=mode==='compact'?packed:oldCompressed;for(let i=0;i<2;i++){if(restore(mode,raw)!==SOURCE)throw Error('bad local recovery');smoke++;}}
function cpuBench(mode,reps){const wire=mode==='compact'?packed:oldCompressed;const times=[];for(let t=0;t<5;t++){
  const start=performance.now();for(let i=0;i<reps;i++)if(restore(mode,wire)!==SOURCE)throw Error('wrong field');times.push((performance.now()-start)/1000);
 }return {iterations:reps,medianSeconds:median(times),medianFieldsPerSec:reps/median(times),medianSourceBytesPerSec:reps*Buffer.byteLength(SOURCE)/median(times)};}
const cpu={compact:cpuBench('compact',10000),legacy:cpuBench('legacy',6)};
const server=createServer(socket=>{
 let buf=Buffer.alloc(0),expected=null;
 socket.on('data',chunk=>{
  buf=Buffer.concat([buf,chunk]);
  if(expected===null&&buf.length>=4){expected=buf.readUInt32BE(0);if(expected>MAX_WIRE){socket.end('ERR');return;}}
  if(expected!==null&&buf.length>=expected+4){const payload=buf.subarray(4,expected+4);const mode=payload.subarray(0,4).toString('ascii')==='OBF2'?'compact':'legacy';try{if(restore(mode,payload)!==SOURCE)throw Error('recovery');socket.end('OK');}catch{socket.end('ERR');}}
 });
 socket.on('error',()=>{});
});
await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve)});
const port=server.address().port;
async function ping(mode){const raw=mode==='compact'?packed:oldCompressed;const head=Buffer.alloc(4);head.writeUInt32BE(raw.length);return new Promise((resolve,reject)=>{
 let resp='';const sock=createConnection(port,'127.0.0.1');const t=performance.now();
 sock.on('connect',()=>{sock.write(head);sock.end(raw)});
 sock.on('data',x=>resp+=x.toString('ascii'));
 sock.on('close',()=>{if(resp!=='OK')reject(new Error('TCP rejected '+resp));else resolve(performance.now()-t)});
 sock.on('error',reject);
 });}
for(let i=0;i<4;i++)await ping(modes[i%2]);
const latency={compact:[],legacy:[]};for(let i=0;i<60;i++)for(const mode of (i%2===0?modes:modes.slice().reverse())){latency[mode].push(await ping(mode));}
await new Promise(resolve=>server.close(resolve));
const pct=(arr,p)=>arr.slice().sort((a,b)=>a-b)[Math.ceil(p*arr.length)-1];
const net=Object.fromEntries(modes.map(m=>[m,{runs:latency[m].length,medianMs:median(latency[m]),p95Ms:pct(latency[m],.95),p99Ms:pct(latency[m],.99)}]));
const output={status:'PASS',mode:'localhost TCP same process, connect per request; warmups=4; 60 samples per mode alternating order',originalBytes:Buffer.byteLength(SOURCE),wireBytes:{legacyJSON:oldRaw.length,legacyDeflate:oldCompressed.length,compact:packed.length},ratios:{vsLegacyJson:oldRaw.length/packed.length,vsLegacyDeflate:oldCompressed.length/packed.length},cpuDecode:cpu,tcp:net,paritySmoke:smoke,limitations:['No quantum hardware or time dilation measurement','CRC32 is not cryptographic authentication','Field is fixed canonical ASTROPHAGE payload; arbitrary payloads are separate typed bytes','CPU decode samples use different iteration counts and include parser validation','Localhost measurements exclude real WAN conditions']};
writeFileSync(new URL('./benchmark-results-v2.1.json',import.meta.url),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify(output,null,2));
