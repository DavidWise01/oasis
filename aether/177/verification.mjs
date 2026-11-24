/** AETHER-177: structural custody checks only; not a cryptographic signature or physical attestation verifier. */
export function adjudicate(record, policy={}) {
  const errors=[];
  const reject=x=>errors.push(x);
  const finish=()=>({status:errors.length?"REJECT":"DOCUMENTARY_REVIEW_ONLY",reasons:[...new Set(errors)].sort(),operational_authority:"HOLD",physical_qualification_percent:0,physical_act_allowed:false});
  if(!record || typeof record!=="object" || !Array.isArray(record.events)||!record.events.length){reject("MISSING_CUSTODY_EVENTS");return finish();}
  if(!/^[0-9a-f]{64}$/i.test(record.original_capture_sha256||""))reject("INVALID_ORIGINAL_CAPTURE_DIGEST");
  if(typeof record.instrument_serial!=="string"||!record.instrument_serial)reject("MISSING_INSTRUMENT_SERIAL");
  if(record.instrument_serial!==policy.expected_instrument_serial)reject("INSTRUMENT_MISMATCH");
  if(typeof record.challenge_id!=="string"||record.challenge_id!==policy.expected_challenge_id)reject("CHALLENGE_MISMATCH");
  if(typeof record.source_origin_id!=="string"||!record.source_origin_id)reject("MISSING_SOURCE_ORIGIN");
  if(record.source_origin_id===policy.dut_owned_origin_id && policy.expected_role!=="DUT")reject("SELF_ORIGIN_REFERENCE");
  if(record.events[0]?.action!=="ACQUIRE")reject("MISSING_INITIAL_ACQUISITION");
  let prevSeq=-1,prevTime=-Infinity,prior=null;
  const ids=new Set(),seenReceipts=new Set(),validActions=new Set(["ACQUIRE","TRANSFER","RECEIVE","SEAL"]);
  for(const event of record.events){
    if(!event||typeof event!=="object"){reject("MALFORMED_EVENT");continue;}
    if(!validActions.has(event.action))reject("INVALID_ACTION");
    if(!Number.isSafeInteger(event.sequence)||event.sequence!==prevSeq+1)reject("NONCONTIGUOUS_SEQUENCE");
    if(!Number.isFinite(event.time_ms)||event.time_ms<=prevTime)reject("NONMONOTONIC_TIME");
    if(typeof event.event_id!=="string"||!event.event_id||ids.has(event.event_id))reject("DUPLICATE_OR_MISSING_EVENT_ID");
    ids.add(event.event_id);
    if(typeof event.custodian_id!=="string"||!event.custodian_id)reject("MISSING_CUSTODIAN");
    if(typeof event.receipt_id!=="string"||!event.receipt_id||seenReceipts.has(event.receipt_id))reject("REPLAYED_RECEIPT");
    seenReceipts.add(event.receipt_id);
    if(!/^[a-f0-9]{64}$/i.test(event.event_sha256||""))reject("INVALID_EVENT_DIGEST");
    if(event.capture_sha256!==record.original_capture_sha256)reject("CAPTURE_SUBSTITUTION");
    if(prior && event.previous_event_sha256!==prior.event_sha256)reject("BROKEN_CUSTODY_LINK");
    if(!prior && event.previous_event_sha256!==null)reject("INVALID_GENESIS_LINK");
    if(prior && prior.action==="TRANSFER" && event.action==="RECEIVE"){
      if(event.custodian_id!==prior.to_custodian_id)reject("TRANSFER_RECEIPT_MISMATCH");
    } else if(event.action==="RECEIVE")reject("UNMATCHED_RECEIVE");
    if(event.action==="TRANSFER" && (!event.to_custodian_id||event.to_custodian_id===event.custodian_id))reject("INVALID_TRANSFER_DESTINATION");
    if(prior && prior.action==="TRANSFER" && event.action!=="RECEIVE")reject("MISSING_TRANSFER_RECEIPT");
    prevSeq=event.sequence;prevTime=event.time_ms;prior=event;
  }
  if(prior?.action!=="SEAL")reject("UNSEALED_CUSTODY");
  if(policy.independent_origin_authenticated!==true)reject("ORIGIN_NOT_INDEPENDENTLY_AUTHENTICATED");
  if(policy.original_hardware_bytes_authenticated!==true)reject("ORIGINAL_BYTES_NOT_AUTHENTICATED");
  if(policy.external_custody_receipts_authenticated!==true)reject("RECEIPTS_NOT_EXTERNALLY_AUTHENTICATED");
  // Structural consistency and asserted flags never amount to physical authorization.
  return finish();
}
