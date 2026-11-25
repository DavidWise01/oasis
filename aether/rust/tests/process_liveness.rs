#![cfg(target_os = "linux")]
use aether_evidence::process_liveness::{
    acquire, assess_owner, inspect, parse_start_ticks, self_owner, Liveness, Owner, LOCK_SCHEMA,
};
use std::{fs, path::PathBuf, sync::atomic::{AtomicUsize,Ordering}};
static NEXT:AtomicUsize=AtomicUsize::new(0);
struct Temp{dir:PathBuf,path:PathBuf}
impl Temp{
 fn new()->Self{
  let dir=std::env::temp_dir().join(format!("aether202-{}-{}",
   std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&dir).unwrap();
  let path=dir.join("ledger.lock");
  Self{dir,path}
 }
}
impl Drop for Temp{fn drop(&mut self){let _=fs::remove_dir_all(&self.dir);}}
fn hypothetical()->Owner{
 Owner{schema:LOCK_SCHEMA.into(),pid:123,proc_start_ticks:987654,
 boot_id:"a".repeat(36)}
}
#[test]fn self_identity_from_kernel(){let o=self_owner().unwrap();assert_eq!(o.pid,std::process::id());assert!(o.proc_start_ticks>0);assert_eq!(o.schema,LOCK_SCHEMA);}
#[test]fn no_lock_is_absent(){let t=Temp::new();let x=inspect(&t.path);assert_eq!(x.state,Liveness::Absent);assert!(!x.may_reclaim);assert!(!x.physical_act_allowed);}
#[test]fn acquisition_and_live_owner(){let t=Temp::new();let g=acquire(&t.path).unwrap();let x=inspect(&t.path);assert_eq!(x.state,Liveness::Alive);assert_eq!(x.owner.unwrap(),*g.owner());}
#[test]fn lock_guard_removes_owned_lock(){let t=Temp::new();{let _g=acquire(&t.path).unwrap();}assert_eq!(inspect(&t.path).state,Liveness::Absent);}
#[test]fn second_writer_rejected(){let t=Temp::new();let _g=acquire(&t.path).unwrap();assert!(acquire(&t.path).err().unwrap().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));}
#[test]fn orphan_does_not_reclaim(){let t=Temp::new();fs::write(&t.path,b"orphan").unwrap();let x=inspect(&t.path);assert_eq!(x.state,Liveness::Unknown);assert!(!x.may_reclaim);assert!(acquire(&t.path).is_err());}
#[test]fn malformed_json_is_unknown(){let t=Temp::new();fs::write(&t.path,b"{broken").unwrap();assert_eq!(inspect(&t.path).state,Liveness::Unknown);}
#[test]fn owner_mismatch_does_not_delete(){let t=Temp::new();let mut g=acquire(&t.path).unwrap();let mut owner=g.owner().clone();owner.pid=owner.pid.saturating_add(1);fs::write(&t.path,serde_json::to_vec(&owner).unwrap()).unwrap();assert!(g.release().unwrap_err().contains("LOCK_OWNER_CHANGED"));drop(g);assert!(t.path.exists());}
#[test]fn replaced_inode_does_not_delete(){let t=Temp::new();let mut g=acquire(&t.path).unwrap();let original=fs::read(&t.path).unwrap();fs::remove_file(&t.path).unwrap();fs::write(&t.path,original).unwrap();assert_eq!(g.release().unwrap_err(),"LOCK_FILE_REPLACED");drop(g);assert!(t.path.exists());}
#[test]fn explicit_release_and_reacquire(){let t=Temp::new();let mut g=acquire(&t.path).unwrap();g.release().unwrap();drop(g);let h=acquire(&t.path).unwrap();assert_eq!(inspect(&t.path).owner.unwrap(),*h.owner());}
#[test]fn live_exact_identity(){let x=hypothetical();assert_eq!(assess_owner(&x,&x.boot_id,Ok(('S',x.proc_start_ticks))),Liveness::Alive);}
#[test]fn pid_reuse_detected(){let x=hypothetical();assert_eq!(assess_owner(&x,&x.boot_id,Ok(('S',x.proc_start_ticks+1))),Liveness::Exited);}
#[test]fn zombie_not_alive(){let x=hypothetical();assert_eq!(assess_owner(&x,&x.boot_id,Ok(('Z',x.proc_start_ticks))),Liveness::Exited);}
#[test]fn process_lookup_error_unknown(){let x=hypothetical();assert_eq!(assess_owner(&x,&x.boot_id,Err("permission denied".into())),Liveness::Unknown);}
#[test]fn forged_boot_id_unknown(){let x=hypothetical();assert_eq!(assess_owner(&x,"another",Ok(('S',x.proc_start_ticks))),Liveness::Unknown);}
#[test]fn forged_schema_unknown(){let mut x=hypothetical();x.schema="legacy".into();assert_eq!(assess_owner(&x,&x.boot_id,Ok(('S',x.proc_start_ticks))),Liveness::Unknown);}
#[test]fn zero_pid_unknown(){let mut x=hypothetical();x.pid=0;assert_eq!(assess_owner(&x,&x.boot_id,Ok(('S',x.proc_start_ticks))),Liveness::Unknown);}
#[test]fn comm_with_parentheses_and_spaces(){
 let fields=vec!["0";18].join(" ");
 let stat=format!("123 (process (name) with spaces) S {fields} 987654 0 0");
 let (state,ticks)=parse_start_ticks(&stat).unwrap();assert_eq!(state,'S');assert_eq!(ticks,987654);
}
#[test]fn malformed_proc_stat_rejected(){assert!(parse_start_ticks("123 no delim S").is_err());}
#[test]fn lock_permissions_private(){use std::os::unix::fs::PermissionsExt;let t=Temp::new();let _g=acquire(&t.path).unwrap();let mode=fs::metadata(&t.path).unwrap().permissions().mode() & 0o777;assert_eq!(mode,0o600);}
