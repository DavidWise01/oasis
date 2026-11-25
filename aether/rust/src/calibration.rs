//! AETHER-197-RS: signed calibration, drift uncertainty, threshold decision interval.
use crate::PublicJwk;
use chrono::DateTime;
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Deserialize,Serialize};
use std::collections::{BTreeSet,HashSet};
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Calibration {
 pub schema:String,pub id:String,pub instrument:String,pub reference:String,pub issuer:String,
 pub reference_root:String,pub device_root:String,pub trace_sha256:String,
 pub valid_from:String,pub valid_until:String,pub uncertainty_nano:u64,
 pub clock_offset_ns:i64,pub clock_uncertainty_ns:u64,pub drift_ppb:u64,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct SignedCalibration {pub record:Calibration,pub signature_hex:String}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Observation {
 pub capture_id:String,pub capture_sha256:String,pub calibration_id:String,
 pub value_nano:i64,pub threshold_nano:i64,pub issued_utc:String,
 pub measured_utc:String,pub expires_utc:String,pub elapsed_ns:u64,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Policy {
 pub expected_instrument:String,pub expected_reference:String,pub expected_issuer:String,
 pub expected_calibration:String,pub expected_trace_sha256:String,pub authority_key:PublicJwk,
 pub max_calibration_uncertainty_nano:u64,pub max_clock_uncertainty_ns:u64,
 pub max_elapsed_ns:u64,pub replay:HashSet<String>,
 pub independently_verified_trace:bool,pub authenticated_clock:bool,pub authenticated_authority:bool,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Decision {
 pub verdict:String,pub reasons:Vec<String>,pub signature_valid:bool,
 pub clock_uncertainty_ns:Option<u64>,pub total_uncertainty_nano:Option<u64>,
 pub interval_low:Option<i128>,pub interval_high:Option<i128>,pub threshold_relation:String,
 pub physical_qualification_percent:u8,pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical(c:&Calibration)->Vec<u8>{serde_json::to_vec(c).unwrap_or_default()}
fn when(s:&str)->Option<i64>{DateTime::parse_from_rfc3339(s).ok().map(|v|v.timestamp_millis())}
fn hash(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
fn signature(s:&SignedCalibration,k:&PublicJwk)->bool{
 let Ok(key)=crate::verifying_key(k)else{return false};
 let Ok(raw)=hex::decode(&s.signature_hex)else{return false};
 let Ok(sig)=Signature::from_slice(&raw)else{return false};
 key.verify(&canonical(&s.record),&sig).is_ok()
}
pub fn assess(s:&SignedCalibration,o:&Observation,p:&Policy)->Decision{
 let c=&s.record;let mut issues=BTreeSet::new();
 let mut add=|v:&str|{issues.insert(v.to_owned());};
 if c.schema!="AETHER-197/calibration-v1"{add("SCHEMA_MISMATCH");}
 if c.id!=p.expected_calibration||o.calibration_id!=c.id{add("CALIBRATION_BINDING_MISMATCH");}
 if c.instrument!=p.expected_instrument||c.reference!=p.expected_reference{add("DEVICE_OR_REFERENCE_SUBSTITUTION");}
 if c.issuer!=p.expected_issuer{add("ISSUER_SUBSTITUTION");}
 if c.reference_root.is_empty()||c.device_root.is_empty()||c.reference_root==c.device_root{add("SHARED_OR_MISSING_ANCESTRY");}
 if !hash(&c.trace_sha256)||c.trace_sha256!=p.expected_trace_sha256{add("TRACEABILITY_HASH_MISMATCH");}
 if o.capture_id.is_empty()||!hash(&o.capture_sha256){add("MISSING_ORIGINAL_CAPTURE");}
 if p.replay.contains(&c.id){add("CALIBRATION_REPLAY");}
 match (when(&c.valid_from),when(&c.valid_until),when(&o.issued_utc),when(&o.measured_utc),when(&o.expires_utc)){
 (Some(a),Some(b),Some(x),Some(y),Some(z))if a<b&&a<=x&&x<=y&&y<=z&&y<=b=>{},
 (Some(_),Some(_),Some(_),Some(_),Some(_))=>add("CALIBRATION_OR_CHALLENGE_EXPIRED"),
 _=>add("INVALID_TIMESTAMP"),
 }
 if c.uncertainty_nano>p.max_calibration_uncertainty_nano{add("CALIBRATION_UNCERTAINTY_TOO_HIGH");}
 if o.elapsed_ns>p.max_elapsed_ns{add("CLOCK_SPAN_TOO_LONG");}
 let drift=(o.elapsed_ns as u128).checked_mul(c.drift_ppb as u128)
 .and_then(|x|x.checked_add(999_999_999)).map(|x|x/1_000_000_000);
 let clock=drift.and_then(|x|x.checked_add(c.clock_uncertainty_ns as u128))
 .and_then(|x|x.checked_add((c.clock_offset_ns as i128).unsigned_abs()));
 let mut cu=None;let mut total=None;let mut lo=None;let mut hi=None;
 let mut relation="UNAVAILABLE".to_owned();
 if let Some(v)=clock{
  if let Ok(n)=u64::try_from(v){
   cu=Some(n);if n>p.max_clock_uncertainty_ns{add("CLOCK_UNCERTAINTY_TOO_HIGH");}
   if let Some(t)=v.checked_add(c.uncertainty_nano as u128){
    if let Ok(n)=u64::try_from(t){
     total=Some(n);let a=o.value_nano as i128-t as i128;let b=o.value_nano as i128+t as i128;
     lo=Some(a);hi=Some(b);
     relation=if a>o.threshold_nano as i128{"ABOVE"}
       else if b<o.threshold_nano as i128{"BELOW"}
       else{"CROSSES_THRESHOLD"}.to_owned();
     if relation=="CROSSES_THRESHOLD"{add("UNCERTAINTY_CHANGES_DECISION");}
    }else{add("UNCERTAINTY_OVERFLOW");}
   }else{add("UNCERTAINTY_OVERFLOW");}
  }else{add("UNCERTAINTY_OVERFLOW");}
 }else{add("UNCERTAINTY_OVERFLOW");}
 let valid=signature(s,&p.authority_key);
 if !valid{add("INVALID_CALIBRATION_SIGNATURE");}
 if !p.independently_verified_trace{add("UNVERIFIED_REFERENCE_ANCESTRY");}
 if !p.authenticated_clock{add("UNAUTHENTICATED_PHYSICAL_CLOCK");}
 if !p.authenticated_authority{add("UNAUTHENTICATED_CALIBRATION_AUTHORITY");}
 let reasons:Vec<String>=issues.into_iter().collect();
 Decision{verdict:if reasons.is_empty(){"DOCUMENTARY_INTERVAL_ONLY"}else{"REJECT"}.into(),
 reasons,signature_valid:valid,clock_uncertainty_ns:cu,total_uncertainty_nano:total,
 interval_low:lo,interval_high:hi,threshold_relation:relation,
 physical_qualification_percent:0,operational_authority:"HOLD".into(),physical_act_allowed:false}
}
