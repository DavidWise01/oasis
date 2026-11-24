/** AETHER-182 — software archive replica integrity checks. No operational ACT. */
export const HEX64=/^[a-f0-9]{64}$/i;
export const RECEIPT_FIELDS=['replica_id','archive_id','root_id','administrator_id','generation','manifest_sha256','bytes_sha256','previous_receipt_sha256','receipt_issued_utc'];
export function canonicalReceipt(r){return JSON.stringify(Object.fromEntries(RECEIPT_FIELDS.map(k=>[k,r[k]])))}
export async function sha256(bytes){
 if(!(bytes instanceof Uint8Array))throw new TypeError('EXPECTED_BYTES');
 const digest=await globalThis.crypto.subtle.digest('SHA-256',bytes);
 return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
}
export async function assess(packet,policy={}){
 const errors=[],add=x=>errors.push(x);
 const output=(extra={})=>({status:errors.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(errors)].sort(),physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false,...extra});
 if(!packet||!packet.manifest||!Array.isArray(packet.replicas)||packet.replicas.length!==3){add('THREE_REPLICAS_REQUIRED');return output()}
 const m=packet.manifest;
 if(m.schema!=='AETHER-182/v1')add('INVALID_MANIFEST_SCHEMA');
 if(!HEX64.test(m.capture_sha256||''))add('INVALID_MANIFEST_CAPTURE_DIGEST');
 if(!Number.isSafeInteger(m.generation)||m.generation<0)add('INVALID_MANIFEST_GENERATION');
 if(typeof m.capture_id!=='string'||!m.capture_id)add('MISSING_CAPTURE_ID');
 if(typeof m.challenge_id!=='string'||m.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_MISMATCH');
 const canonical=JSON.stringify({schema:m.schema,capture_id:m.capture_id,challenge_id:m.challenge_id,generation:m.generation,capture_sha256:m.capture_sha256});
 let manifestHash=null;
 try{manifestHash=await sha256(new TextEncoder().encode(canonical));if(manifestHash!==m.manifest_sha256)add('MANIFEST_DIGEST_MISMATCH')}
 catch{add('MANIFEST_HASH_UNAVAILABLE')}
 const ids=new Set(),archives=new Set(),roots=new Set(),admins=new Set();
 const diagnostics=[];
 for(const item of packet.replicas){
  if(!item||!(item.bytes instanceof Uint8Array)||!item.receipt){add('MISSING_REPLICA_BYTES_OR_RECEIPT');continue}
  const r=item.receipt;
  for(const key of ['replica_id','archive_id','root_id','administrator_id'])if(typeof r[key]!=='string'||!r[key])add('MISSING_'+key.toUpperCase());
  if(ids.has(r.replica_id))add('DUPLICATE_REPLICA_ID');ids.add(r.replica_id);
  if(archives.has(r.archive_id))add('SHARED_ARCHIVE_ID');archives.add(r.archive_id);
  if(roots.has(r.root_id))add('SHARED_ROOT_ANCESTRY');roots.add(r.root_id);
  if(admins.has(r.administrator_id))add('SHARED_ADMINISTRATOR');admins.add(r.administrator_id);
  if(r.generation!==m.generation||!Number.isSafeInteger(r.generation))add('REPLICA_GENERATION_MISMATCH');
  if(Number.isSafeInteger(policy.minimum_generation)&&r.generation<policy.minimum_generation)add('ARCHIVE_ROLLBACK');
  if(r.manifest_sha256!==m.manifest_sha256)add('REPLICA_MANIFEST_MISMATCH');
  if(!HEX64.test(r.bytes_sha256||''))add('INVALID_RECEIPT_BYTES_DIGEST');
  if(!HEX64.test(r.receipt_sha256||''))add('INVALID_RECEIPT_DIGEST');
  if(policy.expected_previous_receipts instanceof Map){
   const expected=policy.expected_previous_receipts.get(r.archive_id);
   if(expected!==undefined&&r.previous_receipt_sha256!==expected)add('BROKEN_ARCHIVE_PREDECESSOR');
  }
  if(!Number.isFinite(Date.parse(r.receipt_issued_utc)))add('INVALID_RECEIPT_TIME');
  let digest=null,receiptDigest=null;
  try {
   digest=await sha256(item.bytes);
   if(digest!==m.capture_sha256||digest!==r.bytes_sha256)add('REPLICA_BYTES_MISMATCH');
   receiptDigest=await sha256(new TextEncoder().encode(canonicalReceipt(r)));
   if(receiptDigest!==r.receipt_sha256)add('RECEIPT_CONTENT_MISMATCH');
  } catch{add('REPLICA_HASH_UNAVAILABLE')}
  diagnostics.push({archive_id:r.archive_id,declared_root:r.root_id,digest,receipt_digest:receiptDigest});
 }
 if(ids.size!==3||archives.size!==3)add('NOT_THREE_DISTINCT_REPLICA_IDS');
 if(roots.size!==3)add('NOT_THREE_DISTINCT_DECLARED_ROOTS');
 if(admins.size!==3)add('NOT_THREE_DISTINCT_DECLARED_ADMINS');
 if(policy.external_archive_root_authentication!==true)add('ARCHIVE_ROOTS_UNAUTHENTICATED');
 if(policy.external_custody_signatures_authenticated!==true)add('ARCHIVE_RECEIPTS_UNAUTHENTICATED');
 if(policy.original_physical_capture_authenticated!==true)add('PHYSICAL_CAPTURE_UNAUTHENTICATED');
 // Equal bytes and declared different roots are never proof of independent real-world origins.
 return output({manifest_digest:manifestHash,replicas_checked:diagnostics});
}
