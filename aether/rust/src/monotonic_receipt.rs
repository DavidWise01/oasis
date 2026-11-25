//! AETHER-211-RS: forward-only signed receipt extension and holder rotation.
//! A later clock timestamp is NEVER proof of a forward history extension.
//! All decisions remain documentary; remote custody and physical ACT unverified.
use crate::{remote_anchor::{self,SignedAnchor,AnchorPolicy},receipt_custody};
use crate::{sha256_hex,PublicJwk};
use serde::{Serialize,Deserialize};
use p256::ecdsa::{signature::Verifier,Signature};

pub const ROTATION_SCHEMA:&str="AETHER-211/holder-rotation-v1";
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct Rotation {
 pub schema:String,pub old_anchor_sha256:String,pub new_anchor_sha256:String,
 pub old_holder_id:String,pub new_holder_id:String,
 pub old_holder_key_sha256:String,pub new_holder_key_sha256:String,
 pub authority_root:String,pub authority_operator:String,pub authority_admin:String,
 pub authorization_id:String,pub rotation_nonce:String,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct SignedRotation {pub record:Rotation,pub signature_hex:String}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct RotationPolicy {
 pub authority_key:PublicJwk,pub pinned_authority_key_sha256:String,
 pub independent_authority_authenticated_out_of_band:bool,
 pub expected_authorization_id:String,pub expected_nonce:String,
 #[serde(default)]pub prior_rotation_ids:std::collections::HashSet<String>,
 #[serde(default)]pub prior_rotation_nonces:std::collections::HashSet<String>,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct ExtensionDecision {
 pub verdict:String,pub reasons:Vec<String>,pub may_store_documentary_receipt:bool,
 pub may_recover:bool,pub physical_qualification_percent:u8,
 pub operational_authority:String,pub physical_act_allowed:bool,
}
fn hex64(v:&str)->bool{v.len()==64&&v.bytes().all(|x|x.is_ascii_hexdigit())}
fn canonical<T:Serialize>(v:&T)->Vec<u8>{serde_json::to_vec(v).unwrap_or_default()}
pub fn rotation_hash(v:&Rotation)->String{sha256_hex(&canonical(v))}
fn fail(reason:&str)->ExtensionDecision {
 ExtensionDecision{verdict:"REJECT".into(),reasons:vec![reason.into()],
 may_store_documentary_receipt:false,may_recover:false,
 physical_qualification_percent:0,operational_authority:"HOLD".into(),
 physical_act_allowed:false}
}
pub fn assess(
 previous:&receipt_custody::Entry,
 next:&SignedAnchor,next_policy:&AnchorPolicy,
 rotation:Option<&SignedRotation>,rotation_policy:Option<&RotationPolicy>,
)->ExtensionDecision {
 let old=&previous.signed_anchor.anchor;let new=&next.anchor;
 let old_hash=remote_anchor::anchor_hash(old);
 let next_hash=remote_anchor::anchor_hash(new);
 if new.ledger_id!=old.ledger_id {
  return fail("ANCHOR_LEDGER_CHANGED");
 }
 if new.prior_anchor_sha256!=old_hash{
  return fail("ANCHOR_PREDECESSOR_NOT_CONTIGUOUS");
 }
 if new.ledger_entries<=old.ledger_entries ||
    new.ledger_head_sha256==old.ledger_head_sha256{
  return fail("ANCHOR_NOT_FORWARD_PROGRESS");
 }
 // The AETHER-209 verifier independently checks the head hash at the new
 // sequence and the current registry digest, so sequence alone is insufficient.
 if new.registry_epoch<old.registry_epoch {
  return fail("ANCHOR_REGISTRY_EPOCH_ROLLBACK");
 }
 if new.source_root!=old.source_root ||
    new.source_operator!=old.source_operator ||
    new.source_admin!=old.source_admin ||
    new.issuer_root!=old.issuer_root ||
    new.issuer_operator!=old.issuer_operator ||
    new.issuer_admin!=old.issuer_admin {
  return fail("SOURCE_OR_ISSUER_ANCESTRY_CHANGED");
 }
 let same_holder=new.holder_id==old.holder_id &&
 new.holder_root==old.holder_root &&
 new.holder_operator==old.holder_operator &&
 new.holder_admin==old.holder_admin &&
 previous.receipt.holder_key_sha256==next_policy.pinned_holder_key_sha256;
 if same_holder {
  if rotation.is_some()||rotation_policy.is_some(){
   return fail("UNEXPECTED_HOLDER_ROTATION_PROOF");
  }
 } else {
  let Some(proof)=rotation else{return fail("UNAUTHORIZED_HOLDER_ROTATION");};
  let Some(policy)=rotation_policy else{return fail("MISSING_ROTATION_TRUST_ANCHOR");};
  let r=&proof.record;
  if r.schema!=ROTATION_SCHEMA||
   r.old_anchor_sha256!=old_hash||r.new_anchor_sha256!=next_hash||
   r.old_holder_id!=old.holder_id||r.new_holder_id!=new.holder_id||
   r.old_holder_key_sha256!=previous.receipt.holder_key_sha256||
   r.new_holder_key_sha256!=next_policy.pinned_holder_key_sha256 {
    return fail("ROTATION_BINDING_MISMATCH");
  }
  if r.authorization_id!=policy.expected_authorization_id ||
   r.rotation_nonce!=policy.expected_nonce||
   r.authorization_id.is_empty()||r.rotation_nonce.is_empty(){
   return fail("ROTATION_CHALLENGE_MISMATCH");
  }
  if policy.prior_rotation_ids.contains(&r.authorization_id)||
   policy.prior_rotation_nonces.contains(&r.rotation_nonce){
   return fail("REPLAYED_ROTATION_AUTHORIZATION");
  }
  if r.authority_root.is_empty()||
   r.authority_operator.is_empty()||r.authority_admin.is_empty()||
   [old.holder_root.as_str(),new.holder_root.as_str(),
     old.source_root.as_str(),old.issuer_root.as_str()].contains(&r.authority_root.as_str())||
   [old.holder_operator.as_str(),new.holder_operator.as_str(),
     old.source_operator.as_str(),old.issuer_operator.as_str()].contains(&r.authority_operator.as_str())||
   [old.holder_admin.as_str(),new.holder_admin.as_str(),
     old.source_admin.as_str(),old.issuer_admin.as_str()].contains(&r.authority_admin.as_str()){
   return fail("ROTATION_AUTHORITY_SHARED_ANCESTRY");
  }
  if !hex64(&policy.pinned_authority_key_sha256)||
   sha256_hex(&canonical(&policy.authority_key))!=policy.pinned_authority_key_sha256{
   return fail("ROTATION_AUTHORITY_PIN_MISMATCH");
  }
  let signature_valid=(||{
   let key=crate::verifying_key(&policy.authority_key).ok()?;
   let raw=hex::decode(&proof.signature_hex).ok()?;
   let signature=Signature::from_slice(&raw).ok()?;
   key.verify(&canonical(r),&signature).ok()?;
   Some(true)
  })().unwrap_or(false);
  if !signature_valid{return fail("ROTATION_AUTHORITY_SIGNATURE_INVALID");}
  if !policy.independent_authority_authenticated_out_of_band{
   return fail("ROTATION_AUTHORITY_ORIGIN_UNVERIFIED");
  }
 }
 ExtensionDecision{verdict:"DOCUMENTARY_FORWARD_EXTENSION_ONLY".into(),
 reasons:vec![],may_store_documentary_receipt:true,
 may_recover:false,physical_qualification_percent:0,
 operational_authority:"HOLD".into(),physical_act_allowed:false}
}
