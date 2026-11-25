use aether_evidence::*;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use p256::ecdsa::{signature::Signer, Signature, SigningKey};
use std::collections::{HashMap, HashSet};

fn signing_key(value: u8) -> SigningKey {
    SigningKey::from_slice(&[value; 32]).expect("deterministic synthetic test key")
}
fn public_jwk(key: &SigningKey) -> PublicJwk {
    let point = key.verifying_key().to_encoded_point(false);
    let bytes = point.as_bytes();
    PublicJwk {
        kty: "EC".into(), crv: "P-256".into(),
        x: URL_SAFE_NO_PAD.encode(&bytes[1..33]),
        y: URL_SAFE_NO_PAD.encode(&bytes[33..65]),
    }
}
fn sign(key: &SigningKey, record: &BlindRecord) -> String {
    let canonical = canonical_record(record).unwrap();
    let signature: Signature = key.sign(&canonical);
    hex::encode(signature.to_bytes())
}
fn fixture() -> (Packet, Policy) {
    let mut entries = Vec::new();
    let mut sources = HashMap::new();
    let mut verifiers = HashMap::new();
    for i in 0..3 {
        let key = signing_key(i + 1);
        let bytes = format!("AETHER-190 Rust synthetic capture {i}").into_bytes();
        let capture_sha256 = sha256_hex(&bytes);
        let record = BlindRecord {
            schema: "AETHER-190/capture-v1".into(),
            trial_id: format!("trial-{i}"),
            capture_id: format!("capture-{i}"),
            challenge_id: "CH-190".into(),
            challenge_nonce: format!("nonce-{i}"),
            capture_sha256: capture_sha256.clone(),
            sample_count: 4,
            acquired_utc: format!("2026-11-24T21:00:0{i}Z"),
            source_handle: format!("handle-{i}"),
            verification_handle: format!("verifier-{i}"),
        };
        let signature_hex = sign(&key, &record);
        entries.push(CaptureEntry { record, bytes, signature_hex, applicant_name: Some("UNTRUSTED NAME".into()) });
        sources.insert(format!("handle-{i}"), SourceIdentity {
            authenticated: true, root_id: format!("root-{i}"),
            operator_id: format!("operator-{i}"), administrator_id: format!("admin-{i}"),
            physical_source_ancestry: format!("source-{i}"), jwk: public_jwk(&key),
        });
        verifiers.insert(format!("verifier-{i}"), VerifierIdentity {
            authenticated: true, root_id: format!("verify-root-{i}"),
            operator_id: format!("verify-operator-{i}"), administrator_id: format!("verify-admin-{i}"),
            physical_source_ancestry: format!("verify-source-{i}"),
            capture_sha256, challenge_id: "CH-190".into(),
        });
    }
    let policy = Policy {
        expected_challenge_id: "CH-190".into(),
        expected_sample_count: 4, external_source_registry: sources,
        external_verifier_registry: verifiers, seen_nonce_keys: HashSet::new(),
        external_registries_out_of_band_authenticated: false,
        real_hardware_origins_authenticated: false,
        physical_replay_observation_authenticated: false,
    };
    (Packet { entries }, policy)
}
fn reject_for<F: FnOnce(&mut Packet, &mut Policy)>(name: &str, reason: &str, modify: F) {
    let (mut packet, mut policy) = fixture();
    modify(&mut packet, &mut policy);
    let result = assess(&packet, &policy);
    assert!(result.reasons.iter().any(|r| r == reason), "{name}: {:?}", result.reasons);
    assert_eq!(result.decision, "REJECT");
    assert_eq!(result.operational_authority, "HOLD");
    assert_eq!(result.physical_qualification_percent, 0);
    assert!(!result.physical_act_allowed);
}
#[test]
fn baseline_checks_actual_signatures_and_fails_closed() {
    let (packet, policy) = fixture();
    let result = assess(&packet, &policy);
    assert_eq!(result.signed_capture_count, 3);
    assert!(result.reasons.contains(&"REGISTRIES_NOT_OUT_OF_BAND_AUTHENTICATED".into()));
    assert!(result.reasons.contains(&"ORIGINAL_HARDWARE_NOT_AUTHENTICATED".into()));
    assert_eq!(result.operational_authority, "HOLD");
    assert!(!result.physical_act_allowed);
}
#[test]
fn no_physical_act_even_with_mock_trust_flags() {
    let (packet, mut policy) = fixture();
    policy.external_registries_out_of_band_authenticated = true;
    policy.real_hardware_origins_authenticated = true;
    policy.physical_replay_observation_authenticated = true;
    let result = assess(&packet, &policy);
    assert_eq!(result.decision, "DOCUMENTARY_BLIND_REVIEW_ONLY");
    assert_eq!(result.physical_qualification_percent, 0);
    assert_eq!(result.operational_authority, "HOLD");
    assert!(!result.physical_act_allowed);
}
#[test]
fn applicant_identity_is_excluded_from_signed_canonical_form() {
    let (packet, _) = fixture();
    let bytes = canonical_record(&packet.entries[0].record).unwrap();
    let rendered = String::from_utf8(bytes).unwrap();
    assert!(!rendered.contains("UNTRUSTED NAME"));
}
#[test]
fn roundtrip_packet_base64_and_policy_json() {
    let (packet, policy) = fixture();
    let serial = serde_json::to_string(&packet).unwrap();
    let restored: Packet = serde_json::from_str(&serial).unwrap();
    assert_eq!(packet.entries[0].bytes, restored.entries[0].bytes);
    let serial = serde_json::to_string(&policy).unwrap();
    let restored: Policy = serde_json::from_str(&serial).unwrap();
    assert_eq!(assess(&packet, &restored).signed_capture_count, 3);
}
#[test]
fn bytes_tamper_is_detected() {
    reject_for("bytes", "RAW_CAPTURE_DIGEST_MISMATCH", |p, _| p.entries[1].bytes[0] ^= 1);
}
#[test]
fn signature_forgery_is_detected() {
    reject_for("signature", "CAPTURE_SIGNATURE_INVALID", |p, _| p.entries[1].signature_hex = "00".repeat(64));
}
#[test]
fn capture_id_replay_is_detected() {
    reject_for("duplicate capture", "DUPLICATE_CAPTURE_ID", |p, _| p.entries[1].record.capture_id = "capture-0".into());
}
#[test]
fn trial_id_replay_is_detected() {
    reject_for("duplicate trial", "DUPLICATE_TRIAL_ID", |p, _| p.entries[1].record.trial_id = "trial-0".into());
}
#[test]
fn challenge_nonce_replay_is_detected() {
    reject_for("duplicate nonce", "CHALLENGE_NONCE_REPLAY", |p, _| p.entries[1].record.challenge_nonce = "nonce-0".into());
}
#[test]
fn previously_seen_nonce_is_detected() {
    reject_for("historical nonce", "CHALLENGE_NONCE_REPLAY", |_, c| { c.seen_nonce_keys.insert("CH-190:nonce-1".into()); });
}
#[test]
fn shared_source_ancestry_is_detected() {
    reject_for("shared ancestry", "DUPLICATED_PHYSICAL_SOURCE_ANCESTRY", |_, c| c.external_source_registry.get_mut("handle-1").unwrap().physical_source_ancestry = "source-0".into());
}
#[test]
fn shared_root_is_detected() {
    reject_for("shared root", "CROSS_CAPTURE_SHARED_ROOT", |_, c| c.external_source_registry.get_mut("handle-1").unwrap().root_id = "root-0".into());
}
#[test]
fn shared_operator_is_detected() {
    reject_for("shared operator", "CROSS_CAPTURE_SHARED_OPERATOR", |_, c| c.external_source_registry.get_mut("handle-1").unwrap().operator_id = "operator-0".into());
}
#[test]
fn shared_administrator_is_detected() {
    reject_for("shared admin", "CROSS_CAPTURE_SHARED_ADMIN", |_, c| c.external_source_registry.get_mut("handle-1").unwrap().administrator_id = "admin-0".into());
}
#[test]
fn source_verifier_shared_control_is_detected() {
    reject_for("shared source verifier", "SOURCE_VERIFIER_SHARED_CONTROL", |_, c| c.external_verifier_registry.get_mut("verifier-1").unwrap().operator_id = "operator-1".into());
}
#[test]
fn external_verifier_digest_substitution_is_detected() {
    reject_for("verifier altered hash", "EXTERNAL_VERIFICATION_MISMATCH", |_, c| c.external_verifier_registry.get_mut("verifier-1").unwrap().capture_sha256 = "f".repeat(64));
}
#[test]
fn missing_external_root_is_detected() {
    reject_for("missing source", "MISSING_INDEPENDENT_REGISTRY_RECORD", |_, c| { c.external_source_registry.remove("handle-1"); });
}
#[test]
fn unauthenticated_external_root_is_detected() {
    reject_for("unauthenticated", "EXTERNAL_CREDENTIAL_UNAUTHENTICATED", |_, c| c.external_source_registry.get_mut("handle-1").unwrap().authenticated = false);
}
#[test]
fn sample_count_substitution_is_detected() {
    reject_for("samples", "SAMPLE_COUNT_MISMATCH", |p, _| p.entries[1].record.sample_count = 8);
}
#[test]
fn invalid_date_is_detected() {
    reject_for("date", "INVALID_CAPTURE_TIME", |p, _| p.entries[1].record.acquired_utc = "yesterday".into());
}
#[test]
fn three_captures_are_required() {
    reject_for("missing capture", "THREE_BLINDED_CAPTURES_REQUIRED", |p, _| { p.entries.pop(); });
}
#[test]
fn unsupported_jwk_curve_does_not_verify() {
    reject_for("curve", "CAPTURE_SIGNATURE_INVALID", |_, c| c.external_source_registry.get_mut("handle-1").unwrap().jwk.crv = "P-384".into());
}
#[test]
fn invalid_json_record_field_is_rejected_not_promoted() {
    reject_for("schema", "CAPTURE_SCHEMA_MISMATCH", |p, _| p.entries[1].record.schema = "OTHER".into());
}
