/** AETHER-188 · signed instrument/clock/challenge contract. Synthetic evidence only; ACT always HOLD. */
export const HEX64=/^[a-f0-9]{64}$/i;
export const CAL_FIELDS=['schema','calibration_id','device_serial','clock_serial','issuer_id','issuer_root_id','valid_from_utc','valid_until_utc','max_drift_ppm','tick_unit_ns','challenge_domain'];
export const CAP_FIELDS=['schema','capture_id','device_serial','clock_serial','calibration_sha256','challenge_id','challenge_nonce','challenge_issued_utc','challenge_expires_utc','captured_utc','first_tick','last_tick','sample_start','sample_end','raw_sha256','device_key_id'];
export const canonical=(obj,fields)=>JSON.stringify(Object.fromEntries(fields.map(k=>[k,obj[k]])));
export const hex=bytes=>Array.from(bytes,v=>v.toString(16).padStart(2,'0')).join('');
export const sha256=async bytes=>{
 if(!(bytes instanceof Uint8Array))throw Error('UINT8ARRAY_REQUIRED');
 return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)));
};
export async function verify(jwk,sig,text){
 try{
  if(!jwk||jwk.kty!=='EC'||jwk.crv!=='P-256'||jwk.d||typeof sig!=='string'||!/^[a-f0-9]{128}$/i.test(sig))return false;
  const key=await crypto.subtle.importKey('jwk',jwk,{name:'ECDSA',namedCurve:'P-256'},false,['verify']);
  return await crypto.subtle.verify({name:'ECDSA',hash:'SHA-256'},key,Uint8Array.from(sig.match(/../g),v=>parseInt(v,16)),new TextEncoder().encode(text));
 }catch{return false}
}
export async function assess(packet,policy={}){
 const reasons=[],reject=x=>reasons.push(x);
 const done=(details={})=>({decision:reasons.length?'REJECT':'DOCUMENTARY_BINDING_ONLY',reasons:[...new Set(reasons)].sort(),...details,physical_qualification_percent:0,operational_authority:'HOLD',physical_act_allowed:false});
 if(!packet||!(packet.raw_bytes instanceof Uint8Array)||!packet.calibration||!packet.capture){reject('MISSING_BYTES_CALIBRATION_OR_CAPTURE');return done()}
 const {raw_bytes,calibration:c,capture:a}=packet;
 if(!raw_bytes.length)reject('EMPTY_CAPTURE_BYTES');
 if(c.schema!=='AETHER-188/calibration-v1'||a.schema!=='AETHER-188/capture-v1')reject('SCHEMA_MISMATCH');
 const req=['device_serial','clock_serial','capture_id','challenge_id','challenge_nonce','device_key_id'];
 for(const k of req)if(typeof a[k]!=='string'||!a[k])reject('MISSING_'+k.toUpperCase());
 if(!HEX64.test(a.raw_sha256||'')||!HEX64.test(a.calibration_sha256||''))reject('INVALID_CAPTURE_OR_CALIBRATION_HASH');
 if(a.device_serial!==c.device_serial||a.device_serial!==policy.expected_device_serial)reject('DEVICE_IDENTITY_SUBSTITUTION');
 if(a.clock_serial!==c.clock_serial||a.clock_serial!==policy.expected_clock_serial)reject('CLOCK_IDENTITY_SUBSTITUTION');
 if(a.challenge_id!==policy.expected_challenge_id||a.challenge_nonce!==policy.expected_challenge_nonce||c.challenge_domain!==policy.expected_challenge_domain)reject('CHALLENGE_BINDING_MISMATCH');
 if(policy.used_nonces instanceof Set&&policy.used_nonces.has(a.challenge_nonce))reject('REPLAYED_CHALLENGE_NONCE');
 if(policy.used_capture_ids instanceof Set&&policy.used_capture_ids.has(a.capture_id))reject('REPLAYED_CAPTURE_ID');
 const issued=Date.parse(a.challenge_issued_utc),expiry=Date.parse(a.challenge_expires_utc),acquired=Date.parse(a.captured_utc);
 const from=Date.parse(c.valid_from_utc),until=Date.parse(c.valid_until_utc);
 if(![issued,expiry,acquired,from,until].every(Number.isFinite))reject('INVALID_TIME_FORMAT');
 else{
  if(!(issued<expiry&&issued<=acquired&&acquired<=expiry))reject('EXPIRED_OR_UNISSUED_CHALLENGE');
  if(!(from<=acquired&&acquired<=until&&from<until))reject('CALIBRATION_EXPIRED_AT_ACQUISITION');
 }
 if(!Number.isSafeInteger(a.first_tick)||!Number.isSafeInteger(a.last_tick)||a.first_tick<0||a.last_tick<=a.first_tick)reject('HARDWARE_TICK_ROLLBACK');
 if(!Number.isSafeInteger(a.sample_start)||!Number.isSafeInteger(a.sample_end)||a.sample_start<0||a.sample_end<a.sample_start)reject('SAMPLE_COUNTER_ROLLBACK');
 if(!Number.isSafeInteger(policy.expected_samples)||a.sample_end-a.sample_start+1!==policy.expected_samples)reject('SAMPLE_COUNT_MISMATCH');
 if(!Number.isSafeInteger(c.tick_unit_ns)||c.tick_unit_ns<=0||!Number.isFinite(c.max_drift_ppm)||c.max_drift_ppm<0||c.max_drift_ppm>1000000)reject('INVALID_CALIBRATION_PARAMETERS');
 if(Number.isSafeInteger(a.first_tick)&&Number.isSafeInteger(a.last_tick)&&Number.isSafeInteger(c.tick_unit_ns)&&c.tick_unit_ns>0){
  const projected=(a.last_tick-a.first_tick)*c.tick_unit_ns/1e6;
  const observed=acquired-issued;
  const limit=Number.isFinite(policy.max_tick_span_ms)?policy.max_tick_span_ms:NaN;
  if(!Number.isFinite(limit)||projected>limit)reject('CLOCK_TICK_SPAN_EXCEEDS_POLICY');
  if(Number.isFinite(observed)&&projected>Math.max(0,observed)+Number(policy.max_clock_skew_ms||0))reject('CLOCK_VS_CHALLENGE_TIME_CONFLICT');
 }
 let rawHash=null,calHash=null;
 try{
  const te=new TextEncoder();rawHash=await sha256(raw_bytes);calHash=await sha256(te.encode(canonical(c,CAL_FIELDS)));
  if(rawHash!==a.raw_sha256)reject('CAPTURE_BYTE_SUBSTITUTION');
  if(calHash!==a.calibration_sha256)reject('CALIBRATION_RECORD_SUBSTITUTION');
 }catch{reject('HASH_UNAVAILABLE')}
 const calibrators=policy.calibrator_keys instanceof Map?policy.calibrator_keys:new Map(),devices=policy.device_keys instanceof Map?policy.device_keys:new Map();
 const calibrator=calibrators.get(c.issuer_id),device=devices.get(a.device_key_id);
 if(!calibrator||!device)reject('SIGNING_KEY_NOT_REGISTERED');
 if(calibrator?.root_id!==c.issuer_root_id)reject('CALIBRATOR_ROOT_MISMATCH');
 if(device?.device_serial!==a.device_serial||device?.clock_serial!==a.clock_serial)reject('DEVICE_KEY_BINDING_MISMATCH');
 if(calibrator?.operator_id&&calibrator.operator_id===device?.operator_id)reject('SHARED_CALIBRATOR_DEVICE_OPERATOR');
 if(calibrator?.revoked===true||device?.revoked===true)reject('REVOKED_SIGNING_KEY');
 const calibration_signature_valid=await verify(calibrator?.jwk,packet.calibration_signature_hex,canonical(c,CAL_FIELDS));
 const capture_signature_valid=await verify(device?.jwk,packet.capture_signature_hex,canonical(a,CAP_FIELDS));
 if(!calibration_signature_valid)reject('CALIBRATION_SIGNATURE_INVALID');
 if(!capture_signature_valid)reject('CAPTURE_SIGNATURE_INVALID');
 if(policy.external_calibrator_authenticated!==true)reject('CALIBRATOR_NOT_EXTERNALLY_AUTHENTICATED');
 if(policy.physical_instrument_authenticated!==true)reject('PHYSICAL_INSTRUMENT_NOT_AUTHENTICATED');
 if(policy.physical_clock_traceability_authenticated!==true)reject('PHYSICAL_CLOCK_NOT_TRACEABLY_CALIBRATED');
 if(policy.original_acquisition_authenticated!==true)reject('ORIGINAL_ACQUISITION_NOT_AUTHENTICATED');
 return done({computed_raw_sha256:rawHash,computed_calibration_sha256:calHash,calibration_signature_valid,capture_signature_valid});
}
