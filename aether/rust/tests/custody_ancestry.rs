use aether_evidence::{PublicJwk, custody_ancestry::*,crash_incident::{Incident,StoreObservation,SCHEMA as INCIDENT_SCHEMA}};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};

fn key(n:u8)->SigningKey{SigningKey::from_slice(&[n;32]).unwrap()}
fn jwk(k:&SigningKey)->PublicJwk{
 let point=k.verifying_key().to_encoded_point(false);let p=point.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),
 x:URL_SAFE_NO_PAD.encode(&p[1..33]),y:URL_SAFE_NO_PAD.encode(&p[33..65])}
}
fn store(label:&str)->StoreObservation{
 StoreObservation{path:label.into(),exists:true,raw_sha256:Some("a".repeat(64)),
 bytes:Some(99),entries:Some(2),head_sha256:Some("b".repeat(64)),issue:None}
}
fn incident()->Incident{
 Incident{schema:INCIDENT_SCHEMA.into(),ledger:store("ledger"),
 registry:store("registry"),receipts:store("receipts"),
 anomalies:vec![],documentary_state:"LOCAL_DOCUMENTARY_SNAPSHOT_CONSISTENT".into(),
 independent_remote_witnesses:0,may_repair:false,may_recover:false,
 may_reclaim_lock:false,physical_qualification_percent:0,
 operational_authority:"HOLD".into(),physical_act_allowed:false}
}
fn sign(k:&SigningKey,o:&Observation)->String{
 let signature:Signature=k.sign(&canonical(o));hex::encode(signature.to_bytes())
}
fn fixture()->(Incident,Vec<SignedObservation>,AuditPolicy){
 let i=incident();let ih=incident_hash(&i);
 let mut observations=Vec::new();let mut pins=Vec::new();
 for n in 1..=3u8 {
  let k=key(n+101);let pubkey=jwk(&k);let fingerprint=hash(&pubkey);
  let id=format!("W{n}");
  let record=Observation{schema:WITNESS_SCHEMA.into(),
   witness_id:id.clone(),witness_root:format!("ROOT-{n}"),
   operator_id:format!("OP-{n}"),administrator_id:format!("ADMIN-{n}"),
   host_id:format!("HOST-{n}"),witness_key_sha256:fingerprint.clone(),
   incident_sha256:ih.clone(),source_corpus_id:"SOURCE-CORPUS".into(),
   evidence_sha256:format!("{n:064x}"),
   capture_method:"independent-claimed-readback".into(),
   receipt_reference:format!("RECEIPT-{n}")};
  observations.push(SignedObservation{signature_hex:sign(&k,&record),record});
  pins.push(WitnessPin{witness_id:id,expected_root:format!("ROOT-{n}"),
   public_key:pubkey,public_key_sha256:fingerprint,
   independently_enrolled:true,independent_receipt_retention_verified:true});
 }
 let p=AuditPolicy{expected_incident_sha256:ih,
 expected_corpus_id:"SOURCE-CORPUS".into(),
 source:SourceAncestry{corpus_id:"SOURCE-CORPUS".into(),
 controlling_root:"OWNED-ROOT".into(),operator_id:"OWNED-OP".into(),
 administrator_id:"OWNED-ADMIN".into(),claimed_locator:"github-owned".into()},
 witnesses:pins,min_declared_distinct_witnesses:3};
 (i,observations,p)
}
fn reject<F:FnOnce(&mut Incident,&mut Vec<SignedObservation>,&mut AuditPolicy)>(reason:&str,edit:F){
 let(mut i,mut obs,mut p)=fixture();edit(&mut i,&mut obs,&mut p);
 let d=assess(&i,&obs,&p);
 assert!(d.reasons.iter().any(|v|v==reason),"missing {reason}: {:?}",d.reasons);
 assert_eq!(d.verdict,"REJECT");assert!(!d.may_recover);
 assert!(!d.may_reclaim_lock);assert!(!d.physical_act_allowed);
 assert_eq!(d.physical_qualification_percent,0);
}
#[test]fn synthetic_three_witness_signatures_are_documentary_only(){
 let(i,obs,p)=fixture();let d=assess(&i,&obs,&p);
 assert_eq!(d.verdict,"DOCUMENTARY_ANCESTRY_CLAIMS_CONSISTENT","{:?}",d.reasons);
 assert_eq!(d.valid_signatures,3);assert_eq!(d.declared_distinct_witnesses,3);
 assert_eq!(d.independently_authenticated_physical_witnesses,0);
 assert!(!d.physical_act_allowed);
}
#[test]fn json_roundtrip(){let(_,obs,_)=fixture();let raw=serde_json::to_vec(&obs).unwrap();
 let copy:Vec<SignedObservation>=serde_json::from_slice(&raw).unwrap();assert_eq!(copy.len(),3);}
