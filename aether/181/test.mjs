import {webcrypto} from 'node:crypto';
import {assess,sha256,canonical} from './verification.mjs';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const enc=new TextEncoder(),H=x=>x.repeat(64),raw=enc.encode('AETHER-181 fixture, no original physical sensor attached');
async function fixture(){
 const record={schema:'AETHER-181/v1',capture_id:'CAP-181',source_id:'REF-ORIGIN',device_serial:'REF-SERIAL',clock_id:'HW-CLOCK-TEST',clock_calibration_receipt_sha256:H('a'),challenge_id:'C-181',challenge_nonce:'N-181',challenge_issued_utc:'2026-11-24T19:00:00Z',challenge_expires_utc:'2026-11-24T19:02:00Z',captured_utc:'2026-11-24T19:01:00Z',sample_start:500,sample_end:502,first_tick_ns:1000000,last_tick_ns:1200000,raw_capture_sha256:await sha256(raw),custody_receipt_sha256:H('b')};
 record.record_sha256=await sha256(enc.encode(canonical(record)));
 return {raw_bytes:new Uint8Array(raw),record}
}
const ctx=()=>({expected_source_id:'REF-ORIGIN',expected_device_serial:'REF-SERIAL',expected_clock_id:'HW-CLOCK-TEST',expected_challenge_id:'C-181',expected_challenge_nonce:'N-181',expected_calibration_sha256:H('a'),expected_custody_sha256:H('b'),expected_sample_count:3,max_duration_ns:1000000,used_challenge_nonces:new Set(),used_capture_ids:new Set(),hardware_clock_attestation_authenticated:false,independent_source_origin_authenticated:false,original_acquisition_authenticated:false,external_custody_receipt_authenticated:false});
const tweak=async f=>{const p=await fixture();f(p);return p};
const cases=[
['missing',null,'MISSING_ORIGINAL_BYTES_OR_RECORD'],
['schema',await tweak(p=>p.record.schema='different'),'SCHEMA_MISMATCH'],
['wrong origin',await tweak(p=>p.record.source_id='DUT'),'SOURCE_ID_MISMATCH'],
['wrong serial',await tweak(p=>p.record.device_serial='BAD'),'DEVICE_SERIAL_MISMATCH'],
['wrong clock',await tweak(p=>p.record.clock_id='WRONG'),'CLOCK_ID_MISMATCH'],
['wrong challenge',await tweak(p=>p.record.challenge_id='OLD'),'CHALLENGE_MISMATCH'],
['challenge replay',await fixture(),'REPLAYED_CHALLENGE',{used_challenge_nonces:new Set(['N-181'])}],
['capture replay',await fixture(),'REPLAYED_CAPTURE',{used_capture_ids:new Set(['CAP-181'])}],
['calibration substitution',await tweak(p=>p.record.clock_calibration_receipt_sha256=H('c')),'CALIBRATION_RECEIPT_MISMATCH'],
['custody substitution',await tweak(p=>p.record.custody_receipt_sha256=H('c')),'CUSTODY_RECEIPT_MISMATCH'],
['expired challenge',await tweak(p=>p.record.captured_utc='2026-11-24T19:05:00Z'),'CAPTURE_OUTSIDE_CHALLENGE_WINDOW'],
['invalid timestamp',await tweak(p=>p.record.captured_utc='yesterday'),'INVALID_TIME_FIELD'],
['counter inversion',await tweak(p=>p.record.sample_end=499),'INVALID_SAMPLE_COUNTER_RANGE'],
['counter count conflict',await tweak(p=>p.record.sample_end=503),'SAMPLE_COUNT_MISMATCH'],
['clock rollback',await tweak(p=>p.record.last_tick_ns=999999),'NONMONOTONIC_HARDWARE_TICKS'],
['long duration',await tweak(p=>p.record.last_tick_ns=4000000),'DURATION_EXCEEDS_LIMIT'],
['raw byte mutation',await tweak(p=>p.raw_bytes[0]^=1),'ORIGINAL_BYTES_DIGEST_MISMATCH'],
['metadata mutation',await tweak(p=>p.record.source_id='OTHER'),'PROVENANCE_RECORD_DIGEST_MISMATCH'],
['bad raw digest',await tweak(p=>p.record.raw_capture_sha256='invalid'),'INVALID_RAW_CAPTURE_SHA256'],
['bad record digest',await tweak(p=>p.record.record_sha256='bad'),'INVALID_RECORD_SHA256'],
['hardware clock unverified',await fixture(),'HARDWARE_CLOCK_NOT_AUTHENTICATED'],
['independent source unverified',await fixture(),'INDEPENDENT_SOURCE_NOT_AUTHENTICATED'],
['physical acquisition unverified',await fixture(),'ORIGINAL_ACQUISITION_NOT_AUTHENTICATED'],
['external receipt unverified',await fixture(),'EXTERNAL_RECEIPT_NOT_AUTHENTICATED']
];
let passed=0;
for(const [name,packet,reason,override]of cases){const r=await assess(packet,{...ctx(),...override});if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+': '+JSON.stringify(r));passed++}
const spoof=await assess(await fixture(),{...ctx(),hardware_clock_attestation_authenticated:true,independent_source_origin_authenticated:true,original_acquisition_authenticated:true,external_custody_receipt_authenticated:true});
if(spoof.status!=='DOCUMENTARY_REVIEW_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false physical ACT');
passed++;
console.log('AETHER-181 '+passed+'/25 synthetic tests PASS; physical 0%, ACT HOLD');
