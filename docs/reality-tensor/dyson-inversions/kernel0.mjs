import {AtomicWitness} from './p443_atomic.mjs';
/** {{ | K . E | }}: kernel zero; three tracks; past/present/future. */
export class KernelZero {
 #core;
 constructor(database,keys){this.#core=new AtomicWitness(database,keys)}
 provisionGenesis(hash){return this.#core.bootstrap(hash)}
 dispatch(signedRequest){return this.#core.execute(signedRequest)}
 provisionPolicy(signedPolicy){return this.#core.applyPolicy(signedPolicy)}
 snapshot({past=null,future=null}={}){
  const r=this.#core.read();if(!r.ok)return r;
  const present=r.stamp;
  if(past&&(past.deployment!==present.deployment||!Number.isSafeInteger(past.epoch)||past.epoch>present.epoch))return {ok:false,reason:'invalid-past'};
  if(future&&(future.deployment!==present.deployment||future.epoch!==present.epoch+1||future.prior!==present.hash))return {ok:false,reason:'invalid-future-intent'};
  return {ok:true,kernel:0,tracks:['identity/intent','consequence/witness','lifecycle'],
    past:past??{epoch:present.epoch===0?null:present.epoch-1,hash:null,verified:false},
    present,future:future?{epoch:future.epoch,next:future.next,status:'candidate-uncommitted'}:null};
 }
 close(){this.#core.close()}
}
export {signPolicy,signIntent,signRequest} from './p443_atomic.mjs';
