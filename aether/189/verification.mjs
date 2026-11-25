/** AETHER-189 · Signed custody handoff / separate-root identity screening.
 * Synthetic credentials do NOT authenticate people or physical custody. ACT always HOLD.
 */
export const HEX64=/^[0-9a-f]{64}$/i;
export const TRANSFER_FIELDS=['schema','handoff_id','capture_id','capture_sha256','from_id','to_id','sender_key_id','challenge_id','sequence','transfer_utc','previous_receipt_sha256'];
export const RECEIPT_FIELDS=['schema','receipt_id','handoff_id','handoff_sha256','capture_id','capture_sha256','from_id','to_id','receiver_key_id','challenge_id','received_utc'];
export const canonical=(v,fields)=>JSON.stringify(Object.fromEntries(fields.map(k=>[k,v[k]])));
export const hex=bytes=>[...bytes].map(b=>b.toString(16).padStart(2,'0')).join('');
export async function sha256(bytes){if(!(bytes instanceof Uint8Array))throw Error('UINT8ARRAY_REQUIRED');return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))}
export async function fingerprint(jwk){if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d)throw Error('INVALID_PUBLIC_KEY');return sha256(new TextEncoder().encode(JSON.stringify({kty:'EC',crv:'P-256',x:jwk.x,y:jwk.y})))}
export async function verify(jwk,sig,text){
 try{
  if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d||typeof sig!=='string'||!/^[a-f0-9]{128}$/i.test(sig))return false;
  const key=await crypto.subtle.importKey('jwk',jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  return await crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,Uint8Array.from(sig.match(/../g),x=>parseInt(x,16)),new TextEncoder().encode(text));
 }catch{return false}
}
export async function assess(packet,policy={}){
 const failures=[],add=x=>failures.push(x);
 const end=(extra={})=>({decision:failures.length?'REJECT':'DOCUMENTARY_HANDOFF_ONLY',reasons:[...new Set(failures)].sort(),...extra,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!packet?.transfer||!packet?.receipt){add('MISSING_TRANSFER_OR_RECEIPT');return end()}
 const t=packet.transfer,r=packet.receipt,enc=new TextEncoder();
 if(t.schema!=='AETHER-189/transfer-v1'||r.schema!=='AETHER-189/receipt-v1')add('SCHEMA_MISMATCH');
 for(const [v,fields]of [[t,TRANSFER_FIELDS],[r,RECEIPT_FIELDS]])for(const field of fields)if(v[field]===undefined)add('MISSING_'+field.toUpperCase());
 if(!HEX64.test(t.capture_sha256||'')||!HEX64.test(r.capture_sha256||''))add('INVALID_CAPTURE_SHA256');
 if(!HEX64.test(r.handoff_sha256||''))add('INVALID_HANDOFF_SHA256');
 if(t.from_id===t.to_id||!t.from_id||!t.to_id)add('SAME_OR_MISSING_CUSTODIAN');
 if(t.sender_key_id===r.receiver_key_id)add('REUSED_CUSTODIAN_KEY');
 if(t.handoff_id!==r.handoff_id||t.capture_id!==r.capture_id||t.capture_sha256!==r.capture_sha256||t.from_id!==r.from_id||t.to_id!==r.to_id)add('TRANSFER_RECEIPT_MISMATCH');
 if(t.challenge_id!==r.challenge_id||t.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_MISMATCH');
 if(!Number.isSafeInteger(t.sequence)||t.sequence<0)add('BAD_SEQUENCE');
 if(policy.used_handoff_ids instanceof Set&&policy.used_handoff_ids.has(t.handoff_id))add('HANDOFF_REPLAY');
 if(policy.used_receipt_ids instanceof Set&&policy.used_receipt_ids.has(r.receipt_id))add('RECEIPT_REPLAY');
 if(policy.expected_previous_receipt_sha256!==undefined&&t.previous_receipt_sha256!==policy.expected_previous_receipt_sha256)add('PREDECESSOR_MISMATCH');
 const transferTime=Date.parse(t.transfer_utc),receiptTime=Date.parse(r.received_utc);
 if(!Number.isFinite(transferTime)||!Number.isFinite(receiptTime))add('INVALID_CUSTODY_TIME');
 else{
  if(receiptTime<transferTime)add('RECEIPT_PRECEDES_TRANSFER');
  if(Number.isFinite(policy.max_receipt_delay_ms)&&receiptTime-transferTime>policy.max_receipt_delay_ms)add('RECEIPT_TOO_LATE');
 }
 let computedHandoff=null;
 try{computedHandoff=await sha256(enc.encode(canonical(t,TRANSFER_FIELDS)));if(computedHandoff!==r.handoff_sha256)add('RECEIPT_HANDOFF_DIGEST_MISMATCH')}
 catch{add('DIGEST_UNAVAILABLE')}
 const keys=policy.custodian_keys instanceof Map?policy.custodian_keys:new Map();
 const sender=keys.get(t.sender_key_id),receiver=keys.get(r.receiver_key_id);
 if(!sender||!receiver)add('MISSING_CUSTODIAN_CREDENTIAL');
 if(sender?.custodian_id!==t.from_id)add('SENDER_KEY_IDENTITY_MISMATCH');
 if(receiver?.custodian_id!==t.to_id)add('RECEIVER_KEY_IDENTITY_MISMATCH');
 if(sender?.revoked===true||receiver?.revoked===true)add('REVOKED_CREDENTIAL');
 if(sender&&!sender.actions?.includes('TRANSFER'))add('SENDER_LACKS_TRANSFER_PERMISSION');
 if(receiver&&!receiver.actions?.includes('RECEIVE'))add('RECEIVER_LACKS_RECEIVE_PERMISSION');
 if(sender&&receiver){
  if(sender.ancestry_root===receiver.ancestry_root)add('SHARED_CREDENTIAL_ANCESTRY');
  if(sender.operator_id===receiver.operator_id)add('SHARED_CREDENTIAL_OPERATOR');
  if(sender.administrator_id===receiver.administrator_id)add('SHARED_CREDENTIAL_ADMINISTRATOR');
 }
 const pins=policy.pinned_root_fingerprints instanceof Map?policy.pinned_root_fingerprints:new Map();
 for(const credential of [sender,receiver]){
  if(!credential)continue;
  try{
   const actual=await fingerprint(credential.jwk);
   if(!credential.ancestry_root||pins.get(credential.ancestry_root)!==actual)add('UNPINNED_CUSTODIAN_ROOT');
  }catch{add('UNPINNED_CUSTODIAN_ROOT')}
 }
 const sender_signature_valid=await verify(sender?.jwk,packet.sender_signature_hex,canonical(t,TRANSFER_FIELDS));
 const receiver_signature_valid=await verify(receiver?.jwk,packet.receiver_signature_hex,canonical(r,RECEIPT_FIELDS));
 if(!sender_signature_valid)add('SENDER_SIGNATURE_INVALID');
 if(!receiver_signature_valid)add('RECEIVER_SIGNATURE_INVALID');
 if(policy.sender_identity_externally_authenticated!==true)add('SENDER_IDENTITY_UNAUTHENTICATED');
 if(policy.receiver_identity_externally_authenticated!==true)add('RECEIVER_IDENTITY_UNAUTHENTICATED');
 if(policy.separate_root_control_externally_authenticated!==true)add('SEPARATE_CONTROL_UNAUTHENTICATED');
 if(policy.original_hardware_custody_physically_verified!==true)add('PHYSICAL_HANDOFF_UNVERIFIED');
 // Never promote actual physical authority from local signatures, pins or boolean attestations.
 return end({computed_handoff_sha256:computedHandoff,sender_signature_valid,receiver_signature_valid});
}
