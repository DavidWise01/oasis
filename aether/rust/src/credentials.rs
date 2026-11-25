//! AETHER-194-RS — externally pinned manufacturer/calibration authority credential import.
//! Pin + signature integrity is documentary. No synthetic credential may enable physical ACT.
use crate::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use chrono::DateTime;
use p256::ecdsa::{signature::Verifier, Signature, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeSet, HashSet};

pub const BOUND: &str = "AETHER-194";
pub const HOLD: &str = "HOLD";

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Anchor {
    pub anchor_id: String,
    pub jwk: PublicJwk,
    pub pinned_sha256: String,
    pub ancestry_id: String,
    pub operator_id: String,
    pub externally_authenticated: bool,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Credential {
    pub schema: String,
    pub serial: String,
    pub issuer_anchor_id: String,
    pub subject_id: String,
    pub role: String,
    pub organization_id: String,
    pub issued_utc: String,
    pub expires_utc: String,
    pub permissions: Vec<String>,
    pub public_key: PublicJwk,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SignedCredential {
    pub credential: Credential,
    pub signature_hex: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CredentialImport {
    pub manufacturer_anchor: Anchor,
    pub calibration_anchor: Anchor,
    pub manufacturer_issuer: SignedCredential,
    pub calibration_authority: SignedCredential,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ImportPolicy {
    pub expected_manufacturer_anchor_id: String,
    pub expected_calibration_anchor_id: String,
    pub expected_instrument_serial: String,
    pub expected_calibration_issuer_id: String,
    pub manufacturer_root_pin: String,
    pub calibration_root_pin: String,
    pub review_utc: String,
    #[serde(default)]
    pub revoked_credential_serials: HashSet<String>,
    #[serde(default)]
    pub revoked_anchor_ids: HashSet<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ImportDecision {
    pub bound: String,
    pub decision: String,
    pub reasons: Vec<String>,
    pub manufacturer_signature_valid: bool,
    pub calibration_signature_valid: bool,
    pub physical_qualification_percent: u8,
    pub operational_authority: String,
    pub physical_act_allowed: bool,
}
fn key(jwk: &PublicJwk) -> Option<VerifyingKey> {
    if jwk.kty != "EC" || jwk.crv != "P-256" { return None; }
    let x = URL_SAFE_NO_PAD.decode(&jwk.x).ok()?;
    let y = URL_SAFE_NO_PAD.decode(&jwk.y).ok()?;
    if x.len() != 32 || y.len() != 32 { return None; }
    let mut sec1 = [0u8; 65];
    sec1[0] = 4;
    sec1[1..33].copy_from_slice(&x);
    sec1[33..].copy_from_slice(&y);
    VerifyingKey::from_sec1_bytes(&sec1).ok()
}
/// Fixed-key JSON serialization avoids map-key ambiguity within this custom protocol.
pub fn canonical_credential(c: &Credential) -> Vec<u8> {
    serde_json::to_vec(c).unwrap_or_default()
}
pub fn root_fingerprint(jwk: &PublicJwk) -> String {
    let raw = format!(r#"{{"kty":"{}","crv":"{}","x":"{}","y":"{}"}}"#, jwk.kty, jwk.crv, jwk.x, jwk.y);
    hex::encode(Sha256::digest(raw.as_bytes()))
}
fn signature_valid(c: &SignedCredential, root: &Anchor) -> bool {
    let Some(key) = key(&root.jwk) else { return false; };
    let Ok(raw) = hex::decode(&c.signature_hex) else { return false; };
    if raw.len() != 64 { return false; }
    let Ok(sig) = Signature::from_slice(&raw) else { return false; };
    key.verify(&canonical_credential(&c.credential), &sig).is_ok()
}
fn time(t: &str) -> Option<i64> { DateTime::parse_from_rfc3339(t).ok().map(|x| x.timestamp_millis()) }
pub fn assess_credentials(input: &CredentialImport, policy: &ImportPolicy) -> ImportDecision {
    let mut errors = BTreeSet::new();
    let mut add = |s: &str| { errors.insert(s.to_owned()); };
    let m = &input.manufacturer_issuer.credential;
    let c = &input.calibration_authority.credential;
    let ma = &input.manufacturer_anchor;
    let ca = &input.calibration_anchor;
    if ma.anchor_id != policy.expected_manufacturer_anchor_id ||
       ca.anchor_id != policy.expected_calibration_anchor_id { add("UNEXPECTED_ANCHOR_ID"); }
    if ma.anchor_id == ca.anchor_id || ma.ancestry_id == ca.ancestry_id ||
       ma.operator_id == ca.operator_id { add("SHARED_ANCHOR_CONTROL"); }
    if ma.ancestry_id.is_empty() || ca.ancestry_id.is_empty() ||
       ma.operator_id.is_empty() || ca.operator_id.is_empty() { add("MISSING_ANCHOR_ANCESTRY"); }
    let manufacturer_fingerprint = root_fingerprint(&ma.jwk);
    let calibration_fingerprint = root_fingerprint(&ca.jwk);
    if ma.pinned_sha256 != manufacturer_fingerprint ||
       policy.manufacturer_root_pin != manufacturer_fingerprint { add("MANUFACTURER_PIN_MISMATCH"); }
    if ca.pinned_sha256 != calibration_fingerprint ||
       policy.calibration_root_pin != calibration_fingerprint { add("CALIBRATION_PIN_MISMATCH"); }
    if !ma.externally_authenticated { add("MANUFACTURER_ROOT_NOT_EXTERNALLY_AUTHENTICATED"); }
    if !ca.externally_authenticated { add("CALIBRATION_ROOT_NOT_EXTERNALLY_AUTHENTICATED"); }
    if policy.revoked_anchor_ids.contains(&ma.anchor_id) ||
       policy.revoked_anchor_ids.contains(&ca.anchor_id) { add("REVOKED_TRUST_ANCHOR"); }
    if m.schema != "AETHER-194/credential-v1" || c.schema != "AETHER-194/credential-v1" {
        add("CREDENTIAL_SCHEMA_MISMATCH");
    }
    if m.issuer_anchor_id != ma.anchor_id || c.issuer_anchor_id != ca.anchor_id {
        add("CREDENTIAL_ISSUER_MISMATCH");
    }
    if m.subject_id == m.issuer_anchor_id || c.subject_id == c.issuer_anchor_id {
        add("SELF_ISSUED_CREDENTIAL");
    }
    if m.role != "DEVICE_ISSUER" || c.role != "CALIBRATION_AUTHORITY" {
        add("CREDENTIAL_ROLE_MISMATCH");
    }
    if m.subject_id != policy.expected_instrument_serial ||
       c.subject_id != policy.expected_calibration_issuer_id { add("SUBJECT_IDENTITY_MISMATCH"); }
    if m.organization_id.is_empty() || c.organization_id.is_empty() ||
       m.organization_id == c.organization_id { add("ORGANIZATION_ANCESTRY_COLLISION"); }
    if !m.permissions.iter().any(|p| p == "SIGN_CAPTURE") ||
       !c.permissions.iter().any(|p| p == "SIGN_CALIBRATION") { add("CERTIFICATE_USAGE_VIOLATION"); }
    if m.serial.is_empty() || c.serial.is_empty() || m.serial == c.serial {
        add("DUPLICATE_OR_MISSING_CREDENTIAL_SERIAL");
    }
    if policy.revoked_credential_serials.contains(&m.serial) ||
       policy.revoked_credential_serials.contains(&c.serial) { add("REVOKED_CREDENTIAL"); }
    if key(&m.public_key).is_none() || key(&c.public_key).is_none() { add("INVALID_SUBJECT_PUBLIC_KEY"); }
    let reviewed = time(&policy.review_utc);
    for cert in [m, c] {
        match (time(&cert.issued_utc), reviewed, time(&cert.expires_utc)) {
            (Some(from), Some(now), Some(to)) if from <= now && now <= to && from < to => {},
            (Some(_), Some(_), Some(_)) => add("EXPIRED_OR_NOT_YET_VALID_CREDENTIAL"),
            _ => add("INVALID_CREDENTIAL_TIME"),
        }
    }
    let manufacturer_signature_valid = signature_valid(&input.manufacturer_issuer, ma);
    let calibration_signature_valid = signature_valid(&input.calibration_authority, ca);
    if !manufacturer_signature_valid { add("MANUFACTURER_SIGNATURE_INVALID"); }
    if !calibration_signature_valid { add("CALIBRATION_SIGNATURE_INVALID"); }
    let reasons: Vec<String> = errors.into_iter().collect();
    ImportDecision {
        bound: BOUND.to_owned(),
        decision: if reasons.is_empty() { "DOCUMENTARY_CREDENTIAL_IMPORT_ONLY" } else { "REJECT" }.to_owned(),
        reasons, manufacturer_signature_valid, calibration_signature_valid,
        physical_qualification_percent: 0, operational_authority: HOLD.to_owned(), physical_act_allowed: false,
    }
}
