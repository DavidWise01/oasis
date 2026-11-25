use aether_evidence::{PublicJwk,remote_anchor::*,durable_ledger::{Entry,Event,digest},
authorization_registry::{Registry,REGISTRY_SCHEMA}};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::collections::{BTreeSet,HashSet};
fn key()->SigningKey{SigningKey::from_slice(&[91u8;32]).unwrap()}
fn jwk()->PublicJwk{let k=key();let p=k.verifying_key().to_encoded_point(false);let b=p.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),
 x:URL_SAFE_NO_PAD.encode(&b[1..33]),y:URL_SAFE_NO_PAD.encode(&b[33..65])}}
fn entries(n:u64)->Vec<Entry>{
 let mut result=Vec::new();let mut prior="AETHER-201/GENESIS".to_string();
 for i in 1..=n{
  let ev=Event{event_id:format!("E{i}"),capture_sha256:format!("{i:064x}"),
  challenge_nonce:format!("N{i}"),review_id:format!("R{i}"),payload_sha256:format!("{:064x}",i+100)};
  let hash=digest(i,&prior,&ev);
  result.push(Entry{seq:i,prev_sha256:prior,event_id:ev.event_id,
   capture_sha256:ev.capture_sha256,challenge_nonce:ev.challenge_nonce,
   review_id:ev.review_id,payload_sha256:ev.payload_sha256,entry_sha256:hash.clone()});
  prior=hash;
 }
 result
}
fn fixture()->(Vec<Entry>,Registry,SignedAnchor,AnchorPolicy){
 let e=entries(3);let head=e.last().unwrap().entry_sha256.clone();
 let reg=Registry{schema:REGISTRY_SCHEMA.into(),ledger_id:"LED209".into(),
 ledger_head_sha256:head.clone(),ledger_entries:3,revocation_epoch:4,
 pinned_issuer_key_sha256:"a".repeat(64),pinned_holder_key_sha256:"b".repeat(64),
 revoked_key_sha256:BTreeSet::new(),consumed_admission_ids:BTreeSet::new(),
 consumed_admission_nonces:BTreeSet::new(),consumed_authorization_ids:BTreeSet::new(),
 consumed_authorization_nonces:BTreeSet::new(),consumed_intent_sha256:BTreeSet::new(),
 consumed_revocation_ids:BTreeSet::new()};
 let a=Anchor{schema:SCHEMA.into(),anchor_id:"ANCHOR209".into(),ledger_id:"LED209".into(),
 ledger_entries:3,ledger_head_sha256:head,
 registry_sha256:aether_evidence::sha256_hex(&canonical(&reg)),registry_epoch:4,
 prior_anchor_sha256:"c".repeat(64),custody_nonce:"NONCE209".into(),
 holder_id:"REMOTE-HOLDER".into(),holder_root:"HR".into(),holder_operator:"HO".into(),
 holder_admin:"HA".into(),issuer_root:"IR".into(),issuer_operator:"IO".into(),
 issuer_admin:"IA".into(),source_root:"SR".into(),source_operator:"SO".into(),source_admin:"SA".into()};
 let signer=key();let sig:Signature=signer.sign(&canonical(&a));
 let packet=SignedAnchor{anchor:a,signature_hex:hex::encode(sig.to_bytes())};
 let policy=AnchorPolicy{ledger_id:"LED209".into(),expected_anchor_id:"ANCHOR209".into(),
 required_nonce:"NONCE209".into(),pinned_anchor_sha256:anchor_hash(&packet.anchor),
 prior_anchor_sha256:"c".repeat(64),holder_id:"REMOTE-HOLDER".into(),
 holder_root:"HR".into(),pinned_holder_key_sha256:key_hash(&jwk()),holder_key:jwk(),
 holder_out_of_band_authenticated:false,independently_retained_remote_receipt_verified:false,
 seen_anchor_ids:HashSet::new(),seen_nonces:HashSet::new()};
 (e,reg,packet,policy)
}
fn reject<F:FnOnce(&mut Vec<Entry>,&mut Registry,&mut SignedAnchor,&mut AnchorPolicy)>(reason:&str,edit:F){
 let(mut e,mut r,mut a,mut p)=fixture();edit(&mut e,&mut r,&mut a,&mut p);
 let result=inspect_records(&e,&r,&a,&p);
 assert!(result.reasons.iter().any(|x|x==reason),"{reason}: {:?}",result.reasons);
 assert_eq!(result.result,"REJECT");assert!(!result.may_recover);
 assert!(!result.may_append);assert!(!result.physical_act_allowed);
 assert_eq!(result.operational_authority,"HOLD");
}
#[test]fn valid_synthetic_signature_lacks_real_remote_custody(){
 let(e,r,a,p)=fixture();let v=inspect_records(&e,&r,&a,&p);
 assert!(v.signature_valid);assert!(v.reasons.contains(&"REMOTE_CUSTODY_NOT_AUTHENTICATED".into()));
}
#[test]fn caller_asserted_remote_auth_does_not_grant_act(){
 let(e,r,a,mut p)=fixture();p.holder_out_of_band_authenticated=true;
 p.independently_retained_remote_receipt_verified=true;
 let v=inspect_records(&e,&r,&a,&p);
 assert_eq!(v.result,"DOCUMENTARY_REMOTE_ANCHOR_CONSISTENT","{:?}",v.reasons);
 assert!(!v.may_append);assert!(!v.may_recover);assert!(!v.physical_act_allowed);
}
#[test]fn json_roundtrip(){let(_,_,a,_)=fixture();let data=serde_json::to_vec(&a).unwrap();let _:SignedAnchor=serde_json::from_slice(&data).unwrap();}
#[test]fn valid_prefix_truncation(){reject("ANCHOR_PROVES_LOCAL_ROLLBACK",|e,_,_,_|{e.pop();});}
#[test]fn deleted_ledger(){reject("ANCHOR_PROVES_LOCAL_ROLLBACK",|e,_,_,_|e.clear());}
#[test]fn joint_rollback_of_ledger_and_registry(){
 reject("ANCHOR_PROVES_LOCAL_ROLLBACK",|e,r,_,_|{
 e.pop();r.ledger_entries=2;r.ledger_head_sha256=e.last().unwrap().entry_sha256.clone();
 });
}
#[test]fn divergent_ledger_history(){
 reject("ANCHOR_HISTORY_DIVERGENCE",|e,_,_,_|e[2].entry_sha256="f".repeat(64));
}
#[test]fn altered_registry_digest(){
 reject("REGISTRY_SNAPSHOT_NOT_ANCHORED",|_,r,_,_|{r.consumed_admission_ids.insert("substitution".into());});
}
#[test]fn higher_registry_epoch(){reject("REGISTRY_SNAPSHOT_NOT_ANCHORED",|_,r,_,_|r.revocation_epoch=5);}
#[test]fn journal_registry_head_diverges(){reject("REGISTRY_JOURNAL_DIVERGENCE",|_,r,_,_|r.ledger_head_sha256="f".repeat(64));}
#[test]fn registry_count_diverges(){reject("REGISTRY_JOURNAL_DIVERGENCE",|_,r,_,_|r.ledger_entries=2);}
#[test]fn forged_signature(){reject("REMOTE_ANCHOR_SIGNATURE_INVALID",|_,_,a,_|a.signature_hex="00".repeat(64));}
#[test]fn changed_expected_anchor_pin(){reject("REMOTE_ANCHOR_PIN_MISMATCH",|_,_,_,p|p.pinned_anchor_sha256="f".repeat(64));}
#[test]fn changed_predecessor(){reject("ANCHOR_PREDECESSOR_MISMATCH",|_,_,a,_|a.anchor.prior_anchor_sha256="e".repeat(64));}
#[test]fn changed_holder_key_pin(){reject("REMOTE_HOLDER_KEY_PIN_MISMATCH",|_,_,_,p|p.pinned_holder_key_sha256="f".repeat(64));}
#[test]fn changed_holder_identity(){reject("REMOTE_HOLDER_IDENTITY_MISMATCH",|_,_,a,_|a.anchor.holder_id="other".into());}
#[test]fn changed_ledger_id(){reject("LEDGER_ID_MISMATCH",|_,_,a,_|a.anchor.ledger_id="other".into());}
#[test]fn shared_source_root(){reject("ANCESTRY_NOT_DISTINCT",|_,_,a,_|a.anchor.source_root="HR".into());}
#[test]fn shared_source_operator(){reject("ANCESTRY_NOT_DISTINCT",|_,_,a,_|a.anchor.issuer_operator="SO".into());}
#[test]fn shared_issuer_admin(){reject("ANCESTRY_NOT_DISTINCT",|_,_,a,_|a.anchor.holder_admin="IA".into());}
#[test]fn missing_holder_root(){reject("ANCHOR_ANCESTRY_MISSING",|_,_,a,_|a.anchor.holder_root.clear());}
#[test]fn nonce_replay(){reject("REPLAYED_REMOTE_ANCHOR",|_,_,a,p|{p.seen_nonces.insert(a.anchor.custody_nonce.clone());});}
#[test]fn anchor_id_replay(){reject("REPLAYED_REMOTE_ANCHOR",|_,_,a,p|{p.seen_anchor_ids.insert(a.anchor.anchor_id.clone());});}
#[test]fn schema_wrong(){reject("ANCHOR_ID_OR_NONCE_MISMATCH",|_,_,a,_|a.anchor.schema="old".into());}
#[test]fn missing_external_custody(){reject("REMOTE_CUSTODY_NOT_AUTHENTICATED",|_,_,_,_|{});}
