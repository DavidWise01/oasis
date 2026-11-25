use aether_evidence::freeze::{assess_freeze, FreezeRecord};
fn baseline() -> FreezeRecord {
    serde_json::from_str(include_str!("../../192/decision.json")).expect("frozen decision JSON must deserialize")
}
fn rejects<F: FnOnce(&mut FreezeRecord)>(reason: &str, edit: F) {
    let mut d = baseline();
    edit(&mut d);
    let a = assess_freeze(&d);
    assert_eq!(a.verdict, "REJECT");
    assert!(a.reasons.iter().any(|r| r == reason), "expected {reason}: {:?}", a.reasons);
    assert_eq!(a.physical_qualification_percent, 0);
    assert_eq!(a.operational_authority, "HOLD");
    assert!(!a.physical_act_allowed);
}
#[test] fn documentary_baseline_is_consistent() {
    let r = assess_freeze(&baseline());
    assert_eq!(r.verdict, "DOCUMENTARY_FREEZE_CONSISTENT");
    assert!(r.reasons.is_empty());
    assert_eq!(r.software_protocol_percent, 100);
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn machine_readable_roundtrip() {
    let d = baseline();
    let encoded = serde_json::to_vec(&d).unwrap();
    let restored: FreezeRecord = serde_json::from_slice(&encoded).unwrap();
    assert_eq!(assess_freeze(&restored).verdict, "DOCUMENTARY_FREEZE_CONSISTENT");
}
#[test] fn incorrect_bound() { rejects("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.bound = "AETHER-191".into()); }
#[test] fn incorrect_phase() { rejects("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.phase = "XV".into()); }
#[test] fn incorrect_turn() { rejects("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.turn = 7); }
#[test] fn incomplete_software() { rejects("INCOMPLETE_DOCUMENTARY_CLOSURE", |r| r.software_protocol_progress_percent = 87); }
#[test] fn false_phase_state() { rejects("INCOMPLETE_DOCUMENTARY_CLOSURE", |r| r.phase_state = "QUALIFIED".into()); }
#[test] fn missing_bound() { rejects("BOUND_ANCESTRY_MISMATCH", |r| { r.completed_bounds.pop(); }); }
#[test] fn reordered_bound() { rejects("BOUND_ANCESTRY_MISMATCH", |r| r.completed_bounds.swap(1, 2)); }
#[test] fn fabricated_capture() { rejects("PHYSICAL_PROOF_NOT_SUPPORTED_BY_FREEZE", |r| r.authenticated_original_hardware_captures = 1); }
#[test] fn fabricated_independent_source() { rejects("PHYSICAL_PROOF_NOT_SUPPORTED_BY_FREEZE", |r| r.independently_authenticated_physical_sources = 1); }
#[test] fn fabricated_alarm() { rejects("PHYSICAL_PROOF_NOT_SUPPORTED_BY_FREEZE", |r| r.physically_observed_alarm_events = 1); }
#[test] fn pretend_physical_submission() { rejects("PHYSICAL_PROOF_NOT_SUPPORTED_BY_FREEZE", |r| r.physical_evidence_submitted = true); }
#[test] fn physical_percent_promoted() { rejects("PHYSICAL_PROOF_NOT_SUPPORTED_BY_FREEZE", |r| r.physical_qualification_percent = 100); }
#[test] fn fake_operational_act() { rejects("OPERATIONAL_ACT_PROMOTION_ATTEMPT", |r| r.operational_authority = "ACT".into()); }
#[test] fn physical_act_flag() { rejects("OPERATIONAL_ACT_PROMOTION_ATTEMPT", |r| r.physical_act_allowed = true); }
#[test] fn false_decision() { rejects("UNSUPPORTED_QUALIFICATION_DECISION", |r| r.decision = "PHYSICALLY_QUALIFIED".into()); }
#[test] fn coverage_incomplete() { rejects("INCOMPLETE_COVERAGE_OR_UNRESOLVED_EVIDENCE", |r| { r.documentary_coverage.pop(); }); }
#[test] fn unresolved_evidence_hidden() { rejects("INCOMPLETE_COVERAGE_OR_UNRESOLVED_EVIDENCE", |r| { r.external_evidence_missing.pop(); }); }
#[test] fn github_immutability_falsely_claimed() { rejects("FREEZE_SAFEGUARD_INCONSISTENCY", |r| r.safeguards.git_branch_technically_immutable = true); }
#[test] fn synthetic_attestation_override() { rejects("FREEZE_SAFEGUARD_INCONSISTENCY", |r| r.safeguards.synthetic_attestations_cannot_grant_act = false); }
#[test] fn new_review_requirement_disabled() { rejects("FREEZE_SAFEGUARD_INCONSISTENCY", |r| r.safeguards.new_physical_evidence_requires_new_review = false); }
#[test] fn predecessor_replaced() { rejects("PREDECESSOR_OR_WATERMARK_MISMATCH", |r| r.prior = "../190/protocol.json".into()); }
#[test] fn phase_xiii_freeze_replaced() { rejects("PREDECESSOR_OR_WATERMARK_MISMATCH", |r| r.phase_xiii_freeze = "../175/protocol.json".into()); }
#[test] fn watermark_modified() { rejects("PREDECESSOR_OR_WATERMARK_MISMATCH", |r| r.watermark = "NONE".into()); }
