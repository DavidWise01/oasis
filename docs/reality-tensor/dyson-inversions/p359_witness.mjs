import {createHash,sign,verify,generateKeyPairSync} from 'node:crypto';
export const CONTEXT='oasis/main';
export function keypair(){return generateKeyPairSync('ed25519');}
export function payload(cp){if(cp?.context!==CONTEXT||!Number.isSafeInteger(cp.epoch)||cp.epoch<0||!Number.isSafeInteger(cp.length)||cp.length<0||!(/^[0-9a-f]{64}$/.test(cp.head)))throw new RangeError('checkpoint');return Buffer.from(JSON.stringify({domain:'ROOT0-P359-v1',context:cp.context,epoch:cp.epoch,length:cp.length,head:cp.head}));}
export const fingerprint=cp=>createHash('sha256').update(payload(cp)).digest('hex');
export function makeVote(id,cp,privateKey){if(typeof id!=='string'||!id)throw new RangeError('id');return {id,checkpoint:cp,signature:sign(null,payload(cp),privateKey).toString('base64')};}
export function verifyVote(v,keys){const key=keys.get(v?.id);if(!key)return false;try{return verify(null,payload(v.checkpoint),key,Buffer.from(v.signature,'base64'));}catch{return false;}}
export function equivocation(a,b,keys){return a.id===b.id&&verifyVote(a,keys)&&verifyVote(b,keys)&&a.checkpoint.context===b.checkpoint.context&&a.checkpoint.epoch===b.checkpoint.epoch&&fingerprint(a.checkpoint)!==fingerprint(b.checkpoint);}
export function ledger(snapshot={}){const recorded=new Map(Object.entries(snapshot));return {
 vote(id,cp,privateKey){const k=`${id}|${cp.context}|${cp.epoch}`,digest=fingerprint(cp),prior=recorded.get(k);if(prior&&prior.digest!==digest)return {ok:false,reason:'double-vote',prior:prior.vote};if(prior)return {ok:true,duplicate:true,vote:prior.vote};const vote=makeVote(id,cp,privateKey);recorded.set(k,{digest,vote});return {ok:true,duplicate:false,vote};},
 snapshot(){return Object.fromEntries(recorded);}
};}