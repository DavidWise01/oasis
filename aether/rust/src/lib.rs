//! AETHER-190 Rust port — blind replay, SHA-256, raw ECDSA P-256 signatures.
//! A software-only documentary verifier. Physical qualification always 0%; ACT HOLD.
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use chrono::DateTime;
use p256::ecdsa::{signature::Verifier, Signature, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeSet, HashMap, HashSet};

pub const BOUND: &str = "AETHER-190";
pub const OPERATIONAL_AUTHORITY: &str = "HOLD";

/// Ordered fields match AETHER-190 RECORD_FIELDS in verification.mjs.
/// Applicant-supplied names and origin assertions are intentionally excluded.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct BlindRecord {
    pub schema: String,
    pub trial_id: String,
    pub capture_id: String,
    pub challenge_id: String,
    pub challenge_nonce: String,
    pub capture_sha256: String,
    pub sample_count: u64,
    pub acquired_utc: String,
    pub source_handle: String,
    pub verification_handle: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaptureEntry {
    pub record: BlindRecord,
    #[serde(with = "bytes_as_base64")]
    pub bytes: Vec<u8>,
    pub signature_hex: String,
    /// Untrusted applicant assertions never affect the blinded assessment.
    #[serde(default)]
    pub applicant_name: Option<String>,
}

