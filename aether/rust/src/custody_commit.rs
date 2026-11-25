//! AETHER-206-RS — custody-bound atomic documentary ledger transition.
//! One Linux OS-owned lock protects custody screening, checkpoint verification,
//! signed transition authorization, fsync append, and full chain readback.
//! Trust-policy pins MUST be independently provisioned; no physical ACT possible.
use crate::{sha256_hex,PublicJwk};
use crate::durable_ledger::{self,Event,State};
use crate::recovery_checkpoint::{self,SignedCheckpoint,RecoveryPolicy};
use crate::external_custody::{self,Packet as CustodyPacket,Policy as CustodyPolicy};
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Serialize,Deserialize};
use std::{collections::{BTreeSet,HashSet},path::Path};

pub const SCHEMA:&str="AETHER-206/transition-v1";
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct TransitionIntent {
 pub schema:String,pub authorization_id:String,pub ledger_id:String,
 pub checkpoint_sha256:String,pub custody_admission_sha256:String,
 pub expected_head_sha256:String,pub expected_entries:u64,pub next_sequence:u64,
 pub event_sha256:String,pub event_id:String,pub capture_sha256:String,
 pub challenge_nonce:String,pub review_id:String,pub payload_sha256:String,
 pub authorization_nonce:String,pub holder_key_sha256:String,pub issuer_key_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct SignedTransition {
 pub intent:TransitionIntent,pub holder_signature_hex:String,
 pub issuer_signature_hex:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct TransitionPolicy {
 pub expected_authorization_id:String,pub expected_authorization_nonce:String,
 pub expected_intent_sha256:String,
 pub pinned_issuer_key_sha256:String,pub pinned_holder_key_sha256:String,
 #[serde(default)]pub seen_authorization_ids:HashSet<String>,
 #[serde(default)]pub seen_authorization_nonces:HashSet<String>,
 #[serde(default)]pub seen_intent_hashes:HashSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct TransitionDecision{
 pub verdict:String,pub reasons:Vec<String>,pub intent_sha256:String,
 pub issuer_signature_valid:bool,pub holder_signature_valid:bool,
 pub may_commit:bool,pub physical_qualification_percent:u8,
 pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(v:&T)->Vec<u8>{serde_json::to_vec(v).unwrap_or_default()}
pub fn intent_hash(v:&TransitionIntent)->String{sha256_hex(&canonical(v))}
pub fn event_hash(v:&Event)->String{sha256_hex(&canonical(v))}
fn hex64(v:&str)->bool{v.len()==64&&v.bytes().all(|b|b.is_ascii_hexdigit())}
fn verify<T:Serialize>(v:&T,hex_signature:&str,key:&PublicJwk)->bool{
 let Ok(k)=crate::verifying_key(key)else{return false};
 let Ok(bytes)=hex::decode(hex_signature)else{return false};
 let Ok(s)=Signature::from_slice(&bytes)else{return false};
 k.verify(&canonical(v),&s).is_ok()
}
pub fn assess_transition(
 packet:&SignedTransition,policy:&TransitionPolicy,
 event:&Event,head:&str,count:u64,
 checkpoint:&SignedCheckpoint,custody:&CustodyPacket,
 custody_policy:&CustodyPolicy
)->TransitionDecision{
 let t=&packet.intent;let mut issues=BTreeSet::new();
 let mut fail=|msg:&str|{issues.insert(msg.to_string());};
 let expected_seq=count.checked_add(1);
 if t.schema!=SCHEMA{fail("INTENT_SCHEMA_MISMATCH");}
 if t.authorization_id.is_empty()||t.authorization_id!=policy.expected_authorization_id||
 t.authorization_nonce.is_empty()||t.authorization_nonce!=policy.expected_authorization_nonce{
  fail("AUTHORIZATION_ID_OR_NONCE_MISMATCH");
 }
 let calculated=intent_hash(t);
 if calculated!=policy.expected_intent_sha256||!hex64(&policy.expected_intent_sha256){
  fail("EXTERNAL_INTENT_PIN_MISMATCH");
 }
 if t.ledger_id!=custody.admission.ledger_id||
 t.ledger_id!=checkpoint.record.ledger_id{
  fail("LEDGER_BINDING_MISMATCH");
 }
 if t.checkpoint_sha256!=recovery_checkpoint::checkpoint_hash(&checkpoint.record)||
 t.custody_admission_sha256!=external_custody::admission_hash(&custody.admission){
  fail("CHECKPOINT_OR_CUSTODY_ADMISSION_MISMATCH");
 }
 if t.expected_head_sha256!=head||t.expected_entries!=count||
 expected_seq!=Some(t.next_sequence){
  fail("STALE_OR_REORDERED_TRANSITION_HEAD");
 }
 if t.event_sha256!=event_hash(event)||
 t.event_id!=event.event_id||t.capture_sha256!=event.capture_sha256||
 t.challenge_nonce!=event.challenge_nonce||t.review_id!=event.review_id||
 t.payload_sha256!=event.payload_sha256{
  fail("EVENT_NOT_BOUND_TO_AUTHORIZATION");
 }
 // The issuer and holder sign the exact same transition intent. Their keys
 // must match custody's pre-pinned keys; a valid unrelated signature is rejected.
 let issuer_hash=external_custody::fingerprint(&custody_policy.issuer_key);
 let holder_hash=external_custody::fingerprint(&custody.admission.holder_key);
 if t.issuer_key_sha256!=issuer_hash||t.holder_key_sha256!=holder_hash||
 policy.pinned_issuer_key_sha256!=issuer_hash||
 policy.pinned_holder_key_sha256!=holder_hash{
  fail("TRANSITION_SIGNER_KEY_PIN_MISMATCH");
 }
 if policy.seen_authorization_ids.contains(&t.authorization_id)||
 policy.seen_authorization_nonces.contains(&t.authorization_nonce)||
 policy.seen_intent_hashes.contains(&calculated){
  fail("REPLAYED_TRANSITION_AUTHORIZATION");
 }
 let issuer_signature_valid=verify(t,&packet.issuer_signature_hex,&custody_policy.issuer_key);
 let holder_signature_valid=verify(t,&packet.holder_signature_hex,&custody.admission.holder_key);
 if !issuer_signature_valid{fail("TRANSITION_ISSUER_SIGNATURE_INVALID");}
 if !holder_signature_valid{fail("TRANSITION_HOLDER_SIGNATURE_INVALID");}
 let reasons:Vec<String>=issues.into_iter().collect();let admitted=reasons.is_empty();
 TransitionDecision{
  verdict:if admitted{"DOCUMENTARY_TRANSITION_AUTHORIZED"}else{"REJECT"}.into(),
  reasons,intent_sha256:calculated,issuer_signature_valid,holder_signature_valid,
  may_commit:admitted,physical_qualification_percent:0,operational_authority:"HOLD".into(),
  physical_act_allowed:false,
 }
}
/// All checks that can authorize a write happen while holding the same guard.
/// Fails closed on rejected custody, checkpoint, intent, local history or lock.
pub fn append_with_custody(
 path:&Path,event:Event,head:&str,count:u64,
 checkpoint:&SignedCheckpoint,recovery_policy:&RecoveryPolicy,
 custody:&CustodyPacket,custody_policy:&CustodyPolicy,
 signed:&SignedTransition,transition_policy:&TransitionPolicy
)->Result<State,String>{
 let lock_path=path.with_extension("lock");
 let guard=crate::process_liveness::acquire(&lock_path)?;
 guard.verify_for(&lock_path)?;
 let entries=durable_ledger::read_all(path).map_err(|e|format!("LEDGER_HOLD: {e}"))?;
 let recovered=recovery_checkpoint::assess_entries(&entries,checkpoint,recovery_policy);
 if !recovered.may_append{
  return Err(format!("CHECKPOINT_HOLD: {}",recovered.reasons.join(",")));
 }
 if recovered.local_entries!=count||recovered.local_head_sha256!=head{
  return Err("STALE_CHECKPOINT_ADMISSION_HEAD".into());
 }
 let admitted=external_custody::assess(custody,custody_policy);
 if admitted.proposed_admission_id.is_none(){
  return Err(format!("CUSTODY_HOLD: {}",admitted.reasons.join(",")));
 }
 if custody.admission.checkpoint_sha256!=recovery_checkpoint::checkpoint_hash(&checkpoint.record)||
 custody.admission.ledger_id!=checkpoint.record.ledger_id{
  return Err("CUSTODY_CHECKPOINT_BINDING_MISMATCH".into());
 }
 let signed_decision=assess_transition(
  signed,transition_policy,&event,head,count,checkpoint,custody,custody_policy
 );
 if !signed_decision.may_commit{
  return Err(format!("TRANSITION_HOLD: {}",signed_decision.reasons.join(",")));
 }
 guard.verify_for(&lock_path)?;
 durable_ledger::append_under_guard(path,event,head,count,&guard)
}
