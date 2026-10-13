// OASIS {{i & dd}} v0.7: dual symbolic permutation lanes, NOT physical quantum hardware.
// Immutable input identities; five passes of the exact instruction string UUDDLRLRBASS.
import {createHash} from 'node:crypto';

export const LEXEME = 'AaaA..ZzzZ';
export const CODE = 'UUDDLRLRBASS';
export const PASSES = 5;
export const LETTERS = Object.freeze(Array.from({length:26},(_,i)=>{
  const hi=String.fromCharCode(65+i),lo=String.fromCharCode(97+i);
  return hi+lo+lo+hi;
}));
const h = x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
const err = msg=>{throw new Error('dual5: '+msg)};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);

function valueToken(value){
  if(typeof value!=='string') err('token must be string');
  if(LETTERS.includes(value)) return {type:'letter',value};
  if(/^(?:0|[1-9][0-9]*)$/.test(value)) return {type:'number',value};
  if(Array.from(value).length===1 && /[^\p{L}\p{N}\s]/u.test(value)) return {type:'special',value};
  err('invalid symbol: '+JSON.stringify(value));
}
export function tokenize(input){
  if(!Array.isArray(input)) err('expected array of tokens');
  return input.map((raw,slot)=>Object.freeze({...valueToken(raw),slot}));
}
function normalized(records){
  if(!Array.isArray(records)) err('expected token records');
  const items=records.map((t,i)=>{
    const valid=valueToken(t?.value);
    if(t?.type!==valid.type || t?.slot!==i) err('token identity mismatch at '+i);
    return {...valid,slot:i};
  });
  return items;
}
function rot(a,k){const n=a.length;if(!n)return [];const s=((k%n)+n)%n;if(s===0)return a.slice();return a.slice(-s).concat(a.slice(0,n-s));}
function paired(a,offset){const b=a.slice();for(let i=offset;i+1<b.length;i+=2)[b[i],b[i+1]]=[b[i+1],b[i]];return b;}
export function applyOperation(input,op,inverse=false){
  const a=input.slice();
  switch(op){
    case 'U': return rot(a,inverse?-1:1);
    case 'D': return rot(a,inverse?1:-1);
    case 'L': return paired(a,0);
    case 'R': return paired(a,1);
    case 'B': return a.reverse();
    case 'A': return rot(a,inverse?-2:2);
    case 'S': return a;
    default: err('unknown operator '+op);
  }
}
export function walk(input,inverse=false,{fullFrames=false}={}){
  let a=input.slice(),prev=h(['start',inverse,a]);
  const trace=[], frames=[];
  for(let pass=0;pass<PASSES;pass++){
    const steps=inverse?Array.from(CODE).reverse():Array.from(CODE);
    for(let step=0;step<steps.length;step++){
      const op=steps[step];
      a=applyOperation(a,op,inverse);
      const head=h(['dual5-v0.7',inverse,pass,step,op,prev,a]);
      const record={pass,step,op,head,seal:op==='S'};
      trace.push(record);if(fullFrames) frames.push({ ...record,positions:a.map(t=>t.slot) });
      prev=head;
    }
  }
  return {items:a,trace,frames,head:prev};
}
export function bindDual(source, {parent='ROOT',generation=0,frames=false}={}) {
  if(typeof parent!=='string'||parent.length===0||parent.length>1024)err('bad parent');
  if(!Number.isSafeInteger(generation)||generation<0)err('bad generation');
  const tokens=tokenize(source);
  const left=walk(tokens,false,{fullFrames:frames});
  const right=walk(tokens.slice().reverse(),true,{fullFrames:frames});
  const identity=h(['dual5-identity',tokens,parent,generation]);
  const output={
    protocol:'{{i & dd}}',version:'0.7',code:CODE,passes:PASSES,
    space:'AaaA..ZzzZ + N0(BigInt decimal) + Unicode symbols',
    identity:{source:tokens,seal:identity,parent,generation},
    dual:{positive:{tokens:left.items,trace:left.trace,head:left.head},
      negative:{tokens:right.items,trace:right.trace,head:right.head}},
    witness:h(['dual5-witness',identity,left.head,right.head,left.items,right.items])
  };
  if(frames)output.frames={positive:left.frames,negative:right.frames};
  return output;
}
export function recoverDual(p){
  if(!p||p.protocol!=='{{i & dd}}'||p.version!=='0.7'||p.code!==CODE||p.passes!==PASSES)err('bad envelope');
  const id=p.identity;
  if(!id||typeof id.parent!=='string'||!id.parent.length||id.parent.length>1024||!Number.isSafeInteger(id.generation)||id.generation<0)err('bad lineage');
  const base=normalized(id.source);
  const tokens=base.map(t=>t.value);
  if(h(['dual5-identity',base,id.parent,id.generation])!==id.seal)err('identity seal mismatch');
  const left=walk(base,false), right=walk(base.slice().reverse(),true);
  for(const [rail,reference] of [['positive',left],['negative',right]]) {
    const found=p.dual?.[rail];
    if(!found||!eq(found.tokens,reference.items)||!eq(found.trace,reference.trace)||found.head!==reference.head)err('rail mismatch '+rail);
  }
  const leftInverted=walk(left.items,true).items;
  const rightInverted=walk(right.items,false).items.reverse();
  if(!eq(leftInverted,base)||!eq(rightInverted,base))err('inverse recovery failed');
  if(h(['dual5-witness',id.seal,left.head,right.head,left.items,right.items])!==p.witness)err('witness mismatch');
  return tokens;
}
export function nextGeneration(p,source){
  recoverDual(p);
  return bindDual(source,{parent:p.witness,generation:p.identity.generation+1});
}
export function dimensions(){return {alphabetFamilies:26,numericDomain:'N0 unbounded (strings)',specialDomain:'Unicode punctuation/symbols',passes:PASSES,stepsPerRail:PASSES*CODE.length,rails:2,operationsBothRails:2*PASSES*CODE.length};}
