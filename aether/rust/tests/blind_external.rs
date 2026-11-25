use aether_evidence::blind_verifier::*;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::collections::HashSet;
fn fixture()->(Packet,Policy){
 let key=SigningKey::from_slice(&[31u8;32]).unwrap();
 let pt=key.verifying_key().to_encoded_point(false);let b=pt.as_bytes();
 let jwk=PublicJwk{kty:"EC".into(),crv:"P-256".into(),x:URL_SAFE_NO_PAD.encode(&b[1..33]),y:URL_SAFE_NO_PAD.encode(&b[33..65])};
 let e=Evidence{schema:"AETHER-198/evidence-v1".into(),review_id:"R198".into(),
 capture_id:"C198".into(),challenge_id:"CH198".into(),
 capture_sha256:"a".repeat(64),source_receipt_sha256:"b".repeat(64),
 custody_sha256:"c".repeat(64),calibration_sha256:"d".repeat(64),
 source_root:"S".into(),custody_root:"C".into(),calibration_root:"K".into(),
 verifier_root:"V".into(),source_operator:"OS".into(),verifier_operator:"OV".into(),
 source_admin:"AS".into(),verifier_admin:"AV".into()};
 let r=Review{schema:"AETHER-198/review-v1".into(),review_id:e.review_id.clone(),
 evidence_sha256:evidence_sha256(&e),nonce:"N198".into(),verdict:"DOCUMENTARY_MATCH".into()};
 let sig:Signature=key.sign(&canonical(&r));
 let packet=Packet{evidence:e,review:r,signature_hex:hex::encode(sig.to_bytes())};
 let policy=Policy{capture_sha256:"a".repeat(64),source_receipt_sha256:"b".repeat(64),
 custody_sha256:"c".repeat(64),calibration_sha256:"d".repeat(64),
 challenge_id:"CH198".into(),nonce:"N198".into(),verifier_public_key:jwk,
 source_authenticated:false,custody_authenticated:false,calibration_authenticated:false,
 verifier_authenticated:false,seen_reviews:HashSet::new(),seen_nonces:HashSet::new()};
 (packet,policy)
}
fn reject<F:FnOnce(&mut Packet,&mut Policy)>(reason:&str,f:F){
 let(mut a,mut p)=fixture();f(&mut a,&mut p);let r=assess(&a,&p);
 assert!(r.reasons.iter().any(|v|v==reason),"{reason}: {:?}",r.reasons);
 assert_eq!(r.verdict,"REJECT");assert!(!r.physical_act_allowed);
 assert_eq!(r.operational_authority,"HOLD");
}
#[test]fn baseline(){let(a,p)=fixture();let r=assess(&a,&p);assert!(r.signature_valid);assert_eq!(r.physical_qualification_percent,0);}
#[test]fn mock_flags_cannot_act(){let(a,mut p)=fixture();p.verifier_authenticated=true;p.source_authenticated=true;p.custody_authenticated=true;p.calibration_authenticated=true;let r=assess(&a,&p);assert_eq!(r.verdict,"DOCUMENTARY_BLIND_REVIEW_ONLY");assert!(!r.physical_act_allowed);}
#[test]fn json_roundtrip(){let(a,p)=fixture();let b=serde_json::to_vec(&a).unwrap();let a:Packet=serde_json::from_slice(&b).unwrap();assert!(assess(&a,&p).signature_valid);}
#[test]fn wrong_schema(){reject("SCHEMA_MISMATCH",|a,_|a.evidence.schema="other".into());}
#[test]fn evidence_mismatch(){reject("REVIEW_DIGEST_MISMATCH",|a,_|a.evidence.capture_id="other".into());}
#[test]fn review_id_mismatch(){reject("REVIEW_DIGEST_MISMATCH",|a,_|a.review.review_id="other".into());}
#[test]fn capture_hash(){reject("ORIGINAL_EVIDENCE_DIGEST_MISMATCH",|a,_|a.evidence.capture_sha256="e".repeat(64));}
#[test]fn receipt_hash(){reject("ORIGINAL_EVIDENCE_DIGEST_MISMATCH",|a,_|a.evidence.source_receipt_sha256="e".repeat(64));}
#[test]fn custody_hash(){reject("ORIGINAL_EVIDENCE_DIGEST_MISMATCH",|a,_|a.evidence.custody_sha256="e".repeat(64));}
#[test]fn calibration_hash(){reject("ORIGINAL_EVIDENCE_DIGEST_MISMATCH",|a,_|a.evidence.calibration_sha256="e".repeat(64));}
#[test]fn challenge(){reject("CAPTURE_CHALLENGE_MISMATCH",|a,_|a.evidence.challenge_id="other".into());}
#[test]fn review_nonce(){reject("REVIEW_NONCE_MISMATCH",|a,_|a.review.nonce="other".into());}
#[test]fn review_verdict(){reject("REVIEW_NOT_ACCEPTED",|a,_|a.review.verdict="NO".into());}
#[test]fn self_verifier(){reject("SHARED_VERIFIER_CONTROL",|a,_|a.evidence.verifier_root="S".into());}
#[test]fn shared_operator(){reject("SHARED_VERIFIER_CONTROL",|a,_|a.evidence.verifier_operator="OS".into());}
#[test]fn shared_admin(){reject("SHARED_VERIFIER_CONTROL",|a,_|a.evidence.verifier_admin="AS".into());}
#[test]fn shared_source(){reject("DUPLICATED_SOURCE_ANCESTRY",|a,_|a.evidence.custody_root="S".into());}
#[test]fn missing_ancestry(){reject("MISSING_ANCESTRY",|a,_|a.evidence.verifier_root.clear());}
#[test]fn replay_id(){reject("REPLAYED_EXTERNAL_REVIEW",|a,p|{p.seen_reviews.insert(a.evidence.review_id.clone());});}
#[test]fn replay_nonce(){reject("REPLAYED_EXTERNAL_REVIEW",|a,p|{p.seen_nonces.insert(a.review.nonce.clone());});}
#[test]fn forged_signature(){reject("VERIFIER_SIGNATURE_INVALID",|a,_|a.signature_hex="00".repeat(64));}
#[test]fn missing_verifier(){reject("EXTERNAL_VERIFIER_UNAUTHENTICATED",|_,_|{});}
#[test]fn missing_source(){reject("PHYSICAL_SOURCE_UNAUTHENTICATED",|_,_|{});}
#[test]fn missing_custody(){reject("CUSTODY_UNAUTHENTICATED",|_,_|{});}
#[test]fn missing_calibration(){reject("CALIBRATION_UNAUTHENTICATED",|_,_|{});}
