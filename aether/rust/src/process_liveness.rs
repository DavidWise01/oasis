//! AETHER-202-RS — Linux /proc process identity and fail-closed lock diagnostics.
//! A deceased owner is NOT permission to delete/reclaim a lock.
//! No physical ACT path; no cross-host or external custody attestation.
use serde::{Deserialize, Serialize};
use std::{fs::{self,File,OpenOptions},io::{Read,Write},path::{Path,PathBuf}};

pub const LOCK_SCHEMA: &str = "AETHER-202/linux-process-lock-v1";
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub struct Owner {
    pub schema:String,
    pub pid:u32,
    pub proc_start_ticks:u64,
    pub boot_id:String,
}
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub enum Liveness {Absent, Alive, Exited, Unknown}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct Inspection {
    pub state:Liveness,
    pub reason:String,
    pub owner:Option<Owner>,
    pub may_reclaim:bool,
    pub physical_act_allowed:bool,
    pub operational_authority:String,
}
pub fn parse_start_ticks(stat:&str)->Result<(char,u64),String>{
    // comm may contain spaces and parentheses. The FINAL ')' delimits comm;
    // field 3 (state) is token 0, field 22 (starttime) is token 19.
    let end=stat.rfind(')').ok_or("INVALID_PROC_STAT")?;
    let remainder=stat.get(end+1..).ok_or("INVALID_PROC_STAT")?;
    let fields:Vec<&str>=remainder.split_whitespace().collect();
    let state=fields.first().and_then(|s|s.chars().next()).ok_or("INVALID_PROC_STATE")?;
    let ticks=fields.get(19).ok_or("MISSING_PROC_STARTTIME")?
        .parse::<u64>().map_err(|_|"INVALID_PROC_STARTTIME")?;
    Ok((state,ticks))
}
#[cfg(target_os="linux")]
fn boot()->Result<String,String>{
    let s=fs::read_to_string("/proc/sys/kernel/random/boot_id")
       .map_err(|e|format!("BOOT_ID_UNAVAILABLE: {e}"))?;
    let s=s.trim().to_owned();
    if s.len()!=36 || !s.chars().all(|c|c.is_ascii_hexdigit()||c=='-'){
        return Err("INVALID_KERNEL_BOOT_ID".into());
    }
    Ok(s)
}
#[cfg(target_os="linux")]
fn observed(pid:u32)->Result<(char,u64),String>{
    if pid==0{return Err("INVALID_PID".into());}
    let stat=fs::read_to_string(format!("/proc/{pid}/stat"))
       .map_err(|e|format!("PROC_STAT_UNAVAILABLE: {e}"))?;
    parse_start_ticks(&stat)
}
#[cfg(target_os="linux")]
pub fn self_owner()->Result<Owner,String>{
    let pid=std::process::id();
    let (state,ticks)=observed(pid)?;
    if state=='Z'||state=='X'||state=='x'||ticks==0{
        return Err("SELF_PROCESS_NOT_LIVE".into());
    }
    Ok(Owner{schema:LOCK_SCHEMA.into(),pid,proc_start_ticks:ticks,boot_id:boot()?})
}
#[cfg(not(target_os="linux"))]
pub fn self_owner()->Result<Owner,String>{Err("UNSUPPORTED_PLATFORM_FAIL_CLOSED".into())}
pub fn assess_owner(owner:&Owner,boot_id:&str,observed:Result<(char,u64),String>)->Liveness{
    if owner.schema!=LOCK_SCHEMA || owner.pid==0 || owner.proc_start_ticks==0 ||
       owner.boot_id!=boot_id {return Liveness::Unknown;}
    match observed {
        Ok((s,t)) if t==owner.proc_start_ticks && s!='Z' && s!='X' && s!='x'=>Liveness::Alive,
        Ok((_,t)) if t!=owner.proc_start_ticks=>Liveness::Exited,
        Ok(('Z'|'X'|'x',_))=>Liveness::Exited,
        Err(_)=>Liveness::Unknown,
        _=>Liveness::Unknown,
    }
}
fn report(state:Liveness,reason:&str,owner:Option<Owner>)->Inspection{
    Inspection{state,reason:reason.into(),owner,may_reclaim:false,
      physical_act_allowed:false,operational_authority:"HOLD".into()}
}
pub fn inspect(path:&Path)->Inspection{
    let payload=match fs::read(path){
       Ok(b)=>b,
       Err(e) if e.kind()==std::io::ErrorKind::NotFound=>
           return report(Liveness::Absent,"NO_LOCK_FILE",None),
       Err(_)=>return report(Liveness::Unknown,"LOCK_READ_FAILED",None),
    };
    let owner:Owner=match serde_json::from_slice(&payload){
       Ok(o)=>o,Err(_)=>return report(Liveness::Unknown,"MALFORMED_LOCK_METADATA",None),
    };
    #[cfg(target_os="linux")]
    {
        let boot_id=match boot(){Ok(b)=>b,Err(_)=>return report(Liveness::Unknown,"BOOT_ID_UNAVAILABLE",Some(owner))};
        let result=observed(owner.pid);
        let liveness=assess_owner(&owner,&boot_id,result);
        let reason=match liveness {
            Liveness::Alive=>"LIVE_OWNER_VERIFIED_BY_LINUX_PROC",
            Liveness::Exited=>"OWNER_EXIT_OR_PID_REUSE_OBSERVED_NO_RECLAIM",
            Liveness::Unknown=>"OWNER_IDENTITY_UNVERIFIED_NO_RECLAIM",
            Liveness::Absent=>"NO_LOCK_FILE",
        };
        report(liveness,reason,Some(owner))
    }
    #[cfg(not(target_os="linux"))]
    {report(Liveness::Unknown,"UNSUPPORTED_PLATFORM_FAIL_CLOSED",Some(owner))}
}
fn directory_sync(path:&Path)->Result<(),String>{
    let dir=path.parent().filter(|p|!p.as_os_str().is_empty()).unwrap_or(Path::new("."));
    File::open(dir).and_then(|f|f.sync_all()).map_err(|e|format!("DIR_SYNC: {e}"))
}
pub struct Guard {path:PathBuf,file:File,owner:Owner,released:bool}
impl Guard{
    pub fn owner(&self)->&Owner{&self.owner}
    pub fn release(&mut self)->Result<(),String>{
        if self.released{return Ok(());}
        // Metadata tampering or replacement leaves the lock in place for
        // independent incident review; never erase another owner's file.
        let actual=fs::read(&self.path).map_err(|e|format!("LOCK_READ: {e}"))?;
        let recorded:Owner=serde_json::from_slice(&actual).map_err(|_|"LOCK_METADATA_CHANGED")?;
        if recorded!=self.owner{return Err("LOCK_OWNER_CHANGED".into());}
        #[cfg(unix)]
        {
            use std::os::unix::fs::MetadataExt;
            let held=self.file.metadata().map_err(|e|format!("FD_STAT: {e}"))?;
            let on_disk=fs::symlink_metadata(&self.path).map_err(|e|format!("PATH_STAT: {e}"))?;
            if held.ino()!=on_disk.ino()||held.dev()!=on_disk.dev(){
                return Err("LOCK_FILE_REPLACED".into());
            }
        }
        self.file.sync_all().map_err(|e|format!("LOCK_FSYNC: {e}"))?;
        fs::remove_file(&self.path).map_err(|e|format!("LOCK_RELEASE: {e}"))?;
        directory_sync(&self.path)?;
        self.released=true;
        Ok(())
    }
}
impl Drop for Guard{fn drop(&mut self){let _=self.release();}}
/// Exclusive creation is the only acquisition route. Existing locks are
/// NEVER deleted automatically, even if Linux reports that owner exited.
pub fn acquire(path:&Path)->Result<Guard,String>{
    let owner=self_owner()?;
    #[cfg(unix)]
    let mut options={
        use std::os::unix::fs::OpenOptionsExt;
        let mut o=OpenOptions::new();o.write(true).create_new(true).mode(0o600);o
    };
    #[cfg(not(unix))]
    let mut options={let mut o=OpenOptions::new();o.write(true).create_new(true);o};
    let file=options.open(path).map_err(|e|format!("LOCK_UNAVAILABLE_FAIL_CLOSED: {e}"))?;
    let mut guard=Guard{path:path.into(),file,owner,released:false};
    let data=serde_json::to_vec(guard.owner()).map_err(|e|format!("LOCK_SERIALIZATION: {e}"))?;
    guard.file.write_all(&data).map_err(|e|format!("LOCK_WRITE: {e}"))?;
    guard.file.sync_all().map_err(|e|format!("LOCK_FSYNC: {e}"))?;
    directory_sync(path)?;
    if inspect(path).state!=Liveness::Alive{return Err("SELF_LOCK_OWNER_NOT_VERIFIED".into());}
    Ok(guard)
}
