use aether_evidence::{PublicJwk, custody_ancestry::*,crash_incident::{Incident,StoreObservation,SCHEMA as INCIDENT_SCHEMA}, cross_host_equivocation as host, adversarial_qualification as qualification};
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

struct Case {
 incident:Incident,obs:Vec<SignedObservation>,ancestry:AuditPolicy,
 hosts:Vec<host::SignedHostReceipt>,host_policy:host::Policy,
 request:qualification::Request, policy:qualification::QualificationPolicy,
}
fn full()->Case{
 let(i,obs,ancestry)=fixture();
 let mut hosts=Vec::new();
 for (n,o) in obs.iter().enumerate(){
  let k=key(n as u8+102);
  let w=&o.record;
  let rec=host::HostReceipt{schema:host::SCHEMA.into(),
   receipt_id:w.receipt_reference.clone(),witness_id:w.witness_id.clone(),
   corpus_id:w.source_corpus_id.clone(),ledger_id:"LEDGER215".into(),
   sequence:9,head_sha256:"a".repeat(64),predecessor_sha256:"b".repeat(64),
   registry_sha256:"c".repeat(64),registry_epoch:5,
   witness_root:w.witness_root.clone(),witness_operator:w.operator_id.clone(),
   witness_administrator:w.administrator_id.clone(),witness_host:w.host_id.clone(),
   key_sha256:w.witness_key_sha256.clone(),claimed_timestamp:"2999-01-01T00:00:00Z".into()};
  let signature:Signature=k.sign(&host::canonical(&rec));
  hosts.push(host::SignedHostReceipt{record:rec,signature_hex:hex::encode(signature.to_bytes())});
 }
 let host_policy=host::Policy{expected_corpus_id:"SOURCE-CORPUS".into(),
 expected_ledger_id:"LEDGER215".into(),
 source:ancestry.source.clone(),witnesses:ancestry.witnesses.clone(),required_witnesses:3};
 let request=qualification::Request{
 schema:qualification::SCHEMA.into(),requested_operation:"READ_ONLY_QUALIFICATION".into(),
 claimed_remote_witnesses:3,incident_sha256:incident_hash(&i),
 witness_envelope_sha256:qualification::digest(&obs),
 host_receipts_sha256:qualification::digest(&hosts),
 claimed_original_capture_sha256:"d".repeat(64)};
 let policy=qualification::QualificationPolicy{
 expected_incident_sha256:request.incident_sha256.clone(),
 expected_witness_envelope_sha256:request.witness_envelope_sha256.clone(),
 expected_host_receipts_sha256:request.host_receipts_sha256.clone(),
 external_original_capture_authenticated:false,
 external_custody_independently_authenticated:false};
 Case{incident:i,obs,ancestry,hosts,host_policy,request,policy}
}
fn assess_case(c:&Case)->qualification::Decision{
 qualification::assess(&c.incident,&c.obs,&c.ancestry,
  &c.hosts,&c.host_policy,&c.request,&c.policy)
}
fn resign_host(c:&mut Case,n:usize){
 let signature:Signature=key(n as u8+102).sign(&host::canonical(&c.hosts[n].record));
 c.hosts[n].signature_hex=hex::encode(signature.to_bytes());
 c.request.host_receipts_sha256=qualification::digest(&c.hosts);
 c.policy.expected_host_receipts_sha256=c.request.host_receipts_sha256.clone();
}
fn repin_incident(c:&mut Case){
 c.request.incident_sha256=incident_hash(&c.incident);
 c.policy.expected_incident_sha256=c.request.incident_sha256.clone();
 c.ancestry.expected_incident_sha256=c.request.incident_sha256.clone();
 for (n,o) in c.obs.iter_mut().enumerate(){
  o.record.incident_sha256=c.request.incident_sha256.clone();
  o.signature_hex=sign(&key(n as u8+102),&o.record);
 }
 c.request.witness_envelope_sha256=qualification::digest(&c.obs);
 c.policy.expected_witness_envelope_sha256=c.request.witness_envelope_sha256.clone();
}
fn fails<F:FnOnce(&mut Case)>(reason:&str,change:F){
 let mut c=full();change(&mut c);let d=assess_case(&c);
 assert!(d.reasons.iter().any(|x|x==reason),"{reason} absent from {:?}",d.reasons);
 assert_eq!(d.verdict,"REJECT");assert!(!d.may_recover);
 assert!(!d.may_repair);assert!(!d.may_reclaim_lock);
 assert!(!d.may_select_history);assert!(!d.physical_act_allowed);
 assert_eq!(d.operational_authority,"HOLD");
}
#[test]fn all_synthetic_signatures_still_hold(){
 let d=assess_case(&full());assert_eq!(d.verdict,"DOCUMENTARY_ENSEMBLE_CONSISTENT_AUTHORITY_HOLD","{:?}",d.reasons);
 assert_eq!(d.valid_incident_signatures,3);assert_eq!(d.valid_host_signatures,3);
 assert_eq!(d.independently_authenticated_physical_witnesses,0);
 assert!(!d.may_recover);assert!(!d.physical_act_allowed);
}
#[test]fn claimed_external_authentication_still_does_not_grant_act(){
 let mut c=full();c.policy.external_original_capture_authenticated=true;
 c.policy.external_custody_independently_authenticated=true;
 let d=assess_case(&c);assert_eq!(d.verdict,"DOCUMENTARY_ENSEMBLE_CONSISTENT_AUTHORITY_HOLD");
 assert!(d.reasons.iter().any(|x|x=="EXTERNAL_AUTHENTICATION_ASSERTED_NOT_INDEPENDENTLY_VERIFIED"));
 assert!(!d.may_recover);
}
#[test]fn json_roundtrip(){let c=full();let b=serde_json::to_vec(&c.request).unwrap();
 let _:qualification::Request=serde_json::from_slice(&b).unwrap();}
