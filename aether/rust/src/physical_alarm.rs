//! AETHER-199-RS: two signed documentary reports of response and physical-alarm observation.
//! Authentication claims are not real-world observations. Never authorizes ACT.
use crate::{sha256_hex,PublicJwk};
use chrono::DateTime;
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Serialize,Deserialize};
use std::collections::{BTreeSet,HashSet};
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Response {
 pub schema:String,pub event_id:String,pub capture_id:String,pub capture_sha256:String,
 pub challenge_id:String,pub challenge_nonce:String,pub device_id:String,
 pub sensor_id:String,pub source_root:String,pub source_operator:String,pub source_admin:String,
 pub measured_nano:i64,pub reference_nano:i64,pub tolerance_nano:u64,
 pub observed_utc:String,pub calibration_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Alarm {
 pub schema:String,pub alarm_id:String,pub response_sha256:String,pub capture_sha256:String,
 pub challenge_nonce:String,pub observed_state:String,pub observer_id:String,
 pub observer_root:String,pub observer_operator:String,pub observer_admin:String,
 pub alarm_utc:String,pub acknowledgement_utc:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Packet {
 pub response:Response,pub response_signature_hex:String,
 pub alarm:Alarm,pub observer_signature_hex:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Policy {
 pub capture_sha256:String,pub challenge_id:String,pub challenge_nonce:String,
 pub device_id:String,pub calibration_sha256:String,pub expected_observer:String,
 pub response_key:PublicJwk,pub observer_key:PublicJwk,
 pub max_alarm_delay_ms:i64,pub max_ack_delay_ms:i64,pub review_utc:String,
 pub instrument_authenticated:bool,pub independent_observer_authenticated:bool,
 pub physical_alarm_observed:bool,pub calibrated_clock_authenticated:bool,
 pub seen_event_ids:HashSet<String>,pub seen_alarm_ids:HashSet<String>,
 pub seen_challenge_nonces:HashSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Decision {
 pub verdict:String,pub reasons:Vec<String>,
 pub response_signature_valid:bool,pub observer_signature_valid:bool,
 pub response_sha256:String,pub response_error_nano:u64,
 pub physical_qualification_percent:u8,pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(r:&T)->Vec<u8>{serde_json::to_vec(r).unwrap_or_default()}
pub fn response_sha256(r:&Response)->String{sha256_hex(&canonical(r))}
fn valid_hash(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
fn time(s:&str)->Option<i64>{DateTime::parse_from_rfc3339(s).ok().map(|d|d.timestamp_millis())}
fn verify<T:Serialize>(r:&T,sig_hex:&str,key:&PublicJwk)->bool{
 let Ok(k)=crate::verifying_key(key)else{return false};
 let Ok(bytes)=hex::decode(sig_hex)else{return false};
 let Ok(sig)=Signature::from_slice(&bytes)else{return false};
 k.verify(&canonical(r),&sig).is_ok()
}
pub fn assess(p:&Packet,policy:&Policy)->Decision{
 let r=&p.response;let a=&p.alarm;let mut faults=BTreeSet::new();
 let mut fail=|s:&str|{faults.insert(s.to_owned());};
 if r.schema!="AETHER-199/response-v1"||a.schema!="AETHER-199/alarm-v1"{fail("INVALID_EVIDENCE_SCHEMA");}
 if !valid_hash(&r.capture_sha256)||r.capture_sha256!=policy.capture_sha256||
 a.capture_sha256!=r.capture_sha256{fail("ORIGINAL_CAPTURE_MISMATCH");}
 if !valid_hash(&r.calibration_sha256)||r.calibration_sha256!=policy.calibration_sha256{
  fail("CALIBRATION_CAPTURE_MISMATCH");
 }
 if r.capture_id.is_empty()||r.event_id.is_empty()||a.alarm_id.is_empty(){fail("MISSING_EVENT_ID");}
 if r.challenge_id!=policy.challenge_id||r.challenge_nonce!=policy.challenge_nonce||
 a.challenge_nonce!=r.challenge_nonce{fail("CHALLENGE_BINDING_MISMATCH");}
 if r.device_id!=policy.device_id{fail("DEVICE_IDENTITY_MISMATCH");}
 if a.observer_id!=policy.expected_observer{fail("OBSERVER_IDENTITY_MISMATCH");}
 let digest=response_sha256(r);
 if a.response_sha256!=digest{fail("ALARM_RESPONSE_LINK_MISMATCH");}
 if a.observed_state!="PHYSICAL_ALARM_OBSERVED_AND_ACKNOWLEDGED"{fail("ALARM_NOT_PHYSICALLY_OBSERVED");}
 if r.sensor_id.is_empty()||r.source_root.is_empty()||r.source_operator.is_empty()||
 r.source_admin.is_empty()||a.observer_root.is_empty()||a.observer_operator.is_empty()||
 a.observer_admin.is_empty(){fail("MISSING_ANCESTRY");}
 if a.observer_root==r.source_root||a.observer_operator==r.source_operator||
 a.observer_admin==r.source_admin{fail("OBSERVER_SHARES_SOURCE_CONTROL");}
 if policy.seen_event_ids.contains(&r.event_id)||policy.seen_alarm_ids.contains(&a.alarm_id)||
 policy.seen_challenge_nonces.contains(&r.challenge_nonce){fail("PHYSICAL_OBSERVATION_REPLAY");}
 let error=r.measured_nano.abs_diff(r.reference_nano);
 if error>r.tolerance_nano{fail("RESPONSE_OUTSIDE_TOLERANCE");}
 match(time(&r.observed_utc),time(&a.alarm_utc),time(&a.acknowledgement_utc),time(&policy.review_utc)){
  (Some(measure),Some(alarm),Some(ack),Some(review))=>{
   if !(measure<=alarm&&alarm<=ack&&ack<=review){fail("NONMONOTONIC_ALARM_TIME");}
   if policy.max_alarm_delay_ms<0||alarm.saturating_sub(measure)>policy.max_alarm_delay_ms{
    fail("ALARM_DELAY_EXCEEDED");
   }
   if policy.max_ack_delay_ms<0||ack.saturating_sub(alarm)>policy.max_ack_delay_ms{
    fail("ACK_DELAY_EXCEEDED");
   }
  },
  _=>fail("INVALID_ALARM_TIME"),
 }
 let response_signature_valid=verify(r,&p.response_signature_hex,&policy.response_key);
 let observer_signature_valid=verify(a,&p.observer_signature_hex,&policy.observer_key);
 if !response_signature_valid{fail("RESPONSE_SIGNATURE_INVALID");}
 if !observer_signature_valid{fail("OBSERVER_SIGNATURE_INVALID");}
 if !policy.instrument_authenticated{fail("ORIGINAL_INSTRUMENT_UNAUTHENTICATED");}
 if !policy.independent_observer_authenticated{fail("EXTERNAL_OBSERVER_UNAUTHENTICATED");}
 if !policy.physical_alarm_observed{fail("PHYSICAL_ALARM_NOT_INDEPENDENTLY_CONFIRMED");}
 if !policy.calibrated_clock_authenticated{fail("PHYSICAL_CLOCK_UNAUTHENTICATED");}
 let reasons:Vec<String>=faults.into_iter().collect();
 Decision{verdict:if reasons.is_empty(){"DOCUMENTARY_ALARM_REVIEW_ONLY"}else{"REJECT"}.into(),
 reasons,response_signature_valid,observer_signature_valid,response_sha256:digest,
 response_error_nano:error,physical_qualification_percent:0,operational_authority:"HOLD".into(),
 physical_act_allowed:false}
}
