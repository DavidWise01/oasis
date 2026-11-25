/** AETHER-190 — Blind external-source replay audit. No physical ACT pathway. */
export const HEX64=/^[a-f0-9]{64}$/i;
export const RECORD_FIELDS=['schema','trial_id','capture_id','challenge_id','challenge_nonce','capture_sha256','sample_count','acquired_utc','source_handle','verification_handle'];
export const canonical=(o,fields)=>JSON.stringify(Object.fromEntries(fields.map(k=>[k,o[k]])));
export const hex=b=>Array.from(b,x=>x.toString(16).padStart(2,'0')).join('');
export const sha256=async bytes=>{if(!(bytes instanceof Uint8Array))throw Error('UINT8ARRAY_REQUIRED');return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))};
export function blindView(record){
 return Object.freeze({trial_id:record.trial_id,capture_id:record.capture_id,challenge_id:record.challenge_id,challenge_nonce:record.challenge_nonce,capture_sha256:record.capture_sha256,sample_count:record.sample_count,acquired_utc:record.acquired_utc,source_handle:record.source_handle,verification_handle:record.verification_handle});
}
export async function verify(jwk,sig,obj){
 try{
  if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d||typeof sig!=='string'||!/^[0-9a-f]{128}$/i.test(sig))return false;
  const key=await crypto.subtle.importKey('jwk',jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  return crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,Uint8Array.from(sig.match(/../g),v=>parseInt(v,16)),new TextEncoder().encode(canonical(obj,RECORD_FIELDS)));
 }catch{return false}
}
export async function assess(packet,policy={}){
 const failures=[],add=x=>failures.push(x);
 const done=(details={})=>({decision:failures.length?'REJECT':'DOCUMENTARY_BLIND_REVIEW_ONLY',reasons:[...new Set(failures)].sort(),...details,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!Array.isArray(packet?.entries)||packet.entries.length!==3){add('THREE_BLINDED_CAPTURES_REQUIRED');return done()}
 const sources=policy.external_source_registry instanceof Map?policy.external_source_registry:new Map();
 const verifiers=policy.external_verifier_registry instanceof Map?policy.external_verifier_registry:new Map();
 const history=policy.seen_nonce_keys instanceof Set?policy.seen_nonce_keys:new Set();
 const seenNonces=new Set(),seenCaptures=new Set(),seenTrials=new Set(),roots=new Set(),operators=new Set(),admins=new Set(),sourceOwners=new Set(),verifierOwners=new Set();
 const diagnostics=[];let signatureCount=0;
 for(const e of packet.entries){
  if(!e?.record||!(e.bytes instanceof Uint8Array)){add('MISSING_CAPTURE_OR_BYTES');continue}
  const r=blindView(e.record);
  if(e.record.schema!=='AETHER-190/capture-v1')add('CAPTURE_SCHEMA_MISMATCH');
  if(!HEX64.test(r.capture_sha256||''))add('MALFORMED_CAPTURE_HASH');
  if(r.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_ID_MISMATCH');
  if(!Number.isSafeInteger(r.sample_count)||r.sample_count<1||r.sample_count!==policy.expected_sample_count)add('SAMPLE_COUNT_MISMATCH');
  if(!Number.isFinite(Date.parse(r.acquired_utc)))add('INVALID_CAPTURE_TIME');
  if(seenTrials.has(r.trial_id))add('DUPLICATE_TRIAL_ID');seenTrials.add(r.trial_id);
  if(seenCaptures.has(r.capture_id))add('DUPLICATE_CAPTURE_ID');seenCaptures.add(r.capture_id);
  const nonceKey=r.challenge_id+':'+r.challenge_nonce;
  if(!r.challenge_nonce||seenNonces.has(nonceKey)||history.has(nonceKey))add('CHALLENGE_NONCE_REPLAY');
  seenNonces.add(nonceKey);
  let actual=null;try{actual=await sha256(e.bytes);if(actual!==r.capture_sha256)add('RAW_CAPTURE_DIGEST_MISMATCH')}catch{add('DIGEST_UNAVAILABLE')}
  const s=sources.get(r.source_handle),v=verifiers.get(r.verification_handle);
  if(!s||!v){add('MISSING_INDEPENDENT_REGISTRY_RECORD');continue}
  if(!s.authenticated||!v.authenticated)add('EXTERNAL_CREDENTIAL_UNAUTHENTICATED');
  if(s.root_id===v.root_id||s.operator_id===v.operator_id||s.administrator_id===v.administrator_id)add('SOURCE_VERIFIER_SHARED_CONTROL');
  if(s.operator_id===v.operator_id||s.administrator_id===v.administrator_id)add('VERIFIER_NOT_INDEPENDENT');
  if(roots.has(s.root_id))add('CROSS_CAPTURE_SHARED_ROOT');roots.add(s.root_id);
  if(operators.has(s.operator_id))add('CROSS_CAPTURE_SHARED_OPERATOR');operators.add(s.operator_id);
  if(admins.has(s.administrator_id))add('CROSS_CAPTURE_SHARED_ADMIN');admins.add(s.administrator_id);
  if(sourceOwners.has(s.physical_source_ancestry))add('DUPLICATED_PHYSICAL_SOURCE_ANCESTRY');sourceOwners.add(s.physical_source_ancestry);
  if(verifierOwners.has(v.physical_source_ancestry))add('REUSED_EXTERNAL_VERIFIER_ANCESTRY');verifierOwners.add(v.physical_source_ancestry);
  if(!s.physical_source_ancestry||!v.physical_source_ancestry)add('MISSING_EXTERNAL_ANCESTRY');
  if(s.root_id===v.physical_source_ancestry||s.physical_source_ancestry===v.physical_source_ancestry)add('ROOT_ANCESTRY_COLLISION');
  if(v.capture_sha256!==r.capture_sha256||v.challenge_id!==r.challenge_id)add('EXTERNAL_VERIFICATION_MISMATCH');
  const ok=await verify(s.jwk,e.signature_hex,e.record);if(!ok)add('CAPTURE_SIGNATURE_INVALID');else signatureCount++;
  diagnostics.push({capture_id:r.capture_id,blind:r,computed_sha256:actual,signature_valid:ok});
 }
 if(seenTrials.size!==3||seenCaptures.size!==3||seenNonces.size!==3)add('THREE_UNIQUE_TRIALS_REQUIRED');
 if(roots.size!==3||operators.size!==3||admins.size!==3||sourceOwners.size!==3)add('THREE_DISTINCT_DECLARED_ROOTS_REQUIRED');
 if(policy.external_registries_out_of_band_authenticated!==true)add('REGISTRIES_NOT_OUT_OF_BAND_AUTHENTICATED');
 if(policy.real_hardware_origins_authenticated!==true)add('ORIGINAL_HARDWARE_NOT_AUTHENTICATED');
 if(policy.physical_replay_observation_authenticated!==true)add('PHYSICAL_REPLAY_NOT_AUTHENTICATED');
 return done({signed_capture_count:signatureCount,review:diagnostics});
}
