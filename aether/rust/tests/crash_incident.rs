use aether_evidence::{
 crash_incident::{read_only_incident,json_report,SCHEMA},
 durable_ledger::{self,Event,Entry as LedgerEntry},
 authorization_registry::{self,Registry,REGISTRY_SCHEMA},
 receipt_custody::{self,Receipt,Entry as ReceiptEntry},
 remote_anchor::{self,SignedAnchor,Anchor,SCHEMA as ANCHOR_SCHEMA}
};
use std::{collections::BTreeSet,fs,path::PathBuf,sync::atomic::{AtomicUsize,Ordering}};
static NEXT:AtomicUsize=AtomicUsize::new(0);
struct Fixture{dir:PathBuf,ledger:PathBuf,receipts:PathBuf}
impl Fixture{
 fn new()->Self{
  let dir=std::env::temp_dir().join(format!("aether212-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();
  let ledger=dir.join("evidence.jsonl");let receipts=dir.join("receipts.jsonl");
  let f=Self{dir,ledger,receipts};f.populate();f
 }
 fn populate(&self){
  let events=[event(1),event(2),event(3)];let mut prior=durable_ledger::GENESIS.to_string();
  let mut records=Vec::new();
  for (idx,e) in events.iter().enumerate(){
   let seq=idx as u64+1;let hash=durable_ledger::digest(seq,&prior,e);
   records.push(LedgerEntry{seq,prev_sha256:prior,
    event_id:e.event_id.clone(),capture_sha256:e.capture_sha256.clone(),
    challenge_nonce:e.challenge_nonce.clone(),review_id:e.review_id.clone(),
    payload_sha256:e.payload_sha256.clone(),entry_sha256:hash.clone()});prior=hash;
  }
  lines(&self.ledger,&records);
  let reg=Registry{schema:REGISTRY_SCHEMA.into(),ledger_id:"LEDGER-212".into(),
   ledger_head_sha256:prior.clone(),ledger_entries:3,revocation_epoch:4,
   pinned_issuer_key_sha256:"a".repeat(64),pinned_holder_key_sha256:"b".repeat(64),
   revoked_key_sha256:BTreeSet::new(),consumed_admission_ids:BTreeSet::new(),
   consumed_admission_nonces:BTreeSet::new(),consumed_authorization_ids:BTreeSet::new(),
   consumed_authorization_nonces:BTreeSet::new(),consumed_intent_sha256:BTreeSet::new(),
   consumed_revocation_ids:BTreeSet::new()};
  fs::write(authorization_registry::registry_path(&self.ledger),serde_json::to_vec(&reg).unwrap()).unwrap();
  let a=Anchor{schema:ANCHOR_SCHEMA.into(),anchor_id:"A212".into(),
   ledger_id:"LEDGER-212".into(),ledger_entries:3,ledger_head_sha256:prior,
   registry_sha256:"d".repeat(64),registry_epoch:4,prior_anchor_sha256:"c".repeat(64),
   custody_nonce:"N212".into(),holder_id:"H212".into(),holder_root:"RH".into(),
   holder_operator:"OH".into(),holder_admin:"AH".into(),issuer_root:"RI".into(),
   issuer_operator:"OI".into(),issuer_admin:"AI".into(),source_root:"RS".into(),
   source_operator:"OS".into(),source_admin:"AS".into()};
  let anchor=SignedAnchor{anchor:a,signature_hex:"".into()};
  let receipt=Receipt{schema:receipt_custody::SCHEMA.into(),receipt_id:"R212".into(),
   source_locator:"claim".into(),remote_receipt_sha256:remote_anchor::anchor_hash(&anchor.anchor),
   anchor_sha256:remote_anchor::anchor_hash(&anchor.anchor),holder_id:"H212".into(),
   holder_key_sha256:"b".repeat(64),custody_nonce:"N212".into(),
   observed_utc:"2026-11-25T00:00:00Z".into()};
  let hash=receipt_custody::digest(1,receipt_custody::GENESIS,&receipt,&anchor);
  lines(&self.receipts,&[ReceiptEntry{seq:1,
   previous_entry_sha256:receipt_custody::GENESIS.into(),
   receipt,signed_anchor:anchor,entry_sha256:hash}]);
 }
 fn registry(&self)->PathBuf{authorization_registry::registry_path(&self.ledger)}
}
impl Drop for Fixture{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
fn lines<T:serde::Serialize>(path:&std::path::Path,values:&[T]){
 fs::write(path,values.iter().map(|v|serde_json::to_string(v).unwrap())
 .collect::<Vec<_>>().join("\n")+"\n").unwrap();
}
fn event(i:u64)->Event{
 Event{event_id:format!("E{i}"),capture_sha256:format!("{i:064x}"),
 challenge_nonce:format!("N{i}"),review_id:format!("REV{i}"),
 payload_sha256:format!("{:064x}",i+100)}
}
fn assert_anomaly<F:FnOnce(&Fixture)>(expected:&str,alter:F){
 let f=Fixture::new();alter(&f);
 let i=read_only_incident(&f.ledger,&f.receipts);
 assert!(i.anomalies.iter().any(|x|x==expected),"{expected} not in {:?}",i.anomalies);
 assert_eq!(i.documentary_state,"INCIDENT_HOLD");assert!(!i.may_repair);
 assert!(!i.may_recover);assert!(!i.may_reclaim_lock);assert!(!i.physical_act_allowed);
 assert_eq!(i.operational_authority,"HOLD");
}
fn edit_registry<F:FnOnce(&mut serde_json::Value)>(f:&Fixture,change:F){
 let path=f.registry();let mut r:serde_json::Value=serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
 change(&mut r);fs::write(path,serde_json::to_vec(&r).unwrap()).unwrap();
}
fn edit_receipts<F:FnOnce(&mut serde_json::Value)>(f:&Fixture,change:F){
 let mut r:serde_json::Value=serde_json::from_str(fs::read_to_string(&f.receipts).unwrap().trim()).unwrap();
 change(&mut r);lines(&f.receipts,&[r]);
}
#[test]fn coherent_three_store_documentary_snapshot(){
 let f=Fixture::new();let i=read_only_incident(&f.ledger,&f.receipts);
 assert_eq!(i.schema,SCHEMA);assert_eq!(i.documentary_state,"LOCAL_DOCUMENTARY_SNAPSHOT_CONSISTENT","{:?}",i.anomalies);
 assert_eq!(i.ledger.entries,Some(3));assert_eq!(i.receipts.entries,Some(1));
 assert_eq!(i.independent_remote_witnesses,0);assert!(!i.physical_act_allowed);
}
#[test]fn json_report_preserves_hold(){
 let f=Fixture::new();let i=read_only_incident(&f.ledger,&f.receipts);
 let txt=json_report(&i).unwrap();let v:serde_json::Value=serde_json::from_str(&txt).unwrap();
 assert_eq!(v["may_repair"],false);assert_eq!(v["operational_authority"],"HOLD");
}
#[test]fn missing_ledger(){assert_anomaly("LEDGER_MISSING_OR_UNREADABLE",|f|fs::remove_file(&f.ledger).unwrap());}
#[test]fn missing_registry(){assert_anomaly("REGISTRY_MISSING_OR_UNREADABLE",|f|fs::remove_file(f.registry()).unwrap());}
#[test]fn missing_receipt_store(){assert_anomaly("RECEIPT_STORE_MISSING_OR_UNREADABLE",|f|fs::remove_file(&f.receipts).unwrap());}
#[test]fn corrupt_ledger_json(){assert_anomaly("LEDGER_VALIDATION_FAILED",|f|fs::write(&f.ledger,b"{bad}\n").unwrap());}
#[test]fn torn_ledger_tail(){assert_anomaly("LEDGER_VALIDATION_FAILED",|f|{use std::io::Write;let mut x=fs::OpenOptions::new().append(true).open(&f.ledger).unwrap();x.write_all(b"torn").unwrap();});}
#[test]fn corrupt_registry(){assert_anomaly("REGISTRY_VALIDATION_FAILED",|f|fs::write(f.registry(),b"bad").unwrap());}
#[test]fn registry_head_diverges(){assert_anomaly("LEDGER_REGISTRY_DIVERGENCE",|f|edit_registry(f,|r|r["ledger_head_sha256"]=serde_json::json!("f".repeat(64))));}
#[test]fn registry_count_diverges(){assert_anomaly("LEDGER_REGISTRY_DIVERGENCE",|f|edit_registry(f,|r|r["ledger_entries"]=serde_json::json!(1)));}
#[test]fn registry_schema_invalid(){assert_anomaly("REGISTRY_SCHEMA_INVALID",|f|edit_registry(f,|r|r["schema"]=serde_json::json!("legacy")));}
#[test]fn pending_registry_publication(){assert_anomaly("REGISTRY_PENDING_PUBLICATION",|f|fs::write(f.registry().with_extension("pending"),b"pending").unwrap());}
#[test]fn orphaned_evidence_lock(){assert_anomaly("UNRESOLVED_PROCESS_LOCK",|f|fs::write(f.ledger.with_extension("lock"),b"orphan").unwrap());}
#[test]fn orphaned_receipt_lock(){assert_anomaly("UNRESOLVED_PROCESS_LOCK",|f|fs::write(f.receipts.with_extension("lock"),b"orphan").unwrap());}
#[test]fn torn_receipt_tail(){assert_anomaly("RECEIPT_VALIDATION_FAILED",|f|fs::write(&f.receipts,b"torn").unwrap());}
#[test]fn changed_receipt_record_digest(){assert_anomaly("RECEIPT_VALIDATION_FAILED",|f|edit_receipts(f,|r|r["receipt"]["receipt_id"]=serde_json::json!("REPLACED")));}
#[test]fn anchor_claims_future_ledger_sequence(){assert_anomaly("RECEIPT_PROVES_JOURNAL_ROLLBACK",|f|edit_receipts(f,|r|{
 r["signed_anchor"]["anchor"]["ledger_entries"]=serde_json::json!(5);
 let a:SignedAnchor=serde_json::from_value(r["signed_anchor"].clone()).unwrap();
 let mut receipt:Receipt=serde_json::from_value(r["receipt"].clone()).unwrap();
 receipt.anchor_sha256=remote_anchor::anchor_hash(&a.anchor);receipt.remote_receipt_sha256=receipt.anchor_sha256.clone();
 r["receipt"]=serde_json::to_value(&receipt).unwrap();
 let e=receipt_custody::digest(1,receipt_custody::GENESIS,&receipt,&a);
 r["entry_sha256"]=serde_json::json!(e);
 }));}
