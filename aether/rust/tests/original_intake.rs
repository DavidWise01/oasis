use aether_evidence::intake::{assess_intake, ExternalIssuer, Intake, IntakePolicy};
use aether_evidence::{sha256_hex, BlindRecord, PublicJwk};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use p256::ecdsa::{signature::Signer, Signature, SigningKey};
use std::collections::HashSet;

fn fixture() -> (Intake, IntakePolicy) {
    let key = SigningKey::from_slice(&[9u8; 32]).unwrap();
    let point = key.verifying_key().to_encoded_point(false);
    let raw = point.as_bytes();
    let jwk = PublicJwk {
        kty: "EC".into(), crv: "P-256".into(),
        x: URL_SAFE_NO_PAD.encode(&raw[1..33]),
        y: URL_SAFE_NO_PAD.encode(&raw[33..65]),
    };
    let bytes = b"AETHER-193 synthetic acquisition, not independently observed hardware".to_vec();
    let capture = BlindRecord {
        schema: "AETHER-190/capture-v1".into(),
        trial_id: "trial-193".into(), capture_id: "capture-193".into(),
        challenge_id: "CH-193".into(), challenge_nonce: "nonce-193".into(),
        capture_sha256: sha256_hex(&bytes), sample_count: 3,
        acquired_utc: "2026-11-25T14:00:01Z".into(),
        source_handle: "origin-193".into(), verification_handle: "verifier-193".into(),
    };
    let canonical = serde_json::to_vec(&capture).unwrap();
    let signature: Signature = key.sign(&canonical);
    let intake = Intake {
        capture, original_bytes: bytes,
        capture_signature_hex: hex::encode(signature.to_bytes()),
        origin_device_serial: "instrument-193".into(),
        custodian_id: "custodian-193".into(), issuer_key_id: "issuer-193".into(),
        challenge_issued_utc: "2026-11-25T14:00:00Z".into(),
        challenge_expiry_utc: "2026-11-25T14:01:00Z".into(),
        calibration_id: "cal-193".into(), calibration_sha256: "a".repeat(64),
        declared_origin_root: "origin-root-193".into(),
        declared_custodian_root: "custody-root-193".into(),
    };
    let policy = IntakePolicy {
        expected_device_serial: "instrument-193".into(),
        expected_challenge_id: "CH-193".into(),
        expected_nonce: "nonce-193".into(),
        expected_calibration_sha256: "a".repeat(64),
        max_capture_bytes: 4096, issuer_key_id: "issuer-193".into(),
        external_issuer: Some(ExternalIssuer {
            public_key: jwk, device_serial: "instrument-193".into(),
            origin_root: "origin-root-193".into(), custodian_root: "custody-root-193".into(),
            revoked: false, independent_registry_authenticated: false,
            hardware_origin_authenticated: false, custody_physically_observed: false,
        }),
        seen_capture_ids: HashSet::new(), seen_nonce_keys: HashSet::new(),
    };
    (intake, policy)
}
fn reject_for<F: FnOnce(&mut Intake, &mut IntakePolicy)>(reason: &str, edit: F) {
    let (mut intake, mut policy) = fixture(); edit(&mut intake, &mut policy);
    let result = assess_intake(&intake, &policy);
    assert!(result.reasons.iter().any(|x| x == reason), "missing {reason}: {:?}", result.reasons);
    assert_eq!(result.decision, "REJECT");
    assert!(!result.physical_act_allowed);
    assert_eq!(result.operational_authority, "HOLD");
    assert_eq!(result.physical_qualification_percent, 0);
}
#[test] fn baseline_has_real_crypto_but_not_real_hardware_proof() {
    let (intake, policy) = fixture();
    let r = assess_intake(&intake, &policy);
    assert!(r.capture_signature_valid);
    assert!(r.reasons.contains(&"REGISTRY_NOT_EXTERNALLY_AUTHENTICATED".into()));
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn all_mock_trust_flags_still_cannot_authorize_act() {
    let (intake, mut policy) = fixture();
    let source = policy.external_issuer.as_mut().unwrap();
    source.independent_registry_authenticated = true;
    source.hardware_origin_authenticated = true;
    source.custody_physically_observed = true;
    let r = assess_intake(&intake, &policy);
    assert_eq!(r.decision, "DOCUMENTARY_INTAKE_ONLY");
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn serialized_intake_roundtrips_raw_bytes() {
    let (intake, _) = fixture();
    let json = serde_json::to_vec(&intake).unwrap();
    let parsed: Intake = serde_json::from_slice(&json).unwrap();
    assert_eq!(intake.original_bytes, parsed.original_bytes);
}
#[test] fn tampered_capture_bytes() { reject_for("ORIGINAL_BYTES_HASH_MISMATCH", |i, _| i.original_bytes[0] ^= 1); }
#[test] fn missing_bytes() { reject_for("ORIGINAL_BYTES_MISSING", |i, _| i.original_bytes.clear()); }
#[test] fn oversized_bytes() { reject_for("CAPTURE_SIZE_EXCEEDS_LIMIT", |_, p| p.max_capture_bytes = 8); }
#[test] fn unknown_schema() { reject_for("CAPTURE_SCHEMA_MISMATCH", |i, _| i.capture.schema = "other".into()); }
#[test] fn sample_count_zero() { reject_for("INVALID_SAMPLE_COUNT", |i, _| i.capture.sample_count = 0); }
#[test] fn reused_capture() { reject_for("CAPTURE_REPLAY_OR_MISSING_ID", |_, p| { p.seen_capture_ids.insert("capture-193".into()); }); }
#[test] fn missing_capture_id() { reject_for("CAPTURE_REPLAY_OR_MISSING_ID", |i, _| i.capture.capture_id.clear()); }
#[test] fn challenge_swapped() { reject_for("CHALLENGE_BINDING_MISMATCH", |i, _| i.capture.challenge_id = "wrong".into()); }
#[test] fn nonce_swapped() { reject_for("CHALLENGE_BINDING_MISMATCH", |i, _| i.capture.challenge_nonce = "wrong".into()); }
#[test] fn nonce_replay() { reject_for("CHALLENGE_NONCE_REPLAY", |_, p| { p.seen_nonce_keys.insert("CH-193:nonce-193".into()); }); }
#[test] fn device_swapped() { reject_for("DEVICE_SERIAL_MISMATCH", |i, _| i.origin_device_serial = "other".into()); }
#[test] fn calibration_swapped() { reject_for("CALIBRATION_BINDING_MISMATCH", |i, _| i.calibration_sha256 = "b".repeat(64)); }
#[test] fn issuer_key_swapped() { reject_for("ISSUER_KEY_ID_MISMATCH", |i, _| i.issuer_key_id = "other".into()); }
#[test] fn challenge_expired() { reject_for("CHALLENGE_EXPIRED_OR_NONMONOTONIC", |i, _| i.challenge_expiry_utc = "2026-11-25T13:59:00Z".into()); }
#[test] fn bad_capture_time() { reject_for("INVALID_CAPTURE_TIME", |i, _| i.capture.acquired_utc = "invalid".into()); }
#[test] fn common_custody_root() { reject_for("MISSING_OR_SHARED_CUSTODY_ANCESTRY", |i, _| i.declared_custodian_root = "origin-root-193".into()); }
#[test] fn missing_external_issuer() { reject_for("EXTERNAL_ISSUER_MISSING", |_, p| p.external_issuer = None); }
#[test] fn revoked_issuer() { reject_for("ISSUER_REVOKED", |_, p| p.external_issuer.as_mut().unwrap().revoked = true); }
#[test] fn bad_issuer_ancestry() { reject_for("EXTERNAL_ISSUER_ANCESTRY_MISMATCH", |_, p| p.external_issuer.as_mut().unwrap().origin_root = "other".into()); }
#[test] fn forged_capture_signature() { reject_for("ORIGINAL_CAPTURE_SIGNATURE_INVALID", |i, _| i.capture_signature_hex = "00".repeat(64)); }
#[test] fn missing_registry_auth() { reject_for("REGISTRY_NOT_EXTERNALLY_AUTHENTICATED", |_, _| {}); }
#[test] fn missing_hardware_auth() { reject_for("HARDWARE_ORIGIN_NOT_AUTHENTICATED", |_, _| {}); }
#[test] fn missing_physical_custody() { reject_for("PHYSICAL_CUSTODY_NOT_OBSERVED", |_, _| {}); }
