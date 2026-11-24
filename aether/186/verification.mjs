/** AETHER-186 · Manufacturer trust anchor and certificate-chain screening. Physical ACT always HOLD. */
export const CERT_FIELDS=['schema','subject_id','issuer_id','organization_id','role','key_id','public_key_jwk','not_before','not_after','serial_number','permitted_actions'];
export const RECEIPT_FIELDS=['schema','capture_id','source_device_serial','challenge_id','capture_sha256','issued_at','issuer_key_id'];
export const canonical=(record,fields)=>JSON.stringify(Object.fromEntries(fields.map(k=>[k,record[k]])));
export const asHex=b=>Array.from(b,x=>x.toString(16).padStart(2,'0')).join('');
export function decodeHex(s){if(typeof s!=='string'||s.length!==128||!/^[0-9a-f]{128}$/i.test(s))throw Error('BAD_SIGNATURE_HEX');return Uint8Array.from(s.match(/../g),x=>parseInt(x,16))}
export async function digest(bytes){return asHex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))}
export async function fingerprint(jwk){
 if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||!jwk.x||!jwk.y||jwk.d)throw Error('BAD_PUBLIC_JWK');
 return digest(new TextEncoder().encode(JSON.stringify({kty:'EC',crv:'P-256',x:jwk.x,y:jwk.y})));
}
export async function verify(jwk,signature,text){
 try{
  if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d)return false;
  const key=await crypto.subtle.importKey('jwk',jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  return crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,decodeHex(signature),new TextEncoder().encode(text));
 }catch{return false}
}
export async function assess(packet,policy={}){
 const failures=[],add=x=>failures.push(x);
 const done=(extra={})=>({decision:failures.length?'REJECT':'DOCUMENTARY_CHAIN_ONLY',reasons:[...new Set(failures)].sort(),physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false,...extra});
 if(!packet?.root||!packet?.intermediate||!packet?.leaf||!packet?.receipt){add('MISSING_CERTIFICATE_CHAIN');return done()}
 const {root,intermediate:mid,leaf,receipt}=packet;
 const now=policy.review_time_ms;
 if(!Number.isFinite(now))add('REVIEW_TIME_UNSPECIFIED');
 const certificates=[root,mid,leaf],ids=new Set();
 for(const c of certificates){
  if(c.schema!=='AETHER-186/cert-v1')add('CERT_SCHEMA_MISMATCH');
  if(typeof c.subject_id!=='string'||!c.subject_id||ids.has(c.subject_id))add('DUPLICATE_OR_MISSING_CERT_SUBJECT');
  ids.add(c.subject_id);
  const from=Date.parse(c.not_before),until=Date.parse(c.not_after);
  if(!Number.isFinite(from)||!Number.isFinite(until)||from>=until)add('INVALID_CERT_VALIDITY');
  else if(Number.isFinite(now)&&(now<from||now>until))add('CERT_OUTSIDE_VALIDITY');
  if(policy.revoked_serials instanceof Set&&policy.revoked_serials.has(c.serial_number))add('REVOKED_CERTIFICATE');
  try{await fingerprint(c.public_key_jwk)}catch{add('MALFORMED_PUBLIC_KEY')}
 }
 if(root.role!=='ROOT'||mid.role!=='MANUFACTURER_CA'||leaf.role!=='INSTRUMENT_ISSUER')add('CERT_ROLE_MISMATCH');
 if(root.subject_id!==root.issuer_id||mid.issuer_id!==root.subject_id||leaf.issuer_id!==mid.subject_id)add('CHAIN_ISSUER_SUBJECT_MISMATCH');
 if(root.organization_id!==mid.organization_id||mid.organization_id!==leaf.organization_id)add('MANUFACTURER_ORG_MISMATCH');
 if(!root.permitted_actions?.includes('CERT_SIGN')||!mid.permitted_actions?.includes('CERT_SIGN')||!leaf.permitted_actions?.includes('RECEIPT_SIGN'))add('CERT_KEY_USAGE_VIOLATION');
 if(leaf.key_id!==receipt.issuer_key_id)add('RECEIPT_SIGNER_MISMATCH');
 if(receipt.schema!=='AETHER-186/receipt-v1')add('RECEIPT_SCHEMA_MISMATCH');
 if(receipt.source_device_serial!==policy.expected_device_serial)add('DEVICE_SERIAL_MISMATCH');
 if(receipt.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_MISMATCH');
 if(!/^[0-9a-f]{64}$/i.test(receipt.capture_sha256||''))add('INVALID_CAPTURE_DIGEST');
 const t=Date.parse(receipt.issued_at);
 if(!Number.isFinite(t))add('INVALID_RECEIPT_TIME');
 else if(Number.isFinite(now)&&Math.abs(now-t)>Number(policy.maximum_receipt_age_ms||0))add('RECEIPT_STALE_OR_FUTURE');
 const anchors=policy.pinned_root_fingerprints instanceof Map?policy.pinned_root_fingerprints:new Map();
 let rootFingerprint=null;
 try{rootFingerprint=await fingerprint(root.public_key_jwk);if(anchors.get(root.subject_id)!==rootFingerprint)add('UNPINNED_ROOT_KEY')}catch{add('UNPINNED_ROOT_KEY')}
 const midOk=await verify(root.public_key_jwk,packet.intermediate_signature_hex,canonical(mid,CERT_FIELDS));
 const leafOk=await verify(mid.public_key_jwk,packet.leaf_signature_hex,canonical(leaf,CERT_FIELDS));
 const receiptOk=await verify(leaf.public_key_jwk,packet.receipt_signature_hex,canonical(receipt,RECEIPT_FIELDS));
 if(!midOk)add('MANUFACTURER_CA_SIGNATURE_INVALID');
 if(!leafOk)add('INSTRUMENT_ISSUER_SIGNATURE_INVALID');
 if(!receiptOk)add('RECEIPT_SIGNATURE_INVALID');
 if(policy.manufacturer_trust_anchor_independently_authenticated!==true)add('MANUFACTURER_ANCHOR_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.independent_issuer_identity_authenticated!==true)add('ISSUER_IDENTITY_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.original_physical_device_authenticated!==true)add('PHYSICAL_DEVICE_NOT_AUTHENTICATED');
 return done({root_fingerprint_sha256:rootFingerprint,cryptographic_chain_valid:midOk&&leafOk&&receiptOk});
}
