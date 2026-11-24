import {evaluate} from './verification.mjs';
const t=Date.parse('2026-11-24T15:00:00Z'),nonce='new-170';
const base={challenge_id:'ch-170',nonce,issued_at:'2026-11-24T14:59:00Z',expires_at:'2026-11-24T15:01:00Z',device_serial:'DUT-170',manufacturer:'test',device_key_fingerprint:'test',device_response_signature:'test',manufacturer_attestation:'test',original_capture_sha256:'a'.repeat(64),external_registry_receipt:'test'};
const ctx={expected_challenge:'ch-170',expected_nonce:nonce,expected_serial:'DUT-170',now_ms:t,used_nonces:new Set(),trusted_manufacturer_validation:false,external_registry_validation:false,original_physical_capture_validated:false};
const scenarios=[
 ['empty',null,'INVALID_RECORD'],
 ['missing identity',{...base,device_serial:''},'MISSING_DEVICE_SERIAL'],
 ['replayed nonce',base,'NONCE_REPLAY',{used_nonces:new Set([nonce])}],
 ['wrong nonce',{...base,nonce:'wrong'},'NONCE_MISMATCH'],
 ['wrong challenge',{...base,challenge_id:'wrong'},'CHALLENGE_MISMATCH'],
 ['wrong device',{...base,device_serial:'wrong'},'SERIAL_MISMATCH'],
 ['expired',base,'INVALID_CHALLENGE_WINDOW',{now_ms:t+120000}],
 ['bad digest',{...base,original_capture_sha256:'fake'},'INVALID_DIGEST'],
 ['unverified manufacturer',base,'MANUFACTURER_NOT_AUTHENTICATED'],
 ['unverified registry',base,'EXTERNAL_REGISTRY_NOT_AUTHENTICATED'],
 ['unverified original capture',base,'ORIGINAL_CAPTURE_NOT_AUTHENTICATED']
];
let passed=0;
for(const [name,candidate,expected,overrides] of scenarios){const r=evaluate(candidate,{...ctx,...overrides});if(r.reasons.includes(expected)&&r.operational_authority==='HOLD'&&!r.physical_act_allowed)passed++;else throw Error('FAIL '+name+' '+JSON.stringify(r))}
const documentary=evaluate(base,{...ctx,trusted_manufacturer_validation:true,external_registry_validation:true,original_physical_capture_validated:true});
if(documentary.status!=='DOCUMENTARY_REVIEW_ONLY'||documentary.operational_authority!=='HOLD'||documentary.physical_act_allowed)throw Error('false physical promotion');
passed++;
console.log('AETHER-170: '+passed+'/12 synthetic structural assertions PASSED; physical qualification 0%; operational HOLD.');
