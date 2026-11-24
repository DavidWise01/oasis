import{webcrypto}from'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import{assess,canonical,transferFields,receiptFields,sha256,hex}from'./verification.mjs';
const enc=new TextEncoder();
const keysA=await crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
const keysB=await crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
const ja=await crypto.subtle.exportKey('jwk',keysA.publicKey),jb=await crypto.subtle.exportKey('jwk',keysB.publicKey);
const registry=()=>new Map([
['key-sender',{custodian_id:'custodian-A',allowed_actions:['TRANSFER'],public_key_jwk:ja,revoked:false}],
['key-receiver',{custodian_id:'custodian-B',allowed_actions:['RECEIVE'],public_key_jwk:jb,revoked:false}]]);
const context=()=>({expected_challenge_id:'nonce-180',expected_previous_receipt_sha256:null,max_receipt_delay_ms:60000,key_registry:registry(),external_sender_identity_authenticated:false,external_receiver_identity_authenticated:false,independent_root_ancestry_authenticated:false,original_physical_capture_authenticated:false});
async function make(){
 const transfer={schema:'AETHER-180/transfer-v1',transfer_id:'t-180',capture_sha256:'a'.repeat(64),from_custodian:'custodian-A',to_custodian:'custodian-B',sender_key_id:'key-sender',challenge_id:'nonce-180',sequence:0,time_utc:'2026-11-24T19:00:00.000Z',previous_receipt_sha256:null};
 const transfer_sha256=await sha256(enc.encode(canonical(transfer,transferFields)));
 const receipt={schema:'AETHER-180/receipt-v1',receipt_id:'r-180',transfer_id:'t-180',transfer_sha256,capture_sha256:'a'.repeat(64),from_custodian:'custodian-A',to_custodian:'custodian-B',receiver_key_id:'key-receiver',challenge_id:'nonce-180',time_utc:'2026-11-24T19:00:01.000Z'};
 const sender_signature_hex=hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},keysA.privateKey,enc.encode(canonical(transfer,transferFields)))));
 const receiver_signature_hex=hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},keysB.privateKey,enc.encode(canonical(receipt,receiptFields)))));
 return {transfer,receipt,sender_signature_hex,receiver_signature_hex};
}
const initial=await make();
const clone=()=>structuredClone(initial);
const cases=[
['missing',null,'MISSING_TRANSFER_OR_RECEIPT'],
['schema',Object.assign(clone(),{transfer:{...initial.transfer,schema:'other'}}),'BAD_SCHEMA'],
['same holder',Object.assign(clone(),{transfer:{...initial.transfer,to_custodian:'custodian-A'}}),'SAME_CUSTODIAN_BOTH_ROLES'],
['reused key',Object.assign(clone(),{receipt:{...initial.receipt,receiver_key_id:'key-sender'}}),'REUSED_KEY_FOR_BOTH_ROLES'],
['wrong receiver',Object.assign(clone(),{receipt:{...initial.receipt,to_custodian:'wrong'}}),'TRANSFER_RECEIPT_MISMATCH'],
['nonce',Object.assign(clone(),{receipt:{...initial.receipt,challenge_id:'wrong'}}),'CHALLENGE_MISMATCH'],
['transfer replay',clone(),'REPLAYED_TRANSFER',{used_transfer_ids:new Set(['t-180'])}],
['receipt replay',clone(),'REPLAYED_RECEIPT',{used_receipt_ids:new Set(['r-180'])}],
['clock inversion',Object.assign(clone(),{receipt:{...initial.receipt,time_utc:'2026-11-24T18:00:00Z'}}),'RECEIPT_BEFORE_TRANSFER'],
['late',Object.assign(clone(),{receipt:{...initial.receipt,time_utc:'2026-11-24T19:20:00Z'}}),'RECEIPT_DELAY_EXCEEDED'],
['tamper transfer',Object.assign(clone(),{transfer:{...initial.transfer,sequence:1}}),'RECEIPT_NOT_BOUND_TO_TRANSFER'],
['tamper receipt',Object.assign(clone(),{receipt:{...initial.receipt,capture_sha256:'b'.repeat(64)}}),'RECEIVER_SIGNATURE_INVALID'],
['fake sender sig',Object.assign(clone(),{sender_signature_hex:'00'.repeat(64)}),'SENDER_SIGNATURE_INVALID'],
['fake receiver sig',Object.assign(clone(),{receiver_signature_hex:'00'.repeat(64)}),'RECEIVER_SIGNATURE_INVALID'],
['sender key absent',clone(),'UNREGISTERED_CUSTODIAN_KEY',{key_registry:new Map([['key-receiver',context().key_registry.get('key-receiver')]])}],
['revoked sender',clone(),'REVOKED_CUSTODIAN_KEY',{key_registry:(()=>{const x=registry();x.get('key-sender').revoked=true;return x})()}],
['unauthorized receiver',clone(),'RECEIVER_NOT_AUTHORIZED',{key_registry:(()=>{const x=registry();x.get('key-receiver').allowed_actions=[];return x})()}],
['broken predecessor',clone(),'BROKEN_ESCROW_PREDECESSOR',{expected_previous_receipt_sha256:'f'.repeat(64)}],
['sender identity not independent',clone(),'SENDER_IDENTITY_UNAUTHENTICATED'],
['receiver identity not independent',clone(),'RECEIVER_IDENTITY_UNAUTHENTICATED'],
['root not independent',clone(),'ROOT_ANCESTRY_UNAUTHENTICATED'],
['physical source absent',clone(),'PHYSICAL_CAPTURE_UNAUTHENTICATED']
];
let passed=0;for(const [name,packet,reason,override]of cases){const r=await assess(packet,{...context(),...override});if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+' '+JSON.stringify(r));passed++}
const good=await assess(initial,context());if(!good.cryptographic_sender_valid||!good.cryptographic_receiver_valid||good.operational_authority!=='HOLD')throw Error('correct signed sample rejected');passed++;
const spoof=await assess(initial,{...context(),external_sender_identity_authenticated:true,external_receiver_identity_authenticated:true,independent_root_ancestry_authenticated:true,original_physical_capture_authenticated:true});
if(spoof.status!=='DOCUMENTARY_REVIEW_ONLY'||!spoof.cryptographic_sender_valid||!spoof.cryptographic_receiver_valid||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('simulated trust promoted physical ACT');passed++;
console.log('AETHER-180 '+passed+'/24 synthetic cryptographic assertions PASS; physical 0%, ACT HOLD.');