#[test]fn incident_pin_substituted(){reject("INCIDENT_PIN_MISMATCH",|_,_,p|p.expected_incident_sha256="f".repeat(64));}
#[test]fn incident_content_modified(){reject("INCIDENT_PIN_MISMATCH",|i,_,_|i.ledger.path="different".into());}
#[test]fn forged_incident_schema(){reject("INCIDENT_SCHEMA_MISMATCH",|i,_,_|i.schema="OLD".into());}
#[test]fn incident_promotes_act(){reject("INCIDENT_AUTHORITY_PROMOTION",|i,_,_|i.physical_act_allowed=true);}
#[test]fn incident_promotes_repair(){reject("INCIDENT_AUTHORITY_PROMOTION",|i,_,_|i.may_repair=true);}
#[test]fn source_corpus_changed(){reject("SOURCE_ANCESTRY_MISSING",|_,_,p|p.source.corpus_id="other".into());}
#[test]fn source_operator_missing(){reject("SOURCE_ANCESTRY_MISSING",|_,_,p|p.source.operator_id.clear());}
#[test]fn fewer_witnesses(){reject("THREE_WITNESS_ENVELOPE_REQUIRED",|_,obs,_|{obs.pop();});}
#[test]fn fewer_pins(){reject("THREE_WITNESS_ENVELOPE_REQUIRED",|_,_,p|{p.witnesses.pop();});}
#[test]fn wrong_witness_count_policy(){reject("THREE_WITNESS_ENVELOPE_REQUIRED",|_,_,p|p.min_declared_distinct_witnesses=2);}
#[test]fn duplicated_witness_identity(){reject("DUPLICATED_OBSERVATION_OR_RECEIPT",|_,obs,_|obs[1].record.witness_id=obs[0].record.witness_id.clone());}
#[test]fn copied_receipt_reference(){reject("DUPLICATED_OBSERVATION_OR_RECEIPT",|_,obs,_|obs[1].record.receipt_reference=obs[0].record.receipt_reference.clone());}
#[test]fn same_root_different_host(){reject("WITNESS_ANCESTRY_NOT_DISTINCT",|_,obs,_|obs[2].record.witness_root=obs[0].record.witness_root.clone());}
#[test]fn shared_operator_different_root(){reject("WITNESS_ANCESTRY_NOT_DISTINCT",|_,obs,_|obs[2].record.operator_id=obs[1].record.operator_id.clone());}
#[test]fn shared_admin_different_operator(){reject("WITNESS_ANCESTRY_NOT_DISTINCT",|_,obs,_|obs[2].record.administrator_id=obs[1].record.administrator_id.clone());}
#[test]fn copied_host_not_independent(){reject("WITNESS_ANCESTRY_NOT_DISTINCT",|_,obs,_|obs[2].record.host_id=obs[1].record.host_id.clone());}
#[test]fn mirror_of_owned_corpus_root(){reject("SOURCE_AND_WITNESS_SHARED_CONTROL",|_,obs,_|obs[0].record.witness_root="OWNED-ROOT".into());}
#[test]fn mirror_of_owned_operator(){reject("SOURCE_AND_WITNESS_SHARED_CONTROL",|_,obs,_|obs[0].record.operator_id="OWNED-OP".into());}
#[test]fn mirror_of_owned_admin(){reject("SOURCE_AND_WITNESS_SHARED_CONTROL",|_,obs,_|obs[0].record.administrator_id="OWNED-ADMIN".into());}
#[test]fn changed_issuer_key_pin(){reject("WITNESS_KEY_OR_ROOT_PIN_MISMATCH",|_,_,p|p.witnesses[0].public_key_sha256="f".repeat(64));}
#[test]fn forged_signature(){reject("WITNESS_SIGNATURE_INVALID",|_,obs,_|obs[1].signature_hex="00".repeat(64));}
#[test]fn missing_external_enrollment(){reject("WITNESS_EXTERNAL_ENROLLMENT_UNVERIFIED",|_,_,p|p.witnesses[0].independently_enrolled=false);}
#[test]fn missing_remote_retention(){reject("WITNESS_EXTERNAL_ENROLLMENT_UNVERIFIED",|_,_,p|p.witnesses[0].independent_receipt_retention_verified=false);}
#[test]fn changed_incident_reference(){reject("OBSERVATION_INCIDENT_OR_SOURCE_MISMATCH",|_,obs,_|obs[0].record.incident_sha256="f".repeat(64));}
#[test]fn changed_evidence_source(){reject("OBSERVATION_INCIDENT_OR_SOURCE_MISMATCH",|_,obs,_|obs[0].record.source_corpus_id="OTHER".into());}
#[test]fn empty_capture_method(){reject("OBSERVATION_FIELDS_INVALID",|_,obs,_|obs[0].record.capture_method.clear());}
#[test]fn invalid_evidence_sha256(){reject("OBSERVATION_FIELDS_INVALID",|_,obs,_|obs[0].record.evidence_sha256="0".into());}
#[test]fn unresolved_incident_anomaly(){reject("INCIDENT_HAS_UNRESOLVED_ANOMALIES",|i,_,_|i.anomalies.push("LEDGER_REGISTRY_DIVERGENCE".into()));}