mod bytes_as_base64 {
    use super::*;
    use serde::{Deserializer, Serializer};
    pub fn serialize<S: Serializer>(value: &Vec<u8>, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_str(&URL_SAFE_NO_PAD.encode(value))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(deserializer: D) -> Result<Vec<u8>, D::Error> {
        let value = String::deserialize(deserializer)?;
        URL_SAFE_NO_PAD.decode(value).map_err(serde::de::Error::custom)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Packet {
    pub entries: Vec<CaptureEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PublicJwk {
    pub kty: String,
    pub crv: String,
    pub x: String,
    pub y: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SourceIdentity {
    pub authenticated: bool,
    pub root_id: String,
    pub operator_id: String,
    pub administrator_id: String,
    pub physical_source_ancestry: String,
    pub jwk: PublicJwk,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerifierIdentity {
    pub authenticated: bool,
    pub root_id: String,
    pub operator_id: String,
    pub administrator_id: String,
    pub physical_source_ancestry: String,
    pub capture_sha256: String,
    pub challenge_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Policy {
    pub expected_challenge_id: String,
    pub expected_sample_count: u64,
    pub external_source_registry: HashMap<String, SourceIdentity>,
    pub external_verifier_registry: HashMap<String, VerifierIdentity>,
    #[serde(default)]
    pub seen_nonce_keys: HashSet<String>,
    #[serde(default)]
    pub external_registries_out_of_band_authenticated: bool,
    #[serde(default)]
    pub real_hardware_origins_authenticated: bool,
    #[serde(default)]
    pub physical_replay_observation_authenticated: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaptureDiagnostic {
    pub capture_id: String,
    pub computed_sha256: String,
    pub signature_valid: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditResult {
    pub decision: String,
    pub reasons: Vec<String>,
    pub signed_capture_count: usize,
    pub review: Vec<CaptureDiagnostic>,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

pub fn canonical_record(record: &BlindRecord) -> Result<Vec<u8>, serde_json::Error> {
    serde_json::to_vec(record)
}

/// JWK EC P-256 public point (x, y) is the uncompressed SEC1 point 04||x||y.
pub fn verifying_key(jwk: &PublicJwk) -> Result<VerifyingKey, &'static str> {
    if jwk.kty != "EC" || jwk.crv != "P-256" {
        return Err("UNSUPPORTED_JWK_CURVE");
    }
    let x = URL_SAFE_NO_PAD.decode(&jwk.x).map_err(|_| "BAD_JWK_X")?;
    let y = URL_SAFE_NO_PAD.decode(&jwk.y).map_err(|_| "BAD_JWK_Y")?;
    if x.len() != 32 || y.len() != 32 {
        return Err("BAD_JWK_COORDINATE_LENGTH");
    }
    let mut sec1 = [0u8; 65];
    sec1[0] = 4;
    sec1[1..33].copy_from_slice(&x);
    sec1[33..65].copy_from_slice(&y);
    VerifyingKey::from_sec1_bytes(&sec1).map_err(|_| "INVALID_PUBLIC_POINT")
}

pub fn verify_capture_signature(record: &BlindRecord, sig_hex: &str, jwk: &PublicJwk) -> bool {
    let Ok(key) = verifying_key(jwk) else { return false; };
    let Ok(signature_bytes) = hex::decode(sig_hex) else { return false; };
    if signature_bytes.len() != 64 { return false; }
    let Ok(signature) = Signature::from_slice(&signature_bytes) else { return false; };
    let Ok(content) = canonical_record(record) else { return false; };
    key.verify(&content, &signature).is_ok()
}

/// Fail-closed structural screening. A documentary pass is *never* physical approval.
pub fn assess(packet: &Packet, policy: &Policy) -> AuditResult {
    let mut failures: BTreeSet<String> = BTreeSet::new();
    let mut add = |reason: &str| { failures.insert(reason.to_owned()); };
    let mut diagnostics = Vec::new();
    let mut signed_count = 0;
    if packet.entries.len() != 3 {
        add("THREE_BLINDED_CAPTURES_REQUIRED");
    }
    let mut nonces = HashSet::new();
    let mut captures = HashSet::new();
    let mut trials = HashSet::new();
    let mut roots = HashSet::new();
    let mut operators = HashSet::new();
    let mut admins = HashSet::new();
    let mut source_ancestries = HashSet::new();
    let mut verifier_ancestries = HashSet::new();
    for entry in &packet.entries {
        let record = &entry.record;
        if record.schema != "AETHER-190/capture-v1" { add("CAPTURE_SCHEMA_MISMATCH"); }
        if record.trial_id.is_empty() || !trials.insert(&record.trial_id) { add("DUPLICATE_TRIAL_ID"); }
        if record.capture_id.is_empty() || !captures.insert(&record.capture_id) { add("DUPLICATE_CAPTURE_ID"); }
        if record.challenge_id != policy.expected_challenge_id { add("CHALLENGE_ID_MISMATCH"); }
        if record.sample_count == 0 || record.sample_count != policy.expected_sample_count {
            add("SAMPLE_COUNT_MISMATCH");
        }
        if DateTime::parse_from_rfc3339(&record.acquired_utc).is_err() {
            add("INVALID_CAPTURE_TIME");
        }
        let nonce_key = format!("{}:{}", record.challenge_id, record.challenge_nonce);
        if record.challenge_nonce.is_empty()
            || !nonces.insert(nonce_key.clone())
            || policy.seen_nonce_keys.contains(&nonce_key)
        {
            add("CHALLENGE_NONCE_REPLAY");
        }
        let computed_sha256 = sha256_hex(&entry.bytes);
        if record.capture_sha256.len() != 64 || !record.capture_sha256.bytes().all(|b| b.is_ascii_hexdigit()) {
            add("MALFORMED_CAPTURE_HASH");
        }
        if computed_sha256 != record.capture_sha256 {
            add("RAW_CAPTURE_DIGEST_MISMATCH");
        }
        let Some(source) = policy.external_source_registry.get(&record.source_handle) else {
            add("MISSING_INDEPENDENT_REGISTRY_RECORD"); continue;
        };
        let Some(verifier) = policy.external_verifier_registry.get(&record.verification_handle) else {
            add("MISSING_INDEPENDENT_REGISTRY_RECORD"); continue;
        };
        if !source.authenticated || !verifier.authenticated {
            add("EXTERNAL_CREDENTIAL_UNAUTHENTICATED");
        }
        if source.root_id == verifier.root_id
            || source.operator_id == verifier.operator_id
            || source.administrator_id == verifier.administrator_id
        {
            add("SOURCE_VERIFIER_SHARED_CONTROL");
        }
        if !roots.insert(&source.root_id) { add("CROSS_CAPTURE_SHARED_ROOT"); }
        if !operators.insert(&source.operator_id) { add("CROSS_CAPTURE_SHARED_OPERATOR"); }
        if !admins.insert(&source.administrator_id) { add("CROSS_CAPTURE_SHARED_ADMIN"); }
        if !source_ancestries.insert(&source.physical_source_ancestry) {
            add("DUPLICATED_PHYSICAL_SOURCE_ANCESTRY");
        }
        if !verifier_ancestries.insert(&verifier.physical_source_ancestry) {
            add("REUSED_EXTERNAL_VERIFIER_ANCESTRY");
        }
        if source.physical_source_ancestry.is_empty() || verifier.physical_source_ancestry.is_empty() {
            add("MISSING_EXTERNAL_ANCESTRY");
        }
        if source.physical_source_ancestry == verifier.physical_source_ancestry {
            add("ROOT_ANCESTRY_COLLISION");
        }
        if verifier.capture_sha256 != record.capture_sha256
            || verifier.challenge_id != record.challenge_id
        {
            add("EXTERNAL_VERIFICATION_MISMATCH");
        }
        let valid = verify_capture_signature(record, &entry.signature_hex, &source.jwk);
        if !valid { add("CAPTURE_SIGNATURE_INVALID"); } else { signed_count += 1; }
        diagnostics.push(CaptureDiagnostic {
            capture_id: record.capture_id.clone(), computed_sha256, signature_valid: valid,
        });
    }
    if nonces.len() != 3 || captures.len() != 3 || trials.len() != 3 {
        add("THREE_UNIQUE_TRIALS_REQUIRED");
    }
    if roots.len() != 3 || operators.len() != 3 || admins.len() != 3 || source_ancestries.len() != 3 {
        add("THREE_DISTINCT_DECLARED_ROOTS_REQUIRED");
    }
    if !policy.external_registries_out_of_band_authenticated {
        add("REGISTRIES_NOT_OUT_OF_BAND_AUTHENTICATED");
    }
    if !policy.real_hardware_origins_authenticated {
        add("ORIGINAL_HARDWARE_NOT_AUTHENTICATED");
    }
    if !policy.physical_replay_observation_authenticated {
        add("PHYSICAL_REPLAY_NOT_AUTHENTICATED");
    }
    let reasons: Vec<String> = failures.into_iter().collect();
    AuditResult {
        decision: if reasons.is_empty() {
            "DOCUMENTARY_BLIND_REVIEW_ONLY".to_owned()
        } else { "REJECT".to_owned() },
        reasons,
        signed_capture_count: signed_count,
        review: diagnostics,
        physical_qualification_percent: 0,
        operational_authority: OPERATIONAL_AUTHORITY.to_owned(),
        physical_act_allowed: false,
    }
}

/// AETHER-191-RS: physical-response/alarm documentary evidence gate.
pub mod alarm;

/// AETHER-192-RS: fail-closed Phase XIV documentary qualification freeze.
pub mod freeze;

/// AETHER-193-RS: fail-closed original capture ingestion.
pub mod intake;

/// AETHER-194-RS: independently pinned manufacturer/calibration authority credentials.
pub mod credentials;

/// AETHER-195-RS: signed fresh acquisition challenge, receipt, and replay ledger.
pub mod challenge;

/// AETHER-196-RS: signed sender export and receiver custody receipt.
pub mod custody_export;

/// AETHER-197-RS: signed calibration uncertainty gate.
pub mod calibration;

/// AETHER-198-RS: blinded external verifier ancestry and digest gate.
pub mod blind_verifier;

/// AETHER-199-RS: dual-signed physical response and alarm observation screening.
pub mod physical_alarm;

/// AETHER-200-RS: fail-closed Phase XV documentary freeze.
pub mod phase_xv_freeze;

/// AETHER-201-RS: durable local append/recovery and replay detection.
pub mod durable_ledger;
