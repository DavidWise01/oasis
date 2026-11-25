import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {assess,canonical,hex,sha256,fingerprint,TRANSFER_FIELDS,RECEIPT_FIELDS} from './verification.mjs';
const enc=new TextEncoder();
const pair=()=>crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
const [keyA,keyB]=await Promise.all([pair(),pair()]);
const [pubA,pubB]=await Promise.all([keyA,keyB].map(k=>crypto.subtle.exportKey('jwk',k.publicKey)));
const sign=async(k,r,fields)=>hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},k.privateKey,enc.encode(canonical(r,fields)))));
const sender=()=>({custodian_id:'lab-A',ancestry_root:'root-A',operator_id:'operator-A',administrator_id:'admin-A',actions:['TRANSFER'],jwk:pubA});
const receiver=()=>({custodian_id:'lab-B',ancestry_root:'root-B',operator_id:'operator-B',administrator_id:'admin-B',actions:['RECEIVE'],jwk:pubB});
const context=async()=>({expected_challenge_id:'nonce-189',expected_previous_receipt_sha256:null,max_receipt_delay_ms:60000,used_handoff_ids:new Set(),used_receipt_ids:new Set(),custodian_keys:new Map([['key-A',sender()],['key-B',receiver()]]),pinned_root_fingerprints:new Map([['root-A',await fingerprint(pubA)],['root-B',await fingerprint(pubB)]])});
async function make(){
 const transfer={schema:'AETHER-189/transfer-v1',handoff_id:'H-189',capture_id:'CAP-189',capture_sha256:'a'.repeat(64),from_id:'lab-A',to_id:'lab-B',sender_key_id:'key-A',challenge_id:'nonce-189',sequence:0,transfer_utc:'2026-11-24T21:00:00Z',previous_receipt_sha256:null};
 const receipt={schema:'AETHER-189/receipt-v1',receipt_id:'R-189',handoff_id:transfer.handoff_id,handoff_sha256:await sha256(enc.encode(canonical(transfer,TRANSFER_FIELDS))),capture_id:'CAP-189',capture_sha256:transfer.capture_sha256,from_id:'lab-A',to_id:'lab-B',receiver_key_id:'key-B',challenge_id:'nonce-189',received_utc:'2026-11-24T21:00:01Z'};
 return {transfer,receipt,sender_signature_hex:await sign(keyA,transfer,TRANSFER_FIELDS),receiver_signature_hex:await sign(keyB,receipt,RECEIPT_FIELDS)};
}
const original=await make();
const copy=()=>structuredClone(original);
const mutate=f=>{const p=copy();f(p);return p};
const cases=[
['missing',null,'MISSING_TRANSFER_OR_RECEIPT'],
['schema',mutate(p=>p.transfer.schema='other'),'SCHEMA_MISMATCH'],
['same holder',mutate(p=>p.transfer.to_id='lab-A'),'SAME_OR_MISSING_CUSTODIAN'],
['same key',mutate(p=>p.receipt.receiver_key_id='key-A'),'REUSED_CUSTODIAN_KEY'],
['capture swapped',mutate(p=>p.receipt.capture_sha256='b'.repeat(64)),'TRANSFER_RECEIPT_MISMATCH'],
['nonce substituted',mutate(p=>p.receipt.challenge_id='OLD'),'CHALLENGE_MISMATCH'],
['sequence invalid',mutate(p=>p.transfer.sequence=-1),'BAD_SEQUENCE'],
['handoff replay',copy(),'HANDOFF_REPLAY',{used_handoff_ids:new Set(['H-189'])}],
['receipt replay',copy(),'RECEIPT_REPLAY',{used_receipt_ids:new Set(['R-189'])}],
['predecessor mismatch',copy(),'PREDECESSOR_MISMATCH',{expected_previous_receipt_sha256:'f'.repeat(64)}],
['clock inversion',mutate(p=>p.receipt.received_utc='2026-11-24T20:59:00Z'),'RECEIPT_PRECEDES_TRANSFER'],
['late receipt',mutate(p=>p.receipt.received_utc='2026-11-24T21:10:00Z'),'RECEIPT_TOO_LATE'],
['altered transfer',mutate(p=>p.transfer.capture_id='TAMPER'),'RECEIPT_HANDOFF_DIGEST_MISMATCH'],
['sender identity mismatch',copy(),'SENDER_KEY_IDENTITY_MISMATCH',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-A').custodian_id='lab-C';return m})()}],
['receiver identity mismatch',copy(),'RECEIVER_KEY_IDENTITY_MISMATCH',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-B').custodian_id='lab-C';return m})()}],
['revoked receiver',copy(),'REVOKED_CREDENTIAL',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-B').revoked=true;return m})()}],
['sender missing permission',copy(),'SENDER_LACKS_TRANSFER_PERMISSION',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-A').actions=[];return m})()}],
['receiver missing permission',copy(),'RECEIVER_LACKS_RECEIVE_PERMISSION',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-B').actions=[];return m})()}],
['shared ancestry',copy(),'SHARED_CREDENTIAL_ANCESTRY',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-B').ancestry_root='root-A';return m})()}],
['shared operator',copy(),'SHARED_CREDENTIAL_OPERATOR',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-B').operator_id='operator-A';return m})()}],
['shared admin',copy(),'SHARED_CREDENTIAL_ADMINISTRATOR',{custodian_keys:(()=>{const m=new Map([['key-A',sender()],['key-B',receiver()]]);m.get('key-B').administrator_id='admin-A';return m})()}],
['unpinned key',copy(),'UNPINNED_CUSTODIAN_ROOT',{pinned_root_fingerprints:new Map()}],
['forged sender',mutate(p=>p.sender_signature_hex='00'.repeat(64)),'SENDER_SIGNATURE_INVALID'],
['forged receiver',mutate(p=>p.receiver_signature_hex='00'.repeat(64)),'RECEIVER_SIGNATURE_INVALID'],
['sender unauthenticated',copy(),'SENDER_IDENTITY_UNAUTHENTICATED'],
['receiver unauthenticated',copy(),'RECEIVER_IDENTITY_UNAUTHENTICATED'],
['control unauthenticated',copy(),'SEPARATE_CONTROL_UNAUTHENTICATED'],
['physical handoff missing',copy(),'PHYSICAL_HANDOFF_UNVERIFIED']
];
let count=0;
for(const [name,packet,reason,override] of cases){
 const result=await assess(packet,{...await context(),...override});
 if(!result.reasons.includes(reason)||result.operational_authority!=='HOLD'||result.physical_act_allowed)throw Error('FAIL '+name+': '+JSON.stringify(result));
 count++;
}
const valid=await assess(copy(),await context());
if(!valid.sender_signature_valid||!valid.receiver_signature_valid||valid.operational_authority!=='HOLD')throw Error('valid signatures not verified');count++;
const flagged=await assess(copy(),{...await context(),sender_identity_externally_authenticated:true,receiver_identity_externally_authenticated:true,separate_root_control_externally_authenticated:true,original_hardware_custody_physically_verified:true});
if(flagged.decision!=='DOCUMENTARY_HANDOFF_ONLY'||flagged.operational_authority!=='HOLD'||flagged.physical_act_allowed)throw Error('client flags escalated ACT');count++;
console.log('AETHER-189 '+count+'/30 synthetic custody cases PASS · physical 0% · ACT HOLD');
