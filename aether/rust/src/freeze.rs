//! AETHER-192-RS: Phase XIV documentary freeze assessment.
//! The evaluator is deliberately incapable of authorizing a physical ACT.
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

pub const EXPECTED_BOUNDS: [&str; 8] = [
    "AETHER-185", "AETHER-186", "AETHER-187", "AETHER-188",
    "AETHER-189", "AETHER-190", "AETHER-191", "AETHER-192",
];

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Safeguards {
    pub historical_append_only_intent: bool,
    pub git_branch_technically_immutable: bool,
    pub synthetic_attestations_cannot_grant_act: bool,
    pub all_passes_documentary_only: bool,
    pub new_physical_evidence_requires_new_review: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FreezeRecord {
    pub bound: String,
    pub implementation: String,
    pub phase: String,
    pub turn: u8,
    pub planned_turns: u8,
    pub phase_state: String,
    pub software_protocol_progress_percent: u8,
    pub completed_bounds: Vec<String>,
    pub physical_qualification_percent: u8,
    pub authenticated_original_hardware_captures: u64,
    pub independently_authenticated_physical_sources: u64,
    pub physically_observed_alarm_events: u64,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
    pub decision: String,
    pub documentary_coverage: Vec<String>,
    pub external_evidence_missing: Vec<String>,
    pub safeguards: Safeguards,
    pub prior: String,
    pub phase_xiii_freeze: String,
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

/// Rejects inconsistent documentary records. The returned physical authorization
/// is always HOLD, including if a caller forges successful attestation flags.
pub fn assess_freeze(record: &FreezeRecord) -> FreezeAssessment {
    let mut errors: BTreeSet<String> = BTreeSet::new();
    let mut add = |error: &str| { errors.insert(error.to_owned()); };
    if record.bound != "AETHER-192" || record.phase != "XIV"
        || record.turn != 8 || record.planned_turns != 8
    {
        add("BOUND_PHASE_OR_TURN_MISMATCH");
    }
    if record.phase_state != "CLOSED_DOCUMENTARY_SOFTWARE_PROTOCOL"
        || record.software_protocol_progress_percent != 100
    {
        add("INCOMPLETE_DOCUMENTARY_CLOSURE");
    }
    if record.completed_bounds.iter().map(String::as_str).collect::<Vec<_>>()
        != EXPECTED_BOUNDS.to_vec()
    {
        add("BOUND_ANCESTRY_MISMATCH");
    }
    if record.physical_qualification_percent != 0
        || record.authenticated_original_hardware_captures != 0
        || record.independently_authenticated_physical_sources != 0
        || record.physically_observed_alarm_events != 0
        || record.physical_evidence_submitted
    {
        add("PHYSICAL_PROOF_NOT_SUPPORTED_BY_FREEZE");
    }
    if record.operational_authority != "HOLD" || record.physical_act_allowed {
        add("OPERATIONAL_ACT_PROMOTION_ATTEMPT");
    }
    if record.decision != "PHYSICAL_QUALIFICATION_DENIED_PENDING_ORIGINAL_INDEPENDENT_EVIDENCE" {
        add("UNSUPPORTED_QUALIFICATION_DECISION");
    }
    if record.documentary_coverage.len() != 8 || record.external_evidence_missing.len() != 6 {
        add("INCOMPLETE_COVERAGE_OR_UNRESOLVED_EVIDENCE");
    }
    if !record.safeguards.historical_append_only_intent
        || record.safeguards.git_branch_technically_immutable
        || !record.safeguards.synthetic_attestations_cannot_grant_act
        || !record.safeguards.all_passes_documentary_only
        || !record.safeguards.new_physical_evidence_requires_new_review
    {
        add("FREEZE_SAFEGUARD_INCONSISTENCY");
    }
    if record.prior != "../191/protocol.json"
        || record.phase_xiii_freeze != "../184/decision.json"
        || record.watermark != ".dlw"
    {
        add("PREDECESSOR_OR_WATERMARK_MISMATCH");
    }
    let reasons: Vec<String> = errors.into_iter().collect();
    FreezeAssessment {
        verdict: if reasons.is_empty() { "DOCUMENTARY_FREEZE_CONSISTENT" } else { "REJECT" }.to_string(),
        reasons,
        software_protocol_percent: if record.software_protocol_progress_percent == 100 { 100 } else { 0 },
        physical_qualification_percent: 0,
        operational_authority: "HOLD".to_owned(),
        physical_act_allowed: false,
    }
}
