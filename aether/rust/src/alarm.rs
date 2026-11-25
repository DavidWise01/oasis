//! AETHER-191 — deterministic physical-response / alarm evidence screening.
//! Signed synthetic claims never qualify real hardware or authorize ACT.
use crate::{sha256_hex, verify_capture_signature, BlindRecord, PublicJwk};
use chrono::DateTime;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeSet, HashSet};

pub const BOUND: &str = "AETHER-191";
pub const AUTHORITY: &str = "HOLD";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResponseEvidence {
    pub capture: BlindRecord,
    #[serde(with = "base64_bytes")]
    pub raw_bytes: Vec<u8>,
    pub capture_signature_hex: String,
    pub capture_signer: PublicJwk,
    pub device_serial: String,
    pub instrument_serial: String,
    pub challenge_nonce: String,
    pub challenge_expires_utc: String,
    pub calibration_id: String,
    pub calibration_sha256: String,
    pub reference_root_id: String,
    pub device_root_id: String,
    pub observed_response_milliunits: i64,
    pub reference_response_milliunits: i64,
    pub tolerance_milliunits: u64,
    pub response_observed_utc: String,
    pub alarm_id: String,
    pub alarm_issued_utc: String,
    pub alarm_acknowledged_utc: String,
    pub alarm_capture_sha256: String,
    pub alarm_challenge_nonce: String,
    pub alarm_state: String,
}
mod base64_bytes {
    use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
    use serde::{Deserialize, Serializer, Deserializer};
    pub fn serialize<S: Serializer>(bytes: &Vec<u8>, ser: S) -> Result<S::Ok, S::Error> {
        ser.serialize_str(&URL_SAFE_NO_PAD.encode(bytes))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(de: D) -> Result<Vec<u8>, D::Error> {
        let text = String::deserialize(de)?;
        URL_SAFE_NO_PAD.decode(text).map_err(serde::de::Error::custom)
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlarmPolicy {
    pub expected_device_serial: String,
    pub expected_instrument_serial: String,
    pub expected_challenge_nonce: String,
    pub expected_calibration_sha256: String,
    pub expected_device_root_id: String,
    pub expected_reference_root_id: String,
    pub maximum_response_delay_ms: i64,
    pub maximum_alarm_delay_ms: i64,
    pub maximum_ack_delay_ms: i64,
    #[serde(default)]
    pub previously_seen_alarm_ids: HashSet<String>,
    #[serde(default)]
    pub previously_seen_capture_ids: HashSet<String>,
    #[serde(default)]
    pub independent_reference_authenticated: bool,
    #[serde(default)]
    pub original_hardware_response_authenticated: bool,
    #[serde(default)]
    pub physical_alarm_authenticated: bool,
    #[serde(default)]
    pub calibrated_clock_authenticated: bool,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlarmAudit {
    pub bound: String,
    pub decision: String,
    pub reasons: Vec<String>,
    pub capture_signature_valid: bool,
    pub computed_capture_sha256: String,
    pub absolute_response_error_milliunits: u64,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}
fn time(value: &str) -> Option<i64> {
    DateTime::parse_from_rfc3339(value).ok().map(|t| t.timestamp_millis())
}
pub fn assess_alarm(input: &ResponseEvidence, policy: &AlarmPolicy) -> AlarmAudit {
    let mut errors: BTreeSet<String> = BTreeSet::new();
    let mut add = |name: &str| { errors.insert(name.to_owned()); };
    if input.capture.schema != "AETHER-190/capture-v1" {
        add("INVALID_CAPTURE_SCHEMA");
    }
    let computed_capture_sha256 = sha256_hex(&input.raw_bytes);
    if input.raw_bytes.is_empty() {
        add("MISSING_ORIGINAL_CAPTURE_BYTES");
    }
    if input.capture.capture_sha256 != computed_capture_sha256 {
        add("CAPTURE_BYTES_MISMATCH");
    }
    let capture_signature_valid = verify_capture_signature(
        &input.capture, &input.capture_signature_hex, &input.capture_signer,
    );
    if !capture_signature_valid {
        add("CAPTURE_SIGNATURE_INVALID");
    }
    if input.device_serial != policy.expected_device_serial
        || input.instrument_serial != policy.expected_instrument_serial
    {
        add("DEVICE_OR_INSTRUMENT_SUBSTITUTED");
    }
    if input.challenge_nonce != policy.expected_challenge_nonce
        || input.capture.challenge_nonce != input.challenge_nonce
        || input.alarm_challenge_nonce != input.challenge_nonce
    {
        add("CHALLENGE_NONCE_MISMATCH");
    }
    if input.calibration_id.is_empty()
        || input.calibration_sha256 != policy.expected_calibration_sha256
        || !input.calibration_sha256.bytes().all(|b| b.is_ascii_hexdigit())
        || input.calibration_sha256.len() != 64
    {
        add("CALIBRATION_PROVENANCE_MISMATCH");
    }
    if input.device_root_id != policy.expected_device_root_id
        || input.reference_root_id != policy.expected_reference_root_id
        || input.device_root_id == input.reference_root_id
    {
        add("SHARED_OR_UNEXPECTED_PHYSICAL_ANCESTRY");
    }
    if input.alarm_capture_sha256 != input.capture.capture_sha256 {
        add("ALARM_CAPTURE_SUBSTITUTION");
    }
    if input.alarm_state != "ISSUED_AND_ACKNOWLEDGED" {
        add("ALARM_LIFECYCLE_INCOMPLETE");
    }
    if input.alarm_id.is_empty() || policy.previously_seen_alarm_ids.contains(&input.alarm_id) {
        add("ALARM_ID_MISSING_OR_REPLAYED");
    }
    if input.capture.capture_id.is_empty() || policy.previously_seen_capture_ids.contains(&input.capture.capture_id) {
        add("CAPTURE_ID_MISSING_OR_REPLAYED");
    }
    let error = input.observed_response_milliunits.abs_diff(input.reference_response_milliunits);
    if error > input.tolerance_milliunits {
        add("RESPONSE_OUTSIDE_TOLERANCE");
    }
    let sequence = [
        time(&input.capture.acquired_utc),
        time(&input.response_observed_utc),
        time(&input.alarm_issued_utc),
        time(&input.alarm_acknowledged_utc),
        time(&input.challenge_expires_utc),
    ];
    if let [Some(captured), Some(observed), Some(issued), Some(ack), Some(expires)] = sequence {
        if !(captured <= observed && observed <= issued && issued <= ack && captured <= expires) {
            add("NONMONOTONIC_RESPONSE_ALARM_TIMELINE");
        }
        if policy.maximum_response_delay_ms < 0
            || observed.saturating_sub(captured) > policy.maximum_response_delay_ms
        {
            add("RESPONSE_OBSERVATION_DELAY_EXCEEDED");
        }
        if policy.maximum_alarm_delay_ms < 0
            || issued.saturating_sub(observed) > policy.maximum_alarm_delay_ms
        {
            add("ALARM_ISSUANCE_DELAY_EXCEEDED");
        }
        if policy.maximum_ack_delay_ms < 0
            || ack.saturating_sub(issued) > policy.maximum_ack_delay_ms
        {
            add("ALARM_ACKNOWLEDGEMENT_DELAY_EXCEEDED");
        }
    } else {
        add("INVALID_RESPONSE_ALARM_TIME");
    }
    if !policy.independent_reference_authenticated {
        add("INDEPENDENT_REFERENCE_UNAUTHENTICATED");
    }
    if !policy.original_hardware_response_authenticated {
        add("ORIGINAL_HARDWARE_RESPONSE_UNAUTHENTICATED");
    }
    if !policy.physical_alarm_authenticated {
        add("PHYSICAL_ALARM_UNAUTHENTICATED");
    }
    if !policy.calibrated_clock_authenticated {
        add("CALIBRATED_PHYSICAL_CLOCK_UNAUTHENTICATED");
    }
    let reasons: Vec<String> = errors.into_iter().collect();
    AlarmAudit {
        bound: BOUND.to_owned(),
        decision: if reasons.is_empty() { "DOCUMENTARY_RESPONSE_ONLY" } else { "REJECT" }.into(),
        reasons, capture_signature_valid, computed_capture_sha256,
        absolute_response_error_milliunits: error,
        physical_qualification_percent: 0,
        operational_authority: AUTHORITY.to_owned(),
        physical_act_allowed: false,
    }
}
