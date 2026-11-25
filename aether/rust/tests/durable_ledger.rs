use aether_evidence::durable_ledger::{append,inspect,Event,GENESIS};
use std::{fs,fs::OpenOptions,io::Write,path::PathBuf,sync::atomic::{AtomicUsize,Ordering}};
static NEXT:AtomicUsize=AtomicUsize::new(0);
struct Temp{dir:PathBuf,path:PathBuf}
impl Temp {
 fn new()->Self{
  let dir=std::env::temp_dir().join(format!("aether201-{}-{}-{}",std::process::id(),
  std::thread::current().name().unwrap_or("test").replace(':',"_"),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();let path=dir.join("ledger.jsonl");
  Self{dir,path}
 }
}
impl Drop for Temp{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
fn event(n:u32)->Event{
 Event{event_id:format!("event-{n}"),capture_sha256:format!("{n:064x}"),
 challenge_nonce:format!("nonce-{n}"),review_id:format!("review-{n}"),
 payload_sha256:format!("{:064x}",n+1000)}
}
#[test]fn empty_is_genesis(){let t=Temp::new();let s=inspect(&t.path).unwrap();assert_eq!(s.entries,0);assert_eq!(s.head_sha256,GENESIS);assert!(!s.physical_act_allowed);}
#[test]fn append_one_and_readback(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();assert_eq!(s.entries,1);assert_eq!(inspect(&t.path).unwrap().head_sha256,s.head_sha256);assert_eq!(s.operational_authority,"HOLD");}
#[test]fn append_multiple_recovery(){let t=Temp::new();let mut s=inspect(&t.path).unwrap();for i in 1..=25{s=append(&t.path,event(i),&s.head_sha256,s.entries).unwrap();}assert_eq!(inspect(&t.path).unwrap().entries,25);}
#[test]fn stale_head_rejected(){let t=Temp::new();append(&t.path,event(1),GENESIS,0).unwrap();assert!(append(&t.path,event(2),GENESIS,0).unwrap_err().contains("STALE_HEAD"));}
#[test]fn duplicate_event_rejected(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();assert_eq!(append(&t.path,event(1),&s.head_sha256,1).unwrap_err(),"REPLAY");}
#[test]fn duplicate_nonce_rejected(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();let mut e=event(2);e.challenge_nonce="nonce-1".into();assert_eq!(append(&t.path,e,&s.head_sha256,1).unwrap_err(),"REPLAY");}
#[test]fn duplicate_payload_rejected(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();let mut e=event(2);e.payload_sha256=event(1).payload_sha256;assert_eq!(append(&t.path,e,&s.head_sha256,1).unwrap_err(),"REPLAY");}
#[test]fn duplicate_capture_rejected(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();let mut e=event(2);e.capture_sha256=event(1).capture_sha256;assert_eq!(append(&t.path,e,&s.head_sha256,1).unwrap_err(),"REPLAY");}
#[test]fn duplicate_review_rejected(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();let mut e=event(2);e.review_id="review-1".into();assert_eq!(append(&t.path,e,&s.head_sha256,1).unwrap_err(),"REPLAY");}
#[test]fn malformed_event_rejected(){let t=Temp::new();let mut e=event(1);e.capture_sha256="bad".into();assert_eq!(append(&t.path,e,GENESIS,0).unwrap_err(),"INVALID_EVENT");}
#[test]fn torn_tail_detected(){let t=Temp::new();append(&t.path,event(1),GENESIS,0).unwrap();let mut f=OpenOptions::new().append(true).open(&t.path).unwrap();f.write_all(b"partial").unwrap();f.sync_all().unwrap();assert_eq!(inspect(&t.path).unwrap_err(),"TORN_TAIL");}
#[test]fn corrupted_json_detected(){let t=Temp::new();fs::write(&t.path,b"bad-json\n").unwrap();assert_eq!(inspect(&t.path).unwrap_err(),"CORRUPT_LEDGER_JSON");}
#[test]fn tampered_digest_detected(){let t=Temp::new();append(&t.path,event(1),GENESIS,0).unwrap();let s=fs::read_to_string(&t.path).unwrap().replace("event-1","event-X");fs::write(&t.path,s).unwrap();assert_eq!(inspect(&t.path).unwrap_err(),"HASH_CHAIN_OR_SEQUENCE_MISMATCH");}
#[test]fn missing_sequence_detected(){let t=Temp::new();append(&t.path,event(1),GENESIS,0).unwrap();let s=fs::read_to_string(&t.path).unwrap().replace("\"seq\":1","\"seq\":2");fs::write(&t.path,s).unwrap();assert_eq!(inspect(&t.path).unwrap_err(),"HASH_CHAIN_OR_SEQUENCE_MISMATCH");}
#[test]fn orphan_lock_fails_closed(){let t=Temp::new();fs::write(t.path.with_extension("lock"),b"orphaned").unwrap();assert!(append(&t.path,event(1),GENESIS,0).unwrap_err().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));assert!(!t.path.exists());}
#[test]fn lock_released_after_stale_head(){let t=Temp::new();let s=append(&t.path,event(1),GENESIS,0).unwrap();let _=append(&t.path,event(2),GENESIS,0).unwrap_err();let r=append(&t.path,event(2),&s.head_sha256,1).unwrap();assert_eq!(r.entries,2);}
#[test]fn reject_corrupted_before_append(){let t=Temp::new();fs::write(&t.path,b"corrupt\n").unwrap();assert_eq!(append(&t.path,event(1),GENESIS,0).unwrap_err(),"CORRUPT_LEDGER_JSON");}
#[test]fn no_act_with_recovered_history(){let t=Temp::new();let s=append(&t.path,event(7),GENESIS,0).unwrap();let r=inspect(&t.path).unwrap();assert_eq!(s.head_sha256,r.head_sha256);assert!(!r.physical_act_allowed);assert_eq!(r.operational_authority,"HOLD");}
