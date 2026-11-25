use aether_evidence::recovery_checkpoint::*;
use aether_evidence::durable_ledger::{append,inspect,Event,GENESIS};
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::{collections::HashSet,fs,path::PathBuf,sync::atomic::{AtomicUsize,Ordering}};
static COUNTER:AtomicUsize=AtomicUsize::new(0);
struct Temp{dir:PathBuf,path:PathBuf}
impl Temp{
 fn new()->Self{
  let dir=std::env::temp_dir().join(format!("aether203-{}-{}",std::process::id(),COUNTER.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();let path=dir.join("journal.jsonl");
  Self{dir,path}
 }
}
impl Drop for Temp{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
fn event(i:u32)->Event{
 Event{event_id:format!("event-{i}"),capture_sha256:format!("{i:064x}"),
 challenge_nonce:format!("nonce-{i}"),review_id:format!("review-{i}"),
 payload_sha256:format!("{:064x}",i+100)}
}
fn fixture()->(Temp,SignedCheckpoint,RecoveryPolicy){
 let t=Temp::new();let mut state=inspect(&t.path).unwrap();
 for i in 1..=3{state=append(&t.path,event(i),&state.head_sha256,state.entries).unwrap();}
 let signing=SigningKey::from_slice(&[53u8;32]).unwrap();
 let bytes=signing.verifying_key().to_encoded_point(false);
 let raw=bytes.as_bytes();
 let key=PublicJwk{kty:"EC".into(),crv:"P-256".into(),
 x:URL_SAFE_NO_PAD.encode(&raw[1..33]),y:URL_SAFE_NO_PAD.encode(&raw[33..65])};
 let record=Checkpoint{
 schema:CHECKPOINT_SCHEMA.into(),checkpoint_id:"CHK-203".into(),holder_id:"HOLDER-203".into(),
 holder_root:"INDEPENDENT-HOLDER-ROOT".into(),holder_operator:"HOLDER-OP".into(),
 holder_administrator:"HOLDER-ADMIN".into(),source_root:"ORIGIN-ROOT".into(),
 source_operator:"ORIGIN-OP".into(),source_administrator:"ORIGIN-ADMIN".into(),
 ledger_id:"LEDGER-203".into(),sequence:3,head_sha256:state.head_sha256,
 predecessor_checkpoint_sha256:"a".repeat(64),challenge_nonce:"CHECKPOINT-NONCE-203".into(),
 };
 let signature:Signature=signing.sign(&canonical(&record));
 let packet=SignedCheckpoint{record,signature_hex:hex::encode(signature.to_bytes())};
 let policy=RecoveryPolicy{
 expected_ledger_id:"LEDGER-203".into(),expected_holder_id:"HOLDER-203".into(),
 expected_holder_root:"INDEPENDENT-HOLDER-ROOT".into(),
 pinned_holder_key_sha256:public_key_fingerprint(&key),
 expected_checkpoint_sha256:checkpoint_hash(&packet.record),
 expected_predecessor_checkpoint_sha256:"a".repeat(64),
 holder_public_key:key,holder_out_of_band_authenticated:false,
 external_checkpoint_custody_verified:false,seen_checkpoint_ids:HashSet::new(),
 seen_challenge_nonces:HashSet::new(),
 };
 (t,packet,policy)
}
fn reject<F:FnOnce(&Temp,&mut SignedCheckpoint,&mut RecoveryPolicy)>(reason:&str,change:F){
 let(t,mut s,mut p)=fixture();change(&t,&mut s,&mut p);
 let r=assess_file(&t.path,&s,&p);
 assert!(r.reasons.iter().any(|v|v==reason),"{reason}: {:?}",r.reasons);
 assert_eq!(r.verdict,"REJECT");assert!(!r.may_append);
 assert!(!r.may_recover_or_reclaim);assert!(!r.physical_act_allowed);
 assert_eq!(r.operational_authority,"HOLD");
}
#[test]fn valid_synthetic_signature_without_custody(){let(t,s,p)=fixture();let r=assess_file(&t.path,&s,&p);assert!(r.signature_valid);assert_eq!(r.local_entries,3);assert!(r.reasons.contains(&"HOLDER_ORIGIN_NOT_EXTERNALLY_AUTHENTICATED".into()));}
#[test]fn flags_cannot_grant_physical_act(){let(t,s,mut p)=fixture();p.holder_out_of_band_authenticated=true;p.external_checkpoint_custody_verified=true;let r=assess_file(&t.path,&s,&p);assert_eq!(r.verdict,"DOCUMENTARY_CHECKPOINT_CONSISTENT");assert!(r.may_append);assert!(!r.physical_act_allowed);assert!(!r.may_recover_or_reclaim);}
#[test]fn signed_checkpoint_json_roundtrip(){let(_,s,_)=fixture();let encoded=serde_json::to_vec(&s).unwrap();let decoded:SignedCheckpoint=serde_json::from_slice(&encoded).unwrap();assert_eq!(s.record,decoded.record);}
#[test]fn truncated_but_valid_prefix_rejected(){reject("LOCAL_LEDGER_ROLLBACK_OR_TRUNCATION",|t,_,_|{let data=fs::read_to_string(&t.path).unwrap();let first=data.lines().next().unwrap();fs::write(&t.path,format!("{first}\n")).unwrap();});}
#[test]fn deleted_ledger_rejected(){reject("LOCAL_LEDGER_ROLLBACK_OR_TRUNCATION",|t,_,_|{fs::remove_file(&t.path).unwrap();});}
#[test]fn diverged_history_rejected(){reject("EXTERNAL_CHECKPOINT_HISTORY_DIVERGENCE",|t,s,_|{
 let original=fs::read_to_string(&t.path).unwrap();
 let mut lines:Vec<serde_json::Value>=original.lines().map(|x|serde_json::from_str(x).unwrap()).collect();
 // This is a synthetic fork with a newly rehashed first entry.
 lines[0]["event_id"]=serde_json::json!("substituted");
 let mut prior=GENESIS.to_string();
 for (i,v) in lines.iter_mut().enumerate(){
 let ev=Event{event_id:v["event_id"].as_str().unwrap().into(),capture_sha256:v["capture_sha256"].as_str().unwrap().into(),
 challenge_nonce:v["challenge_nonce"].as_str().unwrap().into(),review_id:v["review_id"].as_str().unwrap().into(),
 payload_sha256:v["payload_sha256"].as_str().unwrap().into()};
 let d=aether_evidence::durable_ledger::digest(i as u64+1,&prior,&ev);
 v["prev_sha256"]=serde_json::json!(prior);v["entry_sha256"]=serde_json::json!(d.clone());prior=d;
 }
 let joined=lines.iter().map(|v|v.to_string()).collect::<Vec<_>>().join("\n")+"\n";
 fs::write(&t.path,joined).unwrap();
 assert_ne!(prior,s.record.head_sha256);
});}
#[test]fn external_pin_substitution(){reject("EXTERNAL_CHECKPOINT_PIN_MISMATCH",|_,_,p|p.expected_checkpoint_sha256="b".repeat(64));}
#[test]fn signature_forgery(){reject("CHECKPOINT_SIGNATURE_INVALID",|_,s,_|s.signature_hex="00".repeat(64));}
#[test]fn key_fingerprint_changed(){reject("HOLDER_PUBLIC_KEY_PIN_MISMATCH",|_,_,p|p.pinned_holder_key_sha256="b".repeat(64));}
#[test]fn revoked_external_custody_claim(){reject("EXTERNAL_CHECKPOINT_CUSTODY_UNVERIFIED",|_,_,_|{});}
#[test]fn missing_holder_authentication(){reject("HOLDER_ORIGIN_NOT_EXTERNALLY_AUTHENTICATED",|_,_,_|{});}
#[test]fn same_holder_and_origin_root(){reject("SHARED_SOURCE_AND_HOLDER_CONTROL",|_,s,_|s.record.holder_root="ORIGIN-ROOT".into());}
#[test]fn shared_operator(){reject("SHARED_SOURCE_AND_HOLDER_CONTROL",|_,s,_|s.record.holder_operator="ORIGIN-OP".into());}
#[test]fn shared_admin(){reject("SHARED_SOURCE_AND_HOLDER_CONTROL",|_,s,_|s.record.holder_administrator="ORIGIN-ADMIN".into());}
#[test]fn missing_ancestry(){reject("MISSING_CUSTODY_ANCESTRY",|_,s,_|s.record.source_root.clear());}
#[test]fn mismatched_ledger(){reject("LEDGER_IDENTITY_MISMATCH",|_,s,_|s.record.ledger_id="other".into());}
#[test]fn substituted_holder(){reject("CHECKPOINT_HOLDER_MISMATCH",|_,s,_|s.record.holder_id="other".into());}
#[test]fn bad_checkpoint_schema(){reject("CHECKPOINT_SCHEMA_MISMATCH",|_,s,_|s.record.schema="old".into());}
#[test]fn substituted_predecessor(){reject("CHECKPOINT_PREDECESSOR_MISMATCH",|_,s,_|s.record.predecessor_checkpoint_sha256="b".repeat(64));}
#[test]fn replayed_checkpoint(){reject("REPLAYED_EXTERNAL_CHECKPOINT",|_,s,p|{p.seen_checkpoint_ids.insert(s.record.checkpoint_id.clone());});}
#[test]fn replayed_nonce(){reject("REPLAYED_EXTERNAL_CHECKPOINT",|_,s,p|{p.seen_challenge_nonces.insert(s.record.challenge_nonce.clone());});}
#[test]fn corrupted_tail(){reject("LEDGER_CORRUPTION_OR_READ_FAILURE",|t,_,_|{use std::io::Write;let mut f=fs::OpenOptions::new().append(true).open(&t.path).unwrap();f.write_all(b"torn").unwrap();});}
#[test]fn append_rejected_without_external_custody(){let(t,s,p)=fixture();let head=inspect(&t.path).unwrap();let e=event(4);assert!(append_with_checkpoint(&t.path,e,&head.head_sha256,head.entries,&s,&p).unwrap_err().contains("CHECKPOINT_HOLD"));}
#[test]fn append_after_documentary_acceptance(){let(t,s,mut p)=fixture();p.holder_out_of_band_authenticated=true;p.external_checkpoint_custody_verified=true;let old=inspect(&t.path).unwrap();let state=append_with_checkpoint(&t.path,event(4),&old.head_sha256,old.entries,&s,&p).unwrap();assert_eq!(state.entries,4);assert_eq!(state.operational_authority,"HOLD");assert!(!state.physical_act_allowed);}
#[test]fn stale_append_head_refused(){let(t,s,mut p)=fixture();p.holder_out_of_band_authenticated=true;p.external_checkpoint_custody_verified=true;assert_eq!(append_with_checkpoint(&t.path,event(4),GENESIS,0,&s,&p).unwrap_err(),"STALE_CHECKPOINT_ADMISSION_HEAD");}
