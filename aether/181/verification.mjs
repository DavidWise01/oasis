/** AETHER-181 — clock/source/challenge provenance escrow. Software-only; ACT always HOLD. */
export const HEX64=/^[a-f0-9]{64}$/i;
export const canonicalFields=['schema','capture_id','source_id','device_serial','clock_id','clock_calibration_receipt_sha256','challenge_id','challenge_nonce','challenge_issued_utc','challenge_expires_utc','captured_utc','sample_start','sample_end','first_tick_ns','last_tick_ns','raw_capture_sha256','custody_receipt_sha256'];
export function canonical(record){return JSON.stringify(Object.fromEntries(canonicalFields.map(k=>[k,record[k]])))}
export async function sha256(bytes){
 if(!(bytes instanceof Uint8Array))throw Error('RAW_BYTES_REQUIRED');
 const digest=await crypto.subtle.digest('SHA-256',bytes);
 return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
}
export async function assess(packet,policy={}){
 const failures=[];const add=x=>failures.push(x);
 const finish=(extra={})=>({status:failures.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(failures)].sort(),...extra,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!packet||!packet.record||!(packet.raw_bytes instanceof Uint8Array)){add('MISSING_ORIGINAL_BYTES_OR_RECORD');return finish()}
 const r=packet.record;
 if(r.schema!=='AETHER-181/v1')add('SCHEMA_MISMATCH');
 for(const k of ['capture_id','source_id','device_serial','clock_id','challenge_id','challenge_nonce']){
  if(typeof r[k]!=='string'||!r[k])add('MISSING_'+k.toUpperCase());
 }
 if(r.source_id!==policy.expected_source_id)add('SOURCE_ID_MISMATCH');
 if(r.device_serial!==policy.expected_device_serial)add('DEVICE_SERIAL_MISMATCH');
 if(r.clock_id!==policy.expected_clock_id)add('CLOCK_ID_MISMATCH');
 if(r.challenge_id!==policy.expected_challenge_id||r.challenge_nonce!==policy.expected_challenge_nonce)add('CHALLENGE_MISMATCH');
 if(policy.used_challenge_nonces instanceof Set&&policy.used_challenge_nonces.has(r.challenge_nonce))add('REPLAYED_CHALLENGE');
 if(policy.used_capture_ids instanceof Set&&policy.used_capture_ids.has(r.capture_id))add('REPLAYED_CAPTURE');
 for(const key of ['clock_calibration_receipt_sha256','raw_capture_sha256','custody_receipt_sha256','record_sha256'])if(!HEX64.test(r[key]||''))add('INVALID_'+key.toUpperCase());
 if(r.clock_calibration_receipt_sha256!==policy.expected_calibration_sha256)add('CALIBRATION_RECEIPT_MISMATCH');
 if(r.custody_receipt_sha256!==policy.expected_custody_sha256)add('CUSTODY_RECEIPT_MISMATCH');
 const issued=Date.parse(r.challenge_issued_utc),expiry=Date.parse(r.challenge_expires_utc),captured=Date.parse(r.captured_utc);
 if(![issued,expiry,captured].every(Number.isFinite))add('INVALID_TIME_FIELD');
 else if(!(issued<expiry&&captured>=issued&&captured<=expiry))add('CAPTURE_OUTSIDE_CHALLENGE_WINDOW');
 if(!Number.isSafeInteger(r.sample_start)||!Number.isSafeInteger(r.sample_end)||r.sample_start<0||r.sample_end<r.sample_start)add('INVALID_SAMPLE_COUNTER_RANGE');
 if(!Number.isSafeInteger(r.first_tick_ns)||!Number.isSafeInteger(r.last_tick_ns)||r.first_tick_ns<0||r.last_tick_ns<=r.first_tick_ns)add('NONMONOTONIC_HARDWARE_TICKS');
 if(!Number.isSafeInteger(policy.expected_sample_count)||r.sample_end-r.sample_start+1!==policy.expected_sample_count)add('SAMPLE_COUNT_MISMATCH');
 if(!Number.isSafeInteger(policy.max_duration_ns)||policy.max_duration_ns<=0)add('NO_APPROVED_CLOCK_DURATION_LIMIT');
 else if(Number.isSafeInteger(r.first_tick_ns)&&Number.isSafeInteger(r.last_tick_ns)&&r.last_tick_ns-r.first_tick_ns>policy.max_duration_ns)add('DURATION_EXCEEDS_LIMIT');
 let rawHash=null,recordHash=null;
 try{
  rawHash=await sha256(packet.raw_bytes);
  recordHash=await sha256(new TextEncoder().encode(canonical(r)));
  if(rawHash!==r.raw_capture_sha256)add('ORIGINAL_BYTES_DIGEST_MISMATCH');
  if(recordHash!==r.record_sha256)add('PROVENANCE_RECORD_DIGEST_MISMATCH');
 }catch{add('CRYPTOGRAPHIC_DIGEST_UNAVAILABLE')}
 if(policy.hardware_clock_attestation_authenticated!==true)add('HARDWARE_CLOCK_NOT_AUTHENTICATED');
 if(policy.independent_source_origin_authenticated!==true)add('INDEPENDENT_SOURCE_NOT_AUTHENTICATED');
 if(policy.original_acquisition_authenticated!==true)add('ORIGINAL_ACQUISITION_NOT_AUTHENTICATED');
 if(policy.external_custody_receipt_authenticated!==true)add('EXTERNAL_RECEIPT_NOT_AUTHENTICATED');
 return finish({computed_raw_capture_sha256:rawHash,computed_record_sha256:recordHash});
}
