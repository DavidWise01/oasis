/** AETHER-180 — sender/receiver P-256 countersignature validation; physical ACT permanently HOLD. */
export const transferFields=['schema','transfer_id','capture_sha256','from_custodian','to_custodian','sender_key_id','challenge_id','sequence','time_utc','previous_receipt_sha256'];
export const receiptFields=['schema','receipt_id','transfer_id','transfer_sha256','capture_sha256','from_custodian','to_custodian','receiver_key_id','challenge_id','time_utc'];
export const canonical=(obj,keys)=>JSON.stringify(Object.fromEntries(keys.map(k=>[k,obj[k]])));
export const hex=(bytes)=>Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
export const decode=(text)=>{if(typeof text!=='string'||text.length%2||!/^[a-f0-9]*$/i.test(text))throw Error('BAD_HEX');return Uint8Array.from(text.match(/../g)||[],x=>parseInt(x,16))};
export const sha256=async(bytes)=>hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)));
export async function verifySignature(jwk,hexSignature,bytes){
 if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d||!globalThis.crypto?.subtle)return false;
 try {const key=await crypto.subtle.importKey('jwk',jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
 const sig=decode(hexSignature);return sig.length===64&&await crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,sig,bytes)}
 catch{return false}
}
export async function assess(packet,policy={}){
 const reasons=[],add=x=>reasons.push(x);
 const done=(details={})=>({status:reasons.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(reasons)].sort(),...details,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!packet?.transfer||!packet?.receipt){add('MISSING_TRANSFER_OR_RECEIPT');return done()}
 const t=packet.transfer,r=packet.receipt,enc=new TextEncoder(),regex=/^[a-f0-9]{64}$/i;
 if(t.schema!=='AETHER-180/transfer-v1'||r.schema!=='AETHER-180/receipt-v1')add('BAD_SCHEMA');
 for(const [obj,fields]of [[t,transferFields],[r,receiptFields]])for(const k of fields)if(obj[k]===undefined)add('MISSING_'+k.toUpperCase());
 if(!regex.test(t.capture_sha256||'')||!regex.test(r.capture_sha256||''))add('INVALID_CAPTURE_DIGEST');
 if(!regex.test(r.transfer_sha256||''))add('INVALID_TRANSFER_DIGEST');
 if(!Number.isSafeInteger(t.sequence)||t.sequence<0)add('INVALID_SEQUENCE');
 if(t.from_custodian===t.to_custodian)add('SAME_CUSTODIAN_BOTH_ROLES');
 if(t.sender_key_id===r.receiver_key_id)add('REUSED_KEY_FOR_BOTH_ROLES');
 if(t.transfer_id!==r.transfer_id||t.capture_sha256!==r.capture_sha256||t.from_custodian!==r.from_custodian||t.to_custodian!==r.to_custodian)add('TRANSFER_RECEIPT_MISMATCH');
 if(t.challenge_id!==r.challenge_id||t.challenge_id!==policy.expected_challenge_id)add('CHALLENGE_MISMATCH');
 if(policy.used_transfer_ids instanceof Set&&policy.used_transfer_ids.has(t.transfer_id))add('REPLAYED_TRANSFER');
 if(policy.used_receipt_ids instanceof Set&&policy.used_receipt_ids.has(r.receipt_id))add('REPLAYED_RECEIPT');
 const tt=Date.parse(t.time_utc),rt=Date.parse(r.time_utc);
 if(!Number.isFinite(tt)||!Number.isFinite(rt))add('INVALID_TIMESTAMP');
 else if(rt<tt)add('RECEIPT_BEFORE_TRANSFER');
 else if(Number.isFinite(policy.max_receipt_delay_ms)&&rt-tt>policy.max_receipt_delay_ms)add('RECEIPT_DELAY_EXCEEDED');
 if(policy.expected_previous_receipt_sha256!==undefined&&t.previous_receipt_sha256!==policy.expected_previous_receipt_sha256)add('BROKEN_ESCROW_PREDECESSOR');
 const transferBytes=enc.encode(canonical(t,transferFields)),receiptBytes=enc.encode(canonical(r,receiptFields));
 let digest=null;
 try{digest=await sha256(transferBytes);if(digest!==r.transfer_sha256)add('RECEIPT_NOT_BOUND_TO_TRANSFER')}catch{add('HASH_CALCULATION_FAILED')}
 const registry=policy.key_registry instanceof Map?policy.key_registry:new Map(),sender=registry.get(t.sender_key_id),receiver=registry.get(r.receiver_key_id);
 if(!sender||!receiver)add('UNREGISTERED_CUSTODIAN_KEY');
 if(sender&&sender.custodian_id!==t.from_custodian)add('SENDER_IDENTITY_KEY_MISMATCH');
 if(receiver&&receiver.custodian_id!==t.to_custodian)add('RECEIVER_IDENTITY_KEY_MISMATCH');
 if(sender?.revoked===true||receiver?.revoked===true)add('REVOKED_CUSTODIAN_KEY');
 if(sender&&!sender.allowed_actions?.includes('TRANSFER'))add('SENDER_NOT_AUTHORIZED');
 if(receiver&&!receiver.allowed_actions?.includes('RECEIVE'))add('RECEIVER_NOT_AUTHORIZED');
 const senderValid=await verifySignature(sender?.public_key_jwk,packet.sender_signature_hex,transferBytes);
 const receiverValid=await verifySignature(receiver?.public_key_jwk,packet.receiver_signature_hex,receiptBytes);
 if(!senderValid)add('SENDER_SIGNATURE_INVALID');
 if(!receiverValid)add('RECEIVER_SIGNATURE_INVALID');
 if(policy.external_sender_identity_authenticated!==true)add('SENDER_IDENTITY_UNAUTHENTICATED');
 if(policy.external_receiver_identity_authenticated!==true)add('RECEIVER_IDENTITY_UNAUTHENTICATED');
 if(policy.independent_root_ancestry_authenticated!==true)add('ROOT_ANCESTRY_UNAUTHENTICATED');
 if(policy.original_physical_capture_authenticated!==true)add('PHYSICAL_CAPTURE_UNAUTHENTICATED');
 return done({cryptographic_sender_valid:senderValid,cryptographic_receiver_valid:receiverValid,computed_transfer_sha256:digest})
}
