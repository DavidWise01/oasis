import {adjudicate} from './verification.mjs';
const epoch='2026-11-24T16:00:00Z', before='2026-11-23T16:00:00Z',after='2026-11-25T16:00:00Z';
const mk=(subject,issuer,serial,digit)=>({subject,issuer,serial,not_before:before,not_after:after,fingerprint_sha256:digit.repeat(64),signature_algorithm:'RSA-PSS-SHA256'});
const packet={chain:[mk('ref','ca','01','a'),mk('ca','root','02','b'),mk('root','root','03','c')],device_serial:'REF-001',revocation_status:'good',revocation_checked_at:epoch};
const policy={now_ms:Date.parse(epoch),expected_reference_serial:'REF-001',expected_external_root_sha256:'c'.repeat(64),dut_root_sha256:'d'.repeat(64),expected_revocation_timestamp:epoch,external_chain_signature_validation:false,external_revocation_validation:false,external_issuer_registry_validation:false,physical_source_validation:false};
const cases=[
['blank',null,'CHAIN_NOT_THREE_CERTIFICATES'],
['registry',packet,'ISSUER_REGISTRY_NOT_EXTERNALLY_VERIFIED'],
['signature',packet,'CHAIN_SIGNATURE_NOT_EXTERNALLY_VERIFIED'],
['revocation proof',packet,'REVOCATION_NOT_EXTERNALLY_VERIFIED'],
['physical source',packet,'PHYSICAL_SOURCE_NOT_VERIFIED'],
['broken chain',{...packet,chain:[{...packet.chain[0],issuer:'other'},...packet.chain.slice(1)]},'BROKEN_ISSUER_CHAIN'],
['self issued',{...packet,chain:[{...packet.chain[0],issuer:'ref'},...packet.chain.slice(1)]},'SELF_ISSUED_LEAF'],
['expired',{...packet,chain:[{...packet.chain[0],not_after:before},...packet.chain.slice(1)]},'CERT_TIME_INVALID_0'],
['shared root',packet,'SHARED_DUT_ROOT',{dut_root_sha256:'c'.repeat(64)}],
['unpinned root',packet,'ROOT_NOT_PINNED',{expected_external_root_sha256:'e'.repeat(64)}],
['revoked',{...packet,revocation_status:'revoked'},'REVOCATION_NOT_GOOD'],
['stale receipt',{...packet,revocation_checked_at:before},'REVOCATION_RECEIPT_UNBOUND'],
['wrong serial',{...packet,device_serial:'other'},'REFERENCE_DEVICE_MISMATCH'],
['duplicate cert serial',{...packet,chain:[packet.chain[0],{...packet.chain[1],serial:'01'},packet.chain[2]]},'DUPLICATE_CERT_SERIAL'],
['invalid digest',{...packet,chain:[{...packet.chain[0],fingerprint_sha256:'no'},...packet.chain.slice(1)]},'INVALID_FINGERPRINT_0']
];
let passed=0;
for(const [name,input,error,override] of cases){const r=adjudicate(input,{...policy,...override});if(!r.reasons.includes(error)||r.operational_authority!=='HOLD'||r.physical_act_allowed!==false)throw Error('FAIL '+name+': '+JSON.stringify(r));passed++}
const mock=adjudicate(packet,{...policy,external_chain_signature_validation:true,external_revocation_validation:true,external_issuer_registry_validation:true,physical_source_validation:true});
if(mock.status!=='DOCUMENTARY_REVIEW_ONLY'||mock.operational_authority!=='HOLD'||mock.physical_act_allowed)throw Error('false elevation');passed++;
console.log('AETHER-171: '+passed+'/16 synthetic structural assertions passed; operational HOLD; physical 0%.');
