import {createHash} from 'node:crypto';
export const TOPOLOGY='-+5 + 1';
export const LANES=Object.freeze(['state','time','motion','carrier','governance']);
export const ROOT=Object.freeze({index:5,role:'independent-anchor',value:0});
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
export class TrustedAnchor {
 #epochs=new Map();
 reserve(identity,epoch,head){
  if(!Number.isSafeInteger(epoch)||epoch<0||!(/^[a-f0-9]{64}$/.test(head)))throw new RangeError('reservation');
  const key=identity+'|'+epoch,old=this.#epochs.get(key);
  if(old)return {ok:old===head,reason:old===head?'already-reserved':'equivocation'};
  this.#epochs.set(key,head);return {ok:true,reason:'reserved'};
 }
 inspect(identity,epoch){return this.#epochs.get(identity+'|'+epoch)??null;}
 checkpoint(){return hash([...this.#epochs].sort());}
}
export class FivePlusOne {
 constructor(anchor){if(!anchor||typeof anchor.reserve!=='function')throw new TypeError('independent anchor required');this.anchor=anchor;this.lanes=LANES;}
 request({identity,epoch,head,signs}){
  if(!Array.isArray(signs)||signs.length!==5||signs.some(s=>s!==-1&&s!==1))throw new RangeError('five signed lanes');
  const verdict=this.anchor.reserve(identity,epoch,head);
  return {topology:TOPOLOGY,root:ROOT.value,lanes:[...LANES],signs:[...signs],anchor:ROOT.role,...verdict};
 }
}