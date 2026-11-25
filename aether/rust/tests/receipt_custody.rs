#![cfg(target_os="linux")]
use aether_evidence::{PublicJwk,remote_anchor::*,durable_ledger::{Entry,Event,digest},
authorization_registry::{Registry,REGISTRY_SCHEMA}};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::{collections::{BTreeSet,HashSet},fs,path::PathBuf,sync::atomic::{AtomicUsize,Ordering},io::Write};
use aether_evidence::receipt_custody::{self,Receipt,SCHEMA,GENESIS};
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
  let dir=std::env::temp_dir().join(format!("aether210-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();
  Self{ledger:dir.join("ledger.jsonl"),store:dir.join("receipts.jsonl"),dir}
 }
}
impl Drop for Tmp{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
struct TestFixture{
 tmp:Tmp,anchor:SignedAnchor,policy:AnchorPolicy,receipt:Receipt
}
fn setup()->TestFixture{
 let(e,r,a,mut p)=fixture();
 let t=Tmp::new();
 let mut data=e.iter().map(|x|serde_json::to_string(x).unwrap()).collect::<Vec<_>>().join("\n");
 data.push('\n');
 fs::write(&t.ledger,data).unwrap();
 fs::write(aether_evidence::authorization_registry::registry_path(&t.ledger),
 serde_json::to_vec(&r).unwrap()).unwrap();
 p.holder_out_of_band_authenticated=true;
 p.independently_retained_remote_receipt_verified=true;
 let receipt=receipt(&a,&p,"R210");
 TestFixture{tmp:t,anchor:a,policy:p,receipt}
}
fn receipt(a:&SignedAnchor,p:&AnchorPolicy,id:&str)->Receipt{
 Receipt{schema:SCHEMA.into(),receipt_id:id.into(),
 source_locator:"out-of-band-custody-claim".into(),
 remote_receipt_sha256:anchor_hash(&a.anchor),
 anchor_sha256:anchor_hash(&a.anchor),
 holder_id:a.anchor.holder_id.clone(),
 holder_key_sha256:key_hash(&p.holder_key),
 custody_nonce:a.anchor.custody_nonce.clone(),
 observed_utc:"2026-11-25T20:00:00Z".into()}
}
fn append(f:&TestFixture,head:&str,count:u64)->Result<receipt_custody::ReceiptState,String>{
 receipt_custody::ingest(&f.tmp.ledger,&f.tmp.store,f.receipt.clone(),
 f.anchor.clone(),&f.policy,head,count)
}
fn rejected<F:FnOnce(&mut TestFixture)>(reason:&str,change:F){
 let mut f=setup();change(&mut f);
 let err=append(&f,GENESIS,0).unwrap_err();
 assert!(err.contains(reason),"expected {reason}, got {err}");
 assert_eq!(receipt_custody::inspect(&f.tmp.store).unwrap().entries,0);
}
fn advance_anchor(f:&mut TestFixture,id:&str,nonce:&str){
 f.anchor.anchor.anchor_id=id.into();
 f.anchor.anchor.custody_nonce=nonce.into();
 let signature:Signature=key().sign(&canonical(&f.anchor.anchor));
 f.anchor.signature_hex=hex::encode(signature.to_bytes());
 f.policy.expected_anchor_id=id.into();
 f.policy.required_nonce=nonce.into();
 f.policy.pinned_anchor_sha256=anchor_hash(&f.anchor.anchor);
 f.receipt=receipt(&f.anchor,&f.policy,&format!("RECEIPT-{id}"));
}
#[test]fn empty_store_genesis(){
 let f=setup();let r=receipt_custody::inspect(&f.tmp.store).unwrap();
 assert_eq!(r.entries,0);assert_eq!(r.head_sha256,GENESIS);
 assert!(!r.may_recover);assert!(!r.physical_act_allowed);
}
#[test]fn ingests_and_fsynced_readback(){
 let f=setup();let r=append(&f,GENESIS,0).unwrap();
 assert_eq!(r.entries,1);assert_eq!(receipt_custody::inspect(&f.tmp.store).unwrap().head_sha256,r.head_sha256);
 assert_eq!(r.independently_authenticated_remote_receipts,0);
 assert!(!r.physical_act_allowed);
}
#[test]fn second_distinct_signed_anchor_persisted(){
 let mut f=setup();let old=append(&f,GENESIS,0).unwrap();
 advance_anchor(&mut f,"ANCHOR210-B","NONCE210-B");
 let result=append(&f,&old.head_sha256,old.entries).unwrap();
 assert_eq!(result.entries,2);assert_eq!(receipt_custody::inspect(&f.tmp.store).unwrap().entries,2);
}
#[test]fn repeated_receipt_rejected(){
 let f=setup();let old=append(&f,GENESIS,0).unwrap();
 assert_eq!(append(&f,&old.head_sha256,1).unwrap_err(),"REPLAYED_RECEIPT");
}
#[test]fn duplicate_receipt_id_rejected(){
 let mut f=setup();let old=append(&f,GENESIS,0).unwrap();
 advance_anchor(&mut f,"ANCHOR210-B","NONCE210-B");
 f.receipt.receipt_id="R210".into();
 assert_eq!(append(&f,&old.head_sha256,1).unwrap_err(),"REPLAYED_RECEIPT");
}
#[test]fn duplicate_nonce_rejected(){
 let mut f=setup();let old=append(&f,GENESIS,0).unwrap();
 advance_anchor(&mut f,"ANCHOR210-B","NONCE209");
 assert_eq!(append(&f,&old.head_sha256,1).unwrap_err(),"REPLAYED_RECEIPT");
}
#[test]fn stale_head_rejected(){
 let mut f=setup();let _old=append(&f,GENESIS,0).unwrap();
 advance_anchor(&mut f,"ANCHOR210-B","NONCE210-B");
 assert_eq!(append(&f,GENESIS,0).unwrap_err(),"STALE_RECEIPT_STORE_HEAD");
}
#[test]fn missing_external_auth_rejected(){
 rejected("REMOTE_CUSTODY_NOT_AUTHENTICATED",|f|f.policy.holder_out_of_band_authenticated=false);
}
#[test]fn missing_independent_receipt_rejected(){
 rejected("REMOTE_CUSTODY_NOT_AUTHENTICATED",|f|f.policy.independently_retained_remote_receipt_verified=false);
}
#[test]fn forged_anchor_signature_rejected(){
 rejected("REMOTE_ANCHOR_SIGNATURE_INVALID",|f|f.anchor.signature_hex="00".repeat(64));
}
#[test]fn replaced_anchor_pin_rejected(){
 rejected("REMOTE_ANCHOR_PIN_MISMATCH",|f|f.policy.pinned_anchor_sha256="f".repeat(64));
}
#[test]fn wrong_receipt_digest_rejected(){
 rejected("RECEIPT_CONTENT_DIGEST_MISMATCH",|f|f.receipt.remote_receipt_sha256="f".repeat(64));
}
#[test]fn changed_holder_binding_rejected(){
 rejected("RECEIPT_HOLDER_OR_NONCE_MISMATCH",|f|f.receipt.holder_id="FRAUD".into());
}
#[test]fn changed_holder_key_rejected(){
 rejected("RECEIPT_HOLDER_OR_NONCE_MISMATCH",|f|f.receipt.holder_key_sha256="f".repeat(64));
}
#[test]fn changed_nonce_rejected(){
 rejected("RECEIPT_HOLDER_OR_NONCE_MISMATCH",|f|f.receipt.custody_nonce="FAKE".into());
}
#[test]fn malformed_receipt_rejected(){
 rejected("RECEIPT_REQUIRED_FIELDS_INVALID",|f|f.receipt.source_locator.clear());
}
#[test]fn truncated_local_ledger_rejected(){
 rejected("ANCHOR_PROVES_LOCAL_ROLLBACK",|f|{
 let data=fs::read_to_string(&f.tmp.ledger).unwrap();
 fs::write(&f.tmp.ledger,data.lines().take(1).map(|line|format!("{line}\n")).collect::<String>()).unwrap();
 });
}
#[test]fn registry_snapshot_changed_rejected(){
 rejected("REGISTRY_SNAPSHOT_NOT_ANCHORED",|f|{
 let path=aether_evidence::authorization_registry::registry_path(&f.tmp.ledger);
 let mut reg:serde_json::Value=serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
 reg["revocation_epoch"]=serde_json::json!(5);fs::write(path,serde_json::to_vec(&reg).unwrap()).unwrap();
 });
}
#[test]fn torn_receipt_tail_rejected(){
 let f=setup();append(&f,GENESIS,0).unwrap();let mut file=fs::OpenOptions::new().append(true).open(&f.tmp.store).unwrap();
 file.write_all(b"torn").unwrap();file.sync_all().unwrap();
 assert_eq!(receipt_custody::inspect(&f.tmp.store).unwrap_err(),"RECEIPT_TORN_TAIL");
}
#[test]fn altered_receipt_hash_detected(){
 let f=setup();append(&f,GENESIS,0).unwrap();
 let raw=fs::read_to_string(&f.tmp.store).unwrap().replace("R210","R-FAKE");
 fs::write(&f.tmp.store,raw).unwrap();
 assert_eq!(receipt_custody::inspect(&f.tmp.store).unwrap_err(),"RECEIPT_HASH_CHAIN_DIVERGED");
}
#[test]fn orphaned_store_lock_refuses_takeover(){
 let f=setup();fs::write(f.tmp.store.with_extension("lock"),b"orphan").unwrap();
 assert!(append(&f,GENESIS,0).unwrap_err().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));
}
#[test]fn concurrent_store_lock_blocks_writer(){
 let f=setup();let g=aether_evidence::process_liveness::acquire(&f.tmp.store.with_extension("lock")).unwrap();
 assert!(append(&f,GENESIS,0).unwrap_err().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));
 drop(g);
}
#[test]fn receipt_store_deleted_has_no_rollback_evidence(){
 let f=setup();append(&f,GENESIS,0).unwrap();
 fs::remove_file(&f.tmp.store).unwrap();
 let state=receipt_custody::inspect(&f.tmp.store).unwrap();
 assert_eq!(state.entries,0);assert!(!state.may_recover);
}
#[test]fn signed_receipt_never_grants_operational_act(){
 let f=setup();let state=append(&f,GENESIS,0).unwrap();
 assert_eq!(state.physical_qualification_percent,0);
 assert_eq!(state.operational_authority,"HOLD");
 assert!(!state.may_recover);
}
#[test]fn no_remote_custodian_is_counted(){
 let f=setup();let state=append(&f,GENESIS,0).unwrap();
 assert_eq!(state.documentary_receipts,1);
 assert_eq!(state.independently_authenticated_remote_receipts,0);
}
