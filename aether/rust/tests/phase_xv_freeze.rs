use aether_evidence::phase_xv_freeze::{assess_phase_xv, PhaseXVRecord};

fn baseline() -> PhaseXVRecord {
    serde_json::from_str(include_str!("../../200/decision.json"))
        .expect("AETHER-200 decision.json must deserialize")
}
fn reject<F: FnOnce(&mut PhaseXVRecord)>(name: &str, mutate: F) {
    let mut record = baseline();
    mutate(&mut record);
    let outcome = assess_phase_xv(&record);
    assert_eq!(outcome.verdict, "REJECT");
    assert!(outcome.reasons.iter().any(|r| r == name), "{name}: {:?}", outcome.reasons);
    assert_eq!(outcome.physical_qualification_percent, 0);
    assert_eq!(outcome.operational_authority, "HOLD");
    assert!(!outcome.physical_act_allowed);
}
#[test] fn original_decision_consistent_documentary_only() {
    let r = assess_phase_xv(&baseline());
    assert_eq!(r.verdict, "DOCUMENTARY_PHASE_XV_FREEZE_CONSISTENT", "{:?}", r.reasons);
    assert_eq!(r.software_protocol_percent, 100);
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn json_roundtrip() {
    let record = baseline();
    let bytes = serde_json::to_vec(&record).unwrap();
    let restored: PhaseXVRecord = serde_json::from_slice(&bytes).unwrap();
    assert_eq!(assess_phase_xv(&restored).verdict, "DOCUMENTARY_PHASE_XV_FREEZE_CONSISTENT");
}
#[test] fn bound_changed() { reject("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.bound="AETHER-199".into()); }
#[test] fn phase_changed() { reject("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.phase="XIV".into()); }
#[test] fn turn_changed() { reject("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.turn=7); }
#[test] fn wrong_planned_turns() { reject("BOUND_PHASE_OR_TURN_MISMATCH", |r| r.planned_turns=7); }
#[test] fn incomplete_protocol() { reject("INCOMPLETE_DOCUMENTARY_SOFTWARE_CLOSURE", |r| r.software_protocol_progress_percent=87); }
#[test] fn phase_state_promoted() { reject("INCOMPLETE_DOCUMENTARY_SOFTWARE_CLOSURE", |r| r.phase_state="PHYSICALLY_QUALIFIED".into()); }
#[test] fn omitted_bound() { reject("BOUND_SEQUENCE_OR_ANCESTRY_MISMATCH", |r| {r.completed_bounds.pop();}); }
#[test] fn reordered_bounds() { reject("BOUND_SEQUENCE_OR_ANCESTRY_MISMATCH", |r| r.completed_bounds.swap(1,2)); }
#[test] fn invented_hardware_capture() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.authenticated_original_hardware_captures=1); }
#[test] fn invented_independent_source() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.independently_authenticated_physical_sources=1); }
#[test] fn invented_independent_custodian() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.independently_authenticated_custody_holders=1); }
#[test] fn invented_calibration() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.traceable_physical_calibration_chains=1); }
#[test] fn invented_alarm_observation() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.physically_observed_alarm_events=1); }
#[test] fn invented_external_review() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.external_independent_verification_sessions=1); }
#[test] fn physical_percent_promoted() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.physical_qualification_percent=100); }
#[test] fn pretend_real_evidence_received() { reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION", |r| r.physical_evidence_submitted=true); }
#[test] fn act_authority_promoted() { reject("OPERATIONAL_ACT_PROMOTION_ATTEMPT", |r| r.operational_authority="ACT".into()); }
#[test] fn act_allowed_promoted() { reject("OPERATIONAL_ACT_PROMOTION_ATTEMPT", |r| r.physical_act_allowed=true); }
#[test] fn false_qualification_decision() { reject("UNSUPPORTED_PHYSICAL_QUALIFICATION_DECISION", |r| r.decision="PHYSICAL_QUALIFIED".into()); }
#[test] fn missing_coverage() { reject("DOCUMENTARY_COVERAGE_MISSING_OR_REORDERED", |r| {r.documentary_coverage.pop();}); }
#[test] fn reordered_coverage() { reject("DOCUMENTARY_COVERAGE_MISSING_OR_REORDERED", |r| r.documentary_coverage.swap(2,3)); }
#[test] fn hidden_external_evidence() { reject("EXTERNAL_EVIDENCE_REQUIREMENTS_MISSING", |r| {r.external_evidence_missing.pop();}); }
#[test] fn fake_git_branch_immutability() { reject("DOCUMENTARY_FREEZE_SAFEGUARD_MISMATCH", |r| r.safeguards.git_branch_technically_immutable=true); }
#[test] fn allow_synthetic_attestation_to_promote() { reject("DOCUMENTARY_FREEZE_SAFEGUARD_MISMATCH", |r| r.safeguards.synthetic_attestations_cannot_grant_act=false); }
#[test] fn disable_new_review() { reject("DOCUMENTARY_FREEZE_SAFEGUARD_MISMATCH", |r| r.safeguards.new_physical_evidence_requires_new_review=false); }
#[test] fn change_predecessor() { reject("FREEZE_PREDECESSOR_OR_WATERMARK_MISMATCH", |r| r.prior="../198/protocol.json".into()); }
#[test] fn change_phase_xiv_freeze() { reject("FREEZE_PREDECESSOR_OR_WATERMARK_MISMATCH", |r| r.phase_xiv_freeze="../191/protocol.json".into()); }
#[test] fn change_watermark() { reject("FREEZE_PREDECESSOR_OR_WATERMARK_MISMATCH", |r| r.watermark="unmarked".into()); }
