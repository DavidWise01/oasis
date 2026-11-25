use aether_evidence::physical_alarm::*;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::collections::HashSet;
fn key(seed:u8)->SigningKey{SigningKey::from_slice(&[seed;32]).unwrap()}
fn public(k:&SigningKey)->PublicJwk{
 let b=k.verifying_key().to_encoded_point(false);let x=b.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),x:URL_SAFE_NO_PAD.encode(&x[1..33]),y:URL_SAFE_NO_PAD.encode(&x[33..65])}
}
fn sign<T:serde::Serialize>(k:&SigningKey,v:&T)->String{
 let sig:Signature=k.sign(&canonical(v));hex::encode(sig.to_bytes())
}
fn fixture()->(Packet,Policy){
 let source=key(41);let observer=key(42);
 let response=Response{schema:"AETHER-199/response-v1".into(),event_id:"response199".into(),
 capture_id:"capture199".into(),capture_sha256:"a".repeat(64),
 challenge_id:"challenge199".into(),challenge_nonce:"nonce199".into(),
 device_id:"DEVICE199".into(),sensor_id:"SENSOR199".into(),
 source_root:"ROOT_SOURCE".into(),source_operator:"OP_SOURCE".into(),source_admin:"ADMIN_SOURCE".into(),
 measured_nano:1005,reference_nano:1000,tolerance_nano:10,
 observed_utc:"2026-11-25T14:00:01Z".into(),calibration_sha256:"b".repeat(64)};
 let alarm=Alarm{schema:"AETHER-199/alarm-v1".into(),alarm_id:"alarm199".into(),
 response_sha256:response_sha256(&response),capture_sha256:response.capture_sha256.clone(),
 challenge_nonce:"nonce199".into(),observed_state:"PHYSICAL_ALARM_OBSERVED_AND_ACKNOWLEDGED".into(),
 observer_id:"OBSERVER199".into(),observer_root:"ROOT_OBSERVER".into(),
 observer_operator:"OP_OBSERVER".into(),observer_admin:"ADMIN_OBSERVER".into(),
 alarm_utc:"2026-11-25T14:00:02Z".into(),
 acknowledgement_utc:"2026-11-25T14:00:03Z".into()};
 let packet=Packet{response_signature_hex:sign(&source,&response),observer_signature_hex:sign(&observer,&alarm),response,alarm};
 let policy=Policy{capture_sha256:"a".repeat(64),challenge_id:"challenge199".into(),
 challenge_nonce:"nonce199".into(),device_id:"DEVICE199".into(),calibration_sha256:"b".repeat(64),
 expected_observer:"OBSERVER199".into(),response_key:public(&source),observer_key:public(&observer),
 max_alarm_delay_ms:5000,max_ack_delay_ms:5000,review_utc:"2026-11-25T14:00:10Z".into(),
 instrument_authenticated:false,independent_observer_authenticated:false,
 physical_alarm_observed:false,calibrated_clock_authenticated:false,
 seen_event_ids:HashSet::new(),seen_alarm_ids:HashSet::new(),seen_challenge_nonces:HashSet::new()};
 (packet,policy)
}
fn reject<F:FnOnce(&mut Packet,&mut Policy)>(reason:&str,f:F){
 let(mut packet,mut policy)=fixture();f(&mut packet,&mut policy);
 let a=assess(&packet,&policy);
 assert!(a.reasons.iter().any(|s|s==reason),"{reason}: {:?}",a.reasons);
 assert_eq!(a.verdict,"REJECT");assert_eq!(a.physical_qualification_percent,0);
 assert_eq!(a.operational_authority,"HOLD");assert!(!a.physical_act_allowed);
}
#[test]fn synthetic_baseline_unqualified(){
 let(p,c)=fixture();let a=assess(&p,&c);
 assert!(a.response_signature_valid&&a.observer_signature_valid);
 assert_eq!(a.response_error_nano,5);assert!(!a.physical_act_allowed);
}
#[test]fn spoofed_authentication_never_allows_act(){
 let(p,mut c)=fixture();c.instrument_authenticated=true;c.independent_observer_authenticated=true;
 c.physical_alarm_observed=true;c.calibrated_clock_authenticated=true;
 let a=assess(&p,&c);assert_eq!(a.verdict,"DOCUMENTARY_ALARM_REVIEW_ONLY");
 assert_eq!(a.physical_qualification_percent,0);assert!(!a.physical_act_allowed);
}
#[test]fn json_roundtrip(){let(p,c)=fixture();let b=serde_json::to_vec(&p).unwrap();let p:Packet=serde_json::from_slice(&b).unwrap();assert!(assess(&p,&c).observer_signature_valid);}
#[test]fn invalid_schema(){reject("INVALID_EVIDENCE_SCHEMA",|p,_|p.alarm.schema="OTHER".into());}
#[test]fn capture_digest(){reject("ORIGINAL_CAPTURE_MISMATCH",|p,_|p.response.capture_sha256="c".repeat(64));}
#[test]fn calibration_digest(){reject("CALIBRATION_CAPTURE_MISMATCH",|p,_|p.response.calibration_sha256="c".repeat(64));}
#[test]fn missing_event_id(){reject("MISSING_EVENT_ID",|p,_|p.response.event_id.clear());}
#[test]fn swapped_nonce(){reject("CHALLENGE_BINDING_MISMATCH",|p,_|p.alarm.challenge_nonce="stale".into());}
#[test]fn swapped_device(){reject("DEVICE_IDENTITY_MISMATCH",|p,_|p.response.device_id="OTHER".into());}
#[test]fn swapped_observer(){reject("OBSERVER_IDENTITY_MISMATCH",|p,_|p.alarm.observer_id="OTHER".into());}
#[test]fn response_hash_substituted(){reject("ALARM_RESPONSE_LINK_MISMATCH",|p,_|p.alarm.response_sha256="e".repeat(64));}
#[test]fn alarm_not_confirmed(){reject("ALARM_NOT_PHYSICALLY_OBSERVED",|p,_|p.alarm.observed_state="SIMULATED".into());}
#[test]fn empty_root(){reject("MISSING_ANCESTRY",|p,_|p.alarm.observer_root.clear());}
#[test]fn shared_root(){reject("OBSERVER_SHARES_SOURCE_CONTROL",|p,_|p.alarm.observer_root="ROOT_SOURCE".into());}
#[test]fn shared_operator(){reject("OBSERVER_SHARES_SOURCE_CONTROL",|p,_|p.alarm.observer_operator="OP_SOURCE".into());}
#[test]fn shared_admin(){reject("OBSERVER_SHARES_SOURCE_CONTROL",|p,_|p.alarm.observer_admin="ADMIN_SOURCE".into());}
#[test]fn reused_event(){reject("PHYSICAL_OBSERVATION_REPLAY",|p,c|{c.seen_event_ids.insert(p.response.event_id.clone());});}
#[test]fn reused_alarm(){reject("PHYSICAL_OBSERVATION_REPLAY",|p,c|{c.seen_alarm_ids.insert(p.alarm.alarm_id.clone());});}
#[test]fn reused_nonce(){reject("PHYSICAL_OBSERVATION_REPLAY",|p,c|{c.seen_challenge_nonces.insert(p.response.challenge_nonce.clone());});}
#[test]fn outside_tolerance(){reject("RESPONSE_OUTSIDE_TOLERANCE",|p,_|p.response.measured_nano=1100);}
#[test]fn reversed_clock(){reject("NONMONOTONIC_ALARM_TIME",|p,_|p.alarm.alarm_utc="2026-11-25T13:59:00Z".into());}
#[test]fn alarm_delay(){reject("ALARM_DELAY_EXCEEDED",|_,c|c.max_alarm_delay_ms=0);}
#[test]fn ack_delay(){reject("ACK_DELAY_EXCEEDED",|_,c|c.max_ack_delay_ms=0);}
#[test]fn invalid_time(){reject("INVALID_ALARM_TIME",|p,_|p.alarm.acknowledgement_utc="UNKNOWN".into());}
#[test]fn forged_sensor_signature(){reject("RESPONSE_SIGNATURE_INVALID",|p,_|p.response_signature_hex="00".repeat(64));}
#[test]fn forged_observer_signature(){reject("OBSERVER_SIGNATURE_INVALID",|p,_|p.observer_signature_hex="00".repeat(64));}
#[test]fn missing_instrument_auth(){reject("ORIGINAL_INSTRUMENT_UNAUTHENTICATED",|_,_|{});}
#[test]fn missing_observer_auth(){reject("EXTERNAL_OBSERVER_UNAUTHENTICATED",|_,_|{});}
#[test]fn no_observed_alarm(){reject("PHYSICAL_ALARM_NOT_INDEPENDENTLY_CONFIRMED",|_,_|{});}
#[test]fn no_clock_auth(){reject("PHYSICAL_CLOCK_UNAUTHENTICATED",|_,_|{});}
