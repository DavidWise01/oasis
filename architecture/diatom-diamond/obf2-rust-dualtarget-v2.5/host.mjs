import net from 'node:net';
import {readFileSync,writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {encodeDualBytes,decodeDualBytes,crc32} from '../astrophage-compact-v2.1.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';

const wasmPath=new URL('./obf2_rust.wasm',import.meta.url);
const {instance}=await WebAssembly.instantiate(readFileSync(wasmPath),{});
const e=instance.exports;
const mem=()=>new Uint8Array(e.memory.buffer);
const ip=e.input_ptr(),fp=e.frame_ptr(),rp=e.recovered_ptr();
if(e.max_bytes()!==65536)throw Error('wrong maxBytes');
const wasmEncode=bytes=>{
  mem().set(bytes,ip);
  const n=e.encode(bytes.length);
  if(n<0)throw Error('Rust WASM encode failed');
  return Buffer.from(mem().subarray(fp,fp+n));
};
const wasmDecode=wire=>{
  mem().set(wire,fp);
  const n=e.decode(wire.length);
  if(n<0)throw Error('Rust WASM decode failed');
  return Buffer.from(mem().subarray(rp,rp+n));
};
const p50=a=>{a.sort((x,y)=>x-y);return a[Math.floor(a.length/2)]};
const sizes=[214,4096,65536],iters=[7000,1200,140];
function sample(n){
  if(n===214)return Buffer.from(SOURCE,'utf8');
  return Uint8Array.from({length:n},(_,i)=>((i*23)^(i>>3))&255);
}
const verify=()=>{
  let assertions=0;
  const random=[new Uint8Array(),new Uint8Array([0,1,2,255]),Buffer.from(SOURCE,'utf8'),...sizes.map(sample)];
  let x=0xc0ffee12;
  const rand=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
  for(let i=0;i<1600;i++)random.push(Uint8Array.from({length:rand()%4097},()=>rand()&255));
  for(const src of random){
    const ref=encodeDualBytes(src),got=wasmEncode(src);
    if(!got.equals(ref)||!wasmDecode(got).equals(Buffer.from(src))||
       !Buffer.from(decodeDualBytes(got)).equals(Buffer.from(src)))throw Error('WASM parity failure');
    assertions+=3;
    const bad=Buffer.from(got);bad[12]^=1;
    mem().set(bad,fp);if(e.decode(bad.length)!==-1)throw Error('CRC failure');
    assertions++;
    if(src.length>0){
       const contradictory=Buffer.from(got);contradictory[12]^=1;
       contradictory.writeUInt32BE(crc32(contradictory.subarray(0,-4)),contradictory.length-4);
       mem().set(contradictory,fp);
       if(e.decode(contradictory.length)!==-1)throw Error('rail mismatch');
       assertions++;
    }
  }
  const version=Buffer.from(wasmEncode(sample(214)));version[4]=3;
  version.writeUInt32BE(crc32(version.subarray(0,-4)),version.length-4);
  mem().set(version,fp);if(e.decode(version.length)!==-1)throw Error('version accepted');
  assertions++;
  return assertions;
};
function bench(){
  const assertions=verify();
  const outcomes={version:'OBF2 unified Rust v2.4',wasmBytes:readFileSync(wasmPath).length,
    wasmMemoryBytes:e.memory.buffer.byteLength,assertions,micro:[]};
  for(let i=0;i<sizes.length;i++){
    const size=sizes[i],count=iters[i],src=sample(size);
    const methods={wasm:()=>wasmDecode(wasmEncode(src)),node:()=>decodeDualBytes(encodeDualBytes(src))};
    const timings={wasm:[],node:[]};
    for(const fn of Object.values(methods))for(let j=0;j<30;j++)fn();
    for(let sweep=0;sweep<5;sweep++){
      for(const key of sweep%2?['node','wasm']:['wasm','node']){
        const start=performance.now();
        for(let j=0;j<count;j++){const result=methods[key]();if(result.length!==size)throw Error('invalid decode')}
        timings[key].push(1000*(performance.now()-start)/count);
      }
    }
    const result={size,wasmMedianUs:p50(timings.wasm),nodeMedianUs:p50(timings.node),
      wasmSamplesUs:timings.wasm,nodeSamplesUs:timings.node};
    outcomes.micro.push(result);console.log('MICRO_RESULT='+JSON.stringify(result));
  }
  writeFileSync('wasm-micro-results.json',JSON.stringify(outcomes,null,2)+'\n');
  console.log('RUST_WASM_VERIFY='+JSON.stringify({assertions,memory:e.memory.buffer.byteLength,wasmBytes:outcomes.wasmBytes}));
}
function serve(port){
  const maxFrame=16+2*65536;
  const server=net.createServer(socket=>{
    socket.setNoDelay(true);let pending=Buffer.alloc(0);
    socket.on('data',chunk=>{
      pending=Buffer.concat([pending,chunk]);
      while(pending.length>=4){
        const n=pending.readUInt32BE(0);
        if(n<16||n>maxFrame){socket.write(Buffer.from([1,0,0,0,0]));socket.end();return}
        if(pending.length<4+n)break;
        const frame=pending.subarray(4,4+n);pending=pending.subarray(4+n);
        let reply=Buffer.alloc(0),okay=false;
        try{
          const bytes=wasmDecode(frame);
          reply=wasmEncode(bytes);okay=true;
        }catch{}
        const hdr=Buffer.alloc(5);hdr[0]=okay?0:1;hdr.writeUInt32BE(reply.length,1);
        socket.write(Buffer.concat([hdr,reply]));
      }
    });
    socket.on('error',()=>{});
  });
  server.listen(port,'127.0.0.1',()=>console.log('READY rust-wasm '+port));
}
if(process.argv[2]==='serve')serve(Number(process.argv[3]||31222));
else if(process.argv[2]==='bench')bench();
else throw Error('Usage: node host.mjs bench | serve <port>');
