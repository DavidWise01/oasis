use aether_evidence::calibration::*;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::collections::HashSet;
fn fixture()->(SignedCalibration,Observation,Policy){
 let k=SigningKey::from_slice(&[27u8;32]).unwrap();
 let point=k.verifying_key().to_encoded_point(false);let b=point.as_bytes();
 let public=PublicJwk{kty:"EC".into(),crv:"P-256".into(),x:URL_SAFE_NO_PAD.encode(&b[1..33]),y:URL_SAFE_NO_PAD.encode(&b[33..65])};
 let record=Calibration{schema:"AETHER-197/calibration-v1".into(),id:"CAL197".into(),
 instrument:"DEV197".into(),reference:"REF197".into(),issuer:"ISS197".into(),
 reference_root:"ROOT-REF".into(),device_root:"ROOT-DEV".into(),trace_sha256:"a".repeat(64),
 valid_from:"2026-11-24T00:00:00Z".into(),valid_until:"2026-11-27T00:00:00Z".into(),
 uncertainty_nano:10,clock_offset_ns:1,clock_uncertainty_ns:2,drift_ppb:1000};
 let sig:Signature=k.sign(&canonical(&record));
 let signed=SignedCalibration{record,signature_hex:hex::encode(sig.to_bytes())};
 let o=Observation{capture_id:"CAP197".into(),capture_sha256:"b".repeat(64),calibration_id:"CAL197".into(),
 value_nano:1100,threshold_nano:1000,issued_utc:"2026-11-25T14:00:00Z".into(),
 measured_utc:"2026-11-25T14:00:01Z".into(),expires_utc:"2026-11-25T14:01:00Z".into(),elapsed_ns:1_000_000};
 let p=Policy{expected_instrument:"DEV197".into(),expected_reference:"REF197".into(),
 expected_issuer:"ISS197".into(),expected_calibration:"CAL197".into(),expected_trace_sha256:"a".repeat(64),
 authority_key:public,max_calibration_uncertainty_nano:100,max_clock_uncertainty_ns:50,
 max_elapsed_ns:10_000_000,replay:HashSet::new(),independently_verified_trace:false,
 authenticated_clock:false,authenticated_authority:false};
 (signed,o,p)
}
fn check<F:FnOnce(&mut SignedCalibration,&mut Observation,&mut Policy)>(reason:&str,f:F){
 let(mut s,mut o,mut p)=fixture();f(&mut s,&mut o,&mut p);
 let r=assess(&s,&o,&p);assert!(r.reasons.iter().any(|x|x==reason),"{reason}: {:?}",r.reasons);
 assert_eq!(r.verdict,"REJECT");assert_eq!(r.physical_qualification_percent,0);
 assert_eq!(r.operational_authority,"HOLD");assert!(!r.physical_act_allowed);
}
#[test]fn valid_synthetic_signature_not_physical(){let(s,o,p)=fixture();let r=assess(&s,&o,&p);assert!(r.signature_valid);assert_eq!(r.threshold_relation,"ABOVE");assert!(!r.physical_act_allowed);}
#[test]fn forged_flags_never_enable_act(){let(s,o,mut p)=fixture();p.independently_verified_trace=true;p.authenticated_clock=true;p.authenticated_authority=true;let r=assess(&s,&o,&p);assert_eq!(r.verdict,"DOCUMENTARY_INTERVAL_ONLY");assert!(!r.physical_act_allowed);}
#[test]fn crosses_threshold(){check("UNCERTAINTY_CHANGES_DECISION",|_,o,_|o.value_nano=1005);}
#[test]fn wrong_schema(){check("SCHEMA_MISMATCH",|s,_,_|s.record.schema="other".into());}
#[test]fn wrong_calibration(){check("CALIBRATION_BINDING_MISMATCH",|_,o,_|o.calibration_id="other".into());}
#[test]fn swapped_device(){check("DEVICE_OR_REFERENCE_SUBSTITUTION",|s,_,_|s.record.instrument="other".into());}
#[test]fn swapped_reference(){check("DEVICE_OR_REFERENCE_SUBSTITUTION",|s,_,_|s.record.reference="other".into());}
#[test]fn swapped_issuer(){check("ISSUER_SUBSTITUTION",|s,_,_|s.record.issuer="other".into());}
#[test]fn same_root(){check("SHARED_OR_MISSING_ANCESTRY",|s,_,_|s.record.reference_root="ROOT-DEV".into());}
#[test]fn chain_substitution(){check("TRACEABILITY_HASH_MISMATCH",|s,_,_|s.record.trace_sha256="c".repeat(64));}
#[test]fn no_capture(){check("MISSING_ORIGINAL_CAPTURE",|_,o,_|o.capture_id.clear());}
#[test]fn repeat_calibration(){check("CALIBRATION_REPLAY",|_,_,p|{p.replay.insert("CAL197".into());});}
#[test]fn expired(){check("CALIBRATION_OR_CHALLENGE_EXPIRED",|s,_,_|s.record.valid_until="2026-11-24T10:00:00Z".into());}
#[test]fn invalid_time(){check("INVALID_TIMESTAMP",|_,o,_|o.measured_utc="invalid".into());}
#[test]fn uncertainty_high(){check("CALIBRATION_UNCERTAINTY_TOO_HIGH",|s,_,_|s.record.uncertainty_nano=1000);}
#[test]fn clock_uncertainty_high(){check("CLOCK_UNCERTAINTY_TOO_HIGH",|s,_,_|s.record.clock_uncertainty_ns=1000);}
#[test]fn excessive_ticks(){check("CLOCK_SPAN_TOO_LONG",|_,o,_|o.elapsed_ns=1_000_000_000);}
#[test]fn forged_signature(){check("INVALID_CALIBRATION_SIGNATURE",|s,_,_|s.signature_hex="00".repeat(64));}
#[test]fn unverified_trace(){check("UNVERIFIED_REFERENCE_ANCESTRY",|_,_,_|{});}
#[test]fn unknown_clock(){check("UNAUTHENTICATED_PHYSICAL_CLOCK",|_,_,_|{});}
#[test]fn unknown_authority(){check("UNAUTHENTICATED_CALIBRATION_AUTHORITY",|_,_,_|{});}
#[test]fn integer_overflow(){check("UNCERTAINTY_OVERFLOW",|s,o,_|{s.record.clock_offset_ns=i64::MIN;o.elapsed_ns=u64::MAX;s.record.drift_ppb=u64::MAX;});}
