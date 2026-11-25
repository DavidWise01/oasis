use aether_evidence::custody_export::*;
use aether_evidence::{sha256_hex, PublicJwk};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use p256::ecdsa::{signature::Signer, Signature, SigningKey};
use std::collections::HashSet;

fn key(seed: u8) -> SigningKey { SigningKey::from_slice(&[seed; 32]).unwrap() }
fn jwk(k: &SigningKey) -> PublicJwk {
    let p = k.verifying_key().to_encoded_point(false);
    let b = p.as_bytes();
    PublicJwk {
        kty: "EC".into(), crv: "P-256".into(),
        x: URL_SAFE_NO_PAD.encode(&b[1..33]),
        y: URL_SAFE_NO_PAD.encode(&b[33..65]),
    }
}
fn sign<T: serde::Serialize>(k: &SigningKey, record: &T) -> String {
    let signature: Signature = k.sign(&canonical(record));
    hex::encode(signature.to_bytes())
}
fn fixture() -> (CustodyExport, ExportPolicy) {
    let sender_key = key(21);
    let receiver_key = key(22);
    let original_bytes = b"AETHER-196 synthetic bytes, not actual physical acquisition".to_vec();
    let payload_sha256 = sha256_hex(&original_bytes);
    let manifest = ExportManifest {
        schema: "AETHER-196/export-v1".into(),
        export_id: "export-196".into(), capture_id: "capture-196".into(),
        challenge_id: "challenge-196".into(), payload_sha256: payload_sha256.clone(),
        payload_length: original_bytes.len(), source_receipt_sha256: "a".repeat(64),
        from_holder: "sender-196".into(), to_holder: "receiver-196".into(),
        sender_key_id: "sender-key-196".into(), custody_sequence: 1,
        previous_transfer_sha256: "0".repeat(64), transfer_nonce: "nonce-196".into(),
        exported_utc: "2026-11-25T14:00:00Z".into(),
    };
    let receipt = HolderReceipt {
        schema: "AETHER-196/holder-receipt-v1".into(),
        holder_receipt_id: "holder-receipt-196".into(),
        export_id: manifest.export_id.clone(), manifest_sha256: manifest_hash(&manifest),
        capture_id: manifest.capture_id.clone(), payload_sha256: payload_sha256.clone(),
        receiving_holder: "receiver-196".into(), receiver_key_id: "receiver-key-196".into(),
        transfer_nonce: manifest.transfer_nonce.clone(), accepted_utc: "2026-11-25T14:00:01Z".into(),
    };
    let export = CustodyExport {
        sender_signature_hex: sign(&sender_key, &manifest),
        receiver_signature_hex: sign(&receiver_key, &receipt),
        manifest, holder_receipt: receipt, original_bytes,
    };
    let sender = CustodianKey {
        custodian_id: "sender-196".into(), key_id: "sender-key-196".into(),
        jwk: jwk(&sender_key), root_id: "root-A".into(),
        operator_id: "operator-A".into(), administrator_id: "admin-A".into(),
        externally_authenticated: false, revoked: false,
    };
    let receiver = CustodianKey {
        custodian_id: "receiver-196".into(), key_id: "receiver-key-196".into(),
        jwk: jwk(&receiver_key), root_id: "root-B".into(),
        operator_id: "operator-B".into(), administrator_id: "admin-B".into(),
        externally_authenticated: false, revoked: false,
    };
    let policy = ExportPolicy {
        sender, receiver, expected_capture_id: "capture-196".into(),
        expected_challenge_id: "challenge-196".into(),
        expected_source_receipt_sha256: "a".repeat(64),
        expected_previous_transfer_sha256: "0".repeat(64),
        expected_sequence: 1, expected_nonce: "nonce-196".into(),
        review_utc: "2026-11-25T14:00:10Z".into(),
        max_transfer_latency_ms: 5000, max_original_bytes: 4096,
        seen_export_ids: HashSet::new(), seen_holder_receipt_ids: HashSet::new(),
        seen_transfer_nonces: HashSet::new(), physical_possession_independently_observed: false,
    };
    (export, policy)
}
fn rejects<F: FnOnce(&mut CustodyExport, &mut ExportPolicy)>(reason: &str, change: F) {
    let (mut e, mut p) = fixture(); change(&mut e, &mut p);
    let a = assess_export(&e, &p);
    assert!(a.reasons.iter().any(|r| r == reason), "missing {reason}: {:?}", a.reasons);
    assert_eq!(a.verdict, "REJECT");
    assert_eq!(a.operational_authority, "HOLD");
    assert_eq!(a.physical_qualification_percent, 0);
    assert!(!a.physical_act_allowed);
    assert!(a.proposed_export_id.is_none());
}
#[test] fn signed_baseline_rejects_unobserved_possession() {
    let (e,p) = fixture(); let a = assess_export(&e,&p);
    assert!(a.sender_signature_valid && a.receiver_signature_valid);
    assert!(a.reasons.contains(&"PHYSICAL_RECEIVER_POSSESSION_UNOBSERVED".into()));
    assert!(a.reasons.contains(&"EXTERNAL_CUSTODIAN_IDENTITY_UNAUTHENTICATED".into()));
}
#[test] fn asserted_trust_still_cannot_grant_act() {
    let (e,mut p) = fixture();
    p.sender.externally_authenticated = true;
    p.receiver.externally_authenticated = true;
    p.physical_possession_independently_observed = true;
    let a = assess_export(&e,&p);
    assert_eq!(a.verdict, "DOCUMENTARY_CUSTODY_EXPORT_ONLY");
    assert!(a.proposed_export_id.is_some() && a.proposed_receipt_id.is_some());
    assert_eq!(a.physical_qualification_percent, 0);
    assert_eq!(a.operational_authority, "HOLD");
    assert!(!a.physical_act_allowed);
}
#[test] fn original_bytes_round_trip() {
    let (e,_) = fixture();
    let json = serde_json::to_vec(&e).unwrap();
    let round: CustodyExport = serde_json::from_slice(&json).unwrap();
    assert_eq!(e.original_bytes,round.original_bytes);
}
#[test] fn altered_original_bytes() { rejects("ORIGINAL_CAPTURE_BYTES_MISMATCH", |e,_| e.original_bytes[0] ^= 1); }
#[test] fn absent_original_bytes() { rejects("EMPTY_OR_OVERSIZED_ORIGINAL_BYTES", |e,_| e.original_bytes.clear()); }
#[test] fn oversized_export() { rejects("EMPTY_OR_OVERSIZED_ORIGINAL_BYTES", |_,p| p.max_original_bytes=1); }
#[test] fn tampered_payload_length() { rejects("ORIGINAL_CAPTURE_BYTES_MISMATCH", |e,_| e.manifest.payload_length += 1); }
#[test] fn substituted_capture_id() { rejects("ORIGINAL_CAPTURE_IDENTITY_MISMATCH", |e,_| e.manifest.capture_id="fake".into()); }
#[test] fn substituted_challenge() { rejects("ORIGINAL_CAPTURE_IDENTITY_MISMATCH", |e,_| e.manifest.challenge_id="other".into()); }
#[test] fn substituted_original_receipt_digest() { rejects("SOURCE_RECEIPT_DIGEST_MISMATCH", |e,_| e.manifest.source_receipt_sha256="f".repeat(64)); }
#[test] fn substituted_predecessor() { rejects("CUSTODY_PREDECESSOR_OR_SEQUENCE_MISMATCH", |e,_| e.manifest.previous_transfer_sha256="b".repeat(64)); }
#[test] fn sequence_rollback() { rejects("CUSTODY_PREDECESSOR_OR_SEQUENCE_MISMATCH", |e,_| e.manifest.custody_sequence=0); }
#[test] fn nonce_mismatch() { rejects("TRANSFER_NONCE_MISMATCH", |e,_| e.manifest.transfer_nonce="wrong".into()); }
#[test] fn changed_receiver_manifest_hash() { rejects("RECEIVER_ATTESTATION_NOT_BOUND_TO_EXPORT", |e,_| e.holder_receipt.manifest_sha256="c".repeat(64)); }
#[test] fn receiver_capture_hash_swapped() { rejects("RECEIVER_ATTESTATION_NOT_BOUND_TO_EXPORT", |e,_| e.holder_receipt.payload_sha256="c".repeat(64)); }
#[test] fn receiver_swapped() { rejects("CUSTODIAN_OR_KEY_BINDING_MISMATCH", |e,_| e.holder_receipt.receiving_holder="impostor".into()); }
#[test] fn shared_source_and_receiver() { rejects("SHARED_CUSTODIAN_CONTROL", |_,p| p.receiver.custodian_id="sender-196".into()); }
#[test] fn shared_control_operator() { rejects("SHARED_CUSTODIAN_CONTROL", |_,p| p.receiver.operator_id="operator-A".into()); }
#[test] fn shared_admin() { rejects("SHARED_CUSTODIAN_CONTROL", |_,p| p.receiver.administrator_id="admin-A".into()); }
#[test] fn missing_ancestry() { rejects("MISSING_CUSTODIAN_ANCESTRY", |_,p| p.receiver.root_id.clear()); }
#[test] fn revoked_receiver() { rejects("REVOKED_CUSTODIAN_KEY", |_,p| p.receiver.revoked=true); }
#[test] fn untrusted_sender() { rejects("EXTERNAL_CUSTODIAN_IDENTITY_UNAUTHENTICATED", |_,_| {}); }
#[test] fn no_physical_possession() { rejects("PHYSICAL_RECEIVER_POSSESSION_UNOBSERVED", |_,_| {}); }
#[test] fn replayed_export() { rejects("CUSTODY_EXPORT_REPLAY", |e,p| {p.seen_export_ids.insert(e.manifest.export_id.clone());}); }
#[test] fn replayed_receipt() { rejects("CUSTODY_EXPORT_REPLAY", |e,p| {p.seen_holder_receipt_ids.insert(e.holder_receipt.holder_receipt_id.clone());}); }
#[test] fn replayed_nonce() { rejects("CUSTODY_EXPORT_REPLAY", |e,p| {p.seen_transfer_nonces.insert(e.manifest.transfer_nonce.clone());}); }
#[test] fn backwards_custody_time() { rejects("NONMONOTONIC_CUSTODY_TIME", |e,_| e.holder_receipt.accepted_utc="2026-11-25T13:59:00Z".into()); }
#[test] fn late_custody() { rejects("TRANSFER_LATENCY_EXCEEDED", |_,p| p.max_transfer_latency_ms=0); }
#[test] fn invalid_time() { rejects("INVALID_CUSTODY_TIME", |e,_| e.manifest.exported_utc="unknown".into()); }
#[test] fn forged_sender_signature() { rejects("SENDER_SIGNATURE_INVALID", |e,_| e.sender_signature_hex="00".repeat(64)); }
#[test] fn forged_receiver_signature() { rejects("RECEIVER_SIGNATURE_INVALID", |e,_| e.receiver_signature_hex="00".repeat(64)); }
#[test] fn invalid_schema() { rejects("SCHEMA_MISMATCH", |e,_| e.manifest.schema="unknown".into()); }
