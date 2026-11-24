// AETHER-170: deterministic structural identity gate. No physical authorization.
export const REQUIRED = Object.freeze(['challenge_id','nonce','issued_at','expires_at','device_serial','manufacturer','device_key_fingerprint','device_response_signature','manufacturer_attestation','original_capture_sha256','external_registry_receipt']);
export function evaluate(candidate, context={}) {
 const reasons=[];
 if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) return {status:'REJECT',reasons:['INVALID_RECORD'],operational_authority:'HOLD'};
 for (const k of REQUIRED) if(typeof candidate[k]!=='string'||!candidate[k].trim()) reasons.push('MISSING_'+k.toUpperCase());
 const {challenge_id,nonce,issued_at,expires_at,device_serial}=candidate;
 if (typeof challenge_id==='string' && challenge_id!==context.expected_challenge) reasons.push('CHALLENGE_MISMATCH');
 if (typeof nonce==='string' && nonce!==context.expected_nonce) reasons.push('NONCE_MISMATCH');
 if(typeof device_serial==='string' && device_serial!==context.expected_serial) reasons.push('SERIAL_MISMATCH');
 const start=Date.parse(issued_at),end=Date.parse(expires_at),now=Number(context.now_ms);
 if(!Number.isFinite(start)||!Number.isFinite(end)||!Number.isFinite(now)||!(start<=now&&now<=end&&end>start))reasons.push('INVALID_CHALLENGE_WINDOW');
 if(context.used_nonces instanceof Set && context.used_nonces.has(nonce))reasons.push('NONCE_REPLAY');
 if(!/^[a-f0-9]{64}$/i.test(candidate.original_capture_sha256||''))reasons.push('INVALID_DIGEST');
 // Form presence is not authentication: no native trusted manufacturer verifier exists in this laboratory.
 if(context.trusted_manufacturer_validation!==true)reasons.push('MANUFACTURER_NOT_AUTHENTICATED');
 if(context.external_registry_validation!==true)reasons.push('EXTERNAL_REGISTRY_NOT_AUTHENTICATED');
 if(context.original_physical_capture_validated!==true)reasons.push('ORIGINAL_CAPTURE_NOT_AUTHENTICATED');
 // Deliberately no client-verifiable path to operational ACT; even valid structural inputs remain HOLD.
 return {status:reasons.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons,operational_authority:'HOLD',physical_qualification_percent:0,physical_act_allowed:false};
}
