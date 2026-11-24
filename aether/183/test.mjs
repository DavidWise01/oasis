import {webcrypto} from 'node:crypto';
import {assess,sha256,blindView} from './verification.mjs';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const enc=new TextEncoder(),raw=enc.encode('AETHER-183 synthetic evidence: NOT ORIGINAL PHYSICAL HARDWARE');
let hash=await sha256(raw);
const base=()=>({trial_id:'TRIAL-183',capture_id:'CAP-183',capture_sha256:hash,challenge_id:'C-183',sample_count:3,time_start_ms:10,time_end_ms:20,raw_bytes:new Uint8Array(raw),roots:[0,1,2].map(i=>({handle:'handle-'+i,archive_sha256:hash,claimed_name:'untrusted-claim-'+i}))});
const att=()=>new Map([0,1,2].map(i=>['handle-'+i,{authenticated:true,capture_sha256:hash,challenge_id:'C-183',ancestry_root:'root-'+i,issuer_id:'issuer-'+i,administrator_id:'admin-'+i}]));
const policy=()=>({expected_challenge_id:'C-183',expected_sample_count:3,root_attestations:att(),used_capture_ids:new Set(),used_trial_ids:new Set(),independent_verification_service_authenticated:false,raw_physical_acquisition_authenticated:false,calibrated_physical_clock_authenticated:false,physical_alarm_evidence_authenticated:false});
const edit=fn=>{let b=base();fn(b);return b};
const policies=fn=>{let p=policy();fn(p);return p};
const checks=[
['missing bytes',null,policy(),'MISSING_ORIGINAL_BYTES_OR_ROOTS'],
['wrong challenge',edit(b=>b.challenge_id='BAD'),policy(),'CHALLENGE_MISMATCH'],
['capture replay',base(),policies(p=>p.used_capture_ids.add('CAP-183')),'REPLAYED_CAPTURE'],
['trial replay',base(),policies(p=>p.used_trial_ids.add('TRIAL-183')),'REPLAYED_TRIAL'],
['sample mismatch',edit(b=>b.sample_count=4),policy(),'SAMPLE_COUNT_MISMATCH'],
['clock inversion',edit(b=>b.time_end_ms=4),policy(),'INVALID_CAPTURE_WINDOW'],
['only two roots',edit(b=>b.roots.pop()),policy(),'THREE_SOURCE_ROOTS_REQUIRED'],
['duplicate root handle',edit(b=>b.roots[1].handle='handle-0'),policy(),'DUPLICATE_ROOT_HANDLE'],
['invalid archive hash',edit(b=>b.roots[1].archive_sha256='invalid'),policy(),'INVALID_ARCHIVE_DIGEST'],
['archive mismatch',edit(b=>b.roots[1].archive_sha256='b'.repeat(64)),policy(),'ARCHIVE_CAPTURE_MISMATCH'],
['byte substitution',edit(b=>b.raw_bytes[0]^=1),policy(),'CAPTURE_BYTE_MISMATCH'],
['missing external root',base(),policies(p=>p.root_attestations.delete('handle-1')),'MISSING_EXTERNAL_ROOT_ATTESTATION'],
['unverified root',base(),policies(p=>p.root_attestations.get('handle-1').authenticated=false),'ROOT_ATTESTATION_NOT_AUTHENTICATED'],
['common root ancestry',base(),policies(p=>p.root_attestations.get('handle-1').ancestry_root='root-0'),'COMMON_ROOT_ANCESTRY'],
['common issuer',base(),policies(p=>p.root_attestations.get('handle-1').issuer_id='issuer-0'),'COMMON_ISSUER'],
['common administrator',base(),policies(p=>p.root_attestations.get('handle-1').administrator_id='admin-0'),'COMMON_ADMINISTRATOR'],
['external verifier missing',base(),policy(),'INDEPENDENT_VERIFIER_NOT_AUTHENTICATED'],
['physical acquisition missing',base(),policy(),'ORIGINAL_HARDWARE_ACQUISITION_NOT_AUTHENTICATED'],
['calibrated clock missing',base(),policy(),'PHYSICAL_CLOCK_NOT_AUTHENTICATED'],
['alarm missing',base(),policy(),'PHYSICAL_ALARM_NOT_AUTHENTICATED']
];
let n=0;
for(const [name,b,p,reason]of checks){const r=await assess(b,p);if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+': '+JSON.stringify(r));n++}
const blind=blindView(base());
if(!blind||'claimed_name'in blind||JSON.stringify(blind).includes('untrusted-claim'))throw Error('Blind review leaked applicant claims');n++;
const forged=await assess(base(),policies(p=>{p.independent_verification_service_authenticated=true;p.raw_physical_acquisition_authenticated=true;p.calibrated_physical_clock_authenticated=true;p.physical_alarm_evidence_authenticated=true}));
if(forged.decision!=='DOCUMENTARY_SCREEN_ONLY'||forged.operational_authority!=='HOLD'||forged.physical_act_allowed)throw Error('Mock attestations promoted physical ACT');n++;
console.log('AETHER-183 '+n+'/22 synthetic cases PASS. Physical 0%, ACT HOLD.');
