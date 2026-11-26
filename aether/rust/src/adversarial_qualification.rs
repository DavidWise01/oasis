//! AETHER-215-RS — read-only adversarial remote custody qualification.
//! Combines AETHER-212 incidents, 213 signed incident witnesses, and 214
//! cross-host receipt claims. No number of synthetic signatures proves external
//! independent custody. Unresolved conflict cannot authorize recovery or ACT.
use crate::{sha256_hex,crash_incident::Incident,
 custody_ancestry::{self,AuditPolicy,SignedObservation},
 cross_host_equivocation::{self,Policy as HostPolicy,SignedHostReceipt,Conflict}};
use serde::{Serialize,Deserialize};
use std::collections::{BTreeMap,BTreeSet};

pub const SCHEMA:&str="AETHER-215/qualification-v1";
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Request {
 pub schema:String,pub requested_operation:String,pub claimed_remote_witnesses:u64,
 pub incident_sha256:String,pub witness_envelope_sha256:String,
 pub host_receipts_sha256:String,pub claimed_original_capture_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct QualificationPolicy{
 pub expected_incident_sha256:String,pub expected_witness_envelope_sha256:String,
 pub expected_host_receipts_sha256:String,
 pub external_original_capture_authenticated:bool,
 pub external_custody_independently_authenticated:bool,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Decision{
 pub verdict:String,pub reasons:Vec<String>,pub conflicts:Vec<Conflict>,
 pub incident_sha256:String,pub witness_envelope_sha256:String,
 pub host_receipts_sha256:String,pub valid_incident_signatures:usize,
 pub valid_host_signatures:usize,pub independently_authenticated_physical_witnesses:u64,
 pub physical_qualification_percent:u8,pub may_select_history:bool,
 pub may_repair:bool,pub may_recover:bool,pub may_reclaim_lock:bool,
 pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(value:&T)->Vec<u8>{
 serde_json::to_vec(value).unwrap_or_default()
}
pub fn digest<T:Serialize>(value:&T)->String{sha256_hex(&canonical(value))}
fn valid_hash(v:&str)->bool{v.len()==64&&v.bytes().all(|b|b.is_ascii_hexdigit())}
pub fn assess(
 incident:&Incident,observations:&[SignedObservation],
 ancestry_policy:&AuditPolicy,host_receipts:&[SignedHostReceipt],
 host_policy:&HostPolicy,request:&Request,policy:&QualificationPolicy,
)->Decision{
 let incident_hash=custody_ancestry::incident_hash(incident);
 let witnesses_hash=digest(&observations);
 let receipts_hash=digest(&host_receipts);
 let ancestry=custody_ancestry::assess(incident,observations,ancestry_policy);
 let hosts=cross_host_equivocation::assess(host_receipts,host_policy);
 let mut faults=BTreeSet::new();
 let mut fail=|s:&str|{faults.insert(s.to_owned());};
 if request.schema!=SCHEMA{fail("QUALIFICATION_SCHEMA_MISMATCH");}
 if request.requested_operation!="READ_ONLY_QUALIFICATION"{
  fail("OPERATION_NOT_OBSERVATION_ONLY");
 }
 if !valid_hash(&policy.expected_incident_sha256)||
  !valid_hash(&policy.expected_witness_envelope_sha256)||
  !valid_hash(&policy.expected_host_receipts_sha256)||
  request.incident_sha256!=incident_hash||
  request.incident_sha256!=policy.expected_incident_sha256||
  request.witness_envelope_sha256!=witnesses_hash||
  request.witness_envelope_sha256!=policy.expected_witness_envelope_sha256||
  request.host_receipts_sha256!=receipts_hash||
  request.host_receipts_sha256!=policy.expected_host_receipts_sha256{
  fail("QUALIFICATION_EVIDENCE_PIN_MISMATCH");
 }
 if ancestry.verdict!="DOCUMENTARY_ANCESTRY_CLAIMS_CONSISTENT"{
  fail("INCIDENT_WITNESS_CHAIN_REJECTED");
  for reason in &ancestry.reasons{fail(&format!("ANCESTRY: {reason}"));}
 }
 if hosts.verdict!="DOCUMENTARY_CROSS_HOST_CLAIMS_CONSISTENT"{
  fail("CROSS_HOST_WITNESS_CHAIN_REJECTED");
  for reason in &hosts.reasons{fail(&format!("HOST: {reason}"));}
 }
 if !hosts.conflicts.is_empty(){
  fail("SIGNED_HISTORY_FORK_UNRESOLVED");
 }
 if incident.documentary_state!="LOCAL_DOCUMENTARY_SNAPSHOT_CONSISTENT"||
  !incident.anomalies.is_empty(){
  fail("INCIDENT_STILL_UNRESOLVED");
 }
 if incident.may_repair||incident.may_recover||incident.may_reclaim_lock||
  incident.physical_act_allowed||incident.operational_authority!="HOLD"{
  fail("UPSTREAM_INCIDENT_AUTHORITY_PROMOTION");
 }
 if request.claimed_remote_witnesses!=3||
  request.claimed_remote_witnesses!=observations.len() as u64||
  request.claimed_remote_witnesses!=host_receipts.len() as u64{
  fail("CLAIMED_WITNESS_COUNT_MISMATCH");
 }
 if !valid_hash(&request.claimed_original_capture_sha256){
  fail("ORIGINAL_CAPTURE_DIGEST_NOT_DECLARED");
 }
 if ancestry_policy.expected_corpus_id!=host_policy.expected_corpus_id||
  ancestry_policy.source.corpus_id!=host_policy.source.corpus_id||
  ancestry_policy.source.controlling_root!=host_policy.source.controlling_root||
  ancestry_policy.source.operator_id!=host_policy.source.operator_id||
  ancestry_policy.source.administrator_id!=host_policy.source.administrator_id{
  fail("CROSS_PROTOCOL_SOURCE_ANCESTRY_MISMATCH");
 }
 let host_by_witness:BTreeMap<&str,&cross_host_equivocation::HostReceipt>=
 host_receipts.iter().map(|s|(s.record.witness_id.as_str(),&s.record)).collect();
 for obs in observations{
  let w=&obs.record;
  match host_by_witness.get(w.witness_id.as_str()){
   None=>fail("WITNESS_MISSING_HOST_RECEIPT"),
   Some(h)=>{
    if h.receipt_id!=w.receipt_reference||h.key_sha256!=w.witness_key_sha256||
     h.witness_root!=w.witness_root||
     h.witness_operator!=w.operator_id||
     h.witness_administrator!=w.administrator_id||
     h.witness_host!=w.host_id||
     h.corpus_id!=w.source_corpus_id{
     fail("WITNESS_HOST_CUSTODY_BINDING_MISMATCH");
    }
   }
  }
 }
 // These flags are *claims*, not independently authenticated evidence.
 // The open physical-evidence bound remains explicit even if both are true.
 if !policy.external_original_capture_authenticated||
    !policy.external_custody_independently_authenticated{
  fail("EXTERNAL_ORIGINAL_EVIDENCE_UNVERIFIED");
 }else{
  fail("EXTERNAL_AUTHENTICATION_ASSERTED_NOT_INDEPENDENTLY_VERIFIED");
 }
 let reasons=faults.into_iter().collect::<Vec<_>>();
 let verdict=if reasons.iter().all(|r|r=="EXTERNAL_ORIGINAL_EVIDENCE_UNVERIFIED"||
   r=="EXTERNAL_AUTHENTICATION_ASSERTED_NOT_INDEPENDENTLY_VERIFIED"){
  "DOCUMENTARY_ENSEMBLE_CONSISTENT_AUTHORITY_HOLD"
 }else{"REJECT"};
 Decision{
  verdict:verdict.into(),reasons,conflicts:hosts.conflicts,
  incident_sha256:incident_hash,witness_envelope_sha256:witnesses_hash,
  host_receipts_sha256:receipts_hash,
  valid_incident_signatures:ancestry.valid_signatures,
  valid_host_signatures:hosts.valid_signatures,
  independently_authenticated_physical_witnesses:0,
  physical_qualification_percent:0,may_select_history:false,
  may_repair:false,may_recover:false,may_reclaim_lock:false,
  operational_authority:"HOLD".into(),physical_act_allowed:false,
 }
}
