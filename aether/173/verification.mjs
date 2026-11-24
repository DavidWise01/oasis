/* AETHER-173 original capture admission: browser SHA-256 is integrity only, never proof of physical origin. */
export async function assess(packet, env={}) {
 const errors=[];
 const result=()=>({status:errors.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(errors)].sort(),operational_authority:'HOLD',physical_qualification_percent:0,physical_act_allowed:false});
 if(!packet || !Array.isArray(packet.samples) || !(packet.raw_bytes instanceof Uint8Array)){
  errors.push('MISSING_RAW_ACQUISITION');return result();
 }
 if(!packet.samples.length)errors.push('NO_SAMPLES');
 if(packet.raw_bytes.byteLength===0)errors.push('EMPTY_RAW_CAPTURE');
 if(typeof packet.declared_sha256!=='string'|| !/^[a-f0-9]{64}$/i.test(packet.declared_sha256))errors.push('INVALID_DECLARED_SHA256');
 if(typeof packet.device_serial!=='string'||!packet.device_serial)errors.push('MISSING_DEVICE_SERIAL');
 if(packet.device_serial!==env.expected_serial)errors.push('DEVICE_SERIAL_MISMATCH');
 if(typeof packet.challenge_nonce!=='string'||packet.challenge_nonce!==env.expected_nonce)errors.push('CHALLENGE_NONCE_MISMATCH');
 if(typeof packet.clock_source_id!=='string'||!packet.clock_source_id)errors.push('MISSING_CLOCK_SOURCE');
 if(packet.clock_source_id!==env.expected_clock_source)errors.push('CLOCK_SOURCE_MISMATCH');
 if(typeof packet.capture_id!=='string'||!packet.capture_id)errors.push('MISSING_CAPTURE_ID');
 if(env.seen_capture_ids instanceof Set && env.seen_capture_ids.has(packet.capture_id))errors.push('REPLAYED_CAPTURE_ID');
 if(packet.expected_sample_count!==packet.samples.length)errors.push('SAMPLE_COUNT_MISMATCH');
 let prevCounter=null,prevTime=null;
 for(let i=0;i<packet.samples.length;i++){
  const x=packet.samples[i];
  if(!x||!Number.isSafeInteger(x.counter)||!Number.isSafeInteger(x.hardware_time_ns)){
   errors.push('MALFORMED_SAMPLE');continue;
  }
  if(prevCounter!==null && x.counter!==prevCounter+1)errors.push('COUNTER_DISCONTINUITY');
  if(prevTime!==null && x.hardware_time_ns<=prevTime)errors.push('CLOCK_NONMONOTONIC');
  if(i===0 && Number.isSafeInteger(env.expected_first_counter) && x.counter!==env.expected_first_counter)errors.push('INITIAL_COUNTER_MISMATCH');
  prevCounter=x.counter;prevTime=x.hardware_time_ns;
 }
 if(!globalThis.crypto?.subtle){
  errors.push('SHA256_UNAVAILABLE');
 } else {
  try{
   const digest=await globalThis.crypto.subtle.digest('SHA-256',packet.raw_bytes);
   const hex=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
   if(hex.toLowerCase()!==String(packet.declared_sha256).toLowerCase())errors.push('DIGEST_MISMATCH');
  }catch {errors.push('SHA256_COMPUTATION_FAILED')}
 }
 if(env.trusted_hardware_clock_validation!==true)errors.push('HARDWARE_CLOCK_UNAUTHENTICATED');
 if(env.trusted_original_capture_validation!==true)errors.push('ORIGINAL_CAPTURE_UNAUTHENTICATED');
 if(env.trusted_independent_source_validation!==true)errors.push('INDEPENDENT_SOURCE_UNAUTHENTICATED');
 // Flags are simulated test inputs, never external proof and never grant operational ACT.
 return result();
}
