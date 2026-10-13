/**
 * OBS v1.3 framed streaming adaptor.
 * Frozen floor / OBS v1.1 / v1.2 are read-only dependencies.
 * Deterministic, framed dual permutations with bounded application-side buffering.
 * Not equivalent to one global P over all frames; stream framing is explicit.
 */
import {bindOBS, recoverOBS, CHUNK_BYTES} from './obs-token-bus-v1.2.mjs';
import {tokenize} from './frozen/dual5-floor-v0.7/dual5.mjs';
export const VERSION='OBS/stream-v1.3';
export const MAX_TOKENS=32;
export const MAX_TOKEN_BYTES=4980;
export const MAX_FRAME_BYTES=32768;
const enc=new TextEncoder();
function validLimit(value,max,name){if(!Number.isSafeInteger(value)||value<1||value>max)throw new RangeError(name+' must be 1..'+max);return value;}
function checkConfig(c={}){
 if(c===null||typeof c!=='object')throw new TypeError('config object expected');
 return {maxTokens:validLimit(c.maxTokens??MAX_TOKENS,MAX_TOKENS,'maxTokens'),maxBytes:validLimit(c.maxBytes??MAX_FRAME_BYTES,MAX_FRAME_BYTES,'maxBytes')};
}
export function makeFrame(tokens,seq,config={}){
 const {maxTokens,maxBytes}=checkConfig(config);
 if(!Number.isSafeInteger(seq)||seq<0)throw new RangeError('frame sequence invalid');
 if(!Array.isArray(tokens)||tokens.length<1||tokens.length>maxTokens)throw new RangeError('nonempty frame within maxTokens required');
 const bytes=tokens.reduce((n,t)=>{
  tokenize([t]);const size=enc.encode(t).byteLength;
  if(size<1||size>MAX_TOKEN_BYTES)throw new RangeError('token exceeds stream maximum '+MAX_TOKEN_BYTES+' UTF-8 bytes');
  return n+size;
 },0);
 if(bytes>maxBytes)throw new RangeError('frame exceeds maxBytes');
 const packet=bindOBS(tokens);
 return {protocol:VERSION,sequence:seq,bytes,tokens:tokens.length,fragments:packet.rails.positive.length,
  source:packet};
}
export function decodeFrame(frame,seq,config={}){
 const {maxTokens,maxBytes}=checkConfig(config);
 if(!frame||Object.keys(frame).sort().join(',')!=='bytes,fragments,protocol,sequence,source,tokens'||
    frame.protocol!==VERSION||frame.sequence!==seq||!Number.isSafeInteger(frame.bytes)||
    !Number.isSafeInteger(frame.tokens)||!Number.isSafeInteger(frame.fragments)||
    frame.bytes<1||frame.bytes>maxBytes||frame.tokens<1||frame.tokens>maxTokens||frame.fragments<1||
    frame.fragments>maxTokens*Math.ceil(MAX_TOKEN_BYTES/CHUNK_BYTES)||
    !frame.source||!Array.isArray(frame.source.rails?.positive)||
    !Array.isArray(frame.source.rails?.negative)||
    frame.source.rails.negative.length!==frame.fragments)
    throw new Error('invalid stream frame/header');
 const tokens=recoverOBS(frame.source);
 const bytes=tokens.reduce((n,t)=>n+enc.encode(t).byteLength,0);
 if(bytes!==frame.bytes||tokens.length!==frame.tokens||frame.fragments!==frame.source.rails.positive.length)
    throw new Error('frame counts mismatch');
 for(const t of tokens)if(enc.encode(t).length>MAX_TOKEN_BYTES)throw new RangeError('oversized stream token');
 return tokens;
}
async function* asAsync(iterable){for await(const x of iterable)yield x;}
export async function* encodeStream(input,config={}){
 const {maxTokens,maxBytes}=checkConfig(config);
 let buffer=[],bytes=0,sequence=0;
 for await(const token of asAsync(input)){
  tokenize([token]);const size=enc.encode(token).byteLength;
  if(size<1||size>MAX_TOKEN_BYTES||size>maxBytes)throw new RangeError('input token oversized for configured stream frame');
  if(buffer.length && (buffer.length>=maxTokens||bytes+size>maxBytes)){
   yield makeFrame(buffer,sequence++,{maxTokens,maxBytes});buffer=[];bytes=0;
  }
  buffer.push(token);bytes+=size;
 }
 if(buffer.length)yield makeFrame(buffer,sequence,{maxTokens,maxBytes});
}
export async function* decodeStream(frames,config={}){
 let seq=0;
 for await(const frame of asAsync(frames)){
  const tokens=decodeFrame(frame,seq++,config);
  for(const token of tokens)yield token;
 }
}
export async function* inspectStream(frames,config={}){
 let seq=0;
 for await(const frame of asAsync(frames)){
  const tokens=decodeFrame(frame,seq++,config);
  yield {sequence:frame.sequence,tokenCount:tokens.length,fragmentCount:frame.fragments,
    inputBytes:frame.bytes,coordinates:frame.source.rails.positive};
 }
}
export function pointForCell(cell,rail='positive'){
 // Schematic 3D projection only; full decimal coords carried unchanged.
 const o=BigInt(cell.o),b=BigInt(cell.b),s=BigInt(cell.s);
 const m=1000003n;
 const u=Number((o*65537n+b*97n+s*7919n)%m)/Number(m);
 const v=Number((b*1987n+s*113n+o*61n)%m)/Number(m);
 const w=Number((s*233n+o*17n+b*13n)%m)/Number(m);
 return {x:(u*2-1)*3.5+(rail==='positive'?-3.5:3.5),y:(v*2-1)*3.8,z:(w*2-1)*3.8};
}
export function capabilities(){return {version:VERSION,tokenLimitBytes:MAX_TOKEN_BYTES,frameLimitBytes:MAX_FRAME_BYTES,frameLimitTokens:MAX_TOKENS,baseChunkBytes:CHUNK_BYTES,stepsPerFrameBothRails:120,boundedApplicationBuffer:true,globalPacketPermutationEquivalent:false,semanticLLMInference:false};}
