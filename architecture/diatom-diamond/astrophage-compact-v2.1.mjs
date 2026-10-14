/**
 * OASIS/KET ASTROPHAGE Compact Transport v2.1, additive to immutable v2.0.
 * Dual-rail bytes with *implicit* OBS coordinate framing and mirror complement.
 * This is deterministic classical lossless transport, not physical entanglement.
 * No signatures, witnesses, ledger, checkpoint, or new floor semantics.
 */
import {TextEncoder,TextDecoder} from 'node:util';
import {applyOperation,CODE,PASSES} from './frozen/dual5-floor-v0.7/dual5.mjs';
import {parseField,serializeField,SOURCE} from './astrophage-field-v2.0.mjs';

export const VERSION='ASTROPHAGE/compact-v2.1';
export const MAGIC='OBF2';
export const MAX_BYTES=65536;
export const HEADER_BYTES=12, CRC_BYTES=4, FRAME_OVERHEAD=16;
const encoder=new TextEncoder(),decoder=new TextDecoder('utf-8',{fatal:true});
const crcTable=Uint32Array.from({length:256},(_,i)=>{let c=i;for(let j=0;j<8;j++)c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);return c>>>0});
export function crc32(bytes){let c=0xffffffff;for(let i=0;i<bytes.length;i++)c=crcTable[(c^bytes[i])&255]^(c>>>8);return (c^0xffffffff)>>>0;}
const cache=new Map();
export function compileMaps(n){
 if(!Number.isInteger(n)||n<0||n>MAX_BYTES)throw new RangeError('OBS frame length must be 0..65536');
 const found=cache.get(n);if(found)return found;
 let plus=Array.from({length:n},(_,i)=>i);
 let minus=plus.slice().reverse();
 const p=Array.from(CODE),q=p.slice().reverse();
 for(let pass=0;pass<PASSES;pass++){
  for(const op of p)plus=applyOperation(plus,op,false);
  for(const op of q)minus=applyOperation(minus,op,true);
 }
 minus.reverse(); // legacy OBS physical d- rail: cell-order reverse, then complement
 const result={positive:Uint32Array.from(plus),negative:Uint32Array.from(minus)};
 if(cache.size>=24)cache.delete(cache.keys().next().value);
 cache.set(n,result);
 return result;
}
export function encodeDualBytes(input){
 if(!(input instanceof Uint8Array)||input.length>MAX_BYTES)throw new TypeError('expected bounded Uint8Array');
 const n=input.length,{positive,negative}=compileMaps(n);
 const output=Buffer.allocUnsafe(HEADER_BYTES+2*n+CRC_BYTES);
 output.write(MAGIC,0,'ascii');output[4]=1;output[5]=1;output.writeUInt16BE(0,6);output.writeUInt32BE(n,8);
 for(let i=0;i<n;i++){output[HEADER_BYTES+i]=input[positive[i]];output[HEADER_BYTES+n+i]=input[negative[i]];}
 output.writeUInt32BE(crc32(output.subarray(0,output.length-CRC_BYTES)),output.length-CRC_BYTES);
 return output;
}
export function decodeDualBytes(input){
 if(!(input instanceof Uint8Array)||input.length<FRAME_OVERHEAD||input.length>FRAME_OVERHEAD+2*MAX_BYTES)throw new TypeError('invalid bounded OBS compact wire');
 const wire=Buffer.isBuffer(input)?input:Buffer.from(input.buffer,input.byteOffset,input.byteLength);
 if(wire.toString('ascii',0,4)!==MAGIC||wire[4]!==1||wire[5]!==1||wire.readUInt16BE(6)!==0)throw new Error('unsupported wire header');
 const n=wire.readUInt32BE(8);
 if(n>MAX_BYTES||wire.length!==FRAME_OVERHEAD+2*n)throw new Error('inconsistent wire length');
 const actual=crc32(wire.subarray(0,wire.length-CRC_BYTES));
 if(wire.readUInt32BE(wire.length-CRC_BYTES)!==actual)throw new Error('wire CRC32 mismatch');
 const {positive,negative}=compileMaps(n),forward=Buffer.allocUnsafe(n),inverse=Buffer.allocUnsafe(n);
 for(let i=0;i<n;i++){forward[positive[i]]=wire[HEADER_BYTES+i];inverse[negative[i]]=wire[HEADER_BYTES+n+i];}
 if(!forward.equals(inverse))throw new Error('dual rail recovery mismatch');
 return forward;
}
export function encodeField(input=SOURCE){
 // same grammar and canonical source as v2.0, not an arbitrary byte payload
 const bytes=encoder.encode(serializeField(parseField(input)));
 return encodeDualBytes(bytes);
}
export function decodeField(wire){
 const bytes=decodeDualBytes(wire);
 const text=decoder.decode(bytes);
 return serializeField(parseField(text));
}
export function properties(){return {version:VERSION,wire:'12-byte header / d+ bytes / virtual-mirrored d- bytes / CRC32',maxBytes:MAX_BYTES,opsPerRail:CODE.length*PASSES,rails:2,
  interpretedObs:'Both rails carry canonical numeric byte tokens 0..255; existing o/b/s coordinates and negative complement are reproducible on demand, never serialized as 3210-digit decimal strings.',
  security:'CRC32 checks accidental corruption; not a signature, not authentication, not evidence of factual truth',
  quantum:'No quantum-state or no-latency claims.'};}
