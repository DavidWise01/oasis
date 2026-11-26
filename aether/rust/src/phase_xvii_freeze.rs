//! AETHER-216-RS — Phase XVII documentary freeze.
//! Exact milestone closure is not executed test certification, independent
//! remote custody, hardware-origin evidence, physical qualification or ACT.
use serde::{Deserialize,Serialize};
use std::collections::BTreeSet;

pub const EXPECTED_BOUNDS:[&str;8]=[
 "AETHER-209","AETHER-210","AETHER-211","AETHER-212",
 "AETHER-213","AETHER-214","AETHER-215","AETHER-216"
];
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Safeguards{
 pub historical_append_only_intent:bool,
 pub git_branch_technically_immutable:bool,
 pub software_completion_implies_physical_qualification:bool,
 pub signed_claims_prove_controller_independence:bool,
 pub local_copy_counts_as_remote_receipt:bool,
 pub time_or_quorum_resolves_equivocation:bool,
 pub two_or_three_store_updates_crash_atomic:bool,
 pub independently_anchored_rollback_protection_achieved:bool,
 pub unattended_recovery_permitted:bool,
 pub new_phase_requires_explicit_independent_external_evidence:bool,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct FreezeRecord{
 pub bound:String,pub implementation:String,pub phase:String,
 pub turn:u8,pub planned_turns:u8,pub phase_state:String,
 pub software_protocol_progress_percent:u8,pub completed_bounds:Vec<String>,
 pub documentary_coverage:Vec<String>,pub documentary_source_committed:bool,
 pub rust_compilation_verified:bool,pub rust_regression_execution_verified:bool,
 pub github_actions_success_verified:bool,pub live_pages_deployment_verified:bool,
 pub independently_authenticated_remote_receipts:u64,
 pub independently_authenticated_physical_witnesses:u64,
 pub authenticated_original_hardware_captures:u64,
 pub independently_retained_external_checkpoints:u64,
 pub physical_qualification_percent:u8,
 pub operational_authority:String,pub physical_act_allowed:bool,
 pub may_repair:bool,pub may_recover:bool,pub may_reclaim_lock:bool,
 pub may_choose_history:bool,pub decision:String,
 pub unresolved_fail_closed:Vec<String>,pub safeguards:Safeguards,
 pub previous_bound:String,pub previous_phase_freeze:String,
 pub original_physical_evidence_required_before_act:bool,pub watermark:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Assessment{
 pub verdict:String,pub reasons:Vec<String>,
 pub documentary_software_percent:u8,pub physical_qualification_percent:u8,
 pub independently_authenticated_remote_receipts:u64,
 pub may_repair:bool,pub may_recover:bool,pub may_reclaim_lock:bool,
 pub may_choose_history:bool,pub operational_authority:String,
 pub physical_act_allowed:bool,
}
pub fn assess(r:&FreezeRecord)->Assessment{
 let mut reasons=BTreeSet::new();
 let mut fail=|s:&str|{reasons.insert(s.to_owned());};
 if r.bound!="AETHER-216"||r.phase!="XVII"||
 r.turn!=8||r.planned_turns!=8{
  fail("FREEZE_PHASE_OR_BOUND_MISMATCH");
 }
 if r.phase_state!="CLOSED_DOCUMENTARY_SOFTWARE_PROTOCOL"||
 r.software_protocol_progress_percent!=100{
  fail("DOCUMENTARY_CLOSURE_NOT_COMPLETE");
 }
 if r.completed_bounds.iter().map(String::as_str).collect::<Vec<_>>()!=EXPECTED_BOUNDS.to_vec(){
  fail("SOFTWARE_BOUND_SEQUENCE_MISMATCH");
 }
 if r.documentary_coverage.len()!=8||
 r.documentary_coverage.iter().enumerate().any(|(i,line)|
  !line.starts_with(&EXPECTED_BOUNDS[i][7..])){
  fail("DOCUMENTARY_COVERAGE_MISMATCH");
 }
 if !r.documentary_source_committed{
  fail("DOCUMENTARY_SOURCE_NOT_COMMITTED");
 }
 // A falsified runtime attestation is not allowed to turn an authored test
 // into an executed success in the frozen historical record.
 if r.rust_compilation_verified||r.rust_regression_execution_verified||
 r.github_actions_success_verified||r.live_pages_deployment_verified{
  fail("UNVERIFIED_RUNTIME_ASSERTION");
 }
 if r.independently_authenticated_remote_receipts!=0||
 r.independently_authenticated_physical_witnesses!=0||
 r.authenticated_original_hardware_captures!=0||
 r.independently_retained_external_checkpoints!=0||
 r.physical_qualification_percent!=0{
  fail("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_QUALIFICATION");
 }
 if r.operational_authority!="HOLD"||r.physical_act_allowed||
 r.may_repair||r.may_recover||r.may_reclaim_lock||r.may_choose_history{
  fail("OPERATIONAL_AUTHORITY_PROMOTION");
 }
 if r.decision!="DOCUMENTARY_PHASE_XVII_CLOSED_REMOTE_AND_PHYSICAL_EVIDENCE_UNQUALIFIED"{
  fail("FREEZE_DECISION_MISMATCH");
 }
 if r.unresolved_fail_closed.len()!=8||
 r.unresolved_fail_closed.iter().any(|s|s.trim().is_empty()){
  fail("UNRESOLVED_EVIDENCE_REQUIREMENTS_MISSING");
 }
 let s=&r.safeguards;
 if !s.historical_append_only_intent||s.git_branch_technically_immutable||
 s.software_completion_implies_physical_qualification||
 s.signed_claims_prove_controller_independence||
 s.local_copy_counts_as_remote_receipt||
 s.time_or_quorum_resolves_equivocation||
 s.two_or_three_store_updates_crash_atomic||
 s.independently_anchored_rollback_protection_achieved||
 s.unattended_recovery_permitted||
 !s.new_phase_requires_explicit_independent_external_evidence||
 !r.original_physical_evidence_required_before_act{
  fail("FAIL_CLOSED_SAFEGUARDS_MISMATCH");
 }
 if r.previous_bound!="../215/protocol.json"||
 r.previous_phase_freeze!="../208/decision.json"||
 r.watermark!=".dlw"{
  fail("HISTORICAL_FREEZE_ANCESTRY_MISMATCH");
 }
 let reasons:Vec<String>=reasons.into_iter().collect();
 Assessment{
  verdict:if reasons.is_empty(){"DOCUMENTARY_PHASE_XVII_FREEZE_CONSISTENT"}
  else{"REJECT"}.into(),
  reasons,
  documentary_software_percent:if r.software_protocol_progress_percent==100{100}else{0},
  physical_qualification_percent:0,independently_authenticated_remote_receipts:0,
  may_repair:false,may_recover:false,may_reclaim_lock:false,may_choose_history:false,
  operational_authority:"HOLD".into(),physical_act_allowed:false,
 }
}
