import net from 'node:net';
import {writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {encodeDualBytes,decodeDualBytes,crc32} from '../astrophage-compact-v2.1.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';
import {TextEncoder} from 'node:util';
const FIELD=new TextEncoder().encode(SOURCE);
const peers=JSON.parse(process.argv[2]||'{"cpp":31022,"rust":31023,"node":31024}');
const outputFile=process.argv[3]||'network-results.json';
const runs=[{name:'astrophage-214',bytes:FIELD,count:250},{name:'bulk-4096',bytes:Uint8Array.from({length:4096},(_,i)=>((i*19)^(i>>3))&255),count:110},{name:'max-65536',bytes:Uint8Array.from({length:65536},(_,i)=>((i*37)^(i>>7))&255),count:24}];
const rng=(size)=>Uint8Array.from({length:size},(_,i)=>(Math.imul(i+5,23)^((i*31)>>>5))&255);
const percentile=(sorted,p)=>sorted[Math.min(sorted.length-1,Math.ceil(sorted.length*p)-1)];
function connect(port){return new Promise((resolve,reject)=>{const s=net.connect({host:'127.0.0.1',port});s.setNoDelay(true);s.once('connect',()=>resolve(s));s.once('error',reject)})}
class Protocol{
 constructor(s){this.s=s;this.pending=null;this.buf=Buffer.alloc(0);s.on('data',x=>this.onData(x));s.on('error',e=>this.fail(e));s.on('close',()=>this.fail(new Error('server closed')));}
 fail(e){if(this.pending){let x=this.pending;this.pending=null;x.reject(e)}}
 onData(x){this.buf=Buffer.concat([this.buf,x]);if(this.pending&&this.buf.length>=5){const status=this.buf[0],n=this.buf.readUInt32BE(1);if(n>131088)return this.fail(new Error('oversized response'));if(this.buf.length<5+n)return;const body=this.buf.subarray(5,5+n);this.buf=this.buf.subarray(5+n);let p=this.pending;this.pending=null;p.resolve({status,body});}}
 async request(frame){if(this.pending)throw new Error('one request outstanding');let header=Buffer.allocUnsafe(4);header.writeUInt32BE(frame.length);const result=new Promise((resolve,reject)=>this.pending={resolve,reject});this.s.write(Buffer.concat([header,frame]));return await result;}
 close(){this.s.end();}
}
async function check(port){const p=new Protocol(await connect(port));for(const bytes of [new Uint8Array(),new Uint8Array([0,1,2,128,255]),FIELD,rng(33),rng(1024),rng(65536)]){const frame=encodeDualBytes(bytes),out=await p.request(frame);if(out.status!==0||!out.body.equals(frame)||!Buffer.from(decodeDualBytes(out.body)).equals(Buffer.from(bytes)))throw Error('exact OBF2 echo mismatch');}
 let bad=Buffer.from(encodeDualBytes(FIELD));bad[14]^=0x40;let r=await p.request(bad);if(r.status!==1||r.body.length!==0)throw Error('bad crc accepted');
 bad=Buffer.from(encodeDualBytes(FIELD));bad[4]=2;bad.writeUInt32BE(crc32(bad.subarray(0,-4)),bad.length-4);r=await p.request(bad);if(r.status!==1)throw Error('invalid version accepted');
 bad=Buffer.from(encodeDualBytes(FIELD));bad[12]^=1;bad.writeUInt32BE(crc32(bad.subarray(0,-4)),bad.length-4);r=await p.request(bad);if(r.status!==1)throw Error('different rails accepted');
 p.close();return {sampleSizes:[0,5,214,33,1024,65536],invalidRejections:3};}
async function testSize(port,test){const wire=encodeDualBytes(test.bytes);const p=new Protocol(await connect(port));const warmups=10;let durations=[];for(let i=0;i<warmups+test.count;i++){const begin=performance.now();const response=await p.request(wire);const ms=performance.now()-begin;if(response.status!==0||!response.body.equals(wire))throw Error('wire not identical');if(i>=warmups)durations.push(ms);}
 p.close();durations.sort((a,b)=>a-b);const timeSum=durations.reduce((a,b)=>a+b,0);return {tokensPerMessage:test.bytes.length,wireBytes:wire.length,samples:test.count,median_ms:+percentile(durations,.5).toFixed(4),p95_ms:+percentile(durations,.95).toFixed(4),p99_ms:+percentile(durations,.99).toFixed(4),total_elapsed_ms:+timeSum.toFixed(4),throughput_mibps:+((wire.length*test.count/timeSum)*(1e3/(1024*1024))).toFixed(3),wire_bytes_total:wire.length*test.count};}
let result={version:'OBF2-v2.2',runner:process.platform,benchMode:'localhost one persistent TCP socket, sequential requests, native re-encode and JS reference comparison',envelope:'4 byte request size; response status byte + 4 byte size + OBF2 frame',nodes:{},time:new Date().toISOString()};
for(const [name,port] of Object.entries(peers)){let obj={test:await check(port),runs:{}};for(const test of runs)obj.runs[test.name]=await testSize(port,test);result.nodes[name]=obj;console.log(name,JSON.stringify(obj.runs));}
writeFileSync(outputFile,JSON.stringify(result,null,2)+'\n');console.log('RESULT_FILE='+outputFile);
