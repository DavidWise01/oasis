import {KernelZero,signIntent,signPolicy,signRequest} from './kernel0.mjs';
/** One kernel K, nested E (emergence), nested T (time). Operators only i and u. */
export class KET {
 #kernel;
 constructor(database,keys){this.#kernel=new KernelZero(database,keys)}
 genesis(hash){return this.#kernel.provisionGenesis(hash)}
 policy(signedPolicy){return this.#kernel.provisionPolicy(signedPolicy)}
 i(signedRequest){return Object.freeze({operator:'i',intent:signedRequest})}
 u(candidate){
  if(!candidate||candidate.operator!=='i'||!candidate.intent)return {ok:false,reason:'intent-required'};
  const consequence=this.#kernel.dispatch(candidate.intent);
  return {...consequence,K:0,E:consequence.ok?'emerged':'rejected',T:this.#kernel.snapshot()};
 }
 time(views={}){const r=this.#kernel.snapshot(views);return r.ok?{K:0,E:'state',T:{past:r.past,present:r.present,future:r.future}}:r}
 close(){this.#kernel.close()}
}
export {signIntent,signPolicy,signRequest};