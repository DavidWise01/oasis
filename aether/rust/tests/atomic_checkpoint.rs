#![cfg(target_os="linux")]
use aether_evidence::durable_ledger::{append,inspect,Event,GENESIS};
use aether_evidence::recovery_checkpoint::*;
use aether_evidence::process_liveness;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::{collections::HashSet,fs,io::Write,path::PathBuf,sync::atomic::{AtomicUsize,Ordering}};
static NEXT:AtomicUsize=AtomicUsize::new(0);
struct Temp{dir:PathBuf,path:PathBuf}
impl Temp{
 fn new()->Self{
  let dir=std::env::temp_dir().join(format!("aether204-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();
  Self{path:dir.join("evidence.jsonl"),dir}
 }
}
impl Drop for Temp{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
fn event(i:u64)->Event{
 Event{event_id:format!("event-{i}"),capture_sha256:format!("{i:064x}"),
 challenge_nonce:format!("nonce-{i}"),review_id:format!("review-{i}"),
 payload_sha256:format!("{:064x}",i+900)}
}
fn fixture()->(Temp,SignedCheckpoint,RecoveryPolicy){
 let t=Temp::new();let mut head=GENESIS.to_string();let mut count=0;
 for i in 1..=3{let s=append(&t.path,event(i),&head,count).unwrap();head=s.head_sha256;count=s.entries;}
 let signer=SigningKey::from_slice(&[61u8;32]).unwrap();let p=signer.verifying_key().to_encoded_point(false);
 let b=p.as_bytes();
 let pubkey=PublicJwk{kty:"EC".into(),crv:"P-256".into(),
 x:URL_SAFE_NO_PAD.encode(&b[1..33]),y:URL_SAFE_NO_PAD.encode(&b[33..65])};
 let c=Checkpoint{
 schema:CHECKPOINT_SCHEMA.into(),checkpoint_id:"CHK-204".into(),holder_id:"HOLDER-204".into(),
 holder_root:"HOLDER-ROOT".into(),holder_operator:"HOLDER-OP".into(),holder_administrator:"HOLDER-ADMIN".into(),
 source_root:"SOURCE-ROOT".into(),source_operator:"SOURCE-OP".into(),source_administrator:"SOURCE-ADMIN".into(),
 ledger_id:"LEDGER-204".into(),sequence:3,head_sha256:head,
 predecessor_checkpoint_sha256:"a".repeat(64),challenge_nonce:"CHECKPOINT-NONCE-204".into()};
 let sig:Signature=signer.sign(&canonical(&c));
 let signed=SignedCheckpoint{record:c,signature_hex:hex::encode(sig.to_bytes())};
 let policy=RecoveryPolicy{
 expected_ledger_id:"LEDGER-204".into(),expected_holder_id:"HOLDER-204".into(),
 expected_holder_root:"HOLDER-ROOT".into(),pinned_holder_key_sha256:public_key_fingerprint(&pubkey),
 expected_checkpoint_sha256:checkpoint_hash(&signed.record),expected_predecessor_checkpoint_sha256:"a".repeat(64),
 holder_public_key:pubkey,holder_out_of_band_authenticated:true,external_checkpoint_custody_verified:true,
 seen_checkpoint_ids:HashSet::new(),seen_challenge_nonces:HashSet::new()};
 (t,signed,policy)
}
fn assert_hold(error:&str){assert!(!error.is_empty());}
#[test]fn single_lock_checkpoint_admission_and_readback(){
 let(t,c,p)=fixture();let initial=inspect(&t.path).unwrap();
 let result=append_with_checkpoint(&t.path,event(4),&initial.head_sha256,initial.entries,&c,&p).unwrap();
 assert_eq!(result.entries,4);
 assert_eq!(inspect(&t.path).unwrap().head_sha256,result.head_sha256);
 assert_eq!(result.operational_authority,"HOLD");assert!(!result.physical_act_allowed);
 assert!(!t.path.with_extension("lock").exists());
}
#[test]fn held_process_lock_blocks_checkpoint_writer(){
 let(t,c,p)=fixture();let guard=process_liveness::acquire(&t.path.with_extension("lock")).unwrap();
 let state=inspect(&t.path).unwrap();
 let result=append_with_checkpoint(&t.path,event(4),&state.head_sha256,state.entries,&c,&p);
 assert!(result.unwrap_err().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));
 assert_eq!(inspect(&t.path).unwrap().entries,3);
 drop(guard);
}
#[test]fn after_owned_lock_release_checkpoint_writer_succeeds(){
 let(t,c,p)=fixture();let guard=process_liveness::acquire(&t.path.with_extension("lock")).unwrap();drop(guard);
 let state=inspect(&t.path).unwrap();
 assert_eq!(append_with_checkpoint(&t.path,event(4),&state.head_sha256,state.entries,&c,&p).unwrap().entries,4);
}
#[test]fn stale_count_rejected_inside_lock(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();
 assert_eq!(append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries-1,&c,&p).unwrap_err(),"STALE_CHECKPOINT_ADMISSION_HEAD");
 assert_eq!(inspect(&t.path).unwrap().entries,3);
}
#[test]fn stale_head_rejected_inside_lock(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();
 assert_eq!(append_with_checkpoint(&t.path,event(4),GENESIS,s.entries,&c,&p).unwrap_err(),"STALE_CHECKPOINT_ADMISSION_HEAD");
}
#[test]fn previous_writer_advances_head_before_checkpoint_writer(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();
 let advanced=append(&t.path,event(4),&s.head_sha256,s.entries).unwrap();
 let err=append_with_checkpoint(&t.path,event(5),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert_eq!(err,"STALE_CHECKPOINT_ADMISSION_HEAD");
 assert_eq!(inspect(&t.path).unwrap().head_sha256,advanced.head_sha256);
}
#[test]fn previously_accepted_checkpoint_remains_ancestral_after_append(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();
 let a=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap();
 let b=append_with_checkpoint(&t.path,event(5),&a.head_sha256,a.entries,&c,&p).unwrap();
 assert_eq!(b.entries,5);assert_eq!(assess_file(&t.path,&c,&p).verdict,"DOCUMENTARY_CHECKPOINT_CONSISTENT");
}
#[test]fn duplicate_event_blocks_admission(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();
 assert_eq!(append_with_checkpoint(&t.path,event(2),&s.head_sha256,s.entries,&c,&p).unwrap_err(),"REPLAY");
}
#[test]fn valid_prefix_truncation_rejected_under_lock(){
 let(t,c,p)=fixture();let data=fs::read_to_string(&t.path).unwrap();
 let truncated=data.lines().take(2).map(|x|format!("{x}\n")).collect::<String>();
 fs::write(&t.path,truncated).unwrap();let s=inspect(&t.path).unwrap();
 let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("LOCAL_LEDGER_ROLLBACK_OR_TRUNCATION"),"{err}");
 assert_eq!(inspect(&t.path).unwrap().entries,2);
}
#[test]fn torn_tail_rejected_under_lock(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();let mut f=fs::OpenOptions::new().append(true).open(&t.path).unwrap();
 f.write_all(b"partial").unwrap();f.sync_all().unwrap();
 let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("LEDGER_HOLD: TORN_TAIL"),"{err}");
}
#[test]fn corrupt_json_rejected_under_lock(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();
 fs::write(&t.path,b"{bad}\n").unwrap();
 let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("LEDGER_HOLD: CORRUPT_LEDGER_JSON"),"{err}");
}
#[test]fn altered_checkpoint_pin_cannot_append(){
 let(t,c,mut p)=fixture();p.expected_checkpoint_sha256="0".repeat(64);
 let s=inspect(&t.path).unwrap();let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("EXTERNAL_CHECKPOINT_PIN_MISMATCH"),"{err}");
 assert_eq!(inspect(&t.path).unwrap().entries,3);
}
#[test]fn forged_signed_checkpoint_cannot_append(){
 let(t,mut c,p)=fixture();c.signature_hex="00".repeat(64);
 let s=inspect(&t.path).unwrap();let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("CHECKPOINT_SIGNATURE_INVALID"),"{err}");
}
#[test]fn missing_external_custody_cannot_append(){
 let(t,c,mut p)=fixture();p.external_checkpoint_custody_verified=false;
 let s=inspect(&t.path).unwrap();let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("EXTERNAL_CHECKPOINT_CUSTODY_UNVERIFIED"),"{err}");
}
#[test]fn orphan_lock_never_reclaimed(){
 let(t,c,p)=fixture();fs::write(t.path.with_extension("lock"),b"orphan").unwrap();let s=inspect(&t.path).unwrap();
 let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();
 assert!(err.contains("LOCK_UNAVAILABLE_FAIL_CLOSED"),"{err}");
 assert!(t.path.with_extension("lock").exists());
}
#[test]fn guard_refuses_wrong_ledger_lock(){
 let(t,_,_)=fixture();let g=process_liveness::acquire(&t.path.with_extension("lock")).unwrap();
 assert_eq!(g.verify_for(&t.dir.join("other.lock")).unwrap_err(),"LOCK_GUARD_NOT_FOR_LEDGER");
}
#[test]fn guard_refuses_owner_metadata_mutation(){
 let(t,_,_)=fixture();let g=process_liveness::acquire(&t.path.with_extension("lock")).unwrap();
 let mut owner=g.owner().clone();owner.pid=owner.pid.saturating_add(1);
 fs::write(t.path.with_extension("lock"),serde_json::to_vec(&owner).unwrap()).unwrap();
 assert_eq!(g.verify_for(&t.path.with_extension("lock")).unwrap_err(),"LOCK_OWNER_CHANGED");
 drop(g);assert!(t.path.with_extension("lock").exists());
}
#[test]fn guard_refuses_inode_replacement(){
 let(t,_,_)=fixture();let g=process_liveness::acquire(&t.path.with_extension("lock")).unwrap();
 let path=t.path.with_extension("lock");let bytes=fs::read(&path).unwrap();
 fs::remove_file(&path).unwrap();fs::write(&path,bytes).unwrap();
 assert_eq!(g.verify_for(&path).unwrap_err(),"LOCK_FILE_REPLACED");drop(g);assert!(path.exists());
}
#[test]fn failure_releases_only_owned_lock(){
 let(t,c,mut p)=fixture();p.holder_out_of_band_authenticated=false;let s=inspect(&t.path).unwrap();
 let err=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap_err();assert_hold(&err);
 assert!(!t.path.with_extension("lock").exists());
 let next=append(&t.path,event(4),&s.head_sha256,s.entries).unwrap();assert_eq!(next.entries,4);
}
#[test]fn no_physical_act_even_accepted(){
 let(t,c,p)=fixture();let s=inspect(&t.path).unwrap();let result=append_with_checkpoint(&t.path,event(4),&s.head_sha256,s.entries,&c,&p).unwrap();
 assert!(!result.physical_act_allowed);assert_eq!(result.operational_authority,"HOLD");
}
