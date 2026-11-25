import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {assess,sha256,canonical,hex,RECORD_FIELDS,blindView} from './verification.mjs';
const enc=new TextEncoder();
const keys=await Promise.all([0,1,2].map(()=>crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify'])));
const jwks=await Promise.all(keys.map(k=>crypto.subtle.exportKey('jwk',k.publicKey)));
const signed=async(i,r)=>hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},keys[i].privateKey,enc.encode(canonical(r,RECORD_FIELDS)))));
async function make(){
 const entries=[];
 for(let i=0;i<3;i++){
  const bytes=enc.encode('AETHER-190 synthetic physical-source fixture '+i);
  const record={schema:'AETHER-190/capture-v1',trial_id:'trial-'+i,capture_id:'capture-'+i,challenge_id:'CH-190',challenge_nonce:'nonce-'+i,capture_sha256:await sha256(bytes),sample_count:4,acquired_utc:'2026-11-24T21:00:0'+i+'Z',source_handle:'handle-'+i,verification_handle:'verify-'+i,applicant_name:'UNTRUSTED APPLICANT'};
  entries.push({bytes,record,signature_hex:await signed(i,record)});
 }
 return {entries};
}
function context(p){
 const s=new Map(),v=new Map();for(let i=0;i<3;i++){s.set('handle-'+i,{authenticated:true,root_id:'root-'+i,operator_id:'operator-'+i,administrator_id:'admin-'+i,physical_source_ancestry:'source-'+i,jwk:jwks[i]});v.set('verify-'+i,{authenticated:true,root_id:'verifier-root-'+i,operator_id:'verifier-operator-'+i,administrator_id:'verifier-admin-'+i,physical_source_ancestry:'verifier-source-'+i,capture_sha256:p.entries[i].record.capture_sha256,challenge_id:'CH-190'});}
 return {expected_challenge_id:'CH-190',expected_sample_count:4,external_source_registry:s,external_verifier_registry:v,seen_nonce_keys:new Set()};
}
const fixture=await make(),clone=()=>structuredClone(fixture),mutate=f=>{const p=clone();f(p);return p};
const cases=[
 ['not three',mutate(p=>p.entries.pop()),'THREE_BLINDED_CAPTURES_REQUIRED'],
 ['malformed entry',mutate(p=>p.entries[1].bytes=null),'MISSING_CAPTURE_OR_BYTES'],
 ['schema',mutate(p=>p.entries[1].record.schema='other'),'CAPTURE_SCHEMA_MISMATCH'],
 ['wrong hash',mutate(p=>p.entries[1].record.capture_sha256='X'),'MALFORMED_CAPTURE_HASH'],
 ['wrong challenge',mutate(p=>p.entries[1].record.challenge_id='OTHER'),'CHALLENGE_ID_MISMATCH'],
 ['samples',mutate(p=>p.entries[1].record.sample_count=8),'SAMPLE_COUNT_MISMATCH'],
 ['clock invalid',mutate(p=>p.entries[1].record.acquired_utc='invalid'),'INVALID_CAPTURE_TIME'],
 ['duplicate trial',mutate(p=>p.entries[1].record.trial_id='trial-0'),'DUPLICATE_TRIAL_ID'],
 ['duplicate capture',mutate(p=>p.entries[1].record.capture_id='capture-0'),'DUPLICATE_CAPTURE_ID'],
 ['replayed nonce',mutate(p=>p.entries[1].record.challenge_nonce='nonce-0'),'CHALLENGE_NONCE_REPLAY'],
 ['old nonce',clone(),'CHALLENGE_NONCE_REPLAY',c=>c.seen_nonce_keys.add('CH-190:nonce-1')],
 ['byte mutation',mutate(p=>p.entries[1].bytes[0]^=1),'RAW_CAPTURE_DIGEST_MISMATCH'],
 ['unknown registry',clone(),'MISSING_INDEPENDENT_REGISTRY_RECORD',c=>c.external_verifier_registry.delete('verify-1')],
 ['unauthenticated root',clone(),'EXTERNAL_CREDENTIAL_UNAUTHENTICATED',c=>c.external_source_registry.get('handle-1').authenticated=false],
 ['shared source/verifier operator',clone(),'SOURCE_VERIFIER_SHARED_CONTROL',c=>c.external_verifier_registry.get('verify-1').operator_id='operator-1'],
 ['cross-root',clone(),'CROSS_CAPTURE_SHARED_ROOT',c=>c.external_source_registry.get('handle-1').root_id='root-0'],
 ['cross-operator',clone(),'CROSS_CAPTURE_SHARED_OPERATOR',c=>c.external_source_registry.get('handle-1').operator_id='operator-0'],
 ['cross-admin',clone(),'CROSS_CAPTURE_SHARED_ADMIN',c=>c.external_source_registry.get('handle-1').administrator_id='admin-0'],
 ['physical ancestry repeat',clone(),'DUPLICATED_PHYSICAL_SOURCE_ANCESTRY',c=>c.external_source_registry.get('handle-1').physical_source_ancestry='source-0'],
 ['verifier ancestry repeat',clone(),'REUSED_EXTERNAL_VERIFIER_ANCESTRY',c=>c.external_verifier_registry.get('verify-1').physical_source_ancestry='verifier-source-0'],
 ['verification wrong hash',clone(),'EXTERNAL_VERIFICATION_MISMATCH',c=>c.external_verifier_registry.get('verify-1').capture_sha256='c'.repeat(64)],
 ['forged signature',mutate(p=>p.entries[1].signature_hex='00'.repeat(64)),'CAPTURE_SIGNATURE_INVALID'],
 ['registry provenance missing',clone(),'REGISTRIES_NOT_OUT_OF_BAND_AUTHENTICATED'],
 ['hardware missing',clone(),'ORIGINAL_HARDWARE_NOT_AUTHENTICATED'],
 ['physical replay missing',clone(),'PHYSICAL_REPLAY_NOT_AUTHENTICATED']
];
let passed=0;
for(const [name,p,reason,change]of cases){const c=context(fixture);if(change)change(c);const r=await assess(p,c);if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+JSON.stringify(r));passed++}
const b=blindView(fixture.entries[0].record);if('applicant_name' in b||JSON.stringify(b).includes('UNTRUSTED APPLICANT'))throw Error('name leaked');passed++;
const good=await assess(clone(),context(fixture));if(good.signed_capture_count!==3||good.operational_authority!=='HOLD')throw Error('valid mock signatures failed');passed++;
const spoof=await assess(clone(),{...context(fixture),external_registries_out_of_band_authenticated:true,real_hardware_origins_authenticated:true,physical_replay_observation_authenticated:true});
if(spoof.decision!=='DOCUMENTARY_BLIND_REVIEW_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('synthetic trust escalated');passed++;
console.log('AETHER-190 '+passed+'/28 synthetic blind replay checks PASS; physical 0%, ACT HOLD.');
