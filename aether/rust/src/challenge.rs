//! AETHER-195-RS: signed challenge and acquisition receipt with replay ledger.
//! A valid signed challenge is documentary consistency, never proof of physical origin.
use crate::{sha256_hex, PublicJwk};
use chrono::DateTime;
use p256::ecdsa::{signature::Verifier, Signature};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeSet, HashSet};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Challenge {
    pub schema: String,
    pub challenge_id: String,
    pub nonce: String,
    pub device_serial: String,
    pub issuer_key_id: String,
    pub issued_utc: String,
    pub expires_utc: String,
    pub purpose: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaptureReceipt {
    pub schema: String,
    pub capture_id: String,
    pub device_serial: String,
    pub device_key_id: String,
    pub challenge_id: String,
    pub challenge_nonce: String,
    pub challenge_sha256: String,
    pub payload_sha256: String,
    pub payload_len: usize,
    pub captured_utc: String,
    pub calibration_sha256: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Acquisition {
    pub challenge: Challenge,
    pub challenge_signature_hex: String,
    pub receipt: CaptureReceipt,
    pub receipt_signature_hex: String,
    #[serde(with = "base64_bytes")]
    pub payload: Vec<u8>,
}
mod base64_bytes {
    use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
    use serde::{Deserialize, Deserializer, Serializer};
    pub fn serialize<S: Serializer>(bytes: &Vec<u8>, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&URL_SAFE_NO_PAD.encode(bytes))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<Vec<u8>, D::Error> {
        let value = String::deserialize(d)?;
        URL_SAFE_NO_PAD.decode(value).map_err(serde::de::Error::custom)
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReplayLedger {
    pub seen_challenges: HashSet<String>,
    pub seen_nonces: HashSet<String>,
    pub seen_captures: HashSet<String>,
    pub seen_payload_digests: HashSet<String>,
    /// A digest of an externally preserved previous ledger version.
    pub previous_ledger_sha256: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengePolicy {
    pub expected_device_serial: String,
    pub challenge_issuer_key_id: String,
    pub device_key_id: String,
    pub trusted_challenge_key: PublicJwk,
    pub trusted_device_key: PublicJwk,
    pub max_payload_bytes: usize,
    pub max_capture_lag_ms: i64,
    pub expected_calibration_sha256: String,
    pub review_utc: String,
    pub external_issuer_authenticated: bool,
    pub external_device_authenticated: bool,
    pub independent_calibration_authenticated: bool,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AcquisitionDecision {
    pub verdict: String,
    pub reasons: Vec<String>,
    pub challenge_signature_valid: bool,
    pub capture_signature_valid: bool,
    pub payload_sha256: String,
    /// Proposed append-only ledger entries. Commit externally only after review.
    pub proposed_challenge: Option<String>,
    pub proposed_nonce: Option<String>,
    pub proposed_capture: Option<String>,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}
fn canonical<T: Serialize>(record: &T) -> Vec<u8> {
    serde_json::to_vec(record).unwrap_or_default()
}
pub fn challenge_hash(c: &Challenge) -> String { sha256_hex(&canonical(c)) }
fn verify(jwk: &PublicJwk, sig_hex: &str, content: &[u8]) -> bool {
    let Some(key) = crate::verifying_key(jwk).ok() else { return false; };
    let Ok(bytes) = hex::decode(sig_hex) else { return false; };
    if bytes.len() != 64 { return false; }
    let Ok(signature) = Signature::from_slice(&bytes) else { return false; };
    key.verify(content, &signature).is_ok()
}
fn stamp(s: &str) -> Option<i64> {
    DateTime::parse_from_rfc3339(s).ok().map(|x| x.timestamp_millis())
}
pub fn assess_acquisition(a: &Acquisition, p: &ChallengePolicy, l: &ReplayLedger) -> AcquisitionDecision {
    let mut reasons = BTreeSet::new();
    let mut fail = |s: &str| { reasons.insert(s.to_owned()); };
    let c = &a.challenge; let r = &a.receipt;
    if c.schema != "AETHER-195/challenge-v1" || r.schema != "AETHER-195/receipt-v1" {
        fail("RECORD_SCHEMA_MISMATCH");
    }
    if c.purpose != "ORIGINAL_PHYSICAL_ACQUISITION" { fail("UNEXPECTED_CHALLENGE_PURPOSE"); }
    if c.device_serial != p.expected_device_serial || r.device_serial != p.expected_device_serial {
        fail("DEVICE_SERIAL_SUBSTITUTION");
    }
    if c.issuer_key_id != p.challenge_issuer_key_id || r.device_key_id != p.device_key_id {
        fail("SIGNER_IDENTITY_MISMATCH");
    }
    if c.challenge_id.is_empty() || c.nonce.is_empty()
        || r.challenge_id != c.challenge_id || r.challenge_nonce != c.nonce {
        fail("CHALLENGE_RECEIPT_BINDING_MISMATCH");
    }
    if r.capture_id.is_empty() { fail("MISSING_CAPTURE_ID"); }
    let computed_challenge_sha256 = challenge_hash(c);
    if r.challenge_sha256 != computed_challenge_sha256 { fail("CHALLENGE_HASH_MISMATCH"); }
    let computed_payload = sha256_hex(&a.payload);
    if a.payload.is_empty() || a.payload.len() > p.max_payload_bytes || p.max_payload_bytes == 0 {
        fail("EMPTY_OR_OVERSIZED_CAPTURE");
    }
    if r.payload_sha256 != computed_payload || r.payload_len != a.payload.len() {
        fail("PAYLOAD_INTEGRITY_MISMATCH");
    }
    if r.calibration_sha256 != p.expected_calibration_sha256
        || r.calibration_sha256.len() != 64
        || !r.calibration_sha256.bytes().all(|b| b.is_ascii_hexdigit()) {
        fail("CALIBRATION_BINDING_MISMATCH");
    }
    match (stamp(&c.issued_utc),stamp(&r.captured_utc),stamp(&c.expires_utc),stamp(&p.review_utc)) {
        (Some(start),Some(captured),Some(end),Some(now)) => {
            if start >= end || captured < start || captured > end || captured > now {
                fail("EXPIRED_FUTURE_OR_UNISSUED_CAPTURE");
            }
            if p.max_capture_lag_ms < 0 || captured.saturating_sub(start) > p.max_capture_lag_ms {
                fail("CAPTURE_LATENCY_EXCEEDED");
            }
        },
        _ => fail("INVALID_TIMESTAMP"),
    }
    if l.seen_challenges.contains(&c.challenge_id)
        || l.seen_nonces.contains(&format!("{}:{}", c.challenge_id, c.nonce))
        || l.seen_captures.contains(&r.capture_id)
        || l.seen_payload_digests.contains(&computed_payload) {
        fail("REPLAY_LEDGER_COLLISION");
    }
    if l.previous_ledger_sha256.len() != 64
        || !l.previous_ledger_sha256.bytes().all(|b| b.is_ascii_hexdigit()) {
        fail("MISSING_PREVIOUS_LEDGER_DIGEST");
    }
    let challenge_signature_valid = verify(&p.trusted_challenge_key, &a.challenge_signature_hex, &canonical(c));
    let capture_signature_valid = verify(&p.trusted_device_key, &a.receipt_signature_hex, &canonical(r));
    if !challenge_signature_valid { fail("CHALLENGE_SIGNATURE_INVALID"); }
    if !capture_signature_valid { fail("CAPTURE_SIGNATURE_INVALID"); }
    if !p.external_issuer_authenticated { fail("CHALLENGE_AUTHORITY_NOT_EXTERNALLY_VERIFIED"); }
    if !p.external_device_authenticated { fail("PHYSICAL_DEVICE_NOT_EXTERNALLY_VERIFIED"); }
    if !p.independent_calibration_authenticated { fail("CALIBRATION_NOT_INDEPENDENTLY_VERIFIED"); }
    let reasons: Vec<String> = reasons.into_iter().collect();
    let clean = reasons.is_empty();
    AcquisitionDecision {
        verdict: if clean { "DOCUMENTARY_ACQUISITION_ONLY" } else { "REJECT" }.into(),
        reasons, challenge_signature_valid, capture_signature_valid,
        payload_sha256: computed_payload,
        proposed_challenge: clean.then(|| c.challenge_id.clone()),
        proposed_nonce: clean.then(|| format!("{}:{}",c.challenge_id,c.nonce)),
        proposed_capture: clean.then(|| r.capture_id.clone()),
        physical_qualification_percent: 0, operational_authority: "HOLD".into(),
        physical_act_allowed: false,
    }
}
