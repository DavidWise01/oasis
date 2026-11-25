//! AETHER-213-RS: declared custody ancestry and independent-control screening.
//! This validates signatures over incident evidence and checks declared ancestry.
//! It DOES NOT prove that signatures have different real-world controllers.
//! No independent physical witnesses or operational ACT can be inferred.
use crate::{sha256_hex, PublicJwk};
use crate::crash_incident::Incident;
use p256::ecdsa::{signature::Verifier, Signature};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

pub const SCHEMA:&str="AETHER-213/custody-ancestry-v1";
pub const WITNESS_SCHEMA:&str="AETHER-213/witness-v1";

#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct SourceAncestry {
 pub corpus_id:String,pub controlling_root:String,pub operator_id:String,
 pub administrator_id:String,pub claimed_locator:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Observation {
 pub schema:String,pub witness_id:String,pub witness_root:String,
 pub operator_id:String,pub administrator_id:String,pub host_id:String,
 pub witness_key_sha256:String,pub incident_sha256:String,
 pub source_corpus_id:String,pub evidence_sha256:String,
 pub capture_method:String,pub receipt_reference:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct SignedObservation{pub record:Observation,pub signature_hex:String}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct WitnessPin{
 pub witness_id:String,pub expected_root:String,pub public_key:PublicJwk,
 pub public_key_sha256:String,pub independently_enrolled:bool,
 pub independent_receipt_retention_verified:bool,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct AuditPolicy{
 pub expected_incident_sha256:String,pub expected_corpus_id:String,
 pub source:SourceAncestry,pub witnesses:Vec<WitnessPin>,
 pub min_declared_distinct_witnesses:usize,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Decision{
 pub verdict:String,pub reasons:Vec<String>,pub incident_sha256:String,
 pub valid_signatures:usize,pub declared_distinct_witnesses:usize,
 pub independently_authenticated_physical_witnesses:u64,
 pub physical_qualification_percent:u8,pub may_recover:bool,
 pub may_reclaim_lock:bool,pub operational_authority:String,
 pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(value:&T)->Vec<u8>{
 serde_json::to_vec(value).unwrap_or_default()
}
pub fn hash<T:Serialize>(value:&T)->String{sha256_hex(&canonical(value))}
pub fn incident_hash(incident:&Incident)->String{hash(incident)}
fn hex64(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
fn verified(obs:&SignedObservation,key:&PublicJwk)->bool{
 let Ok(verifying)=crate::verifying_key(key)else{return false};
 let Ok(raw)=hex::decode(&obs.signature_hex)else{return false};
 let Ok(sig)=Signature::from_slice(&raw)else{return false};
 verifying.verify(&canonical(&obs.record),&sig).is_ok()
}
pub fn assess(
 incident:&Incident,observations:&[SignedObservation],policy:&AuditPolicy,
)->Decision{
 let incident_sha256=incident_hash(incident);
 let mut issues=BTreeSet::new();
 let mut fail=|s:&str|{issues.insert(s.to_owned());};
 if incident.schema!=crate::crash_incident::SCHEMA{
  fail("INCIDENT_SCHEMA_MISMATCH");
 }
 if incident_sha256!=policy.expected_incident_sha256||
 !hex64(&policy.expected_incident_sha256){
  fail("INCIDENT_PIN_MISMATCH");
 }
 if incident.operational_authority!="HOLD"||incident.physical_act_allowed||
 incident.may_repair||incident.may_recover||incident.may_reclaim_lock{
  fail("INCIDENT_AUTHORITY_PROMOTION");
 }
 let source=&policy.source;
 if source.corpus_id.is_empty()||source.corpus_id!=policy.expected_corpus_id||
 source.controlling_root.is_empty()||source.operator_id.is_empty()||
 source.administrator_id.is_empty()||source.claimed_locator.is_empty(){
  fail("SOURCE_ANCESTRY_MISSING");
 }
 if policy.min_declared_distinct_witnesses!=3||
 policy.witnesses.len()!=3||observations.len()!=3{
  fail("THREE_WITNESS_ENVELOPE_REQUIRED");
 }
 let mut roots=BTreeSet::new();let mut operators=BTreeSet::new();
 let mut admins=BTreeSet::new();let mut hosts=BTreeSet::new();
 let mut ids=BTreeSet::new();let mut key_hashes=BTreeSet::new();
 let mut references=BTreeSet::new();let mut good_signatures=0usize;
 for (i,obs) in observations.iter().enumerate(){
  let o=&obs.record;
  if o.schema!=WITNESS_SCHEMA||o.witness_id.is_empty()||
  o.capture_method.is_empty()||o.receipt_reference.is_empty()||
  !hex64(&o.evidence_sha256){
   fail("OBSERVATION_FIELDS_INVALID");
  }
  if o.incident_sha256!=incident_sha256||
  o.source_corpus_id!=policy.expected_corpus_id{
   fail("OBSERVATION_INCIDENT_OR_SOURCE_MISMATCH");
  }
  if !ids.insert(o.witness_id.as_str())||
  !references.insert(o.receipt_reference.as_str()){
   fail("DUPLICATED_OBSERVATION_OR_RECEIPT");
  }
  if o.witness_root.is_empty()||o.operator_id.is_empty()||
  o.administrator_id.is_empty()||o.host_id.is_empty(){
   fail("WITNESS_ANCESTRY_MISSING");
  }
  if o.witness_root==source.controlling_root||
  o.operator_id==source.operator_id||
  o.administrator_id==source.administrator_id{
   fail("SOURCE_AND_WITNESS_SHARED_CONTROL");
  }
  roots.insert(o.witness_root.as_str());
  operators.insert(o.operator_id.as_str());
  admins.insert(o.administrator_id.as_str());
  hosts.insert(o.host_id.as_str());
  key_hashes.insert(o.witness_key_sha256.as_str());
  if let Some(pin)=policy.witnesses.get(i){
   if pin.witness_id!=o.witness_id||pin.expected_root!=o.witness_root||
   !hex64(&pin.public_key_sha256)||
   pin.public_key_sha256!=hash(&pin.public_key)||
   pin.public_key_sha256!=o.witness_key_sha256{
    fail("WITNESS_KEY_OR_ROOT_PIN_MISMATCH");
   }
   if !pin.independently_enrolled||
   !pin.independent_receipt_retention_verified{
    fail("WITNESS_EXTERNAL_ENROLLMENT_UNVERIFIED");
   }
   if verified(obs,&pin.public_key){good_signatures+=1;}
   else{fail("WITNESS_SIGNATURE_INVALID");}
  }
 }
 if roots.len()!=3||operators.len()!=3||admins.len()!=3||
 hosts.len()!=3||key_hashes.len()!=3{
  fail("WITNESS_ANCESTRY_NOT_DISTINCT");
 }
 if incident.anomalies.len()>0{
  // This is still a documented incident. Signatures cannot conceal anomalies.
  fail("INCIDENT_HAS_UNRESOLVED_ANOMALIES");
 }
 let reasons:Vec<String>=issues.into_iter().collect();
 let matched=reasons.is_empty();
 Decision{
  verdict:if matched{"DOCUMENTARY_ANCESTRY_CLAIMS_CONSISTENT"}
  else{"REJECT"}.into(),reasons,incident_sha256,
  valid_signatures:good_signatures,
  declared_distinct_witnesses:roots.len().min(operators.len()).min(admins.len()).min(hosts.len()),
  independently_authenticated_physical_witnesses:0,
  physical_qualification_percent:0,may_recover:false,
  may_reclaim_lock:false,operational_authority:"HOLD".into(),
  physical_act_allowed:false,
 }
}