#[test]fn anchor_proves_forked_ledger(){assert_anomaly("RECEIPT_LEDGER_HISTORY_FORK",|f|edit_receipts(f,|r|{
 r["signed_anchor"]["anchor"]["ledger_head_sha256"]=serde_json::json!("f".repeat(64));
 let a:SignedAnchor=serde_json::from_value(r["signed_anchor"].clone()).unwrap();
 let mut receipt:Receipt=serde_json::from_value(r["receipt"].clone()).unwrap();
 receipt.anchor_sha256=remote_anchor::anchor_hash(&a.anchor);receipt.remote_receipt_sha256=receipt.anchor_sha256.clone();
 r["receipt"]=serde_json::to_value(&receipt).unwrap();
 r["entry_sha256"]=serde_json::json!(receipt_custody::digest(1,receipt_custody::GENESIS,&receipt,&a));
 }));}
#[test]fn anchor_claims_higher_revocation_epoch(){assert_anomaly("RECEIPT_PROVES_REGISTRY_EPOCH_ROLLBACK",|f|edit_receipts(f,|r|{
 r["signed_anchor"]["anchor"]["registry_epoch"]=serde_json::json!(9);
 let a:SignedAnchor=serde_json::from_value(r["signed_anchor"].clone()).unwrap();
 let mut receipt:Receipt=serde_json::from_value(r["receipt"].clone()).unwrap();
 receipt.anchor_sha256=remote_anchor::anchor_hash(&a.anchor);receipt.remote_receipt_sha256=receipt.anchor_sha256.clone();
 r["receipt"]=serde_json::to_value(&receipt).unwrap();
 r["entry_sha256"]=serde_json::json!(receipt_custody::digest(1,receipt_custody::GENESIS,&receipt,&a));
 }));}
#[test]fn no_repairs_or_lock_seizure_even_if_coherent(){
 let f=Fixture::new();let i=read_only_incident(&f.ledger,&f.receipts);
 assert!(!i.may_repair);assert!(!i.may_recover);assert!(!i.may_reclaim_lock);
 assert_eq!(i.physical_qualification_percent,0);
}
#[test]fn read_only_does_not_modify_bytes(){
 let f=Fixture::new();let before=[&f.ledger,&f.registry(),&f.receipts].map(|p|fs::read(p).unwrap());
 let _=read_only_incident(&f.ledger,&f.receipts);
 let after=[&f.ledger,&f.registry(),&f.receipts].map(|p|fs::read(p).unwrap());
 assert_eq!(before,after);
}
