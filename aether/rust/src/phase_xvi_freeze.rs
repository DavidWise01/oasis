//! AETHER-208-RS — final Phase XVI documentary freeze evaluator.
//! Full software-protocol closure is not proof of external origin, physical metrology,
//! remote checkpoint anchoring, or ACT authority. This module never grants ACT.
use serde::{Deserialize,Serialize};
use std::collections::BTreeSet;

pub const EXPECTED_BOUNDS:[&str;8]=[
 "AETHER-201","AETHER-202","AETHER-203","AETHER-204",
 "AETHER-205","AETHER-206","AETHER-207","AETHER-208",
];
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Safeguards{
 pub historical_append_only_intent:bool,
 pub git_branch_technically_immutable:bool,
 pub software_completion_implies_physical_qualification:bool,
 pub synthetic_signatures_create_external_independence:bool,
 pub interrupted_two_file_transaction_requires_independent_adjudication:bool,
 pub locally_valid_hash_chain_proves_global_nonrollback:bool,
 pub future_original_evidence_requires_new_phase_review:bool,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct FreezeRecord{
 pub bound:String,pub implementation:String,pub phase:String,
 pub turn:u8,pub planned_turns:u8,pub phase_state:String,
 pub software_protocol_progress_percent:u8,
 pub completed_bounds:Vec<String>,pub documentary_coverage:Vec<String>,
 pub documentary_source_committed:bool,
 pub rust_compilation_verified:bool,pub rust_regression_execution_verified:bool,
 pub github_actions_success_verified:bool,pub live_pages_deployment_verified:bool,
 pub authenticated_external_evidence_roots:u64,
 pub independently_authenticated_custody_holders:u64,
 pub authenticated_original_hardware_captures:u64,
 pub independently_observed_physical_alarms:u64,
 pub independent_remote_checkpoint_copies:u64,
 pub physical_qualification_percent:u8,
 pub operational_authority:String,pub physical_act_allowed:bool,
 pub decision:String,pub unresolved_fail_closed:Vec<String>,
 pub safeguards:Safeguards,pub preceding_bound:String,
 pub preceding_phase_freeze:String,
 pub operational_promotion_requires_external_independent_evidence:bool,
 pub watermark:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Assessment{
 pub verdict:String,pub reasons:Vec<String>,
 pub documentary_software_percent:u8,pub physical_qualification_percent:u8,
 pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn assess(record:&FreezeRecord)->Assessment{
 let mut reasons=BTreeSet::new();
 let mut fail=|s:&str|{reasons.insert(s.to_string());};
 if record.bound!="AETHER-208"||record.phase!="XVI"||
 record.turn!=8||record.planned_turns!=8{
  fail("PHASE_BOUND_OR_TURN_MISMATCH");
 }
 if record.phase_state!="CLOSED_DOCUMENTARY_SOFTWARE_PROTOCOL"||
 record.software_protocol_progress_percent!=100{
  fail("DOCUMENTARY_CLOSURE_NOT_COMPLETE");
 }
 if record.completed_bounds.iter().map(String::as_str).collect::<Vec<_>>()!=EXPECTED_BOUNDS.to_vec(){
  fail("SOFTWARE_BOUND_SEQUENCE_MISMATCH");
 }
 if record.documentary_coverage.len()!=8||
 record.documentary_coverage.iter().enumerate().any(|(i,line)|
   !line.starts_with(&EXPECTED_BOUNDS[i][7..]) ){
  fail("DOCUMENTARY_COVERAGE_NOT_COMPLETE");
 }
 if !record.documentary_source_committed{
  fail("DOCUMENTARY_SOURCE_NOT_COMMITTED");
 }
 // As of the recorded freeze, these have NOT been independently certified.
 if record.rust_compilation_verified||record.rust_regression_execution_verified||
 record.github_actions_success_verified||record.live_pages_deployment_verified{
  fail("UNSUBSTANTIATED_RUNTIME_CERTIFICATION");
 }
 if record.authenticated_external_evidence_roots!=0||
 record.independently_authenticated_custody_holders!=0||
 record.authenticated_original_hardware_captures!=0||
 record.independently_observed_physical_alarms!=0||
 record.independent_remote_checkpoint_copies!=0||
 record.physical_qualification_percent!=0{
  fail("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE");
 }
 if record.operational_authority!="HOLD"||record.physical_act_allowed{
  fail("UNAUTHORIZED_ACT_PROMOTION");
 }
 if record.decision!="DOCUMENTARY_PHASE_XVI_CLOSED_EXTERNAL_ORIGINAL_EVIDENCE_UNQUALIFIED"{
  fail("FREEZE_DECISION_MISMATCH");
 }
 if record.unresolved_fail_closed.len()!=8||
 record.unresolved_fail_closed.iter().any(|s|s.trim().is_empty()){
  fail("UNRESOLVED_TRUST_REQUIREMENTS_MISSING");
 }
 let safeguards=&record.safeguards;
 if !safeguards.historical_append_only_intent||
 safeguards.git_branch_technically_immutable||
 safeguards.software_completion_implies_physical_qualification||
 safeguards.synthetic_signatures_create_external_independence||
 !safeguards.interrupted_two_file_transaction_requires_independent_adjudication||
 safeguards.locally_valid_hash_chain_proves_global_nonrollback||
 !safeguards.future_original_evidence_requires_new_phase_review||
 !record.operational_promotion_requires_external_independent_evidence{
  fail("FAIL_CLOSED_SAFEGUARDS_MISMATCH");
 }
 if record.preceding_bound!="../207/protocol.json"||
 record.preceding_phase_freeze!="../200/decision.json"||
 record.watermark!=".dlw"{
  fail("FREEZE_ANCESTRY_OR_WATERMARK_MISMATCH");
 }
 let reasons:Vec<String>=reasons.into_iter().collect();
 Assessment{
  verdict:if reasons.is_empty(){"DOCUMENTARY_PHASE_XVI_FREEZE_CONSISTENT"}else{"REJECT"}.into(),
  reasons,
  documentary_software_percent:if record.software_protocol_progress_percent==100{100}else{0},
  physical_qualification_percent:0,operational_authority:"HOLD".into(),physical_act_allowed:false
 }
}
