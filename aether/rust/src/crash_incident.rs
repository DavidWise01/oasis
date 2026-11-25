//! AETHER-212-RS — read-only crash incident and three-store reconciliation.
//! No file writes, lock reclamation, incident repair or physical ACT.
//! A coherent local snapshot is NOT independently retained remote evidence.
use crate::{sha256_hex,authorization_registry::{self,Registry},
 durable_ledger::{self,Entry as LedgerEntry},
 receipt_custody::{self,Entry as ReceiptEntry}};
use serde::{Serialize,Deserialize};
use std::{fs,path::{Path,PathBuf},collections::BTreeSet};

pub const SCHEMA:&str="AETHER-212/incident-v1";
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct StoreObservation{
 pub path:String,pub exists:bool,pub raw_sha256:Option<String>,
 pub bytes:Option<usize>,pub entries:Option<u64>,
 pub head_sha256:Option<String>,pub issue:Option<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Incident{
 pub schema:String,pub ledger:StoreObservation,pub registry:StoreObservation,
 pub receipts:StoreObservation,pub anomalies:Vec<String>,
 pub documentary_state:String,pub independent_remote_witnesses:u64,
 pub may_repair:bool,pub may_recover:bool,pub may_reclaim_lock:bool,
 pub physical_qualification_percent:u8,pub operational_authority:String,
 pub physical_act_allowed:bool,
}
fn path_string(p:&Path)->String{p.to_string_lossy().into_owned()}
fn observation(p:&Path)->StoreObservation{
 match fs::read(p){
  Ok(bytes)=>StoreObservation{path:path_string(p),exists:true,
   raw_sha256:Some(sha256_hex(&bytes)),bytes:Some(bytes.len()),
   entries:None,head_sha256:None,issue:None},
  Err(e)=>StoreObservation{path:path_string(p),exists:false,
   raw_sha256:None,bytes:None,entries:None,head_sha256:None,
   issue:Some(format!("READ_UNAVAILABLE: {e}"))},
 }
}
pub fn receipt_path(ledger:&Path)->PathBuf{ledger.with_extension("receipts.jsonl")}
pub fn read_only_incident(ledger_path:&Path,receipt_path:&Path)->Incident{
 let registry_path=authorization_registry::registry_path(ledger_path);
 let mut ledger=observation(ledger_path);
 let mut registry=observation(&registry_path);
 let mut receipts=observation(receipt_path);
 let mut issues=BTreeSet::new();
 let mut fail=|s:&str|{issues.insert(s.to_owned());};
 let ledger_entries=match durable_ledger::read_all(ledger_path){
  Ok(v)=>{ledger.entries=Some(v.len() as u64);
   ledger.head_sha256=Some(v.last().map(|x|x.entry_sha256.clone())
    .unwrap_or_else(||durable_ledger::GENESIS.into()));Some(v)},
  Err(e)=>{ledger.issue=Some(e);fail("LEDGER_VALIDATION_FAILED");None}
 };
 if !ledger.exists{fail("LEDGER_MISSING_OR_UNREADABLE");}
 let registry_value:Option<Registry>=match fs::read(&registry_path){
  Ok(bytes)=>match serde_json::from_slice(&bytes){
   Ok(v)=>Some(v),
   Err(_)=>{registry.issue=Some("REGISTRY_JSON_CORRUPT".into());fail("REGISTRY_VALIDATION_FAILED");None}
  },
  Err(_)=>{fail("REGISTRY_MISSING_OR_UNREADABLE");None}
 };
 if let Some(ref r)=registry_value{
  registry.entries=Some(r.ledger_entries);
  registry.head_sha256=Some(r.ledger_head_sha256.clone());
  if r.schema!=authorization_registry::REGISTRY_SCHEMA{
   fail("REGISTRY_SCHEMA_INVALID");
  }
  if let Some(ref l)=ledger_entries{
   let head=l.last().map(|v|v.entry_sha256.clone())
    .unwrap_or_else(||durable_ledger::GENESIS.into());
   if r.ledger_entries!=l.len() as u64||r.ledger_head_sha256!=head{
    fail("LEDGER_REGISTRY_DIVERGENCE");
   }
  }
 }
 // A pending .registry.pending file is evidence of an interrupted publication.
 if registry_path.with_extension("pending").exists(){
  fail("REGISTRY_PENDING_PUBLICATION");
 }
 // A pre-existing lock may be live, orphaned or corrupted: diagnose, never delete.
 for p in [ledger_path.with_extension("lock"),receipt_path.with_extension("lock")]{
  if p.exists(){fail("UNRESOLVED_PROCESS_LOCK");}
 }
 let receipt_entries=match receipt_custody::read_all(receipt_path){
  Ok(v)=>{receipts.entries=Some(v.len() as u64);
   receipts.head_sha256=Some(v.last().map(|e|e.entry_sha256.clone())
    .unwrap_or_else(||receipt_custody::GENESIS.into()));Some(v)},
  Err(e)=>{receipts.issue=Some(e);fail("RECEIPT_VALIDATION_FAILED");None}
 };
 if !receipts.exists{fail("RECEIPT_STORE_MISSING_OR_UNREADABLE");}
 if let (Some(ref l),Some(ref r),Some(ref rec))=
 (ledger_entries.as_ref(),registry_value.as_ref(),receipt_entries.as_ref()){
  compare_histories(l,r,rec,&mut fail);
 }
 // Compare the exact byte-level snapshots again. A concurrent writer invalidates
 // even an internally coherent observation; this is NOT an atomic 3-file read.
 for (path,observed) in [(ledger_path,&ledger),(&registry_path,&registry),(receipt_path,&receipts)]{
  let now=fs::read(path).ok().map(|b|sha256_hex(&b));
  if observed.raw_sha256!=now{fail("SNAPSHOT_CHANGED_DURING_INSPECTION");}
 }
 let anomalies:Vec<String>=issues.into_iter().collect();
 Incident{schema:SCHEMA.into(),ledger,registry,receipts,
  documentary_state:if anomalies.is_empty(){"LOCAL_DOCUMENTARY_SNAPSHOT_CONSISTENT"}
  else{"INCIDENT_HOLD"}.into(),
  anomalies,independent_remote_witnesses:0,
  may_repair:false,may_recover:false,may_reclaim_lock:false,
  physical_qualification_percent:0,operational_authority:"HOLD".into(),
  physical_act_allowed:false}
}
fn compare_histories<F:FnMut(&str)>(
 l:&[LedgerEntry],reg:&Registry,receipts:&[ReceiptEntry],fail:&mut F
){
 for (i,e) in receipts.iter().enumerate(){
  let anchor=&e.signed_anchor.anchor;
  if anchor.ledger_id!=reg.ledger_id{
   fail("RECEIPT_LEDGER_ID_MISMATCH");
  }
  if anchor.ledger_entries==0||anchor.ledger_entries>l.len() as u64{
   fail("RECEIPT_PROVES_JOURNAL_ROLLBACK");
  }else if l.get(anchor.ledger_entries as usize-1)
    .map(|x|x.entry_sha256.as_str())!=Some(anchor.ledger_head_sha256.as_str()){
   fail("RECEIPT_LEDGER_HISTORY_FORK");
  }
  if anchor.registry_epoch>reg.revocation_epoch{
   fail("RECEIPT_PROVES_REGISTRY_EPOCH_ROLLBACK");
  }
  if i>0{
   let previous=&receipts[i-1].signed_anchor.anchor;
   if anchor.prior_anchor_sha256!=crate::remote_anchor::anchor_hash(previous){
    fail("RECEIPT_ANCHOR_PREDECESSOR_DIVERGENCE");
   }
   if anchor.ledger_entries<=previous.ledger_entries{
    fail("RECEIPT_NONMONOTONIC_SEQUENCE");
   }
  }
 }
}
/// No mutation: incident JSON is caller-owned. Serialization of this value does
/// not establish independence, authenticity, durability or an outside witness.
pub fn json_report(incident:&Incident)->Result<String,String>{
 serde_json::to_string_pretty(incident).map_err(|e|format!("INCIDENT_SERIALIZATION: {e}"))
}
