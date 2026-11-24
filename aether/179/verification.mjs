/** AETHER-179 · WebCrypto ECDSA P-256 signature gate. Cryptographic validity != physical identity. */
export const fields=['schema','event_id','capture_sha256','custodian_id','key_id','action','sequence','timestamp','previous_event_sha256','challenge_id'];
export function canonicalEvent(e){const out={};for(const k of fields)out[k]=e[k];return JSON.stringify(out)}
export function hexToBytes(hex){
 if(typeof hex!=='string'||hex.length%2!==0||!/^[0-9a-f]*$/i.test(hex))throw Error('INVALID_HEX');
 return Uint8Array.from(hex.match(/../g)||[],x=>parseInt(x,16))
}
export function bytesToHex(bytes){return Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('')}
export async function sha256(bytes){const digest=await crypto.subtle.digest('SHA-256',bytes);return bytesToHex(new Uint8Array(digest))}
const hex64=/^[0-9a-f]{64}$/i;
export async function assess(packet,policy={}){
 const failures=[];
 const add=x=>failures.push(x);
 const finish=(details={})=>({status:failures.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(failures)].sort(),...details,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!packet||!packet.event||typeof packet.event!=='object')return finish({reasons:['MISSING_CUSTODY_EVENT'],status:'REJECT'});
 const e=packet.event;
 if(e.schema!=='AETHER-179/v1')add('BAD_SCHEMA');
 for(const f of ['event_id','custodian_id','key_id','action','timestamp','challenge_id']){
  if(typeof e[f]!=='string'||!e[f])add('MISSING_'+f.toUpperCase())
 }
 if(!['ACQUIRE','TRANSFER','RECEIVE','SEAL'].includes(e.action))add('INVALID_ACTION');
 if(!Number.isSafeInteger(e.sequence)||e.sequence<0)add('INVALID_SEQUENCE');
 if(!hex64.test(e.capture_sha256||''))add('INVALID_CAPTURE_DIGEST');
 if(e.previous_event_sha256!==null&&!hex64.test(e.previous_event_sha256||''))add('INVALID_PREVIOUS_EVENT_DIGEST');
 if(e.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_MISMATCH');
 if(e.event_id===policy.replayed_event_id||(policy.used_event_ids instanceof Set&&policy.used_event_ids.has(e.event_id)))add('EVENT_REPLAY');
 const t=Date.parse(e.timestamp);
 if(!Number.isFinite(t))add('INVALID_EVENT_TIME');
 if(Number.isFinite(policy.min_time_ms)&&t<policy.min_time_ms)add('EVENT_EXPIRED');
 if(Number.isFinite(policy.max_time_ms)&&t>policy.max_time_ms)add('EVENT_FROM_FUTURE');
 const registry=policy.key_registry instanceof Map?policy.key_registry.get(e.key_id):null;
 if(!registry)add('UNREGISTERED_PUBLIC_KEY');
 else {
  if(registry.custodian_id!==e.custodian_id)add('CUSTODIAN_KEY_MISMATCH');
  if(!Array.isArray(registry.allowed_actions)||!registry.allowed_actions.includes(e.action))add('UNAUTHORIZED_ACTION');
  if(registry.revoked===true)add('REVOKED_KEY');
  if(registry.algorithm!=='ECDSA-P256-SHA256')add('UNSUPPORTED_SIGNER_ALGORITHM');
  if(Number.isFinite(registry.not_before_ms)&&t<registry.not_before_ms)add('SIGNER_NOT_YET_VALID');
  if(Number.isFinite(registry.not_after_ms)&&t>registry.not_after_ms)add('SIGNER_EXPIRED');
  if(registry.expected_fingerprint_sha256&&registry.fingerprint_sha256!==registry.expected_fingerprint_sha256)add('UNTRUSTED_KEY_FINGERPRINT');
 }
 let signatureValid=false;
 try{
  if(!globalThis.crypto?.subtle)throw Error('NO_WEBCRYPTO');
  if(!registry?.public_key_jwk||registry.algorithm!=='ECDSA-P256-SHA256')throw Error('MISSING_OR_INVALID_PUBLIC_KEY');
  if(registry.public_key_jwk.kty!=='EC'||registry.public_key_jwk.crv!=='P-256'||registry.public_key_jwk.d)throw Error('NOT_PUBLIC_P256_JWK');
  const pub=await crypto.subtle.importKey('jwk',registry.public_key_jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  const bytes=new TextEncoder().encode(canonicalEvent(e));
  const signature=hexToBytes(packet.signature_hex);
  if(signature.length!==64)throw Error('BAD_SIGNATURE_LENGTH');
  signatureValid=await crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},pub,signature,bytes);
  if(!signatureValid)add('SIGNATURE_VERIFICATION_FAILED');
 }catch{add('SIGNATURE_VERIFICATION_FAILED')}
 if(!signatureValid)add('UNVERIFIED_CUSTODY_SIGNATURE');
 if(policy.external_custodian_identity_authenticated!==true)add('CUSTODIAN_IDENTITY_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.external_registry_trust_authenticated!==true)add('REGISTRY_ROOT_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.original_hardware_capture_authenticated!==true)add('ORIGINAL_HARDWARE_CAPTURE_NOT_AUTHENTICATED');
 // A client-provided registry, signature and all trust booleans never authorize physical ACT.
 return finish({cryptographic_signature_valid:signatureValid});
}
