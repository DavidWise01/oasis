//! AETHER-210-RS — durable local custody-receipt ingestion.
//! Store is a local documentary copy of a claimed external receipt, NOT an
//! independent remote witness. No recovery, lock seizure or physical ACT.
use crate::{sha256_hex,remote_anchor::{self,SignedAnchor,AnchorPolicy}};
use serde::{Deserialize,Serialize};
use std::{collections::HashSet,fs::{File,OpenOptions},io::{Read,Write},path::Path};

pub const GENESIS:&str="AETHER-210/RECEIPT-GENESIS";
pub const SCHEMA:&str="AETHER-210/receipt-v1";
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub struct Receipt{
 pub schema:String,pub receipt_id:String,pub source_locator:String,
 pub remote_receipt_sha256:String,pub anchor_sha256:String,
 pub holder_id:String,pub holder_key_sha256:String,
 pub custody_nonce:String,pub observed_utc:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Entry{
 pub seq:u64,pub previous_entry_sha256:String,pub receipt:Receipt,
 pub signed_anchor:SignedAnchor,pub entry_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct ReceiptState{
 pub entries:u64,pub head_sha256:String,pub documentary_receipts:u64,
 pub independently_authenticated_remote_receipts:u64,
 pub physical_qualification_percent:u8,pub operational_authority:String,
 pub physical_act_allowed:bool,pub may_recover:bool,
}
#[derive(Serialize)]
struct Body<'a>{
 seq:u64,previous_entry_sha256:&'a str,receipt:&'a Receipt,
 signed_anchor:&'a SignedAnchor,
}
pub fn digest(seq:u64,prev:&str,receipt:&Receipt,anchor:&SignedAnchor)->String{
 sha256_hex(&serde_json::to_vec(&Body{seq,previous_entry_sha256:prev,receipt,
  signed_anchor:anchor}).expect("serializable receipt body"))
}
fn hex64(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
fn validate(receipt:&Receipt,anchor:&SignedAnchor,policy:&AnchorPolicy)->Result<(),String>{
 if receipt.schema!=SCHEMA||receipt.receipt_id.trim().is_empty()
 ||receipt.source_locator.trim().is_empty()||receipt.observed_utc.trim().is_empty(){
  return Err("RECEIPT_REQUIRED_FIELDS_INVALID".into());
 }
 if !hex64(&receipt.remote_receipt_sha256)||
 receipt.remote_receipt_sha256!=receipt.anchor_sha256||
 receipt.anchor_sha256!=remote_anchor::anchor_hash(&anchor.anchor){
  return Err("RECEIPT_CONTENT_DIGEST_MISMATCH".into());
 }
 if receipt.holder_id!=anchor.anchor.holder_id||
 receipt.holder_id!=policy.holder_id||
 receipt.holder_key_sha256!=remote_anchor::key_hash(&policy.holder_key)||
 receipt.holder_key_sha256!=policy.pinned_holder_key_sha256||
 receipt.custody_nonce!=anchor.anchor.custody_nonce{
  return Err("RECEIPT_HOLDER_OR_NONCE_MISMATCH".into());
 }
 Ok(())
}
fn read_all(path:&Path)->Result<Vec<Entry>,String>{
 let mut bytes=Vec::new();
 match File::open(path){
  Ok(mut f)=>f.read_to_end(&mut bytes).map_err(|e|format!("RECEIPT_READ: {e}"))?,
  Err(e)if e.kind()==std::io::ErrorKind::NotFound=>return Ok(vec![]),
  Err(e)=>return Err(format!("RECEIPT_OPEN: {e}")),
 };
 if bytes.is_empty(){return Ok(vec![]);}
 if bytes.last()!=Some(&b'\n'){return Err("RECEIPT_TORN_TAIL".into());}
 let mut previous=GENESIS.to_string();let mut entries=Vec::new();
 let mut ids=HashSet::new();let mut anchors=HashSet::new();
 let mut nonces=HashSet::new();let mut remote_ids=HashSet::new();
 for line in bytes.split(|b|*b==b'\n').filter(|s|!s.is_empty()){
  let entry:Entry=serde_json::from_slice(line).map_err(|_|"RECEIPT_JSON_CORRUPT")?;
  if entry.seq!=entries.len() as u64+1||entry.previous_entry_sha256!=previous||
  entry.entry_sha256!=digest(entry.seq,&previous,&entry.receipt,&entry.signed_anchor){
   return Err("RECEIPT_HASH_CHAIN_DIVERGED".into());
  }
  if entry.receipt.schema!=SCHEMA||
  entry.receipt.anchor_sha256!=remote_anchor::anchor_hash(&entry.signed_anchor.anchor){
   return Err("RECEIPT_ANCHOR_BINDING_DIVERGED".into());
  }
  if !ids.insert(entry.receipt.receipt_id.clone())||
  !anchors.insert(entry.receipt.anchor_sha256.clone())||
  !nonces.insert(entry.receipt.custody_nonce.clone())||
  !remote_ids.insert(entry.signed_anchor.anchor.anchor_id.clone()){
   return Err("RECEIPT_REPLAY_IN_HISTORY".into());
  }
  previous=entry.entry_sha256.clone();entries.push(entry);
 }
 Ok(entries)
}
fn state(v:&[Entry])->ReceiptState{
 ReceiptState{entries:v.len() as u64,
 head_sha256:v.last().map(|e|e.entry_sha256.clone()).unwrap_or_else(||GENESIS.into()),
 documentary_receipts:v.len() as u64,independently_authenticated_remote_receipts:0,
 physical_qualification_percent:0,operational_authority:"HOLD".into(),
 physical_act_allowed:false,may_recover:false}
}
pub fn inspect(store:&Path)->Result<ReceiptState,String>{read_all(store).map(|e|state(&e))}
fn sync_dir(path:&Path)->Result<(),String>{
 let parent=path.parent().filter(|p|!p.as_os_str().is_empty()).unwrap_or(Path::new("."));
 File::open(parent).and_then(|f|f.sync_all()).map_err(|e|format!("RECEIPT_DIR_SYNC: {e}"))
}
/// Documentary receipt ingestion. The receipt store lock is local and
/// separate from the ledger lock: cross-file/remote atomicity is NOT claimed.
pub fn ingest(
 ledger:&Path,store:&Path,receipt:Receipt,anchor:SignedAnchor,policy:&AnchorPolicy,
 expected_head:&str,expected_count:u64,
)->Result<ReceiptState,String>{
 validate(&receipt,&anchor,policy)?;
 let lock_path=store.with_extension("lock");
 let guard=crate::process_liveness::acquire(&lock_path)?;
 guard.verify_for(&lock_path)?;
 let prior=read_all(store)?;
 let old=state(&prior);
 if old.head_sha256!=expected_head||old.entries!=expected_count{
  return Err("STALE_RECEIPT_STORE_HEAD".into());
 }
 if prior.iter().any(|e|e.receipt.receipt_id==receipt.receipt_id||
  e.receipt.anchor_sha256==receipt.anchor_sha256||
  e.receipt.custody_nonce==receipt.custody_nonce||
  e.signed_anchor.anchor.anchor_id==anchor.anchor.anchor_id){
  return Err("REPLAYED_RECEIPT".into());
 }
 // Authenticated status flags are supplied by the caller and cannot prove
 // that the remote holder truly exists or retained this receipt.
 let observation=remote_anchor::inspect_file(ledger,&anchor,policy);
 if observation.result!="DOCUMENTARY_REMOTE_ANCHOR_CONSISTENT"{
  return Err(format!("REMOTE_ANCHOR_HOLD: {}",observation.reasons.join(",")));
 }
 let seq=expected_count.checked_add(1).ok_or("RECEIPT_SEQUENCE_OVERFLOW")?;
 let next=Entry{seq,previous_entry_sha256:old.head_sha256.clone(),
  entry_sha256:digest(seq,&old.head_sha256,&receipt,&anchor),receipt,signed_anchor:anchor};
 let mut file=OpenOptions::new().append(true).create(true).open(store)
  .map_err(|e|format!("RECEIPT_APPEND_OPEN: {e}"))?;
 let mut bytes=serde_json::to_vec(&next).map_err(|e|format!("RECEIPT_SERIALIZE: {e}"))?;
 bytes.push(b'\n');
 file.write_all(&bytes).map_err(|e|format!("RECEIPT_WRITE: {e}"))?;
 file.sync_all().map_err(|e|format!("RECEIPT_FSYNC: {e}"))?;
 sync_dir(store)?;
 let recovered=read_all(store)?;
 if recovered.len()!=prior.len()+1||
 recovered.last().map(|e|e.entry_sha256.as_str())!=Some(next.entry_sha256.as_str()){
  return Err("RECEIPT_READBACK_MISMATCH".into());
 }
 guard.verify_for(&lock_path)?;
 Ok(state(&recovered))
}
