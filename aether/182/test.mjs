import {webcrypto} from 'node:crypto';
import {assess,sha256,canonicalReceipt} from './verification.mjs';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const enc=new TextEncoder(),raw=enc.encode('AETHER-182 mock capture: no physical source.'),H=x=>x.repeat(64);
const keys=['archive-A','archive-B','archive-C'];
async function fixture(){
 const m={schema:'AETHER-182/v1',capture_id:'CAP-182',challenge_id:'CH-182',generation:7,capture_sha256:await sha256(raw)};
 m.manifest_sha256=await sha256(enc.encode(JSON.stringify(m)));
 const replicas=[];
 for(let i=0;i<3;i++){
  const r={replica_id:'replica-'+i,archive_id:keys[i],root_id:'root-'+i,administrator_id:'admin-'+i,generation:7,manifest_sha256:m.manifest_sha256,bytes_sha256:m.capture_sha256,previous_receipt_sha256:null,receipt_issued_utc:'2026-11-24T20:00:00Z'};
  r.receipt_sha256=await sha256(enc.encode(canonicalReceipt(r)));
  replicas.push({bytes:new Uint8Array(raw),receipt:r});
 }
 return {manifest:m,replicas};
}
const ctx=()=>({expected_challenge_id:'CH-182',minimum_generation:7,external_archive_root_authentication:false,external_custody_signatures_authenticated:false,original_physical_capture_authenticated:false});
const change=async fn=>{const p=await fixture();fn(p);return p};
const cases=[
 ['missing',null,'THREE_REPLICAS_REQUIRED'],
 ['two replicas',await change(p=>p.replicas.pop()),'THREE_REPLICAS_REQUIRED'],
 ['wrong schema',await change(p=>p.manifest.schema='OTHER'),'INVALID_MANIFEST_SCHEMA'],
 ['challenge mismatch',await change(p=>p.manifest.challenge_id='replay'),'CHALLENGE_MISMATCH'],
 ['manifest tamper',await change(p=>p.manifest.capture_id='altered'),'MANIFEST_DIGEST_MISMATCH'],
 ['byte corruption',await change(p=>p.replicas[1].bytes[0]^=1),'REPLICA_BYTES_MISMATCH'],
 ['malformed receipt digest',await change(p=>p.replicas[1].receipt.receipt_sha256='wrong'),'INVALID_RECEIPT_DIGEST'],
 ['receipt tamper',await change(p=>p.replicas[1].receipt.receipt_issued_utc='2026-11-24T20:00:01Z'),'RECEIPT_CONTENT_MISMATCH'],
 ['replayed ID',await change(p=>p.replicas[1].receipt.replica_id='replica-0'),'DUPLICATE_REPLICA_ID'],
 ['shared archive',await change(p=>p.replicas[1].receipt.archive_id='archive-A'),'SHARED_ARCHIVE_ID'],
 ['shared root',await change(p=>p.replicas[1].receipt.root_id='root-0'),'SHARED_ROOT_ANCESTRY'],
 ['shared administrator',await change(p=>p.replicas[1].receipt.administrator_id='admin-0'),'SHARED_ADMINISTRATOR'],
 ['older archive generation',await change(p=>{p.replicas.forEach(x=>x.receipt.generation=6);p.manifest.generation=6}),'ARCHIVE_ROLLBACK'],
 ['replica generation mismatch',await change(p=>p.replicas[1].receipt.generation=5),'REPLICA_GENERATION_MISMATCH'],
 ['manifest substitution',await change(p=>p.replicas[1].receipt.manifest_sha256=H('d')),'REPLICA_MANIFEST_MISMATCH'],
 ['receipt time',await change(p=>p.replicas[1].receipt.receipt_issued_utc='not-a-time'),'INVALID_RECEIPT_TIME'],
 ['broken predecessor',await fixture(),'BROKEN_ARCHIVE_PREDECESSOR',{expected_previous_receipts:new Map([['archive-A',H('b')]])}],
 ['root authentication missing',await fixture(),'ARCHIVE_ROOTS_UNAUTHENTICATED'],
 ['signature authentication missing',await fixture(),'ARCHIVE_RECEIPTS_UNAUTHENTICATED'],
 ['physical capture missing',await fixture(),'PHYSICAL_CAPTURE_UNAUTHENTICATED']
];
let passed=0;
for(const [name,input,reason,extra]of cases){
 const r=await assess(input,{...ctx(),...extra});
 if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+JSON.stringify(r));
 passed++;
}
const spoof=await assess(await fixture(),{...ctx(),external_archive_root_authentication:true,external_custody_signatures_authenticated:true,original_physical_capture_authenticated:true});
if(spoof.status!=='DOCUMENTARY_REVIEW_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false ACT');
passed++;
console.log('AETHER-182 '+passed+'/21 synthetic checks passed; physical 0%, ACT HOLD');
