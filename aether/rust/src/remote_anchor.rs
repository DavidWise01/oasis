//! AETHER-209-RS — remote-anchor verification against a local ledger+registry pair.
//! Signed remote-receipt assertions are insufficient without separately authenticated custody.
//! This module cannot create independent remote custody and never authorizes physical ACT.
use crate::{sha256_hex,PublicJwk};
use crate::durable_ledger::{self,Entry};
use crate::authorization_registry::{self,Registry};
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Serialize,Deserialize};
use std::{collections::{BTreeSet,HashSet},fs,path::Path};

pub const SCHEMA:&str="AETHER-209/external-anchor-v1";
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Anchor{
 pub schema:String,pub anchor_id:String,pub ledger_id:String,
 pub ledger_entries:u64,pub ledger_head_sha256:String,pub registry_sha256:String,
 pub registry_epoch:u64,pub prior_anchor_sha256:String,pub custody_nonce:String,
 pub holder_id:String,pub holder_root:String,pub holder_operator:String,pub holder_admin:String,
 pub issuer_root:String,pub issuer_operator:String,pub issuer_admin:String,
 pub source_root:String,pub source_operator:String,pub source_admin:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct SignedAnchor{pub anchor:Anchor,pub signature_hex:String}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct AnchorPolicy{
 pub ledger_id:String,pub expected_anchor_id:String,pub required_nonce:String,
 pub pinned_anchor_sha256:String,pub prior_anchor_sha256:String,
 pub holder_id:String,pub holder_root:String,pub pinned_holder_key_sha256:String,
 pub holder_key:PublicJwk,pub holder_out_of_band_authenticated:bool,
 pub independently_retained_remote_receipt_verified:bool,
 #[serde(default)]pub seen_anchor_ids:HashSet<String>,
 #[serde(default)]pub seen_nonces:HashSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Verdict{
 pub result:String,pub reasons:Vec<String>,pub signature_valid:bool,
 pub anchor_sha256:String,pub local_entries:u64,
 pub may_recover:bool,pub may_append:bool,
 pub physical_qualification_percent:u8,pub operational_authority:String,
 pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(v:&T)->Vec<u8>{serde_json::to_vec(v).unwrap_or_default()}
pub fn anchor_hash(a:&Anchor)->String{sha256_hex(&canonical(a))}
pub fn key_hash(key:&PublicJwk)->String{sha256_hex(&canonical(key))}
fn hex64(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
pub fn inspect_records(
 entries:&[Entry],registry:&Registry,anchor:&SignedAnchor,policy:&AnchorPolicy
)->Verdict{
 let a=&anchor.anchor;let mut issues=BTreeSet::new();
 let mut fail=|s:&str|{issues.insert(s.to_owned());};
 if a.schema!=SCHEMA||a.anchor_id.is_empty()||a.anchor_id!=policy.expected_anchor_id
 ||a.custody_nonce.is_empty()||a.custody_nonce!=policy.required_nonce{
  fail("ANCHOR_ID_OR_NONCE_MISMATCH");
 }
 let hash=anchor_hash(a);
 if hash!=policy.pinned_anchor_sha256||!hex64(&policy.pinned_anchor_sha256){
  fail("REMOTE_ANCHOR_PIN_MISMATCH");
 }
 if a.prior_anchor_sha256!=policy.prior_anchor_sha256||
 !hex64(&a.prior_anchor_sha256){fail("ANCHOR_PREDECESSOR_MISMATCH");}
 if a.ledger_id!=policy.ledger_id||registry.ledger_id!=policy.ledger_id{
  fail("LEDGER_ID_MISMATCH");
 }
 if a.holder_id!=policy.holder_id||a.holder_root!=policy.holder_root{
  fail("REMOTE_HOLDER_IDENTITY_MISMATCH");
 }
 if [&a.holder_root,&a.holder_operator,&a.holder_admin,
 &a.issuer_root,&a.issuer_operator,&a.issuer_admin,
 &a.source_root,&a.source_operator,&a.source_admin]
 .iter().any(|s|s.trim().is_empty()){fail("ANCHOR_ANCESTRY_MISSING");}
 if a.holder_root==a.issuer_root||a.holder_root==a.source_root||
 a.issuer_root==a.source_root||a.holder_operator==a.issuer_operator||
 a.holder_operator==a.source_operator||a.issuer_operator==a.source_operator||
 a.holder_admin==a.issuer_admin||a.holder_admin==a.source_admin||
 a.issuer_admin==a.source_admin{fail("ANCESTRY_NOT_DISTINCT");}
 if a.ledger_entries==0||!hex64(&a.ledger_head_sha256)
 ||a.ledger_entries>entries.len() as u64{
  fail("ANCHOR_PROVES_LOCAL_ROLLBACK");
 }else if entries.get(a.ledger_entries as usize-1)
   .map(|e|e.entry_sha256.as_str())!=Some(a.ledger_head_sha256.as_str()){
  fail("ANCHOR_HISTORY_DIVERGENCE");
 }
 let current_head=entries.last().map(|e|e.entry_sha256.clone())
  .unwrap_or_else(||durable_ledger::GENESIS.into());
 if registry.ledger_entries!=entries.len() as u64||
 registry.ledger_head_sha256!=current_head{
  fail("REGISTRY_JOURNAL_DIVERGENCE");
 }
 // Registry hash is a *snapshot*: admit only the exact externally anchored
 // registry generation. Later append requires a newly authenticated anchor.
 if a.registry_sha256!=sha256_hex(&canonical(registry))||
 a.registry_epoch!=registry.revocation_epoch{
  fail("REGISTRY_SNAPSHOT_NOT_ANCHORED");
 }
 if policy.seen_anchor_ids.contains(&a.anchor_id)||
 policy.seen_nonces.contains(&a.custody_nonce){fail("REPLAYED_REMOTE_ANCHOR");}
 if key_hash(&policy.holder_key)!=policy.pinned_holder_key_sha256||
 !hex64(&policy.pinned_holder_key_sha256){
  fail("REMOTE_HOLDER_KEY_PIN_MISMATCH");
 }
 let signature_valid=(||{
  let key=crate::verifying_key(&policy.holder_key).ok()?;
  let bytes=hex::decode(&anchor.signature_hex).ok()?;
  let signature=Signature::from_slice(&bytes).ok()?;
  key.verify(&canonical(a),&signature).ok()?;Some(true)
 })().unwrap_or(false);
 if !signature_valid{fail("REMOTE_ANCHOR_SIGNATURE_INVALID");}
 if !policy.holder_out_of_band_authenticated||
 !policy.independently_retained_remote_receipt_verified{
  fail("REMOTE_CUSTODY_NOT_AUTHENTICATED");
 }
 let reasons:Vec<String>=issues.into_iter().collect();
 // This bound is an observation gate, not a recovery/ACT mechanism.
 Verdict{result:if reasons.is_empty(){"DOCUMENTARY_REMOTE_ANCHOR_CONSISTENT"}else{"REJECT"}.into(),
 reasons,signature_valid,anchor_sha256:hash,local_entries:entries.len() as u64,
 may_recover:false,may_append:false,physical_qualification_percent:0,
 operational_authority:"HOLD".into(),physical_act_allowed:false}
}
pub fn inspect_file(ledger:&Path,anchor:&SignedAnchor,policy:&AnchorPolicy)->Verdict{
 let failure=|reason:String|Verdict{result:"REJECT".into(),reasons:vec![reason],
 signature_valid:false,anchor_sha256:anchor_hash(&anchor.anchor),local_entries:0,
 may_recover:false,may_append:false,physical_qualification_percent:0,
 operational_authority:"HOLD".into(),physical_act_allowed:false};
 let entries=match durable_ledger::read_all(ledger){
  Ok(e)=>e,Err(e)=>return failure(format!("LEDGER_HOLD: {e}")),
 };
 let path=authorization_registry::registry_path(ledger);
 if path.with_extension("pending").exists(){
  return failure("REGISTRY_PENDING_TRANSACTION_HOLD".into());
 }
 let bytes=match fs::read(&path){
  Ok(v)=>v,Err(e)=>return failure(format!("REGISTRY_READ_HOLD: {e}")),
 };
 let registry:Registry=match serde_json::from_slice(&bytes){
  Ok(v)=>v,Err(_)=>return failure("REGISTRY_CORRUPT_JSON".into()),
 };
 inspect_records(&entries,&registry,anchor,policy)
}
