//! AETHER-193-RS — original evidence intake screening.
//! Supplied bytes and signed records are not independently authenticated physical evidence.
use crate::{sha256_hex, verify_capture_signature, BlindRecord, PublicJwk};
use chrono::DateTime;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

pub const BOUND: &str = "AETHER-193";
pub const AUTHORITY: &str = "HOLD";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Intake {
    pub capture: BlindRecord,
    #[serde(with = "base64_bytes")]
    pub original_bytes: Vec<u8>,
    pub capture_signature_hex: String,
    pub origin_device_serial: String,
    pub custodian_id: String,
    pub issuer_key_id: String,
    pub challenge_issued_utc: String,
    pub challenge_expiry_utc: String,
    pub calibration_id: String,
    pub calibration_sha256: String,
    pub declared_origin_root: String,
    pub declared_custodian_root: String,
}

mod base64_bytes {
    use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
    use serde::{Deserialize, Deserializer, Serializer};
    pub fn serialize<S: Serializer>(bytes: &Vec<u8>, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&URL_SAFE_NO_PAD.encode(bytes))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<Vec<u8>, D::Error> {
        let text = String::deserialize(d)?;
        URL_SAFE_NO_PAD.decode(&text).map_err(serde::de::Error::custom)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExternalIssuer {
    pub public_key: PublicJwk,
    pub device_serial: String,
    pub origin_root: String,
    pub custodian_root: String,
    pub revoked: bool,
    pub independent_registry_authenticated: bool,
    pub hardware_origin_authenticated: bool,
    pub custody_physically_observed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntakePolicy {
    pub expected_device_serial: String,
    pub expected_challenge_id: String,
    pub expected_nonce: String,
    pub expected_calibration_sha256: String,
    pub max_capture_bytes: usize,
    pub issuer_key_id: String,
    pub external_issuer: Option<ExternalIssuer>,
    #[serde(default)]
    pub seen_capture_ids: HashSet<String>,
    #[serde(default)]
    pub seen_nonce_keys: HashSet<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntakeAudit {
    pub bound: String,
    pub decision: String,
    pub reasons: Vec<String>,
    pub computed_capture_sha256: String,
    pub capture_signature_valid: bool,
    pub documentary_integrity_valid: bool,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}

fn parsed_time(s: &str) -> Option<i64> {
    DateTime::parse_from_rfc3339(s).ok().map(|v| v.timestamp_millis())
}

/// Single fail-closed intake evaluation; physical ACT is not an available output.
pub fn assess_intake(input: &Intake, policy: &IntakePolicy) -> IntakeAudit {
    let mut failures: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    let mut add = |reason: &str| { failures.insert(reason.to_owned()); };
    if input.capture.schema != "AETHER-190/capture-v1" {
        add("CAPTURE_SCHEMA_MISMATCH");
    }
    if input.original_bytes.is_empty() {
        add("ORIGINAL_BYTES_MISSING");
    }
    if input.original_bytes.len() > policy.max_capture_bytes || policy.max_capture_bytes == 0 {
        add("CAPTURE_SIZE_EXCEEDS_LIMIT");
    }
    let computed = sha256_hex(&input.original_bytes);
    if input.capture.capture_sha256 != computed {
        add("ORIGINAL_BYTES_HASH_MISMATCH");
    }
    if input.capture.sample_count == 0 {
        add("INVALID_SAMPLE_COUNT");
    }
    if input.capture.capture_id.is_empty()
        || policy.seen_capture_ids.contains(&input.capture.capture_id)
    {
        add("CAPTURE_REPLAY_OR_MISSING_ID");
    }
    if input.capture.challenge_id != policy.expected_challenge_id
        || input.capture.challenge_nonce != policy.expected_nonce
    {
        add("CHALLENGE_BINDING_MISMATCH");
    }
    let nonce_key = format!("{}:{}", input.capture.challenge_id, input.capture.challenge_nonce);
    if input.capture.challenge_nonce.is_empty() || policy.seen_nonce_keys.contains(&nonce_key) {
        add("CHALLENGE_NONCE_REPLAY");
    }
    if input.origin_device_serial != policy.expected_device_serial {
        add("DEVICE_SERIAL_MISMATCH");
    }
    if input.calibration_id.is_empty()
        || input.calibration_sha256 != policy.expected_calibration_sha256
        || input.calibration_sha256.len() != 64
        || !input.calibration_sha256.bytes().all(|b| b.is_ascii_hexdigit())
    {
        add("CALIBRATION_BINDING_MISMATCH");
    }
    if input.issuer_key_id != policy.issuer_key_id {
        add("ISSUER_KEY_ID_MISMATCH");
    }
    let issued = parsed_time(&input.challenge_issued_utc);
    let expired = parsed_time(&input.challenge_expiry_utc);
    let acquired = parsed_time(&input.capture.acquired_utc);
    match (issued, acquired, expired) {
        (Some(start), Some(capture), Some(end)) if start < end && start <= capture && capture <= end => {}
        (Some(_), Some(_), Some(_)) => add("CHALLENGE_EXPIRED_OR_NONMONOTONIC"),
        _ => add("INVALID_CAPTURE_TIME"),
    }
    if input.declared_origin_root.is_empty()
        || input.declared_custodian_root.is_empty()
        || input.declared_origin_root == input.declared_custodian_root
    {
        add("MISSING_OR_SHARED_CUSTODY_ANCESTRY");
    }
    let issuer = policy.external_issuer.as_ref();
    if issuer.is_none() {
        add("EXTERNAL_ISSUER_MISSING");
    }
    if let Some(issuer) = issuer {
        if issuer.revoked { add("ISSUER_REVOKED"); }
        if issuer.device_serial != input.origin_device_serial
            || issuer.origin_root != input.declared_origin_root
            || issuer.custodian_root != input.declared_custodian_root
        {
            add("EXTERNAL_ISSUER_ANCESTRY_MISMATCH");
        }
        if !issuer.independent_registry_authenticated { add("REGISTRY_NOT_EXTERNALLY_AUTHENTICATED"); }
        if !issuer.hardware_origin_authenticated { add("HARDWARE_ORIGIN_NOT_AUTHENTICATED"); }
        if !issuer.custody_physically_observed { add("PHYSICAL_CUSTODY_NOT_OBSERVED"); }
    }
    let signature_valid = issuer.is_some_and(|v| {
        verify_capture_signature(&input.capture, &input.capture_signature_hex, &v.public_key)
    });
    if !signature_valid {
        add("ORIGINAL_CAPTURE_SIGNATURE_INVALID");
    }
    let reasons: Vec<String> = failures.into_iter().collect();
    let documentary_valid = reasons.is_empty();
    IntakeAudit {
        bound: BOUND.to_owned(),
        decision: if documentary_valid { "DOCUMENTARY_INTAKE_ONLY" } else { "REJECT" }.to_owned(),
        reasons,
        computed_capture_sha256: computed,
        capture_signature_valid: signature_valid,
        documentary_integrity_valid: documentary_valid,
        physical_qualification_percent: 0,
        operational_authority: AUTHORITY.to_owned(),
        physical_act_allowed: false,
    }
}
