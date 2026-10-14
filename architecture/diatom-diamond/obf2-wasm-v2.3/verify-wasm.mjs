import {readFileSync,writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {encodeDualBytes,decodeDualBytes,crc32} from '../astrophage-compact-v2.1.mjs';
import {SOURCE} from '../astrophage-field-v2.0.mjs';
const binary=readFileSync(new URL('./obf2_wasm.wasm',import.meta.url));
const {instance}=await WebAssembly.instantiate(binary,{});
const e=instance.exports,m=new Uint8Array(e.memory.buffer);
const ip=e.input_ptr(),fp=e.frame_ptr(),rp=e.recovered_ptr();
const enc=b=>{m.set(b,ip);const n=e.encode(b.length);if(!n)throw Error('WASM encode rejected');return Buffer.from(m.subarray(fp,fp+n));};
const dec=w=>{m.set(w,fp);const n=e.decode(w.length);if(n<0)throw Error('WASM decode rejected');return Buffer.from(m.subarray(rp,rp+n));};
let assertions=0;
const equal=(a,b)=>Buffer.compare(a,b)===0;
const field=new TextEncoder().encode(SOURCE);
const sample=[new Uint8Array(),field,...[1,2,3,4,7,8,31,32,33,256,4096,65536].map(n=>Uint8Array.from({length:n},(_,i)=>((i*23)^(i>>>3))&255))];
let seed=0xdecafbad;const rng=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0};
for(let i=0;i<1000;i++)sample.push(Uint8Array.from({length:rng()%4097},()=>rng()&255));
for(const bytes of sample){
 const ref=encodeDualBytes(bytes),got=enc(bytes);
 if(!equal(ref,got)||!equal(dec(ref),bytes)||!equal(decodeDualBytes(got),bytes))throw Error('codec parity failed');assertions+=3;
 const corrupt=Buffer.from(ref);corrupt[corrupt.length-1]^=1;
 m.set(corrupt,fp);if(e.decode(corrupt.length)!==-1)throw Error('CRC tampering accepted');assertions++;
 if(bytes.length){const mismatch=Buffer.from(ref);mismatch[12]^=1;mismatch.writeUInt32BE(crc32(mismatch.subarray(0,-4)),mismatch.length-4);m.set(mismatch,fp);if(e.decode(mismatch.length)!==-1)throw Error('rail mismatch accepted');assertions++;}
}
for(const n of [0,214,65536]){
 const bytes=Uint8Array.from({length:n},(_,i)=>i&255),frame=enc(bytes);
 frame[4]=2;frame.writeUInt32BE(crc32(frame.subarray(0,-4)),frame.length-4);
 m.set(frame,fp);if(e.decode(frame.length)!==-1)throw Error('version error accepted');assertions++;
}
function median(x){x.sort((a,b)=>a-b);return x[Math.floor(x.length/2)];}
const workloads=[['ASTROPHAGE-214',field,7000],['4KiB',sample.find(b=>b.length===4096),1200],['64KiB',sample.find(b=>b.length===65536),140]];
const results=[];
for(const [name,bytes,count] of workloads){
 let timings={wasm:[],node:[]};
 const fn={wasm:()=>dec(enc(bytes)),node:()=>decodeDualBytes(encodeDualBytes(bytes))};
 for(const f of Object.values(fn))for(let i=0;i<50;i++)f();
 for(let sweep=0;sweep<5;sweep++){for(const key of (sweep%2?['node','wasm']:['wasm','node'])){const t=performance.now();for(let k=0;k<count;k++)fn[key]();timings[key].push((performance.now()-t)*1000/count);}}
 const obj={input_bytes:bytes.length,wasm_us:+median(timings.wasm).toFixed(3),node_us:+median(timings.node).toFixed(3)};
 results.push(obj);console.log(name,JSON.stringify(obj));
}
const report={status:'PASS',version:'OBF2-WASM-v2.3',assertions,wasm_bytes:binary.length,wasm_linear_memory_bytes:e.memory.buffer.byteLength,benchmark:'same-machine single-thread Node host encode+decode, includes copy; excludes TCP',results};
writeFileSync('wasm-ci-results.json',JSON.stringify(report,null,2)+'\n');
console.log('OBF2_WASM_RESULTS='+JSON.stringify(report));
