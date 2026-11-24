/** AETHER-175 - structural synthetic drift/alarm checker, never physical authorization. */
export function assess(packet, policy={}) {
  const failures=[];
  const reject=x=>failures.push(x);
  const finish=()=>({status:failures.length?'REJECT':'DOCUMENTARY_REVIEW_ONLY',reasons:[...new Set(failures)].sort(),operational_authority:'HOLD',physical_qualification_percent:0,physical_act_allowed:false});
  if(!packet || !Array.isArray(packet.samples) || packet.samples.length<2) {reject('MISSING_DRIFT_TRACE');return finish();}
  for(const [key,expected] of [['device_serial',policy.expected_device_serial],['reference_serial',policy.expected_reference_serial],['challenge_nonce',policy.expected_nonce],['clock_source_id',policy.expected_clock_source]]){
    if(!packet[key]||packet[key]!==expected)reject('INVALID_'+key.toUpperCase());
  }
  for(const key of ['dut_capture_sha256','reference_capture_sha256','alarm_capture_sha256']){
    if(!/^[0-9a-f]{64}$/i.test(packet[key]||'')) reject('INVALID_'+key.toUpperCase());
  }
  if(!Number.isFinite(policy.max_drift_per_second)||policy.max_drift_per_second<0)reject('NO_APPROVED_DRIFT_LIMIT');
  if(!Number.isFinite(policy.max_alarm_delay_ms)||policy.max_alarm_delay_ms<=0)reject('NO_APPROVED_ALARM_DEADLINE');
  if(!Number.isFinite(policy.alarm_threshold)||policy.alarm_threshold<=0)reject('NO_APPROVED_ALARM_THRESHOLD');
  if(!Array.isArray(packet.alarms))reject('MISSING_ALARM_EVENT_LIST');
  const alarms=Array.isArray(packet.alarms)?packet.alarms:[];
  let prev=null;
  const detected=[];
  for(const x of packet.samples){
    if(!x||!Number.isSafeInteger(x.counter)||!Number.isFinite(x.time_ms)||!Number.isFinite(x.dut)||!Number.isFinite(x.reference)){
      reject('MALFORMED_SAMPLE');continue;
    }
    if(prev) {
      if(x.counter!==prev.counter+1)reject('COUNTER_GAP');
      if(x.time_ms<=prev.time_ms)reject('CLOCK_ROLLBACK');
      const delta=(x.time_ms-prev.time_ms)/1000;
      if(delta>0){
        const change=Math.abs((x.dut-x.reference)-(prev.dut-prev.reference))/delta;
        if(change>policy.max_drift_per_second)reject('DRIFT_LIMIT_EXCEEDED');
      }
    }
    if(Math.abs(x.dut-x.reference)>policy.alarm_threshold)detected.push(x);
    prev=x;
  }
  const seen=new Set();
  for(const a of alarms){
    if(!a||!Number.isFinite(a.issued_time_ms)||!Number.isSafeInteger(a.source_counter)||typeof a.event_id!=='string'||!a.event_id){
      reject('MALFORMED_ALARM');continue;
    }
    if(seen.has(a.event_id)) reject('DUPLICATE_ALARM_EVENT_ID');
    seen.add(a.event_id);
  }
  for(const trigger of detected){
    const candidates=alarms.filter(a=>a && a.source_counter===trigger.counter && Number.isFinite(a.issued_time_ms));
    if(!candidates.length){reject('SUPPRESSED_ALARM');continue;}
    if(candidates.length>1) reject('DUPLICATE_ALARM_FOR_TRIGGER');
    const delay=candidates[0].issued_time_ms-trigger.time_ms;
    if(delay<0)reject('ALARM_PRECEDES_TRIGGER');
    else if(delay>policy.max_alarm_delay_ms)reject('DELAYED_ALARM');
  }
  if(policy.original_trace_authenticated!==true)reject('ORIGINAL_TRACE_UNAUTHENTICATED');
  if(policy.clock_calibration_authenticated!==true)reject('CLOCK_UNAUTHENTICATED');
  if(policy.reference_independence_authenticated!==true)reject('REFERENCE_UNAUTHENTICATED');
  if(policy.physical_alarm_issuance_authenticated!==true)reject('ALARM_ISSUANCE_UNAUTHENTICATED');
  // Trust flags are mere synthetic inputs; no physical qualification or operational ACT available.
  return finish();
}
