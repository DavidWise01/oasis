use aether_evidence::phase_xvii_freeze::*;
fn fixture()->FreezeRecord{
 serde_json::from_str(include_str!("../../216/decision.json"))
  .expect("AETHER-216 historical decision JSON must deserialize")
}
fn reject<F:FnOnce(&mut FreezeRecord)>(reason:&str,edit:F){
 let mut r=fixture();edit(&mut r);let d=assess(&r);
 assert!(d.reasons.iter().any(|s|s==reason),"{reason}: {:?}",d.reasons);
 assert_eq!(d.verdict,"REJECT");assert!(!d.may_repair);
 assert!(!d.may_recover);assert!(!d.may_reclaim_lock);
 assert!(!d.may_choose_history);assert!(!d.physical_act_allowed);
 assert_eq!(d.operational_authority,"HOLD");
}
#[test]fn canonical_phase_xvii_freeze(){
 let d=assess(&fixture());
 assert_eq!(d.verdict,"DOCUMENTARY_PHASE_XVII_FREEZE_CONSISTENT","{:?}",d.reasons);
 assert_eq!(d.documentary_software_percent,100);
 assert_eq!(d.physical_qualification_percent,0);
 assert_eq!(d.independently_authenticated_remote_receipts,0);
}
#[test]fn json_roundtrip(){
 let data=serde_json::to_vec(&fixture()).unwrap();
 let parsed:FreezeRecord=serde_json::from_slice(&data).unwrap();
 assert_eq!(assess(&parsed).verdict,"DOCUMENTARY_PHASE_XVII_FREEZE_CONSISTENT");
}
#[test]fn wrong_bound(){reject("FREEZE_PHASE_OR_BOUND_MISMATCH",|r|r.bound="AETHER-215".into());}
#[test]fn wrong_phase(){reject("FREEZE_PHASE_OR_BOUND_MISMATCH",|r|r.phase="XVI".into());}
#[test]fn wrong_turn(){reject("FREEZE_PHASE_OR_BOUND_MISMATCH",|r|r.turn=7);}
#[test]fn wrong_total_turns(){reject("FREEZE_PHASE_OR_BOUND_MISMATCH",|r|r.planned_turns=9);}
#[test]fn phase_left_open(){reject("DOCUMENTARY_CLOSURE_NOT_COMPLETE",|r|r.phase_state="OPEN".into());}
#[test]fn phase_percent_reduced(){reject("DOCUMENTARY_CLOSURE_NOT_COMPLETE",|r|r.software_protocol_progress_percent=87);}
#[test]fn bounds_missing(){reject("SOFTWARE_BOUND_SEQUENCE_MISMATCH",|r|{r.completed_bounds.pop();});}
#[test]fn bounds_swapped(){reject("SOFTWARE_BOUND_SEQUENCE_MISMATCH",|r|r.completed_bounds.swap(1,2));}
#[test]fn bounds_duplicated(){reject("SOFTWARE_BOUND_SEQUENCE_MISMATCH",|r|r.completed_bounds[5]="AETHER-213".into());}
#[test]fn coverage_missing(){reject("DOCUMENTARY_COVERAGE_MISMATCH",|r|{r.documentary_coverage.pop();});}
#[test]fn coverage_reordered(){reject("DOCUMENTARY_COVERAGE_MISMATCH",|r|r.documentary_coverage.swap(0,1));}
#[test]fn documentary_source_uncommitted(){reject("DOCUMENTARY_SOURCE_NOT_COMMITTED",|r|r.documentary_source_committed=false);}
#[test]fn fabricated_compilation_success(){reject("UNVERIFIED_RUNTIME_ASSERTION",|r|r.rust_compilation_verified=true);}
#[test]fn fabricated_regression_success(){reject("UNVERIFIED_RUNTIME_ASSERTION",|r|r.rust_regression_execution_verified=true);}
#[test]fn fabricated_actions_success(){reject("UNVERIFIED_RUNTIME_ASSERTION",|r|r.github_actions_success_verified=true);}
#[test]fn fabricated_pages_success(){reject("UNVERIFIED_RUNTIME_ASSERTION",|r|r.live_pages_deployment_verified=true);}
#[test]fn invented_external_receipt(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_QUALIFICATION",|r|r.independently_authenticated_remote_receipts=1);}
#[test]fn invented_physical_witness(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_QUALIFICATION",|r|r.independently_authenticated_physical_witnesses=1);}
#[test]fn invented_hardware_capture(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_QUALIFICATION",|r|r.authenticated_original_hardware_captures=1);}
#[test]fn invented_remote_checkpoint(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_QUALIFICATION",|r|r.independently_retained_external_checkpoints=1);}
#[test]fn physical_qualification_invented(){reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_QUALIFICATION",|r|r.physical_qualification_percent=100);}
#[test]fn act_promotion(){reject("OPERATIONAL_AUTHORITY_PROMOTION",|r|r.operational_authority="ACT".into());}
#[test]fn act_permission(){reject("OPERATIONAL_AUTHORITY_PROMOTION",|r|r.physical_act_allowed=true);}
#[test]fn repair_permission(){reject("OPERATIONAL_AUTHORITY_PROMOTION",|r|r.may_repair=true);}
#[test]fn recovery_permission(){reject("OPERATIONAL_AUTHORITY_PROMOTION",|r|r.may_recover=true);}
#[test]fn seize_lock_permission(){reject("OPERATIONAL_AUTHORITY_PROMOTION",|r|r.may_reclaim_lock=true);}
#[test]fn vote_fork_permission(){reject("OPERATIONAL_AUTHORITY_PROMOTION",|r|r.may_choose_history=true);}
#[test]fn false_qualification_decision(){reject("FREEZE_DECISION_MISMATCH",|r|r.decision="QUALIFIED".into());}
#[test]fn unresolved_requirements_removed(){reject("UNRESOLVED_EVIDENCE_REQUIREMENTS_MISSING",|r|{r.unresolved_fail_closed.pop();});}
#[test]fn unresolved_requirements_empty(){reject("UNRESOLVED_EVIDENCE_REQUIREMENTS_MISSING",|r|r.unresolved_fail_closed[0]=" ".into());}
#[test]fn immutable_git_branch_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.git_branch_technically_immutable=true);}
#[test]fn software_equals_physical_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.software_completion_implies_physical_qualification=true);}
#[test]fn signatures_prove_independence_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.signed_claims_prove_controller_independence=true);}
#[test]fn local_copy_is_remote_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.local_copy_counts_as_remote_receipt=true);}
#[test]fn vote_away_fork_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.time_or_quorum_resolves_equivocation=true);}
#[test]fn two_store_transaction_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.two_or_three_store_updates_crash_atomic=true);}
#[test]fn external_anchor_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.independently_anchored_rollback_protection_achieved=true);}
#[test]fn unattended_recovery_claim(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.unattended_recovery_permitted=true);}
#[test]fn waive_external_evidence(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.safeguards.new_phase_requires_explicit_independent_external_evidence=false);}
#[test]fn waive_physical_capture(){reject("FAIL_CLOSED_SAFEGUARDS_MISMATCH",|r|r.original_physical_evidence_required_before_act=false);}
#[test]fn wrong_previous_bound(){reject("HISTORICAL_FREEZE_ANCESTRY_MISMATCH",|r|r.previous_bound="../214/protocol.json".into());}
#[test]fn wrong_previous_phase(){reject("HISTORICAL_FREEZE_ANCESTRY_MISMATCH",|r|r.previous_phase_freeze="../207/protocol.json".into());}
#[test]fn lost_watermark(){reject("HISTORICAL_FREEZE_ANCESTRY_MISMATCH",|r|r.watermark="".into());}
