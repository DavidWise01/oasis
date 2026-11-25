use aether_evidence::challenge::*;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use p256::ecdsa::{signature::Signer, Signature, SigningKey};
use std::collections::HashSet;

fn key(seed:u8)->SigningKey{SigningKey::from_slice(&[seed;32]).unwrap()}
fn jwk(k:&SigningKey)->PublicJwk{
 let e=k.verifying_key().to_encoded_point(false);let b=e.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),x:URL_SAFE_NO_PAD.encode(&b[1..33]),y:URL_SAFE_NO_PAD.encode(&b[33..65])}
}
fn signature<T:serde::Serialize>(key:&SigningKey,record:&T)->String{
 let sig:Signature=key.sign(&serde_json::to_vec(record).unwrap());hex::encode(sig.to_bytes())
}
fn fixture()->(Acquisition,ChallengePolicy,ReplayLedger){
 let authority=key(17);let device=key(19);
 let challenge=Challenge{
  schema:"AETHER-195/challenge-v1".into(),challenge_id:"challenge-195".into(),
  nonce:"nonce-195".into(),device_serial:"device-195".into(),issuer_key_id:"authority-195".into(),
  issued_utc:"2026-11-25T14:00:00Z".into(),expires_utc:"2026-11-25T14:01:00Z".into(),
  purpose:"ORIGINAL_PHYSICAL_ACQUISITION".into()
 };
 let payload=b"synthetic capture 195 -- not physical hardware".to_vec();
 let receipt=CaptureReceipt{
  schema:"AETHER-195/receipt-v1".into(),capture_id:"capture-195".into(),
  device_serial:"device-195".into(),device_key_id:"device-key-195".into(),
  challenge_id:challenge.challenge_id.clone(),challenge_nonce:challenge.nonce.clone(),
  challenge_sha256:challenge_hash(&challenge),payload_sha256:aether_evidence::sha256_hex(&payload),
  payload_len:payload.len(),captured_utc:"2026-11-25T14:00:01Z".into(),calibration_sha256:"a".repeat(64)
 };
 let acquisition=Acquisition{
  challenge_signature_hex:signature(&authority,&challenge),
  receipt_signature_hex:signature(&device,&receipt),challenge,receipt,payload
 };
 let policy=ChallengePolicy{
  expected_device_serial:"device-195".into(),challenge_issuer_key_id:"authority-195".into(),
  device_key_id:"device-key-195".into(),trusted_challenge_key:jwk(&authority),
  trusted_device_key:jwk(&device),max_payload_bytes:4096,max_capture_lag_ms:5000,
  expected_calibration_sha256:"a".repeat(64),review_utc:"2026-11-25T14:00:10Z".into(),
  external_issuer_authenticated:false,external_device_authenticated:false,
  independent_calibration_authenticated:false
 };
 let ledger=ReplayLedger{
  seen_challenges:HashSet::new(),seen_nonces:HashSet::new(),seen_captures:HashSet::new(),
  seen_payload_digests:HashSet::new(),previous_ledger_sha256:"0".repeat(64)
 };
 (acquisition,policy,ledger)
}
fn reject<F:FnOnce(&mut Acquisition,&mut ChallengePolicy,&mut ReplayLedger)>(expected:&str,mutate:F){
 let (mut a,mut p,mut l)=fixture();mutate(&mut a,&mut p,&mut l);
 let r=assess_acquisition(&a,&p,&l);
 assert!(r.reasons.iter().any(|s|s==expected),"missing {expected}: {:?}",r.reasons);
 assert_eq!(r.verdict,"REJECT");assert!(!r.physical_act_allowed);
 assert_eq!(r.operational_authority,"HOLD");assert_eq!(r.physical_qualification_percent,0);
 assert!(r.proposed_capture.is_none());
}
#[test] fn baseline_valid_signatures_not_physical_proof(){
 let (a,p,l)=fixture();let r=assess_acquisition(&a,&p,&l);
 assert!(r.challenge_signature_valid&&r.capture_signature_valid);
 assert!(r.reasons.contains(&"PHYSICAL_DEVICE_NOT_EXTERNALLY_VERIFIED".into()));
 assert_eq!(r.operational_authority,"HOLD");
}
#[test] fn mock_trust_flags_cannot_enable_act(){
 let (a,mut p,l)=fixture();p.external_issuer_authenticated=true;
 p.external_device_authenticated=true;p.independent_calibration_authenticated=true;
 let r=assess_acquisition(&a,&p,&l);
 assert_eq!(r.verdict,"DOCUMENTARY_ACQUISITION_ONLY");
 assert!(r.proposed_capture.is_some());assert!(!r.physical_act_allowed);
 assert_eq!(r.physical_qualification_percent,0);
}
#[test] fn json_capture_roundtrip(){
 let (a,_,_)=fixture();let data=serde_json::to_vec(&a).unwrap();
 let restored:Acquisition=serde_json::from_slice(&data).unwrap();assert_eq!(a.payload,restored.payload);
}
#[test] fn changed_payload(){reject("PAYLOAD_INTEGRITY_MISMATCH",|a,_,_|a.payload[0]^=1);}
#[test] fn missing_payload(){reject("EMPTY_OR_OVERSIZED_CAPTURE",|a,_,_|a.payload.clear());}
#[test] fn huge_payload(){reject("EMPTY_OR_OVERSIZED_CAPTURE",|_,p,_|p.max_payload_bytes=5);}
#[test] fn tampered_challenge(){reject("CHALLENGE_HASH_MISMATCH",|a,_,_|a.challenge.nonce="attack".into());}
#[test] fn swapped_capture_nonce(){reject("CHALLENGE_RECEIPT_BINDING_MISMATCH",|a,_,_|a.receipt.challenge_nonce="stale".into());}
#[test] fn substituted_device(){reject("DEVICE_SERIAL_SUBSTITUTION",|a,_,_|a.receipt.device_serial="other".into());}
#[test] fn wrong_issuer(){reject("SIGNER_IDENTITY_MISMATCH",|a,_,_|a.challenge.issuer_key_id="other".into());}
#[test] fn wrong_device_key(){reject("SIGNER_IDENTITY_MISMATCH",|a,_,_|a.receipt.device_key_id="other".into());}
#[test] fn replayed_challenge(){reject("REPLAY_LEDGER_COLLISION",|a,_,l|{l.seen_challenges.insert(a.challenge.challenge_id.clone());});}
#[test] fn replayed_nonce(){reject("REPLAY_LEDGER_COLLISION",|a,_,l|{l.seen_nonces.insert(format!("{}:{}",a.challenge.challenge_id,a.challenge.nonce));});}
#[test] fn replayed_capture(){reject("REPLAY_LEDGER_COLLISION",|a,_,l|{l.seen_captures.insert(a.receipt.capture_id.clone());});}
#[test] fn replayed_payload_digest(){reject("REPLAY_LEDGER_COLLISION",|a,_,l|{l.seen_payload_digests.insert(a.receipt.payload_sha256.clone());});}
#[test] fn absent_prior_ledger(){reject("MISSING_PREVIOUS_LEDGER_DIGEST",|_,_,l|l.previous_ledger_sha256.clear());}
#[test] fn expired_capture(){reject("EXPIRED_FUTURE_OR_UNISSUED_CAPTURE",|a,_,_|a.receipt.captured_utc="2026-11-25T14:03:00Z".into());}
#[test] fn future_capture(){reject("EXPIRED_FUTURE_OR_UNISSUED_CAPTURE",|a,_,_|a.receipt.captured_utc="2026-11-25T14:00:20Z".into());}
#[test] fn invalid_clock(){reject("INVALID_TIMESTAMP",|a,_,_|a.receipt.captured_utc="invalid".into());}
#[test] fn lateness(){reject("CAPTURE_LATENCY_EXCEEDED",|_,p,_|p.max_capture_lag_ms=0);}
#[test] fn forged_challenge_signature(){reject("CHALLENGE_SIGNATURE_INVALID",|a,_,_|a.challenge_signature_hex="00".repeat(64));}
#[test] fn forged_receipt_signature(){reject("CAPTURE_SIGNATURE_INVALID",|a,_,_|a.receipt_signature_hex="00".repeat(64));}
#[test] fn calibration_mismatch(){reject("CALIBRATION_BINDING_MISMATCH",|a,_,_|a.receipt.calibration_sha256="b".repeat(64));}
#[test] fn wrong_purpose(){reject("UNEXPECTED_CHALLENGE_PURPOSE",|a,_,_|a.challenge.purpose="OTHER".into());}
#[test] fn wrong_schema(){reject("RECORD_SCHEMA_MISMATCH",|a,_,_|a.receipt.schema="OTHER".into());}
#[test] fn absent_external_issuer(){reject("CHALLENGE_AUTHORITY_NOT_EXTERNALLY_VERIFIED",|_,_,_|{});}
#[test] fn absent_external_device(){reject("PHYSICAL_DEVICE_NOT_EXTERNALLY_VERIFIED",|_,_,_|{});}
#[test] fn absent_calibration(){reject("CALIBRATION_NOT_INDEPENDENTLY_VERIFIED",|_,_,_|{});}
