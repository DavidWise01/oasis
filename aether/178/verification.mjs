/** AETHER-178 — byte-exact synthetic escrow verifier. No physical ACT authorization. */
export const HEX64 = /^[a-f0-9]{64}$/;
export const FIELDS = ['schema','capture_id','instrument_serial','challenge_id','source_origin_id','byte_length','capture_sha256','sequence','prior_manifest_sha256','sealed_at'];
export function canonical(manifest) {
  const out = {};
  for(const k of FIELDS) out[k] = manifest[k];
  return JSON.stringify(out);
}
export async function sha256(bytes){
  if (!(bytes instanceof Uint8Array)) throw new TypeError('Uint8Array required');
  const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('');
}
export async function assess(packet, context={}) {
  const reasons=[];
  const add=x=>reasons.push(x);
  const finish=(computed={})=>({status:reasons.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(reasons)].sort(),...computed,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
  if(!packet || !(packet.bytes instanceof Uint8Array) || !packet.manifest || typeof packet.manifest!=='object') {add('MISSING_BYTES_OR_MANIFEST');return finish()}
  const {bytes,manifest:m}=packet;
  if(!bytes.length)add('EMPTY_CAPTURE');
  if(m.schema!=='AETHER-178/v1')add('BAD_SCHEMA');
  for(const k of ['capture_id','instrument_serial','challenge_id','source_origin_id','sealed_at'])if(typeof m[k]!=='string'||!m[k])add('MISSING_'+k.toUpperCase());
  if(m.instrument_serial!==context.expected_instrument_serial)add('INSTRUMENT_MISMATCH');
  if(m.challenge_id!==context.expected_challenge_id)add('CHALLENGE_MISMATCH');
  if(m.source_origin_id===context.dut_owned_root && context.expected_role!=='DUT')add('SHARED_DUT_ORIGIN');
  if(!Number.isSafeInteger(m.byte_length)||m.byte_length!==bytes.length)add('LENGTH_MISMATCH');
  if(!Number.isSafeInteger(m.sequence)||m.sequence<0)add('BAD_SEQUENCE');
  if(m.sequence===0 && m.prior_manifest_sha256!==null)add('INVALID_GENESIS');
  if(m.sequence>0 && (!HEX64.test(m.prior_manifest_sha256||'')||m.prior_manifest_sha256!==context.expected_predecessor_sha256))add('PREDECESSOR_MISMATCH');
  if(context.used_capture_ids instanceof Set && context.used_capture_ids.has(m.capture_id))add('CAPTURE_ID_REPLAY');
  if(!HEX64.test(m.capture_sha256||''))add('BAD_CAPTURE_DIGEST');
  if(!HEX64.test(m.manifest_sha256||''))add('BAD_MANIFEST_DIGEST');
  if(!Number.isFinite(Date.parse(m.sealed_at)))add('BAD_SEAL_TIMESTAMP');
  let captureDigest=null,manifestDigest=null;
  try{
    captureDigest=await sha256(bytes);
    manifestDigest=await sha256(new TextEncoder().encode(canonical(m)));
    if(captureDigest!==m.capture_sha256)add('CAPTURE_DIGEST_MISMATCH');
    if(manifestDigest!==m.manifest_sha256)add('MANIFEST_DIGEST_MISMATCH');
  }catch{add('DIGEST_CALCULATION_FAILED')}
  if(context.independent_hardware_origin_authenticated!==true)add('ORIGIN_NOT_PHYSICALLY_AUTHENTICATED');
  if(context.external_custodian_signature_authenticated!==true)add('CUSTODIAN_SIGNATURE_NOT_AUTHENTICATED');
  if(context.original_hardware_acquisition_authenticated!==true)add('ACQUISITION_NOT_PHYSICALLY_AUTHENTICATED');
  return finish({computed_capture_sha256:captureDigest,computed_manifest_sha256:manifestDigest});
}
