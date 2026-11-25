//! AETHER-203-RS: independently pinned signed recovery checkpoint.
//! Detects local rollback even if the remaining JSONL hash chain is internally valid.
//! The signer and policy pins MUST come from a separately held trusted source.
//! All decisions are documentary, never physical ACT.
use crate::{sha256_hex, PublicJwk};
use crate::durable_ledger::{read_all,Entry,Event,State};
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Deserialize,Serialize};
use std::collections::HashSet;
use std::path::Path;

pub const CHECKPOINT_SCHEMA:&str="AETHER-203/checkpoint-v1";
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub struct Checkpoint {
 pub schema:String,pub checkpoint_id:String,pub holder_id:String,
 pub holder_root:String,pub holder_operator:String,pub holder_administrator:String,
 pub source_root:String,pub source_operator:String,pub source_administrator:String,
 pub ledger_id:String,pub sequence:u64,pub head_sha256:String,
 pub predecessor_checkpoint_sha256:String,pub challenge_nonce:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct SignedCheckpoint{pub record:Checkpoint,pub signature_hex:String}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct RecoveryPolicy {
 pub expected_ledger_id:String,pub expected_holder_id:String,
 pub expected_holder_root:String,pub pinned_holder_key_sha256:String,
 pub expected_checkpoint_sha256:String,pub expected_predecessor_checkpoint_sha256:String,
 pub holder_public_key:PublicJwk,pub holder_out_of_band_authenticated:bool,
 pub external_checkpoint_custody_verified:bool,
 #[serde(default)]pub seen_checkpoint_ids:HashSet<String>,
 #[serde(default)]pub seen_challenge_nonces:HashSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct RecoveryDecision{
 pub verdict:String,pub reasons:Vec<String>,pub signature_valid:bool,
 pub record_sha256:String,pub local_entries:u64,pub local_head_sha256:String,
 pub may_append:bool,pub may_recover_or_reclaim:bool,
 pub physical_qualification_percent:u8,pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical(c:&Checkpoint)->Vec<u8>{serde_json::to_vec(c).unwrap_or_default()}
pub fn checkpoint_hash(c:&Checkpoint)->String{sha256_hex(&canonical(c))}
fn hex64(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
pub fn public_key_fingerprint(jwk:&PublicJwk)->String{
 // Deterministic serialization; roots must be independently pinned before any admission.
 sha256_hex(&serde_json::to_vec(jwk).unwrap_or_default())
}
fn verify(c:&SignedCheckpoint,key:&PublicJwk)->bool{
 let Ok(k)=crate::verifying_key(key)else{return false};
 let Ok(raw)=hex::decode(&c.signature_hex)else{return false};
 let Ok(sig)=Signature::from_slice(&raw)else{return false};
 k.verify(&canonical(&c.record),&sig).is_ok()
}
pub fn assess_entries(entries:&[Entry],c:&SignedCheckpoint,p:&RecoveryPolicy)->RecoveryDecision{
 let checkpoint=&c.record;
 let mut failures=std::collections::BTreeSet::new();
 let mut fail=|r:&str|{failures.insert(r.to_owned());};
 if checkpoint.schema!=CHECKPOINT_SCHEMA{fail("CHECKPOINT_SCHEMA_MISMATCH");}
 let record_sha256=checkpoint_hash(checkpoint);
 if record_sha256!=p.expected_checkpoint_sha256||!hex64(&p.expected_checkpoint_sha256){
  fail("EXTERNAL_CHECKPOINT_PIN_MISMATCH");
 }
 if checkpoint.predecessor_checkpoint_sha256!=p.expected_predecessor_checkpoint_sha256||
 !hex64(&checkpoint.predecessor_checkpoint_sha256){fail("CHECKPOINT_PREDECESSOR_MISMATCH");}
 if checkpoint.ledger_id!=p.expected_ledger_id||checkpoint.ledger_id.is_empty(){
  fail("LEDGER_IDENTITY_MISMATCH");
 }
 if checkpoint.holder_id!=p.expected_holder_id||
 checkpoint.holder_root!=p.expected_holder_root{fail("CHECKPOINT_HOLDER_MISMATCH");}
 if [&checkpoint.holder_root,&checkpoint.holder_operator,&checkpoint.holder_administrator,
 &checkpoint.source_root,&checkpoint.source_operator,&checkpoint.source_administrator]
 .iter().any(|s|s.is_empty()){fail("MISSING_CUSTODY_ANCESTRY");}
 if checkpoint.holder_root==checkpoint.source_root||
 checkpoint.holder_operator==checkpoint.source_operator||
 checkpoint.holder_administrator==checkpoint.source_administrator{
  fail("SHARED_SOURCE_AND_HOLDER_CONTROL");
 }
 if checkpoint.checkpoint_id.trim().is_empty()||
 checkpoint.challenge_nonce.trim().is_empty(){fail("MISSING_CHECKPOINT_OR_NONCE");}
 if p.seen_checkpoint_ids.contains(&checkpoint.checkpoint_id)||
 p.seen_challenge_nonces.contains(&checkpoint.challenge_nonce){
  fail("REPLAYED_EXTERNAL_CHECKPOINT");
 }
 if checkpoint.sequence==0||!hex64(&checkpoint.head_sha256){
  fail("INVALID_CHECKPOINT_HEAD");
 }else if entries.len()<(checkpoint.sequence as usize){
  fail("LOCAL_LEDGER_ROLLBACK_OR_TRUNCATION");
 }else if entries.get(checkpoint.sequence as usize-1).map(|e|e.entry_sha256.as_str())
       !=Some(checkpoint.head_sha256.as_str()){
  fail("EXTERNAL_CHECKPOINT_HISTORY_DIVERGENCE");
 }
 if p.pinned_holder_key_sha256!=public_key_fingerprint(&p.holder_public_key)||
 !hex64(&p.pinned_holder_key_sha256){fail("HOLDER_PUBLIC_KEY_PIN_MISMATCH");}
 let signature_valid=verify(c,&p.holder_public_key);
 if !signature_valid{fail("CHECKPOINT_SIGNATURE_INVALID");}
 if !p.holder_out_of_band_authenticated{fail("HOLDER_ORIGIN_NOT_EXTERNALLY_AUTHENTICATED");}
 if !p.external_checkpoint_custody_verified{fail("EXTERNAL_CHECKPOINT_CUSTODY_UNVERIFIED");}
 let current_head=entries.last().map(|e|e.entry_sha256.clone())
   .unwrap_or_else(||crate::durable_ledger::GENESIS.into());
 let reasons:Vec<String>=failures.into_iter().collect();
 let accepted=reasons.is_empty();
 RecoveryDecision{
  verdict:if accepted{"DOCUMENTARY_CHECKPOINT_CONSISTENT"}else{"REJECT"}.into(),
  reasons,signature_valid,record_sha256,
  local_entries:entries.len() as u64,local_head_sha256:current_head,
  may_append:accepted,may_recover_or_reclaim:false,
  physical_qualification_percent:0,operational_authority:"HOLD".into(),
  physical_act_allowed:false,
 }
}
pub fn assess_file(path:&Path,c:&SignedCheckpoint,p:&RecoveryPolicy)->RecoveryDecision{
 match read_all(path){
  Ok(entries)=>assess_entries(&entries,c,p),
  Err(error)=>RecoveryDecision{
   verdict:"REJECT".into(),reasons:vec![format!("LEDGER_CORRUPTION_OR_READ_FAILURE: {error}")],
   signature_valid:false,record_sha256:checkpoint_hash(&c.record),local_entries:0,
   local_head_sha256:String::new(),may_append:false,may_recover_or_reclaim:false,
   physical_qualification_percent:0,operational_authority:"HOLD".into(),physical_act_allowed:false,
  },
 }
}
/// AETHER-204: checkpoint adjudication and append use the exact same OS-owned lock.
/// The caller's policy is only documentary; out-of-band authentication MUST be
/// established independently and checked again when the checkpoint is admitted.
/// No automatic recovery, lock seizure, or physical ACT is possible here.
pub fn append_with_checkpoint(path:&Path,event:Event,head:&str,count:u64,
 c:&SignedCheckpoint,p:&RecoveryPolicy)->Result<State,String>{
 let guard=crate::process_liveness::acquire(&path.with_extension("lock"))?;
 guard.verify_for(&path.with_extension("lock"))?;
 let entries=read_all(path).map_err(|e|format!("LEDGER_HOLD: {e}"))?;
 let assessment=assess_entries(&entries,c,p);
 if !assessment.may_append{
  return Err(format!("CHECKPOINT_HOLD: {}",assessment.reasons.join(",")));
 }
 if assessment.local_entries!=count||assessment.local_head_sha256!=head{
  return Err("STALE_CHECKPOINT_ADMISSION_HEAD".into());
 }
 // append_under_guard rereads history and compares expected head and count;
 // its file/dir fsync and complete readback occur while guard is still owned.
 crate::durable_ledger::append_under_guard(path,event,head,count,&guard)
}
