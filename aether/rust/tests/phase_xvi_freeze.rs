use aether_evidence::phase_xvi_freeze::*;
fn fixture()->FreezeRecord{
 serde_json::from_str(include_str!("../../208/decision.json"))
  .expect("AETHER-208 decision fixture must deserialize")
}
fn reject<F:FnOnce(&mut FreezeRecord)>(reason:&str,mutate:F){
 let mut record=fixture();mutate(&mut record);
 let decision=assess(&record);
 assert!(decision.reasons.iter().any(|x|x==reason),"{reason}: {:?}",decision.reasons);
 assert_eq!(decision.verdict,"REJECT");
 assert_eq!(decision.physical_qualification_percent,0);
 assert_eq!(decision.operational_authority,"HOLD");
 assert!(!decision.physical_act_allowed);
}
#[test]fn canonical_documentary_decision_consistent(){
 let d=assess(&fixture());assert_eq!(d.verdict,"DOCUMENTARY_PHASE_XVI_FREEZE_CONSISTENT","{:?}",d.reasons);
 assert_eq!(d.documentary_software_percent,100);assert_eq!(d.physical_qualification_percent,0);
 assert!(!d.physical_act_allowed);
}
#[test]fn serde_roundtrip(){let r=fixture();let v=serde_json::to_vec(&r).unwrap();let r:FreezeRecord=serde_json::from_slice(&v).unwrap();assert_eq!(assess(&r).verdict,"DOCUMENTARY_PHASE_XVI_FREEZE_CONSISTENT");}
#[test]fn bad_bound(){reject("PHASE_BOUND_OR_TURN_MISMATCH",|r|r.bound="AETHER-207".into());}
#[test]fn wrong_phase(){reject("PHASE_BOUND_OR_TURN_MISMATCH",|r|r.phase="XV".into());}
#[test]fn turn_regression(){reject("PHASE_BOUND_OR_TURN_MISMATCH",|r|r.turn=7);}
#[test]fn planned_turns_regression(){reject("PHASE_BOUND_OR_TURN_MISMATCH",|r|r.planned_turns=9);}
#[test]fn phase_not_closed(){reject("DOCUMENTARY_CLOSURE_NOT_COMPLETE",|r|r.phase_state="OPEN".into());}
#[test]fn progress_87_5(){reject("DOCUMENTARY_CLOSURE_NOT_COMPLETE",|r|r.software_protocol_progress_percent=87);}
#[test]fn omitted_phase_bound(){reject("SOFTWARE_BOUND_SEQUENCE_MISMATCH",|r|{r.completed_bounds.pop();});}
#[test]fn duplicated_bound(){reject("SOFTWARE_BOUND_SEQUENCE_MISMATCH",|r|r.completed_bounds[2]="AETHER-202".into());}
#[test]fn swapped_bounds(){reject("SOFTWARE_BOUND_SEQUENCE_MISMATCH",|r|r.completed_bounds.swap(1,2));}
#[test]fn empty_coverage(){reject("DOCUMENTARY_COVERAGE_NOT_COMPLETE",|r|r.documentary_coverage.clear());}
#[test]fn reordered_coverage(){reject("DOCUMENTARY_COVERAGE_NOT_COMPLETE",|r|r.documentary_coverage.swap(0,1));}
#[test]fn documentary_source_not_committed(){reject("DOCUMENTARY_SOURCE_NOT_COMMITTED",|r|r.documentary_source_committed=false);}
#[test]fn invented_cargo_pass(){reject("UNSUBSTANTIATED_RUNTIME_CERTIFICATION",|r|r.rust_compilation_verified=true);}
#[test]fn invented_regression_pass(){reject("UNSUBSTANTIATED_RUNTIME_CERTIFICATION",|r|r.rust_regression_execution_verified=true);}
#[test]fn invented_actions_pass(){reject("UNSUBSTANTIATED_RUNTIME_CERTIFICATION",|r|r.github_actions_success_verified=true);}
#[test]fn invented_pages_pass(){reject("UNSUBSTANTIATED_RUNTIME_CERTIFICATION",|r|r.live_pages_deployment_verified=true);}
#[test]fn invented_external_root(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE",|r|r.authenticated_external_evidence_roots=1);}
#[test]fn invented_custodian(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE",|r|r.independently_authenticated_custody_holders=1);}
#[test]fn invented_original_capture(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE",|r|r.authenticated_original_hardware_captures=1);}
#[test]fn invented_observed_alarm(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE",|r|r.independently_observed_physical_alarms=1);}
#[test]fn invented_remote_checkpoint(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE",|r|r.independent_remote_checkpoint_copies=1);}
#[test]fn invented_physical_qualification(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE",|r|r.physical_qualification_percent=100);}
#[test]fn promote_act_authority(){reject("UNAUTHORIZED_ACT_PROMOTION",|r|r.operational_authority="ACT".into());}
#[test]fn permit_act(){reject("UNAUTHORIZED_ACT_PROMOTION",|r|r.physical_act_allowed=true);}
#[test]fn false_freeze_decision(){reject("FREEZE_DECISION_MISMATCH",|r|r.decision="QUALIFIED".into());}
#[test]fn hide_two_file_crash_risk(){reject("UNRESOLVED_TRUST_REQUIREMENTS_MISSING",|r|{r.unresolved_fail_closed.pop();});}
#[test]fn empty_missing_evidence_disclosure(){reject("UNRESOLVED_TRUST_REQUIREMENTS_MISSING",|r|r.unresolved_fail_closed[0]="".into());}
#[test]fn falsely_claim_immutable_branch(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.git_branch_technically_immutable=true);}
#[test]fn conflate_software_with_physical(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.software_completion_implies_physical_qualification=true);}
#[test]fn synthetic_signatures_claim_independence(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.synthetic_signatures_create_external_independence=true);}
#[test]fn allow_automatic_crash_repair(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.interrupted_two_file_transaction_requires_independent_adjudication=false);}
#[test]fn pretend_local_hash_proves_global_nonrollback(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.locally_valid_hash_chain_proves_global_nonrollback=true);}
#[test]fn deny_new_external_review(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.future_original_evidence_requires_new_phase_review=false);}
#[test]fn disable_external_evidence_requirement(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.operational_promotion_requires_external_independent_evidence=false);}
#[test]fn wrong_preceding_bound(){reject("FREEZE_ANCESTRY_OR_WATERMARK_MISMATCH",|r|r.preceding_bound="../206/protocol.json".into());}
#[test]fn wrong_previous_phase(){reject("FREEZE_ANCESTRY_OR_WATERMARK_MISMATCH",|r|r.preceding_phase_freeze="../199/protocol.json".into());}
#[test]fn watermark_removed(){reject("FREEZE_ANCESTRY_OR_WATERMARK_MISMATCH",|r|r.watermark="".into());}
