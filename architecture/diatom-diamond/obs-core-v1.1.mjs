/**
 * {{ OBS }} nested symbolic core v1.1.
 * One axis per supplied node; exact BigInt mixed-radix indexing.
 * No ledger, checkpoints, signatures or witness requirements.
 * Numbers are cardinalities, not instantiated particles / physical memory.
 */
export const VERSION = 'OBS/core-v1.1';
export const SPEC = '{{ specs {{ OBS {{ o 10^10 {{ b 100^100 {{ s 1000^1000 }} }} }} }} }}';
export const AXES = Object.freeze([
  Object.freeze({key:'o',base:10n, exponent:10n, decPower:10, role:'outer'}),
  Object.freeze({key:'b',base:100n,exponent:100n,decPower:200,role:'body'}),
  Object.freeze({key:'s',base:1000n,exponent:1000n,decPower:3000,role:'seed'})
]);
const expected=['{{','specs','{{','OBS','{{','o','10','^','10','{{','b','100','^','100','{{','s','1000','^','1000','}}','}}','}}','}}','}}'];
export function parseSpec(input){
  if(typeof input!=='string')throw new TypeError('spec must be text');
  const tokens=input.match(/\{\{|\}\}|[A-Za-z]+|\d+|\^/g)||[];
  if(tokens.join('')!==input.replace(/\s+/g,'') || tokens.length!==expected.length || tokens.some((t,i)=>t!==expected[i]))throw new SyntaxError('invalid OBS nesting or scale');
  return {type:'specs',name:'OBS',axes:AXES.map(({key,base,exponent,decPower,role})=>({key,base:base.toString(),exponent:exponent.toString(),decimalExponent:decPower,role}))};
}
export function scale(axis){
  const found=AXES.find(a=>a.key===axis);
  if(!found)throw new RangeError('unknown OBS axis');
  return found.base ** found.exponent;
}
export const O=scale('o'), B=scale('b'), S=scale('s');
export const CAPACITY=O*B*S;
export const SCALE_DIGITS=Object.freeze({o:11,b:201,s:3001,total:3211});
function asNat(x,label){
  if(typeof x==='number' && (!Number.isSafeInteger(x)||x<0))throw new RangeError(label+' must be nonnegative safe integer or decimal string/bigint');
  if(typeof x==='string' && !/^(0|[1-9][0-9]*)$/.test(x))throw new RangeError(label+' noncanonical decimal');
  const v=typeof x==='bigint'?x:BigInt(x);
  if(v<0n)throw new RangeError(label+' negative');
  return v;
}
export function encode(o,b,s){
  const a=asNat(o,'o'),c=asNat(b,'b'),d=asNat(s,'s');
  if(a>=O||c>=B||d>=S)throw new RangeError('OBS axis exceeds its exact capacity');
  return (a*B+c)*S+d;
}
export function decode(index){
  const x=asNat(index,'index');
  if(x>=CAPACITY)throw new RangeError('index exceeds exact OBS capacity');
  const s=x%S, b=(x/S)%B, o=x/(S*B);
  return {o,b,s};
}
export function mirror({o,b,s}){
  const id=encode(o,b,s);
  const src=decode(id);
  return {o:O-1n-src.o,b:B-1n-src.b,s:S-1n-src.s};
}
export function twin(o,b,s){
  const point=decode(encode(o,b,s));
  const inverse=mirror(point);
  return {forward:point,inverse,forwardIndex:encode(point.o,point.b,point.s),inverseIndex:encode(inverse.o,inverse.b,inverse.s)};
}
export function displaySpec(){
  return {
    version:VERSION,source:SPEC,axes:AXES.map(a=>({key:a.key,role:a.role,base:a.base.toString(),exponent:a.exponent.toString(),powerOfTen:a.decPower,digits:a.decPower+1})),
    product:{formula:'10^10 × 10^200 × 10^3000',powerOfTen:3210,digits:3211},
    interpretation:'symbolic nested capacities only; spatial sizes are not scale proportional',
    witnessesRequired:false
  };
}
parseSpec(SPEC);
