//! AETHER-205-RS: externally pinned custody issuer and independently witnessed rotation.
//! All externally authenticated flags are caller assertions, NOT verified external custody.
//! No physical authority or self-issued admission can be derived from this module.
use crate::{sha256_hex,PublicJwk};
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Deserialize,Serialize};
use std::collections::{BTreeSet,HashSet};

pub const SCHEMA:&str="AETHER-205/custody-admission-v1";
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Admission {
 pub schema:String,pub admission_id:String,pub checkpoint_sha256:String,
 pub ledger_id:String,pub holder_id:String,pub holder_root:String,
 pub holder_operator:String,pub holder_admin:String,pub holder_key:PublicJwk,
 pub issuer_id:String,pub issuer_root:String,pub issuer_operator:String,pub issuer_admin:String,
 pub source_root:String,pub source_operator:String,pub source_admin:String,
 pub issuer_key_id:String,pub authorization_nonce:String,pub policy_epoch:u64,
 pub previous_holder_key_sha256:String,pub rotation_approval_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct RotationApproval {
 pub schema:String,pub approval_id:String,pub admission_id:String,
 pub old_holder_key_sha256:String,pub new_holder_key_sha256:String,
 pub approving_root:String,pub approving_operator:String,pub approving_admin:String,
 pub approval_nonce:String,pub epoch:u64,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Packet {
 pub admission:Admission,pub issuer_signature_hex:String,
 pub holder_signature_hex:String,
 pub rotation:Option<RotationApproval>,pub rotation_signature_hex:Option<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Policy {
 pub ledger_id:String,pub checkpoint_sha256:String,pub holder_id:String,
 pub issuer_id:String,pub issuer_key_id:String,
 pub pinned_issuer_key_sha256:String,pub pinned_holder_key_sha256:String,
 pub pinned_rotation_key_sha256:String,
 pub issuer_key:PublicJwk,pub rotation_key:PublicJwk,
 pub previous_holder_key_sha256:String,
 pub expected_policy_epoch:u64,pub required_nonce:String,
 pub issuer_externally_authenticated:bool,pub holder_externally_authenticated:bool,
 pub rotation_authority_externally_authenticated:bool,
 #[serde(default)]pub revoked_key_sha256:HashSet<String>,
 #[serde(default)]pub used_admission_ids:HashSet<String>,
 #[serde(default)]pub used_rotation_ids:HashSet<String>,
 #[serde(default)]pub used_nonces:HashSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Decision {
 pub verdict:String,pub reasons:Vec<String>,
 pub issuer_signature_valid:bool,pub holder_signature_valid:bool,pub rotation_signature_valid:bool,
 pub proposed_admission_id:Option<String>,
 pub admitted_holder_key_sha256:Option<String>,
 pub physical_qualification_percent:u8,pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(record:&T)->Vec<u8>{serde_json::to_vec(record).unwrap_or_default()}
pub fn fingerprint(key:&PublicJwk)->String{sha256_hex(&canonical(key))}
pub fn admission_hash(a:&Admission)->String{sha256_hex(&canonical(a))}
pub fn rotation_hash(a:&RotationApproval)->String{sha256_hex(&canonical(a))}
fn hash(v:&str)->bool{v.len()==64&&v.bytes().all(|b|b.is_ascii_hexdigit())}
fn sig<T:Serialize>(record:&T,signature_hex:&str,key:&PublicJwk)->bool{
 let Ok(public)=crate::verifying_key(key)else{return false};
 let Ok(bytes)=hex::decode(signature_hex)else{return false};
 let Ok(signature)=Signature::from_slice(&bytes)else{return false};
 public.verify(&canonical(record),&signature).is_ok()
}
pub fn assess(packet:&Packet,policy:&Policy)->Decision{
 let a=&packet.admission;
 let issuer_hash=fingerprint(&policy.issuer_key);
 let holder_hash=fingerprint(&a.holder_key);
 let rotation_key_hash=fingerprint(&policy.rotation_key);
 let mut faults=BTreeSet::new();
 let mut fail=|name:&str|{faults.insert(name.to_string());};
 if a.schema!=SCHEMA{fail("ADMISSION_SCHEMA_INVALID");}
 if a.admission_id.is_empty()||a.authorization_nonce.is_empty()
 ||a.authorization_nonce!=policy.required_nonce{fail("ADMISSION_NONCE_OR_ID_INVALID");}
 if a.ledger_id!=policy.ledger_id||a.ledger_id.is_empty()
 ||a.checkpoint_sha256!=policy.checkpoint_sha256||!hash(&a.checkpoint_sha256){
  fail("EXTERNAL_CHECKPOINT_BINDING_MISMATCH");
 }
 if a.holder_id!=policy.holder_id||a.issuer_id!=policy.issuer_id
 ||a.issuer_key_id!=policy.issuer_key_id{fail("ISSUER_OR_HOLDER_IDENTITY_MISMATCH");}
 if a.policy_epoch!=policy.expected_policy_epoch || a.policy_epoch==0{fail("POLICY_EPOCH_MISMATCH");}
 if [&a.holder_root,&a.holder_operator,&a.holder_admin,&a.issuer_root,
 &a.issuer_operator,&a.issuer_admin,&a.source_root,&a.source_operator,&a.source_admin]
 .iter().any(|v|v.trim().is_empty()){fail("MISSING_ANCESTRY");}
 if a.holder_root==a.issuer_root||a.holder_root==a.source_root
 ||a.issuer_root==a.source_root
 ||a.holder_operator==a.issuer_operator||a.holder_operator==a.source_operator
 ||a.issuer_operator==a.source_operator
 ||a.holder_admin==a.issuer_admin||a.holder_admin==a.source_admin
 ||a.issuer_admin==a.source_admin{fail("SHARED_OR_SELF_ISSUED_ANCESTRY");}
 if issuer_hash!=policy.pinned_issuer_key_sha256
 ||!hash(&policy.pinned_issuer_key_sha256){fail("ISSUER_PIN_MISMATCH");}
 if holder_hash!=policy.pinned_holder_key_sha256
 ||!hash(&policy.pinned_holder_key_sha256){fail("HOLDER_PIN_MISMATCH");}
 if policy.revoked_key_sha256.contains(&issuer_hash)
 ||policy.revoked_key_sha256.contains(&holder_hash){fail("REVOKED_ISSUER_OR_HOLDER");}
 if policy.used_admission_ids.contains(&a.admission_id)
 ||policy.used_nonces.contains(&a.authorization_nonce){fail("REPLAYED_ADMISSION");}
 let issuer_signature_valid=sig(a,&packet.issuer_signature_hex,&policy.issuer_key);
 let holder_signature_valid=sig(a,&packet.holder_signature_hex,&a.holder_key);
 if !issuer_signature_valid{fail("ISSUER_SIGNATURE_INVALID");}
 if !holder_signature_valid{fail("HOLDER_POSSESSION_SIGNATURE_INVALID");}
 if !policy.issuer_externally_authenticated || !policy.holder_externally_authenticated{
  fail("EXTERNAL_ORIGIN_UNAUTHENTICATED");
 }
 let rotating=holder_hash!=policy.previous_holder_key_sha256;
 let mut rotation_signature_valid=false;
 if rotating{
  let Some(rot)=packet.rotation.as_ref() else {
   fail("UNAPPROVED_HOLDER_KEY_ROTATION");
   return finish(faults,issuer_signature_valid,holder_signature_valid,false,a,holder_hash);
  };
  if rot.schema!="AETHER-205/rotation-v1"||rot.approval_id.is_empty()
  ||rot.admission_id!=a.admission_id||rot.epoch!=a.policy_epoch
  ||rot.old_holder_key_sha256!=policy.previous_holder_key_sha256
  ||rot.old_holder_key_sha256!=a.previous_holder_key_sha256
  ||rot.new_holder_key_sha256!=holder_hash
  ||rot.approval_nonce.is_empty()||rot.approval_nonce==a.authorization_nonce
  ||a.rotation_approval_sha256!=rotation_hash(rot){fail("ROTATION_BINDING_INVALID");}
  if rot.approving_root.is_empty()||rot.approving_operator.is_empty()
  ||rot.approving_admin.is_empty()||rot.approving_root==a.holder_root
  ||rot.approving_root==a.issuer_root||rot.approving_root==a.source_root
  ||rot.approving_operator==a.holder_operator||rot.approving_operator==a.issuer_operator
  ||rot.approving_operator==a.source_operator
  ||rot.approving_admin==a.holder_admin||rot.approving_admin==a.issuer_admin
  ||rot.approving_admin==a.source_admin{fail("ROTATION_APPROVER_NOT_INDEPENDENT");}
  if policy.pinned_rotation_key_sha256!=rotation_key_hash
  ||!hash(&policy.pinned_rotation_key_sha256){fail("ROTATION_ROOT_PIN_MISMATCH");}
  if policy.revoked_key_sha256.contains(&rotation_key_hash){fail("REVOKED_ROTATION_AUTHORITY");}
  if policy.used_rotation_ids.contains(&rot.approval_id)
  ||policy.used_nonces.contains(&rot.approval_nonce){fail("REPLAYED_ROTATION_APPROVAL");}
  rotation_signature_valid=packet.rotation_signature_hex.as_deref()
    .map(|signature|sig(rot,signature,&policy.rotation_key)).unwrap_or(false);
  if !rotation_signature_valid{fail("ROTATION_APPROVAL_SIGNATURE_INVALID");}
  if !policy.rotation_authority_externally_authenticated{fail("ROTATION_AUTHORITY_UNAUTHENTICATED");}
 }else if a.previous_holder_key_sha256!=holder_hash
  ||packet.rotation.is_some()||packet.rotation_signature_hex.is_some()
  ||!a.rotation_approval_sha256.is_empty(){fail("UNEXPECTED_ROTATION_DATA");}
 finish(faults,issuer_signature_valid,holder_signature_valid,rotation_signature_valid,a,holder_hash)
}
fn finish(
 faults:BTreeSet<String>,issuer:bool,holder:bool,rotation:bool,
 admission:&Admission,holder_hash:String
)->Decision{
 let reasons:Vec<String>=faults.into_iter().collect();
 let valid=reasons.is_empty();
 Decision{verdict:if valid{"DOCUMENTARY_CUSTODY_ADMISSION_ONLY"}else{"REJECT"}.into(),
 reasons,issuer_signature_valid:issuer,holder_signature_valid:holder,
 rotation_signature_valid:rotation,
 proposed_admission_id:valid.then(||admission.admission_id.clone()),
 admitted_holder_key_sha256:valid.then_some(holder_hash),
 physical_qualification_percent:0,operational_authority:"HOLD".into(),
 physical_act_allowed:false}
}
