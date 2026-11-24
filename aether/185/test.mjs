import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {assess,canonical,hex,sha256} from './verification.mjs';
const enc=new TextEncoder();
const kp=await crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
const public_key_jwk=await crypto.subtle.exportKey('jwk',kp.publicKey);
const bytes=enc.encode('AETHER-185 SIMULATED ACQUISITION - NO PHYSICAL HARDWARE');
const registry=()=>new Map([['external-demo-key',{public_key_jwk,origin_id:'external-lab-demo',operator_id:'synthetic-operator'}]]);
const context=()=>({expected_challenge:'nonce-185',expected_device_serial:'device-demo-185',expected_origin_id:'external-lab-demo',owner_operator_id:'owner-operator',trusted_issuers:registry(),min_receipt_time_ms:Date.parse('2026-11-24T00:00:00Z'),max_receipt_time_ms:Date.parse('2026-11-25T00:00:00Z')});
async function fixture(){
 const receipt={schema:'AETHER-185/intake-v1',package_id:'pkg-185',source_device_serial:'device-demo-185',source_origin_id:'external-lab-demo',acquisition_challenge:'nonce-185',capture_sha256:await sha256(bytes),capture_byte_length:bytes.length,issued_at:'2026-11-24T20:00:00Z',intake_id:'intake-185',issuer_key_id:'external-demo-key'};
 const signature_hex=hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},kp.privateKey,enc.encode(canonical(receipt)))));
 return {receipt,signature_hex,bytes:new Uint8Array(bytes)};
}
const clean=await fixture();
const copy=()=>structuredClone(clean);
const edit=fn=>{const v=copy();fn(v);return v};
const scenarios=[
 ['missing',null,'MISSING_BYTES_OR_RECEIPT'],
 ['empty bytes',edit(p=>p.bytes=new Uint8Array()),'EMPTY_ACQUISITION'],
 ['wrong schema',edit(p=>p.receipt.schema='other'),'BAD_RECEIPT_SCHEMA'],
 ['changed original bytes',edit(p=>p.bytes[0]^=1),'CAPTURE_DIGEST_MISMATCH'],
 ['wrong size',edit(p=>p.receipt.capture_byte_length++),'CAPTURE_BYTE_LENGTH_MISMATCH'],
 ['wrong challenge',edit(p=>p.receipt.acquisition_challenge='replay'),'CHALLENGE_MISMATCH'],
 ['wrong device',edit(p=>p.receipt.source_device_serial='fake'),'SOURCE_DEVICE_SERIAL_MISMATCH'],
 ['wrong origin',edit(p=>p.receipt.source_origin_id='owned'),'SOURCE_ORIGIN_MISMATCH'],
 ['package replay',copy(),'PACKAGE_REPLAY',{seen_package_ids:new Set(['pkg-185'])}],
 ['intake replay',copy(),'INTAKE_REPLAY',{seen_intake_ids:new Set(['intake-185'])}],
 ['invalid timestamp',edit(p=>p.receipt.issued_at='yesterday'),'INVALID_ISSUED_TIMESTAMP'],
 ['stale',edit(p=>p.receipt.issued_at='2026-11-21T20:00:00Z'),'STALE_ACQUISITION_RECEIPT'],
 ['future',edit(p=>p.receipt.issued_at='2027-11-24T20:00:00Z'),'FUTURE_ACQUISITION_RECEIPT'],
 ['unknown key',edit(p=>p.receipt.issuer_key_id='other'),'UNKNOWN_ISSUER_KEY'],
 ['revoked key',copy(),'REVOKED_ISSUER',{trusted_issuers:(()=>{const r=registry();r.get('external-demo-key').revoked=true;return r})()}],
 ['issuer origin mismatch',copy(),'ISSUER_ORIGIN_MISMATCH',{trusted_issuers:(()=>{const r=registry();r.get('external-demo-key').origin_id='owned';return r})()}],
 ['self issued',copy(),'SELF_ISSUED_ORIGIN',{owner_operator_id:'synthetic-operator'}],
 ['forged signature',edit(p=>p.signature_hex='00'.repeat(64)),'ACQUISITION_RECEIPT_SIGNATURE_INVALID'],
 ['external registry missing',copy(),'ISSUER_REGISTRY_NOT_EXTERNALLY_AUTHENTICATED'],
 ['hardware not authenticated',copy(),'HARDWARE_ORIGIN_UNVERIFIED'],
 ['physical acquisition missing',copy(),'PHYSICAL_ACQUISITION_UNVERIFIED'],
 ['custody missing',copy(),'INDEPENDENT_CUSTODY_UNVERIFIED']
];
let passed=0;
for(const [name,p,reason,override]of scenarios){
 const r=await assess(p,{...context(),...override});
 if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+' '+JSON.stringify(r));
 passed++;
}
const valid=await assess(copy(),context());
if(!valid.signature_cryptographically_valid||valid.operational_authority!=='HOLD')throw Error('valid ECDSA signature failed');passed++;
const spoof=await assess(copy(),{...context(),externally_authenticated_issuer_registry:true,hardware_source_verified_by_manufacturer:true,original_physical_acquisition_verified:true,independent_custody_verified:true});
if(spoof.decision!=='DOCUMENTARY_INTAKE_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false promotion');passed++;
console.log('AETHER-185 '+passed+'/24 synthetic checks PASS; physical 0%, operational HOLD.');
