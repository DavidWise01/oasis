//! AETHER-198-RS blind external review. Software-only; ACT HOLD.
use crate::PublicJwk;
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Serialize,Deserialize};
use std::collections::{BTreeSet,HashSet};
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Evidence {
 pub schema:String,pub review_id:String,pub capture_id:String,pub challenge_id:String,
 pub capture_sha256:String,pub source_receipt_sha256:String,pub custody_sha256:String,pub calibration_sha256:String,
 pub source_root:String,pub custody_root:String,pub calibration_root:String,pub verifier_root:String,
 pub source_operator:String,pub verifier_operator:String,pub source_admin:String,pub verifier_admin:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Review {pub schema:String,pub review_id:String,pub evidence_sha256:String,pub nonce:String,pub verdict:String}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Packet {pub evidence:Evidence,pub review:Review,pub signature_hex:String}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Policy {
 pub capture_sha256:String,pub source_receipt_sha256:String,pub custody_sha256:String,
 pub calibration_sha256:String,pub challenge_id:String,pub nonce:String,
 pub verifier_public_key:PublicJwk,pub source_authenticated:bool,pub custody_authenticated:bool,
 pub calibration_authenticated:bool,pub verifier_authenticated:bool,
 pub seen_reviews:HashSet<String>,pub seen_nonces:HashSet<String>,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Decision {
 pub verdict:String,pub reasons:Vec<String>,pub signature_valid:bool,pub evidence_sha256:String,
 pub proposed_review:Option<String>,pub physical_qualification_percent:u8,
 pub operational_authority:String,pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(v:&T)->Vec<u8>{serde_json::to_vec(v).unwrap_or_default()}
pub fn evidence_sha256(e:&Evidence)->String{crate::sha256_hex(&canonical(e))}
fn hash(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
fn verify(r:&Review,sig:&str,jwk:&PublicJwk)->bool{
 let Ok(key)=crate::verifying_key(jwk)else{return false};
 let Ok(bytes)=hex::decode(sig)else{return false};
 let Ok(signature)=Signature::from_slice(&bytes)else{return false};
 key.verify(&canonical(r),&signature).is_ok()
}
pub fn assess(p:&Packet,policy:&Policy)->Decision{
 let e=&p.evidence;let r=&p.review;let mut issues=BTreeSet::new();
 let mut fail=|s:&str|{issues.insert(s.to_string());};
 if e.schema!="AETHER-198/evidence-v1"||r.schema!="AETHER-198/review-v1"{fail("SCHEMA_MISMATCH");}
 let digest=evidence_sha256(e);
 if r.review_id!=e.review_id||e.review_id.is_empty()||r.evidence_sha256!=digest{fail("REVIEW_DIGEST_MISMATCH");}
 for(a,b)in[(&e.capture_sha256,&policy.capture_sha256),(&e.source_receipt_sha256,&policy.source_receipt_sha256),(&e.custody_sha256,&policy.custody_sha256),(&e.calibration_sha256,&policy.calibration_sha256)]{
  if !hash(a)||a!=b{fail("ORIGINAL_EVIDENCE_DIGEST_MISMATCH");}
 }
 if e.capture_id.is_empty()||e.challenge_id!=policy.challenge_id{fail("CAPTURE_CHALLENGE_MISMATCH");}
 if r.nonce.is_empty()||r.nonce!=policy.nonce{fail("REVIEW_NONCE_MISMATCH");}
 if r.verdict!="DOCUMENTARY_MATCH"{fail("REVIEW_NOT_ACCEPTED");}
 if [&e.source_root,&e.custody_root,&e.calibration_root,&e.verifier_root,&e.source_operator,&e.verifier_operator,&e.source_admin,&e.verifier_admin].iter().any(|v|v.is_empty()){fail("MISSING_ANCESTRY");}
 if e.verifier_root==e.source_root||e.verifier_root==e.custody_root||e.verifier_root==e.calibration_root||e.verifier_operator==e.source_operator||e.verifier_admin==e.source_admin{fail("SHARED_VERIFIER_CONTROL");}
 if e.source_root==e.custody_root||e.source_root==e.calibration_root{fail("DUPLICATED_SOURCE_ANCESTRY");}
 if policy.seen_reviews.contains(&e.review_id)||policy.seen_nonces.contains(&r.nonce){fail("REPLAYED_EXTERNAL_REVIEW");}
 let signature_valid=verify(r,&p.signature_hex,&policy.verifier_public_key);
 if !signature_valid{fail("VERIFIER_SIGNATURE_INVALID");}
 if !policy.verifier_authenticated{fail("EXTERNAL_VERIFIER_UNAUTHENTICATED");}
 if !policy.source_authenticated{fail("PHYSICAL_SOURCE_UNAUTHENTICATED");}
 if !policy.custody_authenticated{fail("CUSTODY_UNAUTHENTICATED");}
 if !policy.calibration_authenticated{fail("CALIBRATION_UNAUTHENTICATED");}
 let reasons:Vec<String>=issues.into_iter().collect();
 Decision{verdict:if reasons.is_empty(){"DOCUMENTARY_BLIND_REVIEW_ONLY"}else{"REJECT"}.into(),
 proposed_review:reasons.is_empty().then(||e.review_id.clone()),reasons,
 signature_valid,evidence_sha256:digest,physical_qualification_percent:0,
 operational_authority:"HOLD".into(),physical_act_allowed:false}
}
