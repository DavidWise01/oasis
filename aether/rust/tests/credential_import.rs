use aether_evidence::credentials::*;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use p256::ecdsa::{signature::Signer, Signature, SigningKey};
use std::collections::HashSet;

fn key(seed: u8) -> SigningKey { SigningKey::from_slice(&[seed; 32]).unwrap() }
fn public(k: &SigningKey) -> PublicJwk {
    let p = k.verifying_key().to_encoded_point(false);
    let b = p.as_bytes();
    PublicJwk { kty: "EC".into(), crv: "P-256".into(),
        x: URL_SAFE_NO_PAD.encode(&b[1..33]), y: URL_SAFE_NO_PAD.encode(&b[33..65]) }
}
fn signed(c: Credential, issuer: &SigningKey) -> SignedCredential {
    let sig: Signature = issuer.sign(&canonical_credential(&c));
    SignedCredential { credential: c, signature_hex: hex::encode(sig.to_bytes()) }
}
fn fixture() -> (CredentialImport, ImportPolicy) {
    let mk = key(11); let ck = key(12); let device_key = key(13); let calibrator_key = key(14);
    let mroot = public(&mk); let croot = public(&ck);
    let ma = Anchor { anchor_id: "manufacturer-root".into(), pinned_sha256: root_fingerprint(&mroot),
        jwk: mroot.clone(), ancestry_id: "manufacturer-origin".into(),
        operator_id: "manufacturer-operator".into(), externally_authenticated: false };
    let ca = Anchor { anchor_id: "calibration-root".into(), pinned_sha256: root_fingerprint(&croot),
        jwk: croot.clone(), ancestry_id: "calibration-origin".into(),
        operator_id: "calibration-operator".into(), externally_authenticated: false };
    let cert = |serial: &str, issuer: &str, subject: &str, role: &str, org: &str, use_name: &str, key: &SigningKey| Credential {
        schema: "AETHER-194/credential-v1".into(), serial: serial.into(),
        issuer_anchor_id: issuer.into(), subject_id: subject.into(), role: role.into(),
        organization_id: org.into(), issued_utc: "2026-11-24T00:00:00Z".into(),
        expires_utc: "2026-11-27T00:00:00Z".into(),
        permissions: vec![use_name.into()], public_key: public(key),
    };
    let manufacturer_issuer = signed(cert("serial-M", "manufacturer-root", "DEVICE-194",
        "DEVICE_ISSUER", "MANUFACTURER", "SIGN_CAPTURE", &device_key), &mk);
    let calibration_authority = signed(cert("serial-C", "calibration-root", "CALIBRATOR-194",
        "CALIBRATION_AUTHORITY", "CALIBRATION-LAB", "SIGN_CALIBRATION", &calibrator_key), &ck);
    let policy = ImportPolicy {
        expected_manufacturer_anchor_id: "manufacturer-root".into(),
        expected_calibration_anchor_id: "calibration-root".into(),
        expected_instrument_serial: "DEVICE-194".into(),
        expected_calibration_issuer_id: "CALIBRATOR-194".into(),
        manufacturer_root_pin: root_fingerprint(&mroot),
        calibration_root_pin: root_fingerprint(&croot),
        review_utc: "2026-11-25T14:00:00Z".into(),
        revoked_credential_serials: HashSet::new(), revoked_anchor_ids: HashSet::new(),
    };
    (CredentialImport { manufacturer_anchor: ma, calibration_anchor: ca,
        manufacturer_issuer, calibration_authority }, policy)
}
fn expect_reject<F: FnOnce(&mut CredentialImport, &mut ImportPolicy)>(reason: &str, edit: F) {
    let (mut input, mut policy) = fixture(); edit(&mut input, &mut policy);
    let r = assess_credentials(&input, &policy);
    assert!(r.reasons.iter().any(|s| s == reason), "expected {reason}: {:?}", r.reasons);
    assert_eq!(r.decision, "REJECT");
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn signed_synthetic_anchors_still_untrusted() {
    let (v, p) = fixture(); let r = assess_credentials(&v, &p);
    assert!(r.manufacturer_signature_valid && r.calibration_signature_valid);
    assert!(r.reasons.contains(&"MANUFACTURER_ROOT_NOT_EXTERNALLY_AUTHENTICATED".into()));
    assert!(r.reasons.contains(&"CALIBRATION_ROOT_NOT_EXTERNALLY_AUTHENTICATED".into()));
    assert!(!r.physical_act_allowed);
}
#[test] fn forged_authentication_flags_never_enable_act() {
    let (mut v, p) = fixture();
    v.manufacturer_anchor.externally_authenticated = true;
    v.calibration_anchor.externally_authenticated = true;
    let r = assess_credentials(&v, &p);
    assert_eq!(r.decision, "DOCUMENTARY_CREDENTIAL_IMPORT_ONLY");
    assert_eq!(r.physical_qualification_percent, 0);
    assert_eq!(r.operational_authority, "HOLD");
    assert!(!r.physical_act_allowed);
}
#[test] fn import_json_roundtrip() {
    let (v, p) = fixture();
    let round: CredentialImport = serde_json::from_slice(&serde_json::to_vec(&v).unwrap()).unwrap();
    assert_eq!(assess_credentials(&round, &p).manufacturer_signature_valid, true);
}
#[test] fn bad_manufacturer_pin() { expect_reject("MANUFACTURER_PIN_MISMATCH", |_, p| p.manufacturer_root_pin = "0".repeat(64)); }
#[test] fn bad_calibration_pin() { expect_reject("CALIBRATION_PIN_MISMATCH", |_, p| p.calibration_root_pin = "0".repeat(64)); }
#[test] fn untrusted_manufacturer_root() { expect_reject("MANUFACTURER_ROOT_NOT_EXTERNALLY_AUTHENTICATED", |_, _| {}); }
#[test] fn untrusted_calibration_root() { expect_reject("CALIBRATION_ROOT_NOT_EXTERNALLY_AUTHENTICATED", |_, _| {}); }
#[test] fn shared_root_id() { expect_reject("SHARED_ANCHOR_CONTROL", |v, _| v.calibration_anchor.anchor_id = "manufacturer-root".into()); }
#[test] fn shared_control_operator() { expect_reject("SHARED_ANCHOR_CONTROL", |v, _| v.calibration_anchor.operator_id = "manufacturer-operator".into()); }
#[test] fn missing_ancestry() { expect_reject("MISSING_ANCHOR_ANCESTRY", |v, _| v.calibration_anchor.ancestry_id.clear()); }
#[test] fn wrong_root_identity() { expect_reject("UNEXPECTED_ANCHOR_ID", |v, _| v.manufacturer_anchor.anchor_id = "fake".into()); }
#[test] fn revoked_anchor() { expect_reject("REVOKED_TRUST_ANCHOR", |_, p| { p.revoked_anchor_ids.insert("manufacturer-root".into()); }); }
#[test] fn revoked_credential() { expect_reject("REVOKED_CREDENTIAL", |_, p| { p.revoked_credential_serials.insert("serial-M".into()); }); }
#[test] fn tamper_manufacturer_cert() { expect_reject("MANUFACTURER_SIGNATURE_INVALID", |v, _| v.manufacturer_issuer.credential.organization_id = "other".into()); }
#[test] fn tamper_calibration_cert() { expect_reject("CALIBRATION_SIGNATURE_INVALID", |v, _| v.calibration_authority.credential.organization_id = "other".into()); }
#[test] fn fake_manufacturer_sig() { expect_reject("MANUFACTURER_SIGNATURE_INVALID", |v, _| v.manufacturer_issuer.signature_hex = "00".repeat(64)); }
#[test] fn fake_calibration_sig() { expect_reject("CALIBRATION_SIGNATURE_INVALID", |v, _| v.calibration_authority.signature_hex = "00".repeat(64)); }
#[test] fn self_issued_credential() { expect_reject("SELF_ISSUED_CREDENTIAL", |v, _| v.manufacturer_issuer.credential.subject_id = "manufacturer-root".into()); }
#[test] fn wrong_issuer_chain() { expect_reject("CREDENTIAL_ISSUER_MISMATCH", |v, _| v.calibration_authority.credential.issuer_anchor_id = "fake-root".into()); }
#[test] fn wrong_roles() { expect_reject("CREDENTIAL_ROLE_MISMATCH", |v, _| v.manufacturer_issuer.credential.role = "CERT_SIGN".into()); }
#[test] fn wrong_device_serial() { expect_reject("SUBJECT_IDENTITY_MISMATCH", |v, _| v.manufacturer_issuer.credential.subject_id = "OTHER-DEVICE".into()); }
#[test] fn same_organization() { expect_reject("ORGANIZATION_ANCESTRY_COLLISION", |v, _| v.calibration_authority.credential.organization_id = "MANUFACTURER".into()); }
#[test] fn missing_permission() { expect_reject("CERTIFICATE_USAGE_VIOLATION", |v, _| v.calibration_authority.credential.permissions.clear()); }
#[test] fn identical_serials() { expect_reject("DUPLICATE_OR_MISSING_CREDENTIAL_SERIAL", |v, _| v.calibration_authority.credential.serial = "serial-M".into()); }
#[test] fn expired_certificate() { expect_reject("EXPIRED_OR_NOT_YET_VALID_CREDENTIAL", |v, _| v.manufacturer_issuer.credential.expires_utc = "2026-11-24T01:00:00Z".into()); }
#[test] fn bad_time() { expect_reject("INVALID_CREDENTIAL_TIME", |v, _| v.calibration_authority.credential.issued_utc = "INVALID".into()); }
#[test] fn invalid_public_key() { expect_reject("INVALID_SUBJECT_PUBLIC_KEY", |v, _| v.manufacturer_issuer.credential.public_key.crv = "P-384".into()); }
#[test] fn wrong_schema() { expect_reject("CREDENTIAL_SCHEMA_MISMATCH", |v, _| v.manufacturer_issuer.credential.schema = "UNKNOWN".into()); }
