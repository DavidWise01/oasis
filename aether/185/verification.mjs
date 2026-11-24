/** AETHER-185 · Intake acquisition receipt gate. Authenticated-format != physically authenticated. */
export const HEX64=/^[0-9a-f]{64}$/i;
export const receiptFields=['schema','package_id','source_device_serial','source_origin_id','acquisition_challenge','capture_sha256','capture_byte_length','issued_at','intake_id','issuer_key_id'];
export const canonical=r=>JSON.stringify(Object.fromEntries(receiptFields.map(k=>[k,r[k]])));
export const hex=b=>Array.from(b,x=>x.toString(16).padStart(2,'0')).join('');
export async function sha256(bytes){if(!(bytes instanceof Uint8Array))throw Error('UINT8ARRAY_REQUIRED');return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))}
export function decode(s){if(typeof s!=='string'||s.length!==128||!/^[0-9a-f]+$/i.test(s))throw Error('BAD_P1363_SIGNATURE');return Uint8Array.from(s.match(/../g),x=>parseInt(x,16))}
export async function assess(packet,context={}){
 const reasons=[],add=x=>reasons.push(x);
 const finish=(extra={})=>({decision:reasons.length?'REJECT':'DOCUMENTARY_INTAKE_ONLY',reasons:[...new Set(reasons)].sort(),...extra,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!packet?.receipt||!(packet.bytes instanceof Uint8Array)){add('MISSING_BYTES_OR_RECEIPT');return finish()}
 const r=packet.receipt,bytes=packet.bytes;
 if(!bytes.length)add('EMPTY_ACQUISITION');
 if(r.schema!=='AETHER-185/intake-v1')add('BAD_RECEIPT_SCHEMA');
 for(const key of ['package_id','source_device_serial','source_origin_id','acquisition_challenge','intake_id','issuer_key_id'])if(typeof r[key]!=='string'||!r[key])add('MISSING_'+key.toUpperCase());
 if(!HEX64.test(r.capture_sha256||''))add('INVALID_CAPTURE_DIGEST');
 if(!Number.isSafeInteger(r.capture_byte_length)||r.capture_byte_length!==bytes.length)add('CAPTURE_BYTE_LENGTH_MISMATCH');
 if(r.acquisition_challenge!==context.expected_challenge)add('CHALLENGE_MISMATCH');
 if(r.source_device_serial!==context.expected_device_serial)add('SOURCE_DEVICE_SERIAL_MISMATCH');
 if(r.source_origin_id!==context.expected_origin_id)add('SOURCE_ORIGIN_MISMATCH');
 if(context.seen_package_ids instanceof Set&&context.seen_package_ids.has(r.package_id))add('PACKAGE_REPLAY');
 if(context.seen_intake_ids instanceof Set&&context.seen_intake_ids.has(r.intake_id))add('INTAKE_REPLAY');
 const issued=Date.parse(r.issued_at);
 if(!Number.isFinite(issued))add('INVALID_ISSUED_TIMESTAMP');
 if(Number.isFinite(context.min_receipt_time_ms)&&issued<context.min_receipt_time_ms)add('STALE_ACQUISITION_RECEIPT');
 if(Number.isFinite(context.max_receipt_time_ms)&&issued>context.max_receipt_time_ms)add('FUTURE_ACQUISITION_RECEIPT');
 let captureDigest=null;try{captureDigest=await sha256(bytes);if(captureDigest!==r.capture_sha256)add('CAPTURE_DIGEST_MISMATCH')}catch{add('CAPTURE_HASH_UNAVAILABLE')}
 const issuer=context.trusted_issuers instanceof Map?context.trusted_issuers.get(r.issuer_key_id):null;
 if(!issuer)add('UNKNOWN_ISSUER_KEY');
 else{
  if(issuer.revoked===true)add('REVOKED_ISSUER');
  if(issuer.origin_id!==r.source_origin_id)add('ISSUER_ORIGIN_MISMATCH');
  if(issuer.operator_id===context.owner_operator_id)add('SELF_ISSUED_ORIGIN');
 }
 let signatureValid=false;
 try{
  if(!issuer?.public_key_jwk||issuer.public_key_jwk.kty!=='EC'||issuer.public_key_jwk.crv!=='P-256'||issuer.public_key_jwk.d)throw Error('INVALID_ISSUER_KEY');
  const key=await crypto.subtle.importKey('jwk',issuer.public_key_jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  signatureValid=await crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,decode(packet.signature_hex),new TextEncoder().encode(canonical(r)));
  if(!signatureValid)add('ACQUISITION_RECEIPT_SIGNATURE_INVALID');
 }catch{add('ACQUISITION_RECEIPT_SIGNATURE_INVALID')}
 if(context.externally_authenticated_issuer_registry!==true)add('ISSUER_REGISTRY_NOT_EXTERNALLY_AUTHENTICATED');
 if(context.hardware_source_verified_by_manufacturer!==true)add('HARDWARE_ORIGIN_UNVERIFIED');
 if(context.original_physical_acquisition_verified!==true)add('PHYSICAL_ACQUISITION_UNVERIFIED');
 if(context.independent_custody_verified!==true)add('INDEPENDENT_CUSTODY_UNVERIFIED');
 return finish({computed_capture_sha256:captureDigest,signature_cryptographically_valid:signatureValid})
}
