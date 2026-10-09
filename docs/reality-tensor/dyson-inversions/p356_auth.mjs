import {generateKeyPairSync,sign,verify as verifySignature} from 'node:crypto';
import {checkpoint,verify as verifyChain} from './p355_chain.mjs';
export function keypair(){return generateKeyPairSync('ed25519');}
const document=(cp,epoch,context)=>Buffer.from(JSON.stringify({domain:'ROOT0-P356-v1',context,epoch,length:cp.length,head:cp.head}));
export function seal(records,epoch,privateKey,context='oasis/main'){
 if(!Number.isSafeInteger(epoch)||epoch<0||typeof context!=='string'||!context)throw new RangeError('checkpoint fields');
 const cp=checkpoint(records);return {...cp,epoch,context,signature:sign(null,document(cp,epoch,context),privateKey).toString('base64')};
}
export function authenticate(records,stamp,publicKey,{context='oasis/main',minimumEpoch=0,minimumLength=0}={}){
 if(!stamp||!Number.isSafeInteger(stamp.epoch)||stamp.epoch<minimumEpoch||stamp.context!==context||!Number.isSafeInteger(stamp.length)||stamp.length<minimumLength)return {ok:false,reason:'policy-or-replay'};
 if(typeof stamp.head!=='string'||typeof stamp.signature!=='string')return {ok:false,reason:'format'};
 let valid=false;try{valid=verifySignature(null,document(stamp,stamp.epoch,stamp.context),publicKey,Buffer.from(stamp.signature,'base64'));}catch{}
 if(!valid)return {ok:false,reason:'signature'};
 const chain=verifyChain(records,{length:stamp.length,head:stamp.head});
 return chain.ok?{ok:true,epoch:stamp.epoch,length:stamp.length,head:stamp.head}:{ok:false,reason:chain.reason};
}
export function accept(records,stamp,publicKey,trusted){
 const verdict=authenticate(records,stamp,publicKey,{context:trusted.context,minimumEpoch:trusted.epoch,minimumLength:trusted.length});
 if(!verdict.ok)return {verdict,trusted};
 if(stamp.epoch===trusted.epoch && (stamp.head!==trusted.head||stamp.length!==trusted.length))return {verdict:{ok:false,reason:'fork-at-epoch'},trusted};
 if(trusted.length>0){const prefix=checkpoint(records.slice(0,trusted.length));if(prefix.length!==trusted.length||prefix.head!==trusted.head)return {verdict:{ok:false,reason:'non-descendant-fork'},trusted};}
 return {verdict,trusted:{context:stamp.context,epoch:stamp.epoch,length:stamp.length,head:stamp.head}};
}
