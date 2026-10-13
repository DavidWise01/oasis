/**
 * OASIS/KET OBS Token Bus v1.2 — additive link to the frozen dual floor.
 * Zero signatures, external witnesses, checkpoints, or physical quantum claims.
 * Packet = ordered sequence of canonical OBS coordinates; no monolithic 10^3210 allocation.
 */
import {encode,decode,mirror,O,B,S} from './obs-core-v1.1.mjs';
import {CODE,PASSES,applyOperation,tokenize,LETTERS} from './frozen/dual5-floor-v0.7/dual5.mjs';
export const VERSION='OBS/token-bus-v1.2';
export const CHUNK_BYTES=1245;
export const TOKEN_KIND=Object.freeze({number:26,special:27});
const encoder=new TextEncoder();
const decoder=new TextDecoder('utf-8',{fatal:true});
const same=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
function asDecimal(n,label){
  if(typeof n!=='string'||!/^(0|[1-9]\d*)$/.test(n))throw new TypeError(label+' must be a canonical decimal string');
  return BigInt(n);
}
function kindOf(value){
  const x=tokenize([value])[0];
  return x.type==='letter'?LETTERS.indexOf(value):TOKEN_KIND[x.type];
}
function bytesToSeed(bytes){
  if(bytes.length<1||bytes.length>CHUNK_BYTES)throw new RangeError('invalid fragment byte length');
  const value=BigInt('0x'+Buffer.from(bytes).toString('hex'));
  const seed=(1n << BigInt(bytes.length*8))+value;
  if(seed>=S)throw new RangeError('seed out of OBS bound');
  return seed;
}
function seedToBytes(value){
  if(value<=1n||value>=S)throw new RangeError('seed outside length-prefixed byte range');
  const hex=value.toString(16);
  if(hex[0]!=='1'||hex.length%2!==1)throw new RangeError('malformed length-prefixed seed');
  const len=(hex.length-1)/2;
  if(len<1||len>CHUNK_BYTES)throw new RangeError('seed payload length outside bound');
  return Buffer.from(hex.slice(1),'hex');
}
function canonicalCell(c){
  if(!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).sort().join(',')!=='b,o,s')throw new TypeError('cell requires exactly o,b,s');
  const o=asDecimal(c.o,'o'),b=asDecimal(c.b,'b'),s=asDecimal(c.s,'s');
  encode(o,b,s); // original v1.1 bounds and exact arithmetic
  return {o,b,s};
}
export function packTokens(tokens){
  if(!Array.isArray(tokens))throw new TypeError('expected token array');
  const cells=[];
  for(const token of tokens){
    const kind=BigInt(kindOf(token));
    const bytes=encoder.encode(token);
    for(let start=0,chunk=0n;start<bytes.length;start+=CHUNK_BYTES,chunk++){
      if(chunk>=B)throw new RangeError('token exceeds bounded OBS chunk-coordinate count');
      const s=bytesToSeed(bytes.subarray(start,start+CHUNK_BYTES));
      cells.push({o:kind.toString(),b:chunk.toString(),s:s.toString()});
    }
  }
  return cells;
}
export function unpackTokens(cells){
  if(!Array.isArray(cells))throw new TypeError('expected OBS cell array');
  const out=[];
  let activeKind=null,fragments=[],expected=0n;
  function flush(){
    if(activeKind===null)return;
    const value=decoder.decode(Buffer.concat(fragments));
    if(BigInt(kindOf(value))!==activeKind)throw new Error('token kind is not canonical');
    out.push(value);activeKind=null;fragments=[];expected=0n;
  }
  for(const raw of cells){
    const {o,b,s}=canonicalCell(raw);
    if(o>27n)throw new RangeError('unassigned OBS token kind');
    if(b===0n){flush();activeKind=o;}
    if(activeKind===null||o!==activeKind||b!==expected)throw new Error('fragment ordering or kind mismatch');
    fragments.push(seedToBytes(s));expected++;
  }
  flush();
  const canon=packTokens(out);
  if(canon.length!==cells.length||canon.some((c,i)=>c.o!==cells[i].o||c.b!==cells[i].b||c.s!==cells[i].s))throw new Error('noncanonical OBS fragment framing');
  return out;
}
export function transform(tokens,inverse=false){
  let state=tokenize(tokens).map(x=>x.value);
  const ops=inverse?Array.from(CODE).reverse():Array.from(CODE);
  for(let pass=0;pass<PASSES;pass++)for(const op of ops)state=applyOperation(state,op,inverse);
  return state;
}
function invertCell(cell){
  const {o,b,s}=canonicalCell(cell);
  const n=mirror({o,b,s});
  return {o:n.o.toString(),b:n.b.toString(),s:n.s.toString()};
}
export function bindOBS(tokens){
  tokenize(tokens); // use the exact frozen lexical semantics
  const plus=transform(tokens,false);
  const minus=transform(tokens.slice().reverse(),true);
  return {version:VERSION,frame:'{{i & dd}} / {{ OBS }}',sourceLength:tokens.length,
    floor:{code:CODE,passes:PASSES,opsPerRail:CODE.length*PASSES},
    rails:{positive:packTokens(plus),negative:packTokens(minus).reverse().map(invertCell)}};
}
export function recoverOBS(packet){
  if(!packet||packet.version!==VERSION||packet.frame!=='{{i & dd}} / {{ OBS }}'||
    packet.floor?.code!==CODE||packet.floor?.passes!==PASSES||packet.floor?.opsPerRail!==60||
    !Number.isSafeInteger(packet.sourceLength)||packet.sourceLength<0)throw new Error('bad OBS packet header');
  const plus=unpackTokens(packet.rails?.positive);
  const neg=unpackTokens(packet.rails?.negative.map(invertCell).reverse());
  const restored=transform(plus,true);
  const viaMinus=transform(neg,false).reverse();
  if(!same(restored,viaMinus)||restored.length!==packet.sourceLength)throw new Error('dual reconstruction mismatch');
  return restored;
}
export function addressView(token){
  const cells=packTokens([token]);
  return {kind:tokenize([token])[0].type,fragments:cells.length,
    addresses:cells.map(c=>encode(BigInt(c.o),BigInt(c.b),BigInt(c.s)).toString()),cells};
}
export function capacities(){return {version:VERSION,kindSlots:'28 of 10^10 outer codes assigned',bLimit:'10^200',sLimit:'10^3000',maxFragmentBytes:CHUNK_BYTES,rails:2,steps:120,space:'finite coordinate per cell, arbitrary-length streams; bounded chunk count per token',checks:'reversible framing; no security witness or physical quantum state'};}
