/** AETHER-187 · signed external verifier/capture custody; synthetic fixtures are NOT physical evidence. */
export const HEX64=/^[a-f0-9]{64}$/i;
export const ACQ_FIELDS=['schema','capture_id','device_serial','challenge_id','capture_sha256','byte_length','acquired_at','source_root_id','issuer_key_id'];
export const VERIFY_FIELDS=['schema','verification_id','capture_id','capture_sha256','acquisition_receipt_sha256','custody_receipt_sha256','verifier_id','verifier_root_id','verifier_key_id','verified_at'];
export const CUSTODY_FIELDS=['schema','custody_id','capture_id','capture_sha256','from_party','to_party','transfer_at'];
export const canonical=(obj,fields)=>JSON.stringify(Object.fromEntries(fields.map(k=>[k,obj[k]])));
export const hex=bytes=>[...bytes].map(v=>v.toString(16).padStart(2,'0')).join('');
export const sha256=async bytes=>{if(!(bytes instanceof Uint8Array))throw Error('EXPECTED_RAW_BYTES');return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))};
export async function verify(jwk,signature_hex,text){
 try{
  if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d||typeof signature_hex!=='string'||!/^[a-f0-9]{128}$/i.test(signature_hex))return false;
  const key=await crypto.subtle.importKey('jwk',jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  return await crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,Uint8Array.from(signature_hex.match(/../g),v=>parseInt(v,16)),new TextEncoder().encode(text));
 }catch{return false}
}
export async function assess(packet,policy={}){
 const reasons=[],add=x=>reasons.push(x);
 const finish=(extra={})=>({decision:reasons.length?'REJECT':'DOCUMENTARY_VERIFICATION_ONLY',reasons:[...new Set(reasons)].sort(),physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false,...extra});
 if(!packet||!(packet.raw_bytes instanceof Uint8Array)||!packet.acquisition||!packet.custody||!packet.verification){add('INCOMPLETE_EXTERNAL_EVIDENCE_BUNDLE');return finish()}
 const a=packet.acquisition,c=packet.custody,v=packet.verification;
 if(a.schema!=='AETHER-187/acquisition-v1'||c.schema!=='AETHER-187/custody-v1'||v.schema!=='AETHER-187/verification-v1')add('SCHEMA_MISMATCH');
 if(!packet.raw_bytes.length)add('EMPTY_ACQUISITION_BYTES');
 if(!HEX64.test(a.capture_sha256||'')||!HEX64.test(c.capture_sha256||'')||!HEX64.test(v.capture_sha256||''))add('INVALID_CAPTURE_DIGEST');
 if(a.capture_id!==c.capture_id||a.capture_id!==v.capture_id||a.capture_sha256!==c.capture_sha256||a.capture_sha256!==v.capture_sha256)add('CROSS_RECORD_CAPTURE_MISMATCH');
 if(!Number.isSafeInteger(a.byte_length)||packet.raw_bytes.length!==a.byte_length)add('BYTE_LENGTH_MISMATCH');
 if(a.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_MISMATCH');
 if(a.device_serial!==policy.expected_device_serial)add('DEVICE_SERIAL_MISMATCH');
 if(policy.seen_capture_ids instanceof Set&&policy.seen_capture_ids.has(a.capture_id))add('REPLAYED_CAPTURE');
 if(policy.seen_verification_ids instanceof Set&&policy.seen_verification_ids.has(v.verification_id))add('REPLAYED_VERIFICATION');
 if(a.source_root_id===v.verifier_root_id)add('SHARED_SOURCE_VERIFIER_ROOT');
 const acquired=Date.parse(a.acquired_at),transfer=Date.parse(c.transfer_at),verified=Date.parse(v.verified_at);
 if(![acquired,transfer,verified].every(Number.isFinite)||!(acquired<=transfer&&transfer<=verified))add('NONMONOTONIC_CUSTODY_TIME');
 if(c.from_party===c.to_party||!c.from_party||!c.to_party)add('INVALID_CUSTODY_HANDOFF');
 if(v.verifier_id===c.to_party||v.verifier_id===c.from_party)add('VERIFIER_OVERLAPS_CUSTODIAN');
 let computed_capture=null,acquisition_hash=null,custody_hash=null;
 try{
  const te=new TextEncoder();computed_capture=await sha256(packet.raw_bytes);acquisition_hash=await sha256(te.encode(canonical(a,ACQ_FIELDS)));custody_hash=await sha256(te.encode(canonical(c,CUSTODY_FIELDS)));
  if(computed_capture!==a.capture_sha256)add('RAW_CAPTURE_SUBSTITUTION');
  if(acquisition_hash!==v.acquisition_receipt_sha256)add('ACQUISITION_RECEIPT_DIGEST_MISMATCH');
  if(custody_hash!==v.custody_receipt_sha256)add('CUSTODY_RECEIPT_DIGEST_MISMATCH');
 }catch{add('HASH_CALCULATION_FAILED')}
 const issuers=policy.issuer_keys instanceof Map?policy.issuer_keys:new Map(),verifiers=policy.verifier_keys instanceof Map?policy.verifier_keys:new Map();
 const issuer=issuers.get(a.issuer_key_id),verifier=verifiers.get(v.verifier_key_id);
 if(!issuer||!verifier)add('EXTERNAL_KEYS_NOT_REGISTERED');
 if(issuer&&issuer.root_id!==a.source_root_id)add('ISSUER_ROOT_MISMATCH');
 if(verifier&&(verifier.root_id!==v.verifier_root_id||verifier.verifier_id!==v.verifier_id))add('VERIFIER_IDENTITY_KEY_MISMATCH');
 if(issuer?.operator_id&&issuer.operator_id===verifier?.operator_id)add('SHARED_ISSUER_VERIFIER_OPERATOR');
 if(issuer?.administrator_id&&issuer.administrator_id===verifier?.administrator_id)add('SHARED_ISSUER_VERIFIER_ADMINISTRATOR');
 if(issuer?.revoked||verifier?.revoked)add('REVOKED_SIGNER');
 const acquisitionSignatureValid=await verify(issuer?.jwk,packet.acquisition_signature_hex,canonical(a,ACQ_FIELDS));
 const verificationSignatureValid=await verify(verifier?.jwk,packet.verification_signature_hex,canonical(v,VERIFY_FIELDS));
 if(!acquisitionSignatureValid)add('ACQUISITION_SIGNATURE_INVALID');
 if(!verificationSignatureValid)add('EXTERNAL_VERIFIER_SIGNATURE_INVALID');
 if(policy.independent_issuer_identity_authenticated!==true)add('ISSUER_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.independent_verifier_identity_authenticated!==true)add('VERIFIER_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.original_hardware_capture_authenticated!==true)add('ORIGINAL_HARDWARE_NOT_AUTHENTICATED');
 if(policy.external_custody_provenance_authenticated!==true)add('CUSTODY_NOT_EXTERNALLY_AUTHENTICATED');
 return finish({computed_capture_sha256:computed_capture,acquisition_signature_valid:acquisitionSignatureValid,verification_signature_valid:verificationSignatureValid});
}
