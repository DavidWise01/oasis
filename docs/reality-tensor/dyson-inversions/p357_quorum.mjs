import {generateKeyPairSync,sign,verify} from 'node:crypto';
export const CONTEXT='oasis/main',QUORUM=3;
export function witness(id){const {publicKey,privateKey}=generateKeyPairSync('ed25519');return {id,publicKey,privateKey};}
const canonical=cp=>Buffer.from(JSON.stringify({domain:'ROOT0-P357-v1',context:cp.context,epoch:cp.epoch,length:cp.length,head:cp.head}));
export function vote(w,cp){return {id:w.id,signature:sign(null,canonical(cp),w.privateKey).toString('base64')};}
export function decide(cp,votes,authorized,trusted){
 if(cp.context!==CONTEXT||!Number.isSafeInteger(cp.epoch)||cp.epoch<=trusted.epoch||!Number.isSafeInteger(cp.length)||cp.length<trusted.length||!/^[a-f0-9]{64}$/.test(cp.head))return {ok:false,reason:'policy'};
 if(!Array.isArray(votes))return {ok:false,reason:'votes'};
 const seen=new Set();let valid=0;
 for(const v of votes){if(seen.has(v.id)||!authorized.has(v.id)||typeof v.signature!=='string')continue;seen.add(v.id);try{if(verify(null,canonical(cp),authorized.get(v.id),Buffer.from(v.signature,'base64')))valid++;}catch{}}
 return valid>=QUORUM?{ok:true,votes:valid,checkpoint:cp}:{ok:false,votes:valid,reason:'quorum'};
}
export function verifyDescendant(records,trusted,candidate){if(records.length!==candidate.length)return false;if(trusted.length===0)return true;if(trusted.length>records.length)return false;return records[trusted.length-1]?.hash===trusted.head;}
export function accept(cp,votes,authorized,trusted,records){const verdict=decide(cp,votes,authorized,trusted);if(!verdict.ok)return verdict;if(!verifyDescendant(records,trusted,cp)||records.at(-1)?.hash!==cp.head)return {ok:false,reason:'fork-or-missing-chain'};return verdict;}
