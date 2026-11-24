/** AETHER-183 · Blinded physical-evidence admission screen.
 * A single deterministic, fail-closed reviewer; NOT a physical qualification system.
 */
export const HEX64=/^[a-f0-9]{64}$/i;
export async function sha256(bytes){
 if(!(bytes instanceof Uint8Array))throw new TypeError('EXPECTED_UINT8ARRAY');
 return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
}
export function blindView(bundle){
 // The review sees measurements and opaque root handles, not claimed names or applicant rhetoric.
 if(!bundle||!Array.isArray(bundle.roots))return null;
 return Object.freeze({
  trial_id:bundle.trial_id,
  capture_id:bundle.capture_id,
  capture_sha256:bundle.capture_sha256,
  challenge_id:bundle.challenge_id,
  sample_count:bundle.sample_count,
  time_start_ms:bundle.time_start_ms,
  time_end_ms:bundle.time_end_ms,
  root_handles:bundle.roots.map(r=>r.handle),
  archive_digests:bundle.roots.map(r=>r.archive_sha256)
 });
}
export async function assess(bundle,external={}){
 const failures=[],add=x=>failures.push(x);
 const end=(detail={})=>({decision:failures.length?'REJECT':'DOCUMENTARY_SCREEN_ONLY',reasons:[...new Set(failures)].sort(),...detail,phase:'XIII',turn:7,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!bundle||!(bundle.raw_bytes instanceof Uint8Array)||!Array.isArray(bundle.roots)){add('MISSING_ORIGINAL_BYTES_OR_ROOTS');return end()}
 const b=blindView(bundle);
 if(!b||typeof b.trial_id!=='string'||!b.trial_id||typeof b.capture_id!=='string'||!b.capture_id)add('MISSING_TRIAL_OR_CAPTURE_ID');
 if(!HEX64.test(b.capture_sha256||''))add('MALFORMED_CAPTURE_DIGEST');
 if(b.challenge_id!==external.expected_challenge_id)add('CHALLENGE_MISMATCH');
 if(external.used_capture_ids instanceof Set&&external.used_capture_ids.has(b.capture_id))add('REPLAYED_CAPTURE');
 if(external.used_trial_ids instanceof Set&&external.used_trial_ids.has(b.trial_id))add('REPLAYED_TRIAL');
 if(!Number.isSafeInteger(b.sample_count)||b.sample_count<1)add('INVALID_SAMPLE_COUNT');
 if(!Number.isFinite(b.time_start_ms)||!Number.isFinite(b.time_end_ms)||b.time_end_ms<=b.time_start_ms)add('INVALID_CAPTURE_WINDOW');
 if(!Number.isSafeInteger(external.expected_sample_count)||b.sample_count!==external.expected_sample_count)add('SAMPLE_COUNT_MISMATCH');
 if(b.root_handles.length!==3)add('THREE_SOURCE_ROOTS_REQUIRED');
 const handles=new Set(),declaredDigests=new Set();
 for(const h of b.root_handles){if(typeof h!=='string'||!h)add('MISSING_ROOT_HANDLE');if(handles.has(h))add('DUPLICATE_ROOT_HANDLE');handles.add(h)}
 for(const d of b.archive_digests){if(!HEX64.test(d||''))add('INVALID_ARCHIVE_DIGEST');declaredDigests.add(d);if(d!==b.capture_sha256)add('ARCHIVE_CAPTURE_MISMATCH')}
 if(declaredDigests.size>1)add('ARCHIVE_DIGEST_DISAGREEMENT');
 let measured=null;
 try{measured=await sha256(bundle.raw_bytes);if(measured!==b.capture_sha256)add('CAPTURE_BYTE_MISMATCH')}catch{add('HASH_UNAVAILABLE')}
 // Trust anchors must originate OUTSIDE the applicant bundle; bundle-root ancestry claims are ignored.
 const attest=external.root_attestations instanceof Map?external.root_attestations:new Map();
 const parents=new Set(),issuers=new Set(),administrators=new Set();
 for(const handle of handles){
  const a=attest.get(handle);
  if(!a){add('MISSING_EXTERNAL_ROOT_ATTESTATION');continue}
  if(a.authenticated!==true)add('ROOT_ATTESTATION_NOT_AUTHENTICATED');
  if(a.capture_sha256!==b.capture_sha256)add('ATTESTED_CAPTURE_MISMATCH');
  if(a.challenge_id!==b.challenge_id)add('ATTESTED_CHALLENGE_MISMATCH');
  for(const key of ['ancestry_root','issuer_id','administrator_id'])if(typeof a[key]!=='string'||!a[key])add('MISSING_ATTESTED_'+key.toUpperCase());
  if(parents.has(a.ancestry_root))add('COMMON_ROOT_ANCESTRY');parents.add(a.ancestry_root);
  if(issuers.has(a.issuer_id))add('COMMON_ISSUER');issuers.add(a.issuer_id);
  if(administrators.has(a.administrator_id))add('COMMON_ADMINISTRATOR');administrators.add(a.administrator_id);
 }
 if(attest.size!==3||parents.size!==3||issuers.size!==3||administrators.size!==3)add('EXTERNAL_ROOT_INDEPENDENCE_NOT_ESTABLISHED');
 if(external.independent_verification_service_authenticated!==true)add('INDEPENDENT_VERIFIER_NOT_AUTHENTICATED');
 if(external.raw_physical_acquisition_authenticated!==true)add('ORIGINAL_HARDWARE_ACQUISITION_NOT_AUTHENTICATED');
 if(external.calibrated_physical_clock_authenticated!==true)add('PHYSICAL_CLOCK_NOT_AUTHENTICATED');
 if(external.physical_alarm_evidence_authenticated!==true)add('PHYSICAL_ALARM_NOT_AUTHENTICATED');
 // Even a locally fabricated independent-attestation Map may not promote to physical ACT.
 return end({computed_capture_sha256:measured,blind_review_fields:b,declared_external_attestations:attest.size});
}
