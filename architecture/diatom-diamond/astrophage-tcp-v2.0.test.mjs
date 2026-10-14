import assert from 'node:assert/strict';
import {createServer,createConnection} from 'node:net';
import {deflateRawSync,inflateRawSync} from 'node:zlib';
import {performance} from 'node:perf_hooks';
import {SOURCE,routeIntoOBS,recoverFromOBS} from './astrophage-field-v2.0.mjs';
const packet=routeIntoOBS(SOURCE);
const uncompressed=Buffer.from(JSON.stringify(packet),'utf8');
const compressed=deflateRawSync(uncompressed,{level:6});
const MAX_WIRE=1024*1024,MAX_INFLATED=2*1024*1024;
async function roundtrip(payload){
 const server=createServer();
 let processed; let started=0;
 const done=new Promise((resolve,reject)=>{
  server.on('connection',socket=>{
   let buffer=Buffer.alloc(0),closed=false;
   socket.on('data',bytes=>{
    if(closed)return;
    buffer=Buffer.concat([buffer,bytes]);
    if(buffer.length>=4){
     const size=buffer.readUInt32BE(0);
     if(size>MAX_WIRE){closed=true;socket.end('ERR:wire-limit');return;}
     if(buffer.length>=size+4){
      closed=true;
      try{
       const result=inflateRawSync(buffer.subarray(4,size+4),{maxOutputLength:MAX_INFLATED});
       const wire=JSON.parse(result.toString('utf8'));
       const restored=recoverFromOBS(wire);
       processed=restored;
       socket.end('OK');
      }catch{socket.end('ERR:rejected');}
     }
    }
   });
   socket.on('error',reject);
  });
  server.on('error',reject);
 });
 await new Promise((resolve,reject)=>server.listen(0,'127.0.0.1',e=>e?reject(e):resolve()));
 const port=server.address().port;
 const result=await new Promise((resolve,reject)=>{
  const c=createConnection(port,'127.0.0.1');
  let receipt='';
  c.on('connect',()=>{
   started=performance.now();
   const len=Buffer.alloc(4);len.writeUInt32BE(payload.length);
   c.write(len);c.end(payload);
  });
  c.on('data',buf=>receipt+=buf.toString('ascii'));
  c.on('close',()=>resolve({receipt,latencyMs:performance.now()-started,restored:processed}));
  c.on('error',reject);
 });
 await new Promise(resolve=>server.close(resolve));
 return result;
}
let successful=0,rejections=0;const lat=[];
for(let i=0;i<12;i++){
 const r=await roundtrip(compressed);
 assert.equal(r.receipt,'OK');assert.equal(r.restored,SOURCE);
 successful++;lat.push(r.latencyMs);
}
const corrupt=Buffer.from(compressed);corrupt[Math.floor(corrupt.length/2)]^=0xff;
const b=await roundtrip(corrupt);
assert.ok(b.receipt.startsWith('ERR:'));rejections++;
const over=await roundtrip(Buffer.alloc(MAX_WIRE+1,0));
assert.ok(over.receipt.startsWith('ERR:'));rejections++;
lat.sort((a,b)=>a-b);
const median=lat[Math.floor(lat.length/2)],p95=lat[Math.ceil(.95*lat.length)-1];
console.log(JSON.stringify({status:'PASS',successful,rejections,tokenBytes:packet.byteLength,
 wireJsonBytes:uncompressed.length,compressedBytes:compressed.length,
 compressionRatio:Number((uncompressed.length/compressed.length).toFixed(1)),
 loopbackMedianMs:Number(median.toFixed(2)),loopbackP95Ms:Number(p95.toFixed(2)),
 environment:'localhost IPv4 same machine; synthetic field, no remote network or quantum timing test'},null,2));