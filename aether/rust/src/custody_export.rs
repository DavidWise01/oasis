//! AETHER-196-RS — immutable-in-history custody export and separately countersigned holder receipt.
//! Cryptographic coherence does not establish actual physical possession or independent origin.
use crate::{sha256_hex, PublicJwk};
use chrono::DateTime;
use p256::ecdsa::{signature::Verifier, Signature};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeSet, HashSet};

pub const BOUND: &str = "AETHER-196";
pub const AUTHORITY: &str = "HOLD";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportManifest {
    pub schema: String,
    pub export_id: String,
    pub capture_id: String,
    pub challenge_id: String,
    pub payload_sha256: String,
    pub payload_length: usize,
    pub source_receipt_sha256: String,
    pub from_holder: String,
    pub to_holder: String,
    pub sender_key_id: String,
    pub custody_sequence: u64,
    pub previous_transfer_sha256: String,
    pub transfer_nonce: String,
    pub exported_utc: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HolderReceipt {
    pub schema: String,
    pub holder_receipt_id: String,
    pub export_id: String,
    pub manifest_sha256: String,
    pub capture_id: String,
    pub payload_sha256: String,
    pub receiving_holder: String,
    pub receiver_key_id: String,
    pub transfer_nonce: String,
    pub accepted_utc: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustodyExport {
    pub manifest: ExportManifest,
    pub sender_signature_hex: String,
    pub holder_receipt: HolderReceipt,
    pub receiver_signature_hex: String,
    #[serde(with = "base64_bytes")]
    pub original_bytes: Vec<u8>,
}
mod base64_bytes {
    use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
    use serde::{Deserialize, Deserializer, Serializer};
    pub fn serialize<S: Serializer>(bytes: &Vec<u8>, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_str(&URL_SAFE_NO_PAD.encode(bytes))
    }
    pub fn deserialize<'de, D: Deserializer<'de>>(deserializer: D) -> Result<Vec<u8>, D::Error> {
        let encoded = String::deserialize(deserializer)?;
        URL_SAFE_NO_PAD.decode(encoded).map_err(serde::de::Error::custom)
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustodianKey {
    pub custodian_id: String,
    pub key_id: String,
    pub jwk: PublicJwk,
    pub root_id: String,
    pub operator_id: String,
    pub administrator_id: String,
    pub externally_authenticated: bool,
    pub revoked: bool,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportPolicy {
    pub sender: CustodianKey,
    pub receiver: CustodianKey,
    pub expected_capture_id: String,
    pub expected_challenge_id: String,
    pub expected_source_receipt_sha256: String,
    pub expected_previous_transfer_sha256: String,
    pub expected_sequence: u64,
    pub expected_nonce: String,
    pub review_utc: String,
    pub max_transfer_latency_ms: i64,
    pub max_original_bytes: usize,
    #[serde(default)]
    pub seen_export_ids: HashSet<String>,
    #[serde(default)]
    pub seen_holder_receipt_ids: HashSet<String>,
    #[serde(default)]
    pub seen_transfer_nonces: HashSet<String>,
    #[serde(default)]
    pub physical_possession_independently_observed: bool,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportAssessment {
    pub verdict: String,
    pub reasons: Vec<String>,
    pub computed_payload_sha256: String,
    pub computed_manifest_sha256: String,
    pub sender_signature_valid: bool,
    pub receiver_signature_valid: bool,
    pub proposed_export_id: Option<String>,
    pub proposed_receipt_id: Option<String>,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}
pub fn canonical<T: Serialize>(record: &T) -> Vec<u8> {
    serde_json::to_vec(record).unwrap_or_default()
}
pub fn manifest_hash(m: &ExportManifest) -> String {
    sha256_hex(&canonical(m))
}
fn valid_hex_sha256(s: &str) -> bool {
    s.len() == 64 && s.bytes().all(|v| v.is_ascii_hexdigit())
}
fn signature_valid(record: &[u8], signature_hex: &str, jwk: &PublicJwk) -> bool {
    let Ok(key) = crate::verifying_key(jwk) else { return false };
    let Ok(bytes) = hex::decode(signature_hex) else { return false };
    let Ok(signature) = Signature::from_slice(&bytes) else { return false };
    key.verify(record, &signature).is_ok()
}
fn time(s: &str) -> Option<i64> {
    DateTime::parse_from_rfc3339(s).ok().map(|v| v.timestamp_millis())
}
pub fn assess_export(export: &CustodyExport, policy: &ExportPolicy) -> ExportAssessment {
    let mut reasons = BTreeSet::new();
    let mut fail = |s: &str| { reasons.insert(s.to_owned()); };
    let manifest = &export.manifest;
    let receipt = &export.holder_receipt;
    if manifest.schema != "AETHER-196/export-v1" || receipt.schema != "AETHER-196/holder-receipt-v1" {
        fail("SCHEMA_MISMATCH");
    }
    let computed_payload_sha256 = sha256_hex(&export.original_bytes);
    let computed_manifest_sha256 = manifest_hash(manifest);
    if export.original_bytes.is_empty() || policy.max_original_bytes == 0
        || export.original_bytes.len() > policy.max_original_bytes {
        fail("EMPTY_OR_OVERSIZED_ORIGINAL_BYTES");
    }
    if !valid_hex_sha256(&manifest.payload_sha256)
        || manifest.payload_sha256 != computed_payload_sha256
        || manifest.payload_length != export.original_bytes.len() {
        fail("ORIGINAL_CAPTURE_BYTES_MISMATCH");
    }
    if manifest.capture_id != policy.expected_capture_id
        || manifest.challenge_id != policy.expected_challenge_id
        || manifest.capture_id != receipt.capture_id {
        fail("ORIGINAL_CAPTURE_IDENTITY_MISMATCH");
    }
    if !valid_hex_sha256(&manifest.source_receipt_sha256)
        || manifest.source_receipt_sha256 != policy.expected_source_receipt_sha256 {
        fail("SOURCE_RECEIPT_DIGEST_MISMATCH");
    }
    if !valid_hex_sha256(&manifest.previous_transfer_sha256)
        || manifest.previous_transfer_sha256 != policy.expected_previous_transfer_sha256
        || manifest.custody_sequence != policy.expected_sequence {
        fail("CUSTODY_PREDECESSOR_OR_SEQUENCE_MISMATCH");
    }
    if manifest.transfer_nonce != policy.expected_nonce
        || receipt.transfer_nonce != manifest.transfer_nonce
        || manifest.transfer_nonce.is_empty() {
        fail("TRANSFER_NONCE_MISMATCH");
    }
    if receipt.export_id != manifest.export_id
        || receipt.capture_id != manifest.capture_id
        || receipt.payload_sha256 != manifest.payload_sha256
        || receipt.manifest_sha256 != computed_manifest_sha256 {
        fail("RECEIVER_ATTESTATION_NOT_BOUND_TO_EXPORT");
    }
    if manifest.from_holder != policy.sender.custodian_id
        || manifest.to_holder != policy.receiver.custodian_id
        || receipt.receiving_holder != policy.receiver.custodian_id
        || manifest.sender_key_id != policy.sender.key_id
        || receipt.receiver_key_id != policy.receiver.key_id {
        fail("CUSTODIAN_OR_KEY_BINDING_MISMATCH");
    }
    if policy.sender.custodian_id == policy.receiver.custodian_id
        || policy.sender.key_id == policy.receiver.key_id
        || policy.sender.root_id == policy.receiver.root_id
        || policy.sender.operator_id == policy.receiver.operator_id
        || policy.sender.administrator_id == policy.receiver.administrator_id {
        fail("SHARED_CUSTODIAN_CONTROL");
    }
    if policy.sender.root_id.is_empty() || policy.receiver.root_id.is_empty()
        || policy.sender.operator_id.is_empty() || policy.receiver.operator_id.is_empty()
        || policy.sender.administrator_id.is_empty() || policy.receiver.administrator_id.is_empty() {
        fail("MISSING_CUSTODIAN_ANCESTRY");
    }
    if policy.sender.revoked || policy.receiver.revoked {
        fail("REVOKED_CUSTODIAN_KEY");
    }
    if !policy.sender.externally_authenticated || !policy.receiver.externally_authenticated {
        fail("EXTERNAL_CUSTODIAN_IDENTITY_UNAUTHENTICATED");
    }
    if !policy.physical_possession_independently_observed {
        fail("PHYSICAL_RECEIVER_POSSESSION_UNOBSERVED");
    }
    if manifest.export_id.is_empty() || receipt.holder_receipt_id.is_empty()
        || policy.seen_export_ids.contains(&manifest.export_id)
        || policy.seen_holder_receipt_ids.contains(&receipt.holder_receipt_id)
        || policy.seen_transfer_nonces.contains(&manifest.transfer_nonce) {
        fail("CUSTODY_EXPORT_REPLAY");
    }
    match (time(&manifest.exported_utc), time(&receipt.accepted_utc), time(&policy.review_utc)) {
        (Some(exported), Some(accepted), Some(review)) => {
            if accepted < exported || accepted > review {
                fail("NONMONOTONIC_CUSTODY_TIME");
            }
            if policy.max_transfer_latency_ms < 0
                || accepted.saturating_sub(exported) > policy.max_transfer_latency_ms {
                fail("TRANSFER_LATENCY_EXCEEDED");
            }
        }
        _ => fail("INVALID_CUSTODY_TIME"),
    }
    let sender_signature_valid = signature_valid(&canonical(manifest), &export.sender_signature_hex, &policy.sender.jwk);
    let receiver_signature_valid = signature_valid(&canonical(receipt), &export.receiver_signature_hex, &policy.receiver.jwk);
    if !sender_signature_valid { fail("SENDER_SIGNATURE_INVALID"); }
    if !receiver_signature_valid { fail("RECEIVER_SIGNATURE_INVALID"); }
    let reasons: Vec<String> = reasons.into_iter().collect();
    let clean = reasons.is_empty();
    ExportAssessment {
        verdict: if clean { "DOCUMENTARY_CUSTODY_EXPORT_ONLY" } else { "REJECT" }.into(),
        reasons, computed_payload_sha256, computed_manifest_sha256,
        sender_signature_valid, receiver_signature_valid,
        proposed_export_id: clean.then(|| manifest.export_id.clone()),
        proposed_receipt_id: clean.then(|| receipt.holder_receipt_id.clone()),
        physical_qualification_percent: 0, operational_authority: AUTHORITY.into(),
        physical_act_allowed: false,
    }
}
