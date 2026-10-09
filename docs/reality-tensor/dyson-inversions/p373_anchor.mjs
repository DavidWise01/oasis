import {sign,verify} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {SerializedAuthority} from './p372_authority.mjs';
const canonical=cp=>Buffer.from(JSON.stringify({domain:'ROOT0-P373',context:cp.context,epoch:cp.epoch,count:cp.count,head:cp.head}));
export function attest(status,epoch,privateKey,context='oasis/main'){
 if(!Number.isSafeInteger(epoch)||epoch<0||!Number.isSafeInteger(status.count)||!/^[0-9a-f]{64}$/.test(status.head))throw new RangeError('checkpoint');
 const checkpoint={context,epoch,count:status.count,head:status.head};
 return {...checkpoint,signature:sign(null,canonical(checkpoint),privateKey).toString('base64')};
}
export function verifyAttestation(stamp,publicKey,context='oasis/main'){
 if(!stamp||stamp.context!==context||!Number.isSafeInteger(stamp.epoch)||!Number.isSafeInteger(stamp.count)||!/^[0-9a-f]{64}$/.test(stamp.head)||typeof stamp.signature!=='string')return false;
 try{return verify(null,canonical(stamp),publicKey,Buffer.from(stamp.signature,'base64'));}catch{return false;}
}
export function verifyAgainstTrusted(dbFile,stamp,publicKey,minimumTrusted){
 if(!verifyAttestation(stamp,publicKey))return {ok:false,reason:'invalid-signature'};
 if(!minimumTrusted||!verifyAttestation(minimumTrusted,publicKey))return {ok:false,reason:'missing-trusted-watermark'};
 if(stamp.epoch<minimumTrusted.epoch||stamp.count<minimumTrusted.count||(stamp.epoch===minimumTrusted.epoch&&(stamp.count!==minimumTrusted.count||stamp.head!==minimumTrusted.head)))return {ok:false,reason:'checkpoint-rollback'};
 const db=new SerializedAuthority(dbFile);
 try{const actual=db.status();if(actual.count!==stamp.count||actual.head!==stamp.head||actual.integrity!=='ok')return {ok:false,reason:'database-mismatch'};return {ok:true,checkpoint:stamp};}finally{db.close();}
}
export async function saveTrusted(path,stamp){await writeFile(path,JSON.stringify(stamp));}
export async function loadTrusted(path){try{return JSON.parse(await readFile(path,'utf8'));}catch{return null;}}
