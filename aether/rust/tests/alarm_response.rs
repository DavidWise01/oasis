use aether_evidence::alarm::*;
use aether_evidence::{sha256_hex, BlindRecord, PublicJwk};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use p256::ecdsa::{signature::Signer, Signature, SigningKey};
use std::collections::HashSet;

fn key() -> SigningKey {
    SigningKey::from_slice(&[7u8; 32]).expect("synthetic test key")
}
fn public(key: &SigningKey) -> PublicJwk {
    let pt = key.verifying_key().to_encoded_point(false);
    let bytes = pt.as_bytes();
    PublicJwk {
        kty: "EC".into(), crv: "P-256".into(),
        x: URL_SAFE_NO_PAD.encode(&bytes[1..33]),
        y: URL_SAFE_NO_PAD.encode(&bytes[33..65]),
    }
}
fn fixture() -> (ResponseEvidence, AlarmPolicy) {
    let key = key();
    let bytes = b"synthetic physical response -- NO hardware".to_vec();
    let capture = BlindRecord {
        schema: "AETHER-190/capture-v1".into(),
        trial_id: "trial191".into(), capture_id: "capture191".into(),
        challenge_id: "challenge191".into(), challenge_nonce: "nonce191".into(),
        capture_sha256: sha256_hex(&bytes), sample_count: 3,
        acquired_utc: "2026-11-24T20:00:00Z".into(),
        source_handle: "source191".into(), verification_handle: "verifier191".into(),
    };
    let sig: Signature = key.sign(&serde_json::to_vec(&capture).unwrap());
    let input = ResponseEvidence {
        capture: capture.clone(), raw_bytes: bytes,
        capture_signature_hex: hex::encode(sig.to_bytes()), capture_signer: public(&key),
        device_serial: "DEV191".into(), instrument_serial: "REF191".into(),
        challenge_nonce: "nonce191".into(), challenge_expires_utc: "2026-11-24T20:02:00Z".into(),
        calibration_id: "CAL191".into(), calibration_sha256: "a".repeat(64),
        reference_root_id: "reference-root".into(), device_root_id: "device-root".into(),
        observed_response_milliunits: 995, reference_response_milliunits: 1000,
        tolerance_milliunits: 10, response_observed_utc: "2026-11-24T20:00:01Z".into(),
        alarm_id: "ALARM191".into(), alarm_issued_utc: "2026-11-24T20:00:02Z".into(),
        alarm_acknowledged_utc: "2026-11-24T20:00:03Z".into(),
        alarm_capture_sha256: capture.capture_sha256,
        alarm_challenge_nonce: "nonce191".into(),
        alarm_state: "ISSUED_AND_ACKNOWLEDGED".into(),
    };
    let policy = AlarmPolicy {
        expected_device_serial: "DEV191".into(), expected_instrument_serial: "REF191".into(),
        expected_challenge_nonce: "nonce191".into(), expected_calibration_sha256: "a".repeat(64),
        expected_device_root_id: "device-root".into(), expected_reference_root_id: "reference-root".into(),
        maximum_response_delay_ms: 5_000, maximum_alarm_delay_ms: 5_000, maximum_ack_delay_ms: 5_000,
        previously_seen_alarm_ids: HashSet::new(), previously_seen_capture_ids: HashSet::new(),
        independent_reference_authenticated: false, original_hardware_response_authenticated: false,
        physical_alarm_authenticated: false, calibrated_clock_authenticated: false,
    };
    (input, policy)
}
fn reject_for<F: FnOnce(&mut ResponseEvidence, &mut AlarmPolicy)>(reason: &str, change: F) {
    let (mut record, mut policy) = fixture();
    change(&mut record, &mut policy);
    let out = assess_alarm(&record, &policy);
    assert!(out.reasons.iter().any(|s| s == reason), "missing {reason}: {:?}", out.reasons);
    assert_eq!(out.decision, "REJECT");
    assert_eq!(out.operational_authority, "HOLD");
    assert!(!out.physical_act_allowed);
}
#[test]
fn synthetic_baseline_is_not_physical_qualification() {
    let (record, policy) = fixture();
    let r = assess_alarm(&record, &policy);
    assert!(r.capture_signature_valid);
    assert_eq!(r.absolute_response_error_milliunits, 5);
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test]
fn mock_authentication_flags_cannot_enable_act() {
    let (record, mut policy) = fixture();
    policy.independent_reference_authenticated = true;
    policy.original_hardware_response_authenticated = true;
    policy.physical_alarm_authenticated = true;
    policy.calibrated_clock_authenticated = true;
    let r = assess_alarm(&record, &policy);
    assert_eq!(r.decision, "DOCUMENTARY_RESPONSE_ONLY");
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn substituted_bytes() { reject_for("CAPTURE_BYTES_MISMATCH", |r, _| r.raw_bytes[0] ^= 1); }
#[test] fn forged_signature() { reject_for("CAPTURE_SIGNATURE_INVALID", |r, _| r.capture_signature_hex = "00".repeat(64)); }
#[test] fn different_device() { reject_for("DEVICE_OR_INSTRUMENT_SUBSTITUTED", |r, _| r.device_serial = "FAKE".into()); }
#[test] fn different_instrument() { reject_for("DEVICE_OR_INSTRUMENT_SUBSTITUTED", |r, _| r.instrument_serial = "FAKE".into()); }
#[test] fn nonce_substitution() { reject_for("CHALLENGE_NONCE_MISMATCH", |r, _| r.alarm_challenge_nonce = "REPLAY".into()); }
#[test] fn calibration_substitution() { reject_for("CALIBRATION_PROVENANCE_MISMATCH", |r, _| r.calibration_sha256 = "b".repeat(64)); }
#[test] fn same_root() { reject_for("SHARED_OR_UNEXPECTED_PHYSICAL_ANCESTRY", |r, _| r.reference_root_id = "device-root".into()); }
#[test] fn alarm_capture_substitution() { reject_for("ALARM_CAPTURE_SUBSTITUTION", |r, _| r.alarm_capture_sha256 = "b".repeat(64)); }
#[test] fn alarm_unacknowledged() { reject_for("ALARM_LIFECYCLE_INCOMPLETE", |r, _| r.alarm_state = "ISSUED".into()); }
#[test] fn alarm_replay() { reject_for("ALARM_ID_MISSING_OR_REPLAYED", |_, p| { p.previously_seen_alarm_ids.insert("ALARM191".into()); }); }
#[test] fn capture_replay() { reject_for("CAPTURE_ID_MISSING_OR_REPLAYED", |_, p| { p.previously_seen_capture_ids.insert("capture191".into()); }); }
#[test] fn response_outside_tolerance() { reject_for("RESPONSE_OUTSIDE_TOLERANCE", |r, _| r.observed_response_milliunits = 2000); }
#[test] fn response_before_capture() { reject_for("NONMONOTONIC_RESPONSE_ALARM_TIMELINE", |r, _| r.response_observed_utc = "2026-11-24T19:00:01Z".into()); }
#[test] fn alarm_before_response() { reject_for("NONMONOTONIC_RESPONSE_ALARM_TIMELINE", |r, _| r.alarm_issued_utc = "2026-11-24T19:00:00Z".into()); }
#[test] fn acknowledgement_before_alarm() { reject_for("NONMONOTONIC_RESPONSE_ALARM_TIMELINE", |r, _| r.alarm_acknowledged_utc = "2026-11-24T20:00:01Z".into()); }
#[test] fn expired_challenge() { reject_for("NONMONOTONIC_RESPONSE_ALARM_TIMELINE", |r, _| r.challenge_expires_utc = "2026-11-24T19:00:01Z".into()); }
#[test] fn response_delay() { reject_for("RESPONSE_OBSERVATION_DELAY_EXCEEDED", |_, p| p.maximum_response_delay_ms = 0); }
#[test] fn alarm_delay() { reject_for("ALARM_ISSUANCE_DELAY_EXCEEDED", |_, p| p.maximum_alarm_delay_ms = 0); }
#[test] fn ack_delay() { reject_for("ALARM_ACKNOWLEDGEMENT_DELAY_EXCEEDED", |_, p| p.maximum_ack_delay_ms = 0); }
#[test] fn malformed_timestamp() { reject_for("INVALID_RESPONSE_ALARM_TIME", |r, _| r.alarm_issued_utc = "bad".into()); }
#[test] fn absent_reference_authentication() { reject_for("INDEPENDENT_REFERENCE_UNAUTHENTICATED", |_, _| {}); }
#[test] fn absent_hardware_authentication() { reject_for("ORIGINAL_HARDWARE_RESPONSE_UNAUTHENTICATED", |_, _| {}); }
#[test] fn absent_physical_alarm_authentication() { reject_for("PHYSICAL_ALARM_UNAUTHENTICATED", |_, _| {}); }
#[test] fn absent_clock_authentication() { reject_for("CALIBRATED_PHYSICAL_CLOCK_UNAUTHENTICATED", |_, _| {}); }
#[test] fn empty_capture() { reject_for("MISSING_ORIGINAL_CAPTURE_BYTES", |r, _| r.raw_bytes.clear()); }
#[test] fn unknown_capture_schema() { reject_for("INVALID_CAPTURE_SCHEMA", |r, _| r.capture.schema = "invalid".into()); }
