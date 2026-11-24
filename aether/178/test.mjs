import {assess,sha256,canonical} from './verification.mjs';
const enc=new TextEncoder(),bytes=enc.encode('AETHER-178 synthetic capture bytes; no physical sensor attached.');
const ctx={expected_instrument_serial:'REF-178',expected_challenge_id:'CH-178',dut_owned_root:'DUT-root',expected_role:'REFERENCE',used_capture_ids:new Set(),independent_hardware_origin_authenticated:false,external_custodian_signature_authenticated:false,original_hardware_acquisition_authenticated:false};
async function make(){const m={schema:'AETHER-178/v1',capture_id:'capture-178',instrument_serial:'REF-178',challenge_id:'CH-178',source_origin_id:'EXTERNAL-DECLARED',byte_length:bytes.length,capture_sha256:await sha256(bytes),sequence:0,prior_manifest_sha256:null,sealed_at:'2026-11-24T12:00:00Z'};m.manifest_sha256=await sha256(enc.encode(canonical(m)));return{bytes:new Uint8Array(bytes),manifest:m}}
async function edit(f){const p=await make();f(p);return p}
const cases=[
['absent',null,'MISSING_BYTES_OR_MANIFEST'],
['empty',await edit(p=>p.bytes=new Uint8Array()),'EMPTY_CAPTURE'],
['byte tampering',await edit(p=>p.bytes[1]^=1),'CAPTURE_DIGEST_MISMATCH'],
['length',await edit(p=>p.manifest.byte_length++),'LENGTH_MISMATCH'],
['metadata tampering',await edit(p=>p.manifest.source_origin_id='ALTERED'),'MANIFEST_DIGEST_MISMATCH'],
['capture replay',await make(),'CAPTURE_ID_REPLAY',{used_capture_ids:new Set(['capture-178'])}],
['wrong instrument',await edit(p=>p.manifest.instrument_serial='UNKNOWN'),'INSTRUMENT_MISMATCH'],
['wrong challenge',await edit(p=>p.manifest.challenge_id='REPLAY'),'CHALLENGE_MISMATCH'],
['shared origin',await edit(p=>p.manifest.source_origin_id='DUT-root'),'SHARED_DUT_ORIGIN'],
['schema',await edit(p=>p.manifest.schema='OTHER'),'BAD_SCHEMA'],
['timestamp',await edit(p=>p.manifest.sealed_at='invalid'),'BAD_SEAL_TIMESTAMP'],
['manifest digest',await edit(p=>p.manifest.manifest_sha256='x'),'BAD_MANIFEST_DIGEST'],
['capture digest',await edit(p=>p.manifest.capture_sha256='x'),'BAD_CAPTURE_DIGEST'],
['genesis',await edit(p=>p.manifest.prior_manifest_sha256='a'.repeat(64)),'INVALID_GENESIS'],
['sequence',await edit(p=>p.manifest.sequence=-1),'BAD_SEQUENCE'],
['origin unverified',await make(),'ORIGIN_NOT_PHYSICALLY_AUTHENTICATED'],
['signature unverified',await make(),'CUSTODIAN_SIGNATURE_NOT_AUTHENTICATED'],
['hardware unverified',await make(),'ACQUISITION_NOT_PHYSICALLY_AUTHENTICATED'],
['predecessor mismatch',await edit(p=>{p.manifest.sequence=1;p.manifest.prior_manifest_sha256='b'.repeat(64)}),'PREDECESSOR_MISMATCH']
];
let passed=0;for(const [name,p,reason,overrides] of cases){const r=await assess(p,{...ctx,...overrides});if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error('FAIL '+name+JSON.stringify(r));passed++}
const synthetic=await assess(await make(),{...ctx,independent_hardware_origin_authenticated:true,external_custodian_signature_authenticated:true,original_hardware_acquisition_authenticated:true});
if(synthetic.status!=='DOCUMENTARY_REVIEW_ONLY'||synthetic.operational_authority!=='HOLD'||synthetic.physical_act_allowed)throw Error('False physical promotion');passed++;
console.log('AETHER-178 '+passed+'/20 synthetic checks PASS · physical 0% · ACT HOLD');