#[test]fn invalid_qualification_schema(){fails("QUALIFICATION_SCHEMA_MISMATCH",|c|c.request.schema="OTHER".into());}
#[test]fn forbidden_repair_request(){fails("OPERATION_NOT_OBSERVATION_ONLY",|c|c.request.requested_operation="REPAIR".into());}
#[test]fn forbidden_recovery_request(){fails("OPERATION_NOT_OBSERVATION_ONLY",|c|c.request.requested_operation="RECOVER".into());}
#[test]fn substituted_incident_pin(){fails("QUALIFICATION_EVIDENCE_PIN_MISMATCH",|c|c.policy.expected_incident_sha256="f".repeat(64));}
#[test]fn substituted_witness_envelope_pin(){fails("QUALIFICATION_EVIDENCE_PIN_MISMATCH",|c|c.request.witness_envelope_sha256="f".repeat(64));}
#[test]fn substituted_host_bundle_pin(){fails("QUALIFICATION_EVIDENCE_PIN_MISMATCH",|c|c.policy.expected_host_receipts_sha256="f".repeat(64));}
#[test]fn forged_incident_observation_signature(){fails("INCIDENT_WITNESS_CHAIN_REJECTED",|c|c.obs[0].signature_hex="00".repeat(64));}
#[test]fn forged_host_receipt_signature(){fails("CROSS_HOST_WITNESS_CHAIN_REJECTED",|c|{c.hosts[1].signature_hex="00".repeat(64);c.request.host_receipts_sha256=qualification::digest(&c.hosts);c.policy.expected_host_receipts_sha256=c.request.host_receipts_sha256.clone();});}
#[test]fn signed_same_sequence_fork_never_voted_away(){
 let mut c=full();c.hosts[2].record.head_sha256="f".repeat(64);resign_host(&mut c,2);
 let d=assess_case(&c);assert_eq!(d.valid_host_signatures,3);
 assert!(d.reasons.iter().any(|r|r=="SIGNED_HISTORY_FORK_UNRESOLVED"));
 assert!(!d.conflicts.is_empty());assert!(!d.may_select_history);
}
#[test]fn signed_conflicting_predecessor(){fails("SIGNED_HISTORY_FORK_UNRESOLVED",|c|{
 c.hosts[1].record.predecessor_sha256="f".repeat(64);resign_host(c,1);});}
#[test]fn signed_conflicting_revocation_epoch(){fails("SIGNED_HISTORY_FORK_UNRESOLVED",|c|{
 c.hosts[1].record.registry_epoch=6;resign_host(c,1);});}
#[test]fn shared_host_controller(){fails("CROSS_HOST_WITNESS_CHAIN_REJECTED",|c|{
 c.hosts[1].record.witness_operator="OP-1".into();resign_host(c,1);});}
#[test]fn copied_host_witness_cannot_pass_cross_protocol(){fails("WITNESS_HOST_CUSTODY_BINDING_MISMATCH",|c|{
 c.hosts[0].record.witness_host="NEW-HOST".into();resign_host(c,0);});}
#[test]fn unrelated_source_control(){fails("CROSS_PROTOCOL_SOURCE_ANCESTRY_MISMATCH",|c|c.host_policy.source.operator_id="DIFFERENT".into());}
#[test]fn lost_witness_host_pair(){fails("WITNESS_MISSING_HOST_RECEIPT",|c|{
 c.hosts[0].record.witness_id="OTHER".into();resign_host(c,0);});}
#[test]fn incident_has_unresolved_divergence(){fails("INCIDENT_STILL_UNRESOLVED",|c|{
 c.incident.anomalies.push("LEDGER_REGISTRY_DIVERGENCE".into());repin_incident(c);});}
#[test]fn forged_incident_act_promotion(){fails("UPSTREAM_INCIDENT_AUTHORITY_PROMOTION",|c|{
 c.incident.physical_act_allowed=true;repin_incident(c);});}
#[test]fn unsupported_original_capture_claim(){fails("ORIGINAL_CAPTURE_DIGEST_NOT_DECLARED",|c|c.request.claimed_original_capture_sha256="X".into());}
#[test]fn inflated_witness_count(){fails("CLAIMED_WITNESS_COUNT_MISMATCH",|c|c.request.claimed_remote_witnesses=99);}
#[test]fn dropped_host_receipt(){fails("CLAIMED_WITNESS_COUNT_MISMATCH",|c|{
 c.hosts.pop();c.request.host_receipts_sha256=qualification::digest(&c.hosts);
 c.policy.expected_host_receipts_sha256=c.request.host_receipts_sha256.clone();});}
#[test]fn claimant_key_replacement_rejected(){fails("INCIDENT_WITNESS_CHAIN_REJECTED",|c|{
 c.ancestry.witnesses[2].public_key_sha256="f".repeat(64);});}
