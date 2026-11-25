import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {assess,sha256,canonical,hex,ACQ_FIELDS,CUSTODY_FIELDS,VERIFY_FIELDS} from './verification.mjs';
const enc=new TextEncoder(),raw=enc.encode('AETHER-187 synthetic original capture — not physical evidence');
const keys=await Promise.all([0,1].map(()=>crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify'])));
const jwks=await Promise.all(keys.map(k=>crypto.subtle.exportKey('jwk',k.publicKey)));
const sign=async(i,record,fields)=>hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},keys[i].privateKey,enc.encode(canonical(record,fields)))));
const issuerRecord=()=>({root_id:'source-root',operator_id:'issuer-operator',administrator_id:'source-admin',jwk:jwks[0]});
const verifierRecord=()=>({root_id:'verifier-root',operator_id:'verifier-operator',administrator_id:'verifier-admin',verifier_id:'independent-verifier',jwk:jwks[1]});
const ctx=()=>({expected_challenge_id:'nonce-187',expected_device_serial:'source-187',issuer_keys:new Map([['issuer-key',issuerRecord()]]),verifier_keys:new Map([['verifier-key',verifierRecord()]]),seen_capture_ids:new Set(),seen_verification_ids:new Set()});
async function fixture(){
 const acquisition={schema:'AETHER-187/acquisition-v1',capture_id:'capture-187',device_serial:'source-187',challenge_id:'nonce-187',capture_sha256:await sha256(raw),byte_length:raw.length,acquired_at:'2026-11-24T20:00:00Z',source_root_id:'source-root',issuer_key_id:'issuer-key'};
 const custody={schema:'AETHER-187/custody-v1',custody_id:'custody-187',capture_id:acquisition.capture_id,capture_sha256:acquisition.capture_sha256,from_party:'acquisition-lab',to_party:'custodian-lab',transfer_at:'2026-11-24T20:00:01Z'};
 const verification={schema:'AETHER-187/verification-v1',verification_id:'verify-187',capture_id:acquisition.capture_id,capture_sha256:acquisition.capture_sha256,acquisition_receipt_sha256:await sha256(enc.encode(canonical(acquisition,ACQ_FIELDS))),custody_receipt_sha256:await sha256(enc.encode(canonical(custody,CUSTODY_FIELDS))),verifier_id:'independent-verifier',verifier_root_id:'verifier-root',verifier_key_id:'verifier-key',verified_at:'2026-11-24T20:00:02Z'};
 return {raw_bytes:new Uint8Array(raw),acquisition,custody,verification,acquisition_signature_hex:await sign(0,acquisition,ACQ_FIELDS),verification_signature_hex:await sign(1,verification,VERIFY_FIELDS)};
}
const base=await fixture(),copy=()=>structuredClone(base),alter=f=>{const p=copy();f(p);return p};
const contexts=f=>{const p=ctx();f(p);return p};
const cases=[
 ['missing',null,ctx(),'INCOMPLETE_EXTERNAL_EVIDENCE_BUNDLE'],
 ['modified bytes',alter(p=>p.raw_bytes[0]^=1),ctx(),'RAW_CAPTURE_SUBSTITUTION'],
 ['length alteration',alter(p=>p.acquisition.byte_length++),ctx(),'BYTE_LENGTH_MISMATCH'],
 ['capture mismatch',alter(p=>p.custody.capture_id='other'),ctx(),'CROSS_RECORD_CAPTURE_MISMATCH'],
 ['wrong challenge',alter(p=>p.acquisition.challenge_id='old'),ctx(),'CHALLENGE_MISMATCH'],
 ['wrong hardware serial',alter(p=>p.acquisition.device_serial='DUT'),ctx(),'DEVICE_SERIAL_MISMATCH'],
 ['capture replay',copy(),contexts(p=>p.seen_capture_ids.add('capture-187')),'REPLAYED_CAPTURE'],
 ['verification replay',copy(),contexts(p=>p.seen_verification_ids.add('verify-187')),'REPLAYED_VERIFICATION'],
 ['shared root',alter(p=>p.verification.verifier_root_id='source-root'),ctx(),'SHARED_SOURCE_VERIFIER_ROOT'],
 ['time reversal',alter(p=>p.custody.transfer_at='2026-11-24T19:00:00Z'),ctx(),'NONMONOTONIC_CUSTODY_TIME'],
 ['same-party handoff',alter(p=>p.custody.to_party='acquisition-lab'),ctx(),'INVALID_CUSTODY_HANDOFF'],
 ['verifier custodian overlap',alter(p=>p.verification.verifier_id='custodian-lab'),ctx(),'VERIFIER_OVERLAPS_CUSTODIAN'],
 ['wrong acquisition receipt hash',alter(p=>p.verification.acquisition_receipt_sha256='c'.repeat(64)),ctx(),'ACQUISITION_RECEIPT_DIGEST_MISMATCH'],
 ['wrong custody receipt hash',alter(p=>p.verification.custody_receipt_sha256='d'.repeat(64)),ctx(),'CUSTODY_RECEIPT_DIGEST_MISMATCH'],
 ['missing external key',copy(),contexts(p=>p.verifier_keys.clear()),'EXTERNAL_KEYS_NOT_REGISTERED'],
 ['wrong verifier identity',copy(),contexts(p=>p.verifier_keys.get('verifier-key').verifier_id='other'),'VERIFIER_IDENTITY_KEY_MISMATCH'],
 ['shared operator',copy(),contexts(p=>p.verifier_keys.get('verifier-key').operator_id='issuer-operator'),'SHARED_ISSUER_VERIFIER_OPERATOR'],
 ['shared administrator',copy(),contexts(p=>p.verifier_keys.get('verifier-key').administrator_id='source-admin'),'SHARED_ISSUER_VERIFIER_ADMINISTRATOR'],
 ['revoked verifier',copy(),contexts(p=>p.verifier_keys.get('verifier-key').revoked=true),'REVOKED_SIGNER'],
 ['forged acquisition signature',alter(p=>p.acquisition_signature_hex='00'.repeat(64)),ctx(),'ACQUISITION_SIGNATURE_INVALID'],
 ['forged verifier signature',alter(p=>p.verification_signature_hex='00'.repeat(64)),ctx(),'EXTERNAL_VERIFIER_SIGNATURE_INVALID'],
 ['issuer trust missing',copy(),ctx(),'ISSUER_NOT_EXTERNALLY_AUTHENTICATED'],
 ['verifier trust missing',copy(),ctx(),'VERIFIER_NOT_EXTERNALLY_AUTHENTICATED'],
 ['physical hardware missing',copy(),ctx(),'ORIGINAL_HARDWARE_NOT_AUTHENTICATED'],
 ['physical custody missing',copy(),ctx(),'CUSTODY_NOT_EXTERNALLY_AUTHENTICATED']
];
let passed=0;
for(const [name,packet,context,reason] of cases){const r=await assess(packet,context);if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+JSON.stringify(r));passed++}
const valid=await assess(copy(),ctx());if(!valid.acquisition_signature_valid||!valid.verification_signature_valid||valid.operational_authority!=='HOLD')throw Error('signature pair rejected');passed++;
const spoof=await assess(copy(),{...ctx(),independent_issuer_identity_authenticated:true,independent_verifier_identity_authenticated:true,original_hardware_capture_authenticated:true,external_custody_provenance_authenticated:true});
if(spoof.decision!=='DOCUMENTARY_VERIFICATION_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false ACT promotion');passed++;
console.log('AETHER-187 '+passed+'/27 synthetic cases PASS; physical 0%, ACT HOLD');
