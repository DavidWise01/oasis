import {assess} from './verification.mjs';
const raw=new Uint8Array([97,98,99]); // abc
const digest='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';
const original={raw_bytes:raw,declared_sha256:digest,device_serial:'DEMO-173',challenge_nonce:'nonce-173',clock_source_id:'clock-173',capture_id:'capture-173',expected_sample_count:3,samples:[{counter:100,hardware_time_ns:1000000},{counter:101,hardware_time_ns:2000000},{counter:102,hardware_time_ns:3000000}]};
const env={expected_serial:'DEMO-173',expected_nonce:'nonce-173',expected_clock_source:'clock-173',expected_first_counter:100,seen_capture_ids:new Set(),trusted_hardware_clock_validation:false,trusted_original_capture_validation:false,trusted_independent_source_validation:false};
const edit=f=>{const x=structuredClone(original);f(x);return x};
const cases=[
['missing record',null,'MISSING_RAW_ACQUISITION'],
['empty raw',edit(x=>x.raw_bytes=new Uint8Array([])),'EMPTY_RAW_CAPTURE'],
['bad digest',edit(x=>x.declared_sha256='bad'),'INVALID_DECLARED_SHA256'],
['tampered bytes',edit(x=>x.raw_bytes[0]=120),'DIGEST_MISMATCH'],
['serial',edit(x=>x.device_serial='other'),'DEVICE_SERIAL_MISMATCH'],
['nonce',edit(x=>x.challenge_nonce='other'),'CHALLENGE_NONCE_MISMATCH'],
['clock',edit(x=>x.clock_source_id='other'),'CLOCK_SOURCE_MISMATCH'],
['replay',original,'REPLAYED_CAPTURE_ID',{seen_capture_ids:new Set(['capture-173'])}],
['sample count',edit(x=>x.expected_sample_count=4),'SAMPLE_COUNT_MISMATCH'],
['counter skip',edit(x=>x.samples[1].counter=104),'COUNTER_DISCONTINUITY'],
['clock rollback',edit(x=>x.samples[1].hardware_time_ns=999999),'CLOCK_NONMONOTONIC'],
['bad initial counter',original,'INITIAL_COUNTER_MISMATCH',{expected_first_counter:99}],
['hardware clock unverified',original,'HARDWARE_CLOCK_UNAUTHENTICATED'],
['original acquisition unverified',original,'ORIGINAL_CAPTURE_UNAUTHENTICATED'],
['independent source unverified',original,'INDEPENDENT_SOURCE_UNAUTHENTICATED']
];
let passed=0;
for(const [name,candidate,expected,override] of cases){const r=await assess(candidate,{...env,...override});if(!r.reasons.includes(expected)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error('FAIL '+name+': '+JSON.stringify(r));passed++}
const forged=await assess(original,{...env,trusted_hardware_clock_validation:true,trusted_original_capture_validation:true,trusted_independent_source_validation:true});
if(forged.status!=='DOCUMENTARY_REVIEW_ONLY'||forged.operational_authority!=='HOLD'||forged.physical_act_allowed)throw Error('false physical promotion');passed++;
console.log('AETHER-173: '+passed+'/16 synthetic tests PASS, hardware samples 0, physical qualification 0%, ACT HOLD.');
