import {createHash} from 'node:crypto';
const hex=s=>createHash('sha256').update(s).digest('hex');
const ZERO='0'.repeat(64);
export function canonical(address,channels){
 if(typeof address!=='string'||!address||!Array.isArray(channels)||channels.length!==3||!channels.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('packet');
 return JSON.stringify([address,channels.map(z=>z.map(v=>Object.is(v,-0)?0:v))]);
}
export function append(ledger,address,channels){
 if(!Array.isArray(ledger))throw new TypeError('ledger');
 const previous=ledger.length?ledger.at(-1).hash:ZERO,sequence=ledger.length;
 const payload=canonical(address,channels);
 const hash=hex(JSON.stringify([sequence,previous,payload]));
 const entry=Object.freeze({sequence,previous,payload,hash});
 return Object.freeze([...ledger,entry]);
}
export function verify(ledger){
 if(!Array.isArray(ledger))return false;
 let prior=ZERO;
 for(let i=0;i<ledger.length;i++){
  const e=ledger[i];if(!e||e.sequence!==i||e.previous!==prior||typeof e.payload!=='string'||e.hash!==hex(JSON.stringify([i,prior,e.payload])))return false;
  try {const [address,channels]=JSON.parse(e.payload);if(canonical(address,channels)!==e.payload)return false;}catch{return false;}
  prior=e.hash;
 }
 return true;
}
export function head(ledger){return ledger.length?ledger.at(-1).hash:ZERO;}
