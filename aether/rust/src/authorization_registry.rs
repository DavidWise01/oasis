//! AETHER-207-RS: durable authorization replay and revocation registry.
//! Ledger + registry updates share the same Linux process-owner lock.
//! Two-file writes are NOT a distributed/atomic transaction: an interrupted write
//! causes a fail-closed head mismatch until independently adjudicated.
//! Caller-provided trust pins do not authenticate external real-world ancestry.
use crate::{durable_ledger::{self,Event,State},custody_commit::{self,SignedTransition,TransitionPolicy},
  recovery_checkpoint::{SignedCheckpoint,RecoveryPolicy},
  external_custody::{Packet as CustodyPacket,Policy as CustodyPolicy}};
use serde::{Serialize,Deserialize};
use std::{collections::BTreeSet,fs::{self,File,OpenOptions},io::Write,path::Path};

pub const REGISTRY_SCHEMA:&str="AETHER-207/authorization-registry-v1";
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub struct Registry {
 pub schema:String,pub ledger_id:String,pub ledger_head_sha256:String,
 pub ledger_entries:u64,pub revocation_epoch:u64,
 pub pinned_issuer_key_sha256:String,pub pinned_holder_key_sha256:String,
 pub revoked_key_sha256:BTreeSet<String>,
 pub consumed_admission_ids:BTreeSet<String>,
 pub consumed_admission_nonces:BTreeSet<String>,
 pub consumed_authorization_ids:BTreeSet<String>,
 pub consumed_authorization_nonces:BTreeSet<String>,
 pub consumed_intent_sha256:BTreeSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct RegistryDecision {
 pub verdict:String,pub reasons:Vec<String>,pub ledger_entries:u64,
 pub ledger_head_sha256:String,pub registry_epoch:u64,
 pub physical_qualification_percent:u8,pub operational_authority:String,
 pub physical_act_allowed:bool,
}
pub fn registry_path(ledger:&Path)->std::path::PathBuf{ledger.with_extension("registry.json")}
fn temp_path(registry:&Path)->std::path::PathBuf{registry.with_extension("registry.pending")}
fn dir_sync(path:&Path)->Result<(),String>{
 let parent=path.parent().filter(|p|!p.as_os_str().is_empty()).unwrap_or(Path::new("."));
 File::open(parent).and_then(|f|f.sync_all()).map_err(|e|format!("DIR_SYNC: {e}"))
}
fn atomic_publish(path:&Path,r:&Registry)->Result<(),String>{
 let pending=temp_path(path);
 let mut f=OpenOptions::new().create_new(true).write(true).open(&pending)
   .map_err(|e|format!("REGISTRY_PENDING_OR_CREATE_FAILED: {e}"))?;
 let payload=serde_json::to_vec(r).map_err(|e|format!("REGISTRY_SERIALIZE: {e}"))?;
 f.write_all(&payload).map_err(|e|format!("REGISTRY_WRITE: {e}"))?;
 f.sync_all().map_err(|e|format!("REGISTRY_FSYNC: {e}"))?;
 fs::rename(&pending,path).map_err(|e|format!("REGISTRY_RENAME: {e}"))?;
 dir_sync(path)?;
 Ok(())
}
fn load(path:&Path)->Result<Registry,String>{
 if temp_path(path).exists(){return Err("REGISTRY_PENDING_TRANSACTION_HOLD".into());}
 let data=fs::read(path).map_err(|e|format!("REGISTRY_MISSING_OR_UNREADABLE: {e}"))?;
 serde_json::from_slice(&data).map_err(|_|"REGISTRY_CORRUPT_JSON".into())
}
fn check(r:&Registry,head:&str,count:u64,ledger_id:&str,issuer_pin:&str,holder_pin:&str,epoch:u64)
 ->Result<(),String>{
 if r.schema!=REGISTRY_SCHEMA||r.ledger_id!=ledger_id{return Err("REGISTRY_IDENTITY_MISMATCH".into());}
 if r.ledger_head_sha256!=head||r.ledger_entries!=count{return Err("REGISTRY_LEDGER_DIVERGENCE_HOLD".into());}
 if r.revocation_epoch!=epoch{return Err("REGISTRY_EPOCH_MISMATCH".into());}
 if r.pinned_issuer_key_sha256!=issuer_pin||r.pinned_holder_key_sha256!=holder_pin{
  return Err("REGISTRY_PIN_MISMATCH".into());
 }
 Ok(())
}
fn state(r:&Registry)->RegistryDecision{
 RegistryDecision{verdict:"DOCUMENTARY_REGISTRY_COHERENT".into(),reasons:vec![],
  ledger_entries:r.ledger_entries,ledger_head_sha256:r.ledger_head_sha256.clone(),
  registry_epoch:r.revocation_epoch,physical_qualification_percent:0,
  operational_authority:"HOLD".into(),physical_act_allowed:false}
}
/// Creates a local snapshot from the current ledger under the same lock.
/// Initial issuer/holder pins and revocation epoch MUST be independently
/// authenticated by the caller. This function cannot certify that fact.
pub fn initialize(ledger:&Path,ledger_id:&str,issuer_pin:&str,holder_pin:&str,epoch:u64)
 ->Result<RegistryDecision,String>{
 if ledger_id.is_empty()||issuer_pin.len()!=64||holder_pin.len()!=64||epoch==0{
  return Err("INVALID_INITIAL_REGISTRY_PINS".into());
 }
 let path=registry_path(ledger);
 let lock_path=ledger.with_extension("lock");
 let guard=crate::process_liveness::acquire(&lock_path)?;
 guard.verify_for(&lock_path)?;
 if path.exists()||temp_path(&path).exists(){return Err("REGISTRY_ALREADY_EXISTS_OR_PENDING".into());}
 let current=durable_ledger::read_all(ledger).map_err(|e|format!("LEDGER_HOLD: {e}"))?;
 let r=Registry{schema:REGISTRY_SCHEMA.into(),ledger_id:ledger_id.into(),
  ledger_head_sha256:current.last().map(|e|e.entry_sha256.clone())
    .unwrap_or_else(||durable_ledger::GENESIS.into()),
  ledger_entries:current.len() as u64,revocation_epoch:epoch,
  pinned_issuer_key_sha256:issuer_pin.into(),pinned_holder_key_sha256:holder_pin.into(),
  revoked_key_sha256:BTreeSet::new(),consumed_admission_ids:BTreeSet::new(),
  consumed_admission_nonces:BTreeSet::new(),consumed_authorization_ids:BTreeSet::new(),
  consumed_authorization_nonces:BTreeSet::new(),consumed_intent_sha256:BTreeSet::new()};
 atomic_publish(&path,&r)?;
 guard.verify_for(&lock_path)?;
 Ok(state(&r))
}
pub fn inspect(ledger:&Path)->Result<RegistryDecision,String>{
 let current=durable_ledger::read_all(ledger).map_err(|e|format!("LEDGER_HOLD: {e}"))?;
 let r=load(&registry_path(ledger))?;
 let head=current.last().map(|e|e.entry_sha256.clone())
   .unwrap_or_else(||durable_ledger::GENESIS.into());
 check(&r,&head,current.len() as u64,&r.ledger_id,
   &r.pinned_issuer_key_sha256,&r.pinned_holder_key_sha256,r.revocation_epoch)?;
 Ok(state(&r))
}
/// One OS lock spans persistent registry load, checkpoint, custody,
/// transition screening, fsynced journal append, and registry publication.
/// Any mismatch leaves future admission on HOLD; no automatic repair.
pub fn append_registered(
 path:&Path,event:Event,head:&str,count:u64,
 checkpoint:&SignedCheckpoint,recovery:&RecoveryPolicy,
 custody:&CustodyPacket,custody_policy:&CustodyPolicy,
 signed:&SignedTransition,transition_policy:&TransitionPolicy
)->Result<State,String>{
 let lock_path=path.with_extension("lock");
 let guard=crate::process_liveness::acquire(&lock_path)?;
 guard.verify_for(&lock_path)?;
 let registry_path=registry_path(path);
 let mut r=load(&registry_path)?;
 let actual=durable_ledger::read_all(path).map_err(|e|format!("LEDGER_HOLD: {e}"))?;
 let current=actual.last().map(|x|x.entry_sha256.clone())
   .unwrap_or_else(||durable_ledger::GENESIS.into());
 check(&r,&current,actual.len() as u64,&custody.admission.ledger_id,
  &transition_policy.pinned_issuer_key_sha256,
  &transition_policy.pinned_holder_key_sha256,custody.admission.policy_epoch)?;
 if current!=head||r.ledger_entries!=count{return Err("STALE_REGISTRY_ADMISSION_HEAD".into());}
 if !r.revoked_key_sha256.is_empty() && (
  r.revoked_key_sha256.contains(&r.pinned_issuer_key_sha256)
  ||r.revoked_key_sha256.contains(&r.pinned_holder_key_sha256)){
  return Err("PERSISTED_ISSUER_OR_HOLDER_REVOKED".into());
 }
 let id=&signed.intent.authorization_id;
 let nonce=&signed.intent.authorization_nonce;
 let intent_digest=custody_commit::intent_hash(&signed.intent);
 if r.consumed_admission_ids.contains(&custody.admission.admission_id)
 ||r.consumed_admission_nonces.contains(&custody.admission.authorization_nonce)
 ||r.consumed_authorization_ids.contains(id)
 ||r.consumed_authorization_nonces.contains(nonce)
 ||r.consumed_intent_sha256.contains(&intent_digest){
  return Err("PERSISTED_AUTHORIZATION_REPLAY".into());
 }
 // Registry is authoritative for revocations/replay, not the caller's mutable sets.
 // Reject contradictory caller input rather than silently weakening checks.
 if custody_policy.revoked_key_sha256.iter().any(|x|!r.revoked_key_sha256.contains(x)){
  return Err("CALLER_REVOCATION_REGISTRY_DIVERGENCE".into());
 }
 let mut cp=custody_policy.clone();
 cp.revoked_key_sha256=r.revoked_key_sha256.iter().cloned().collect();
 cp.used_admission_ids=r.consumed_admission_ids.iter().cloned().collect();
 cp.used_nonces=r.consumed_admission_nonces.iter().cloned().collect();
 let mut tp=transition_policy.clone();
 tp.seen_authorization_ids=r.consumed_authorization_ids.iter().cloned().collect();
 tp.seen_authorization_nonces=r.consumed_authorization_nonces.iter().cloned().collect();
 tp.seen_intent_hashes=r.consumed_intent_sha256.iter().cloned().collect();
 let result=custody_commit::append_with_custody_under_guard(path,event,head,count,
  checkpoint,recovery,custody,&cp,signed,&tp,&guard)?;
 r.ledger_head_sha256=result.head_sha256.clone();
 r.ledger_entries=result.entries;
 r.consumed_admission_ids.insert(custody.admission.admission_id.clone());
 r.consumed_admission_nonces.insert(custody.admission.authorization_nonce.clone());
 r.consumed_authorization_ids.insert(id.clone());
 r.consumed_authorization_nonces.insert(nonce.clone());
 r.consumed_intent_sha256.insert(intent_digest);
 // If this publication fails, journal may be ahead. Subsequent calls detect mismatch
 // and refuse further admission until independently reviewed recovery.
 atomic_publish(&registry_path,&r)?;
 guard.verify_for(&lock_path)?;
 let readback=load(&registry_path)?;
 if readback!=r{return Err("REGISTRY_READBACK_MISMATCH".into());}
 Ok(result)
}
/// Signed external revocation procedures are NOT implemented in AETHER-207.
/// Local revocation amendments may be staged only after independent custody
/// qualification in a later bound. Never trust caller toggles as approval.
pub fn stage_revocation_unsupported()->Result<(),String>{
 Err("REVOCATION_AMENDMENT_REQUIRES_INDEPENDENT_SIGNED_AUTHORITY".into())
}
