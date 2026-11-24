import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {assess,canonical,CERT_FIELDS,RECEIPT_FIELDS,fingerprint,asHex} from './verification.mjs';
const enc=new TextEncoder();
const makeKey=()=>crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
const [rootK,midK,leafK]=await Promise.all([makeKey(),makeKey(),makeKey()]);
const [rootJ,midJ,leafJ]=await Promise.all([rootK,midK,leafK].map(k=>crypto.subtle.exportKey('jwk',k.publicKey)));
const sign=async(key,text)=>asHex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},key.privateKey,enc.encode(text))));
const cert=(subject,issuer,role,key_id,jwk,serial,action)=>({schema:'AETHER-186/cert-v1',subject_id:subject,issuer_id:issuer,organization_id:'mock-manufacturer',role,key_id,public_key_jwk:jwk,not_before:'2026-11-23T00:00:00Z',not_after:'2026-11-26T00:00:00Z',serial_number:serial,permitted_actions:[action]});
async function make(){
 const root=cert('mock-root','mock-root','ROOT','root-key',rootJ,'serial-root','CERT_SIGN');
 const intermediate=cert('mock-intermediate','mock-root','MANUFACTURER_CA','mid-key',midJ,'serial-mid','CERT_SIGN');
 const leaf=cert('mock-leaf','mock-intermediate','INSTRUMENT_ISSUER','leaf-key',leafJ,'serial-leaf','RECEIPT_SIGN');
 const receipt={schema:'AETHER-186/receipt-v1',capture_id:'capture186',source_device_serial:'device186',challenge_id:'nonce186',capture_sha256:'a'.repeat(64),issued_at:'2026-11-24T19:00:00Z',issuer_key_id:'leaf-key'};
 return {root,intermediate,leaf,receipt,intermediate_signature_hex:await sign(rootK,canonical(intermediate,CERT_FIELDS)),leaf_signature_hex:await sign(midK,canonical(leaf,CERT_FIELDS)),receipt_signature_hex:await sign(leafK,canonical(receipt,RECEIPT_FIELDS))};
}
const registry=async()=>new Map([['mock-root',await fingerprint(rootJ)]]);
const policy=async()=>({review_time_ms:Date.parse('2026-11-24T19:00:01Z'),maximum_receipt_age_ms:60000,expected_device_serial:'device186',expected_challenge_id:'nonce186',pinned_root_fingerprints:await registry(),revoked_serials:new Set(),manufacturer_trust_anchor_independently_authenticated:false,independent_issuer_identity_authenticated:false,original_physical_device_authenticated:false});
const baseline=await make(),basePolicy=await policy();
const p=()=>structuredClone(baseline),ctx=()=>structuredClone(basePolicy);
const scenarios=[
 ['missing',null,ctx(),'MISSING_CERTIFICATE_CHAIN'],
 ['root role',{...p(),root:{...baseline.root,role:'LEAF'}},ctx(),'CERT_ROLE_MISMATCH'],
 ['issuer link',{...p(),leaf:{...baseline.leaf,issuer_id:'other'}},ctx(),'CHAIN_ISSUER_SUBJECT_MISMATCH'],
 ['wrong organization',{...p(),leaf:{...baseline.leaf,organization_id:'another'}},ctx(),'MANUFACTURER_ORG_MISMATCH'],
 ['bad key usage',{...p(),leaf:{...baseline.leaf,permitted_actions:['CERT_SIGN']}},ctx(),'CERT_KEY_USAGE_VIOLATION'],
 ['wrong receipt issuer',{...p(),receipt:{...baseline.receipt,issuer_key_id:'wrong'}},ctx(),'RECEIPT_SIGNER_MISMATCH'],
 ['wrong challenge',{...p(),receipt:{...baseline.receipt,challenge_id:'replay'}},ctx(),'CHALLENGE_MISMATCH'],
 ['wrong device',{...p(),receipt:{...baseline.receipt,source_device_serial:'fake'}},ctx(),'DEVICE_SERIAL_MISMATCH'],
 ['malformed digest',{...p(),receipt:{...baseline.receipt,capture_sha256:'bad'}},ctx(),'INVALID_CAPTURE_DIGEST'],
 ['tampered intermediate',{...p(),intermediate:{...baseline.intermediate,serial_number:'tampered'}},ctx(),'MANUFACTURER_CA_SIGNATURE_INVALID'],
 ['tampered leaf',{...p(),leaf:{...baseline.leaf,serial_number:'tampered'}},ctx(),'INSTRUMENT_ISSUER_SIGNATURE_INVALID'],
 ['tampered receipt',{...p(),receipt:{...baseline.receipt,capture_id:'altered'}},ctx(),'RECEIPT_SIGNATURE_INVALID'],
 ['forged sig',{...p(),receipt_signature_hex:'00'.repeat(64)},ctx(),'RECEIPT_SIGNATURE_INVALID'],
 ['unpinned root',p(),{...ctx(),pinned_root_fingerprints:new Map()},'UNPINNED_ROOT_KEY'],
 ['revoked',p(),{...ctx(),revoked_serials:new Set(['serial-mid'])},'REVOKED_CERTIFICATE'],
 ['expired cert',{...p(),leaf:{...baseline.leaf,not_after:'2026-11-22T00:00:00Z'}},ctx(),'CERT_OUTSIDE_VALIDITY'],
 ['stale receipt',p(),{...ctx(),review_time_ms:Date.parse('2026-11-24T21:00:00Z')},'RECEIPT_STALE_OR_FUTURE'],
 ['external manufacturer missing',p(),ctx(),'MANUFACTURER_ANCHOR_NOT_EXTERNALLY_AUTHENTICATED'],
 ['external issuer missing',p(),ctx(),'ISSUER_IDENTITY_NOT_EXTERNALLY_AUTHENTICATED'],
 ['physical device missing',p(),ctx(),'PHYSICAL_DEVICE_NOT_AUTHENTICATED']
];
let count=0;for(const [name,packet,policy,expected]of scenarios){
 const r=await assess(packet,policy);
 if(!r.reasons.includes(expected)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+' '+JSON.stringify(r));
 count++;
}
const clean=await assess(p(),ctx());if(!clean.cryptographic_chain_valid||clean.operational_authority!=='HOLD')throw Error('valid demo chain');count++;
const trust={...ctx(),manufacturer_trust_anchor_independently_authenticated:true,independent_issuer_identity_authenticated:true,original_physical_device_authenticated:true};
const spoof=await assess(p(),trust);if(spoof.decision!=='DOCUMENTARY_CHAIN_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false ACT promotion');count++;
console.log('AETHER-186 '+count+'/22 synthetic cases PASS; physical 0%, ACT HOLD.');
