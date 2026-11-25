use aether_evidence::{PublicJwk,cross_host_equivocation::*,custody_ancestry::{SourceAncestry,WitnessPin}};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
fn key(n:u8)->SigningKey{SigningKey::from_slice(&[n;32]).unwrap()}
fn jwk(k:&SigningKey)->PublicJwk{
 let p=k.verifying_key().to_encoded_point(false);let b=p.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),
 x:URL_SAFE_NO_PAD.encode(&b[1..33]),y:URL_SAFE_NO_PAD.encode(&b[33..65])}
}
fn resign(r:&mut SignedHostReceipt,n:usize){
 let sig:Signature=key(n as u8+111).sign(&canonical(&r.record));
 r.signature_hex=hex::encode(sig.to_bytes());
}
fn fixture()->(Vec<SignedHostReceipt>,Policy){
 let mut out=Vec::new();let mut pins=Vec::new();
 for n in 1..=3{
  let sk=key(n+111);let pk=jwk(&sk);let fp=hash(&pk);
  let record=HostReceipt{schema:SCHEMA.into(),receipt_id:format!("R{n}"),
   witness_id:format!("W{n}"),corpus_id:"CORPUS".into(),ledger_id:"LEDGER".into(),
   sequence:9,head_sha256:"a".repeat(64),predecessor_sha256:"b".repeat(64),
   registry_sha256:"c".repeat(64),registry_epoch:4,
   witness_root:format!("ROOT{n}"),witness_operator:format!("OP{n}"),
   witness_administrator:format!("ADMIN{n}"),witness_host:format!("HOST{n}"),
   key_sha256:fp.clone(),claimed_timestamp:"2999-01-01T00:00:00Z".into()};
  let sig:Signature=sk.sign(&canonical(&record));
  out.push(SignedHostReceipt{record,signature_hex:hex::encode(sig.to_bytes())});
  pins.push(WitnessPin{witness_id:format!("W{n}"),expected_root:format!("ROOT{n}"),
   public_key:pk,public_key_sha256:fp,independently_enrolled:true,
   independent_receipt_retention_verified:true});
 }
 (out,Policy{expected_corpus_id:"CORPUS".into(),expected_ledger_id:"LEDGER".into(),
 source:SourceAncestry{corpus_id:"CORPUS".into(),controlling_root:"OWNED".into(),
 operator_id:"OWNOP".into(),administrator_id:"OWNADMIN".into(),
 claimed_locator:"owned-mirror".into()},
 witnesses:pins,required_witnesses:3})
}
fn fail<F:FnOnce(&mut Vec<SignedHostReceipt>,&mut Policy)>(expected:&str,mutate:F){
 let(mut r,mut p)=fixture();mutate(&mut r,&mut p);
 let d=assess(&r,&p);
 assert!(d.reasons.iter().any(|x|x==expected),"missing {expected} {:?}",d.reasons);
 assert_eq!(d.verdict,"REJECT");assert!(!d.may_choose_history);
 assert!(!d.may_recover);assert!(!d.physical_act_allowed);
 assert_eq!(d.operational_authority,"HOLD");
}
#[test]fn synthetic_matching_same_sequence_is_documentary_only(){
 let(r,p)=fixture();let d=assess(&r,&p);
 assert_eq!(d.verdict,"DOCUMENTARY_CROSS_HOST_CLAIMS_CONSISTENT","{:?}",d.reasons);
 assert_eq!(d.valid_signatures,3);assert_eq!(d.declared_distinct_hosts,3);
 assert_eq!(d.independently_authenticated_external_witnesses,0);
 assert!(!d.may_choose_history);assert!(!d.physical_act_allowed);
}
#[test]fn signed_fork_same_sequence(){
 let(mut r,p)=fixture();r[2].record.head_sha256="f".repeat(64);resign(&mut r[2],3);
 let d=assess(&r,&p);
 assert!(d.conflicts.iter().any(|c|c.kind=="SAME_SEQUENCE_DIFFERENT_HEAD"));
 assert_eq!(d.verdict,"REJECT");assert!(d.valid_signatures==3);
}
#[test]fn conflicting_predecessor(){fail("CROSS_HOST_EQUIVOCATION_UNRESOLVED",|r,_|{r[1].record.predecessor_sha256="f".repeat(64);resign(&mut r[1],2);});}
#[test]fn conflicting_registry_hash(){fail("CROSS_HOST_EQUIVOCATION_UNRESOLVED",|r,_|{r[1].record.registry_sha256="f".repeat(64);resign(&mut r[1],2);});}
#[test]fn conflicting_registry_epoch(){fail("CROSS_HOST_EQUIVOCATION_UNRESOLVED",|r,_|{r[1].record.registry_epoch=6;resign(&mut r[1],2);});}
#[test]fn later_timestamp_cannot_hide_fork(){fail("CROSS_HOST_EQUIVOCATION_UNRESOLVED",|r,_|{r[1].record.claimed_timestamp="9999-01-01".into();r[1].record.head_sha256="f".repeat(64);resign(&mut r[1],2);});}
#[test]fn shared_witness_root(){fail("SHARED_WITNESS_CONTROL_ANCESTRY",|r,_|r[1].record.witness_root="ROOT1".into());}
#[test]fn shared_operator(){fail("SHARED_WITNESS_CONTROL_ANCESTRY",|r,_|r[1].record.witness_operator="OP1".into());}
#[test]fn shared_administrator(){fail("SHARED_WITNESS_CONTROL_ANCESTRY",|r,_|r[1].record.witness_administrator="ADMIN1".into());}
#[test]fn shared_host(){fail("SHARED_WITNESS_CONTROL_ANCESTRY",|r,_|r[1].record.witness_host="HOST1".into());}
#[test]fn mirror_owned_source_root(){fail("OWNED_SOURCE_MIRROR_OR_SHARED_CONTROL",|r,_|r[0].record.witness_root="OWNED".into());}
#[test]fn mirror_owned_operator(){fail("OWNED_SOURCE_MIRROR_OR_SHARED_CONTROL",|r,_|r[0].record.witness_operator="OWNOP".into());}
#[test]fn mirror_owned_admin(){fail("OWNED_SOURCE_MIRROR_OR_SHARED_CONTROL",|r,_|r[0].record.witness_administrator="OWNADMIN".into());}
#[test]fn duplicate_receipt_id(){fail("DUPLICATE_RECEIPT_OR_WITNESS",|r,_|r[1].record.receipt_id="R1".into());}
#[test]fn duplicate_witness_id(){fail("DUPLICATE_RECEIPT_OR_WITNESS",|r,_|r[1].record.witness_id="W1".into());}
#[test]fn fewer_receipts(){fail("THREE_WITNESS_ENVELOPE_REQUIRED",|r,_|{r.pop();});}
#[test]fn missing_pins(){fail("THREE_WITNESS_ENVELOPE_REQUIRED",|_,p|{p.witnesses.pop();});}
#[test]fn wrong_minimum(){fail("THREE_WITNESS_ENVELOPE_REQUIRED",|_,p|p.required_witnesses=2);}
#[test]fn wrong_source_corpus(){fail("SOURCE_OR_LEDGER_BINDING_MISMATCH",|r,_|r[0].record.corpus_id="OTHER".into());}
#[test]fn wrong_ledger_id(){fail("SOURCE_OR_LEDGER_BINDING_MISMATCH",|r,_|r[0].record.ledger_id="OTHER".into());}
#[test]fn malformed_head(){fail("RECEIPT_FIELDS_INVALID",|r,_|r[0].record.head_sha256="short".into());}
#[test]fn zero_sequence(){fail("RECEIPT_FIELDS_INVALID",|r,_|r[0].record.sequence=0);}
#[test]fn missing_host(){fail("WITNESS_ANCESTRY_MISSING",|r,_|r[0].record.witness_host.clear());}
#[test]fn replaced_key_pin(){fail("HOST_KEY_OR_ROOT_PIN_MISMATCH",|_,p|p.witnesses[0].public_key_sha256="f".repeat(64));}
#[test]fn forged_signature(){fail("HOST_SIGNATURE_INVALID",|r,_|r[0].signature_hex="00".repeat(64));}
#[test]fn absent_external_enrollment(){fail("EXTERNAL_HOST_CUSTODY_UNVERIFIED",|_,p|p.witnesses[0].independently_enrolled=false);}
#[test]fn absent_remote_retention(){fail("EXTERNAL_HOST_CUSTODY_UNVERIFIED",|_,p|p.witnesses[0].independent_receipt_retention_verified=false);}
#[test]fn duplicate_pinned_witness(){fail("DUPLICATE_PINNED_WITNESS",|_,p|p.witnesses[1].witness_id="W1".into());}
#[test]fn adjacent_fork(){
 let(mut r,p)=fixture();r[1].record.sequence=10;
 r[1].record.predecessor_sha256="f".repeat(64);resign(&mut r[1],2);
 let d=assess(&r,&p);assert!(d.conflicts.iter().any(|c|c.kind=="ADJACENT_SEQUENCE_FORK"));
}
#[test]fn adjacent_registry_rewind(){
 let(mut r,p)=fixture();r[1].record.sequence=10;
 r[1].record.predecessor_sha256="a".repeat(64);
 r[1].record.registry_epoch=3;resign(&mut r[1],2);
 let d=assess(&r,&p);assert!(d.conflicts.iter().any(|c|c.kind=="REGISTRY_EPOCH_REWIND"));
}
