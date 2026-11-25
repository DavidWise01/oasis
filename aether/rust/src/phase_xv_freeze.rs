//! AETHER-200-RS — Phase XV documentary qualification decision and historical freeze.
//! A consistent signed-software protocol is not authenticated original physical evidence.
//! The return type intentionally has no physical ACT authorization path.
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

pub const EXPECTED_BOUNDS: [&str; 8] = [
    "AETHER-193", "AETHER-194", "AETHER-195", "AETHER-196",
    "AETHER-197", "AETHER-198", "AETHER-199", "AETHER-200",
];

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Safeguards {
    pub historical_append_only_intent: bool,
    pub git_branch_technically_immutable: bool,
    pub synthetic_attestations_cannot_grant_act: bool,
    pub software_completion_is_not_physical_qualification: bool,
    pub new_physical_evidence_requires_new_review: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhaseXVRecord {
    pub bound: String,
    pub implementation: String,
    pub phase: String,
    pub turn: u8,
    pub planned_turns: u8,
    pub phase_state: String,
    pub software_protocol_progress_percent: u8,
    pub completed_bounds: Vec<String>,
    pub authenticated_original_hardware_captures: u64,
    pub independently_authenticated_physical_sources: u64,
    pub independently_authenticated_custody_holders: u64,
    pub traceable_physical_calibration_chains: u64,
    pub physically_observed_alarm_events: u64,
    pub external_independent_verification_sessions: u64,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
    pub decision: String,
    pub documentary_coverage: Vec<String>,
    pub external_evidence_missing: Vec<String>,
    pub safeguards: Safeguards,
    pub prior: String,
    pub phase_xiv_freeze: String,
    pub physical_evidence_submitted: bool,
    pub watermark: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FreezeAssessment {
    pub verdict: String,
    pub reasons: Vec<String>,
    pub software_protocol_percent: u8,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}

/// Evaluates internal documentary consistency only.
/// Do not use this as a device actuator or external-origin authenticator.
pub fn assess_phase_xv(record: &PhaseXVRecord) -> FreezeAssessment {
    let mut problems = BTreeSet::new();
    let mut reject = |reason: &str| { problems.insert(reason.to_owned()); };

    if record.bound != "AETHER-200" || record.phase != "XV" ||
       record.turn != 8 || record.planned_turns != 8 {
        reject("BOUND_PHASE_OR_TURN_MISMATCH");
    }
    if record.phase_state != "CLOSED_DOCUMENTARY_SOFTWARE_PROTOCOL" ||
       record.software_protocol_progress_percent != 100 {
        reject("INCOMPLETE_DOCUMENTARY_SOFTWARE_CLOSURE");
    }
    if record.completed_bounds.iter().map(String::as_str).collect::<Vec<_>>() != EXPECTED_BOUNDS.to_vec() {
        reject("BOUND_SEQUENCE_OR_ANCESTRY_MISMATCH");
    }
    if record.authenticated_original_hardware_captures != 0 ||
       record.independently_authenticated_physical_sources != 0 ||
       record.independently_authenticated_custody_holders != 0 ||
       record.traceable_physical_calibration_chains != 0 ||
       record.physically_observed_alarm_events != 0 ||
       record.external_independent_verification_sessions != 0 ||
       record.physical_qualification_percent != 0 ||
       record.physical_evidence_submitted {
        reject("UNSUPPORTED_PHYSICAL_EVIDENCE_PROMOTION");
    }
    if record.operational_authority != "HOLD" || record.physical_act_allowed {
        reject("OPERATIONAL_ACT_PROMOTION_ATTEMPT");
    }
    if record.decision != "PHYSICAL_QUALIFICATION_DENIED_PENDING_ORIGINAL_INDEPENDENT_EVIDENCE" {
        reject("UNSUPPORTED_PHYSICAL_QUALIFICATION_DECISION");
    }
    if record.documentary_coverage.len() != EXPECTED_BOUNDS.len() ||
       record.documentary_coverage.iter().zip(EXPECTED_BOUNDS.iter()).any(|(entry,bound)| !entry.starts_with(&bound[7..])) {
        reject("DOCUMENTARY_COVERAGE_MISSING_OR_REORDERED");
    }
    if record.external_evidence_missing.len() != 6 ||
       record.external_evidence_missing.iter().any(|entry| entry.trim().is_empty()) {
        reject("EXTERNAL_EVIDENCE_REQUIREMENTS_MISSING");
    }
    let s = &record.safeguards;
    if !s.historical_append_only_intent || s.git_branch_technically_immutable ||
       !s.synthetic_attestations_cannot_grant_act ||
       !s.software_completion_is_not_physical_qualification ||
       !s.new_physical_evidence_requires_new_review {
        reject("DOCUMENTARY_FREEZE_SAFEGUARD_MISMATCH");
    }
    if record.prior != "../199/protocol.json" ||
       record.phase_xiv_freeze != "../192/decision.json" ||
       record.watermark != ".dlw" {
        reject("FREEZE_PREDECESSOR_OR_WATERMARK_MISMATCH");
    }
    let reasons: Vec<String> = problems.into_iter().collect();
    FreezeAssessment {
        verdict: if reasons.is_empty() { "DOCUMENTARY_PHASE_XV_FREEZE_CONSISTENT" }
                 else { "REJECT" }.to_string(),
        reasons,
        software_protocol_percent: if record.software_protocol_progress_percent == 100 { 100 } else { 0 },
        physical_qualification_percent: 0,
        operational_authority: "HOLD".to_string(),
        physical_act_allowed: false,
    }
}
