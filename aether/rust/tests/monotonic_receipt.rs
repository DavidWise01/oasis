#![cfg(target_os="linux")]
use aether_evidence::{PublicJwk,remote_anchor::*,durable_ledger::{Entry,Event,digest},
authorization_registry::{Registry,REGISTRY_SCHEMA}};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::{collections::{BTreeSet,HashSet},fs,path::PathBuf,sync::atomic::{AtomicUsize,Ordering}};
use aether_evidence::receipt_custody::{self,Receipt};
use aether_evidence::monotonic_receipt::{self,SignedRotation,Rotation,RotationPolicy,ROTATION_SCHEMA};
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

static NEXT:AtomicUsize=AtomicUsize::new(0);
struct Tmp{dir:PathBuf,ledger:PathBuf,store:PathBuf}
impl Tmp{
 fn new()->Self{
  let dir=std::env::temp_dir().join(format!("aether211-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();Self{ledger:dir.join("ledger.jsonl"),store:dir.join("receipts.jsonl"),dir}
 }
}
impl Drop for Tmp{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
fn receipt(a:&SignedAnchor,p:&AnchorPolicy)->Receipt{
 Receipt{schema:receipt_custody::SCHEMA.into(),receipt_id:"R211".into(),
 source_locator:"synthetic-remote-claim".into(),remote_receipt_sha256:anchor_hash(&a.anchor),
 anchor_sha256:anchor_hash(&a.anchor),holder_id:a.anchor.holder_id.clone(),
 holder_key_sha256:key_hash(&p.holder_key),custody_nonce:a.anchor.custody_nonce.clone(),
 observed_utc:"2099-11-25T20:00:00Z".into()}
}
fn setup()->(Tmp,SignedAnchor,AnchorPolicy){
 let(e,r,a,mut p)=fixture();let t=Tmp::new();
 fs::write(&t.ledger,e.iter().map(|x|serde_json::to_string(x).unwrap())
 .collect::<Vec<_>>().join("\n")+"\n").unwrap();
 fs::write(aether_evidence::authorization_registry::registry_path(&t.ledger),
 serde_json::to_vec(&r).unwrap()).unwrap();
 p.holder_out_of_band_authenticated=true;
 p.independently_retained_remote_receipt_verified=true;
 (t,a,p)
}
fn pair()->(receipt_custody::Entry,SignedAnchor,AnchorPolicy){
 let(_,_,mut next,mut policy)=fixture();
 let mut prev=next.clone();
 prev.anchor.anchor_id="ANCHOR210-OLD".into();
 prev.anchor.ledger_entries=2;
 prev.anchor.ledger_head_sha256="a".repeat(64);
 prev.anchor.custody_nonce="OLD-NONCE".into();
 let old_hash=anchor_hash(&prev.anchor);
 next.anchor.prior_anchor_sha256=old_hash;
 let old_receipt=Receipt{
  schema:receipt_custody::SCHEMA.into(),receipt_id:"RECEIPT-OLD".into(),
  source_locator:"documentary-claim".into(),remote_receipt_sha256:anchor_hash(&prev.anchor),
  anchor_sha256:anchor_hash(&prev.anchor),holder_id:prev.anchor.holder_id.clone(),
  holder_key_sha256:key_hash(&policy.holder_key),custody_nonce:prev.anchor.custody_nonce.clone(),
  observed_utc:"2100-01-01T00:00:00Z".into()};
 policy.pinned_anchor_sha256=anchor_hash(&next.anchor);
 let prior=receipt_custody::Entry{seq:1,previous_entry_sha256:receipt_custody::GENESIS.into(),
  entry_sha256:receipt_custody::digest(1,receipt_custody::GENESIS,&old_receipt,&prev),
  receipt:old_receipt,signed_anchor:prev};
 (prior,next,policy)
}
fn reject<F:FnOnce(&mut receipt_custody::Entry,&mut SignedAnchor,&mut AnchorPolicy)>(expected:&str,edit:F){
 let(mut prior,mut next,mut p)=pair();edit(&mut prior,&mut next,&mut p);
 let d=monotonic_receipt::assess(&prior,&next,&p,None,None);
 assert!(d.reasons.iter().any(|r|r==expected),"{expected}: {:?}",d.reasons);
 assert!(!d.may_store_documentary_receipt);assert!(!d.may_recover);
 assert!(!d.physical_act_allowed);assert_eq!(d.operational_authority,"HOLD");
}
#[test]fn synthetic_forward_extension_consistent(){
 let(prior,next,p)=pair();
 let d=monotonic_receipt::assess(&prior,&next,&p,None,None);
 assert_eq!(d.verdict,"DOCUMENTARY_FORWARD_EXTENSION_ONLY");
 assert!(d.may_store_documentary_receipt);assert!(!d.may_recover);assert!(!d.physical_act_allowed);
}
#[test]fn changed_ledger_identity(){reject("ANCHOR_LEDGER_CHANGED",|_,next,_|next.anchor.ledger_id="OTHER".into());}
#[test]fn missing_previous_digest(){reject("ANCHOR_PREDECESSOR_NOT_CONTIGUOUS",|_,next,_|next.anchor.prior_anchor_sha256="b".repeat(64));}
#[test]fn older_history_even_with_later_timestamp(){reject("ANCHOR_NOT_FORWARD_PROGRESS",|prior,next,_|next.anchor.ledger_entries=prior.signed_anchor.anchor.ledger_entries);}
#[test]fn unchanged_head(){reject("ANCHOR_NOT_FORWARD_PROGRESS",|prior,next,_|next.anchor.ledger_head_sha256=prior.signed_anchor.anchor.ledger_head_sha256.clone());}
#[test]fn regressed_epoch(){reject("ANCHOR_REGISTRY_EPOCH_ROLLBACK",|prior,next,_|{prior.signed_anchor.anchor.registry_epoch=5;next.anchor.prior_anchor_sha256=anchor_hash(&prior.signed_anchor.anchor);next.anchor.registry_epoch=4;});}
#[test]fn changed_source_root(){reject("SOURCE_OR_ISSUER_ANCESTRY_CHANGED",|_,next,_|next.anchor.source_root="FORK".into());}
#[test]fn changed_source_operator(){reject("SOURCE_OR_ISSUER_ANCESTRY_CHANGED",|_,next,_|next.anchor.source_operator="OTHER".into());}
#[test]fn changed_issuer_root(){reject("SOURCE_OR_ISSUER_ANCESTRY_CHANGED",|_,next,_|next.anchor.issuer_root="OTHER".into());}
#[test]fn changed_issuer_admin(){reject("SOURCE_OR_ISSUER_ANCESTRY_CHANGED",|_,next,_|next.anchor.issuer_admin="OTHER".into());}
#[test]fn holder_id_change_without_rotation(){reject("UNAUTHORIZED_HOLDER_ROTATION",|_,next,_|next.anchor.holder_id="NEW".into());}
#[test]fn holder_key_change_without_rotation(){reject("UNAUTHORIZED_HOLDER_ROTATION",|_,_,p|p.pinned_holder_key_sha256="f".repeat(64));}
#[test]fn holder_root_change_without_rotation(){reject("UNAUTHORIZED_HOLDER_ROTATION",|_,next,_|next.anchor.holder_root="NEWROOT".into());}
#[test]fn holder_operator_change_without_rotation(){reject("UNAUTHORIZED_HOLDER_ROTATION",|_,next,_|next.anchor.holder_operator="NEW-OP".into());}
fn rotation(prior:&receipt_custody::Entry,next:&SignedAnchor,p:&AnchorPolicy)->(SignedRotation,RotationPolicy){
 let signer=SigningKey::from_slice(&[92u8;32]).unwrap();
 let point=signer.verifying_key().to_encoded_point(false);let bytes=point.as_bytes();
 let key=PublicJwk{kty:"EC".into(),crv:"P-256".into(),
 x:URL_SAFE_NO_PAD.encode(&bytes[1..33]),y:URL_SAFE_NO_PAD.encode(&bytes[33..65])};
 let r=Rotation{schema:ROTATION_SCHEMA.into(),
  old_anchor_sha256:anchor_hash(&prior.signed_anchor.anchor),
  new_anchor_sha256:anchor_hash(&next.anchor),
  old_holder_id:prior.signed_anchor.anchor.holder_id.clone(),
  new_holder_id:next.anchor.holder_id.clone(),
  old_holder_key_sha256:prior.receipt.holder_key_sha256.clone(),
  new_holder_key_sha256:p.pinned_holder_key_sha256.clone(),
  authority_root:"INDEPENDENT-ROTATION-ROOT".into(),
  authority_operator:"INDEPENDENT-ROTATION-OP".into(),
  authority_admin:"INDEPENDENT-ROTATION-ADMIN".into(),
  authorization_id:"ROTATION-211".into(),rotation_nonce:"ROT-NONCE-211".into()};
 let signature:Signature=signer.sign(&serde_json::to_vec(&r).unwrap());
 let packet=SignedRotation{record:r,signature_hex:hex::encode(signature.to_bytes())};
 let policy=RotationPolicy{pinned_authority_key_sha256:key_hash(&key),authority_key:key,
 independent_authority_authenticated_out_of_band:true,
 expected_authorization_id:"ROTATION-211".into(),expected_nonce:"ROT-NONCE-211".into(),
 prior_rotation_ids:HashSet::new(),prior_rotation_nonces:HashSet::new()};
 (packet,policy)
}
#[test]fn signed_rotation_is_documentary_not_act(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(r,rp)=rotation(&prior,&next,&p);
 let d=monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp));
 assert_eq!(d.verdict,"DOCUMENTARY_FORWARD_EXTENSION_ONLY","{:?}",d.reasons);
 assert!(!d.physical_act_allowed);assert!(!d.may_recover);
}
#[test]fn rotation_without_policy_rejected(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(r,_)=rotation(&prior,&next,&p);
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),None).reasons[0],"MISSING_ROTATION_TRUST_ANCHOR");
}
#[test]fn forgery_of_rotation_signature(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(mut r,rp)=rotation(&prior,&next,&p);r.signature_hex="00".repeat(64);
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],"ROTATION_AUTHORITY_SIGNATURE_INVALID");
}
#[test]fn shared_rotation_root(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(mut r,rp)=rotation(&prior,&next,&p);r.record.authority_root="HR".into();
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],"ROTATION_AUTHORITY_SHARED_ANCESTRY");
}
#[test]fn replayed_rotation_id(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(r,mut rp)=rotation(&prior,&next,&p);rp.prior_rotation_ids.insert("ROTATION-211".into());
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],"REPLAYED_ROTATION_AUTHORIZATION");
}
#[test]fn missing_external_rotation_authority(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(r,mut rp)=rotation(&prior,&next,&p);rp.independent_authority_authenticated_out_of_band=false;
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],"ROTATION_AUTHORITY_ORIGIN_UNVERIFIED");
}
#[test]fn changed_rotation_pin(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(r,mut rp)=rotation(&prior,&next,&p);rp.pinned_authority_key_sha256="f".repeat(64);
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],"ROTATION_AUTHORITY_PIN_MISMATCH");
}
#[test]fn unexpected_rotation_for_same_holder(){
 let(prior,next,p)=pair();let(r,rp)=rotation(&prior,&next,&p);
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],"UNEXPECTED_HOLDER_ROTATION_PROOF");
}
#[test]fn first_monotonic_receipt_committed(){
 let(t,a,p)=setup();let r=receipt(&a,&p);
 let v=receipt_custody::ingest_monotonic(&t.ledger,&t.store,r,a,&p,receipt_custody::GENESIS,0,None,None).unwrap();
 assert_eq!(v.entries,1);assert!(!v.physical_act_allowed);
}
#[test]fn replayed_anchor_is_rejected_within_lock(){
 let(t,a,p)=setup();let receipt=receipt(&a,&p);
 let first=receipt_custody::ingest_monotonic(&t.ledger,&t.store,receipt.clone(),a.clone(),&p,receipt_custody::GENESIS,0,None,None).unwrap();
 assert_eq!(receipt_custody::ingest_monotonic(&t.ledger,&t.store,receipt,a,&p,&first.head_sha256,first.entries,None,None).unwrap_err(),
 "MONOTONIC_RECEIPT_HOLD: ANCHOR_PREDECESSOR_NOT_CONTIGUOUS");
}

#[test]fn substituted_rotation_target_anchor(){
 let(prior,mut next,p)=pair();next.anchor.holder_id="NEW-HOLDER".into();
 let(mut r,rp)=rotation(&prior,&next,&p);
 r.record.new_anchor_sha256="f".repeat(64);
 assert_eq!(monotonic_receipt::assess(&prior,&next,&p,Some(&r),Some(&rp)).reasons[0],
 "ROTATION_BINDING_MISMATCH");
}
