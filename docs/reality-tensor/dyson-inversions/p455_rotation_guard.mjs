// ROOT0/P455: bind administrator-approved rotation to the currently admitted mTLS identity.
export function rotationControllerAuthorized({fingerprint,requestEpoch,oldPolicy,bootstrapFingerprint}) {
  if(typeof fingerprint!=='string'||!Number.isSafeInteger(requestEpoch))return false;
  if(!oldPolicy)return requestEpoch===0 && fingerprint===bootstrapFingerprint;
  let allowed;
  try{allowed=Array.isArray(oldPolicy.fingerprints)?oldPolicy.fingerprints:JSON.parse(oldPolicy.fingerprints)}catch{return false}
  return requestEpoch===oldPolicy.epoch && Array.isArray(allowed) && allowed.includes(fingerprint);
}