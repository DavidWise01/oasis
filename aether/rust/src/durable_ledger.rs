//! AETHER-201-RS — local durable replay ledger.
//! Exclusive create_new lock; append, fsync, readback, and fail-closed recovery.
//! A local file is NOT independent external custody or physical ACT authorization.
use crate::sha256_hex;
use serde::{Deserialize,Serialize};
use std::collections::HashSet;
use std::fs::{self,File,OpenOptions};
use std::io::{Read,Write};
use std::path::{Path,PathBuf};

pub const GENESIS: &str = "AETHER-201/GENESIS";
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub struct Entry {
 pub seq:u64,pub prev_sha256:String,pub event_id:String,pub capture_sha256:String,
 pub challenge_nonce:String,pub review_id:String,pub payload_sha256:String,
 pub entry_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize,PartialEq,Eq)]
pub struct Event {
 pub event_id:String,pub capture_sha256:String,pub challenge_nonce:String,
 pub review_id:String,pub payload_sha256:String,
}
#[derive(Debug,Clone,Serialize,Deserialize)]
pub struct State {pub entries:u64,pub head_sha256:String,pub physical_act_allowed:bool,pub operational_authority:String}
pub fn digest(seq:u64,prev:&str,event:&Event)->String {
 // Canonical field order is fixed by this struct.
 #[derive(Serialize)]
 struct Body<'a>{seq:u64,prev_sha256:&'a str,event_id:&'a str,capture_sha256:&'a str,challenge_nonce:&'a str,review_id:&'a str,payload_sha256:&'a str}
 let b=Body{seq,prev_sha256:prev,event_id:&event.event_id,capture_sha256:&event.capture_sha256,
 challenge_nonce:&event.challenge_nonce,review_id:&event.review_id,payload_sha256:&event.payload_sha256};
 sha256_hex(&serde_json::to_vec(&b).expect("canonical serializable body"))
}
fn hex64(s:&str)->bool{s.len()==64&&s.bytes().all(|c|c.is_ascii_hexdigit())}
fn validate_event(e:&Event)->Result<(),String>{
 if e.event_id.trim().is_empty()||e.challenge_nonce.trim().is_empty()||e.review_id.trim().is_empty()
 ||!hex64(&e.capture_sha256)||!hex64(&e.payload_sha256){return Err("INVALID_EVENT".into());}
 Ok(())
}
fn read_all(path:&Path)->Result<Vec<Entry>,String>{
 let mut bytes=Vec::new();match File::open(path){
  Ok(mut f)=>{f.read_to_end(&mut bytes).map_err(|e|format!("READ: {e}"))?;},
  Err(e)if e.kind()==std::io::ErrorKind::NotFound=>return Ok(vec![]),
  Err(e)=>return Err(format!("OPEN: {e}")),
 }
 if bytes.is_empty(){return Ok(vec![]);}
 if bytes.last()!=Some(&b'\n'){return Err("TORN_TAIL".into());}
 let mut entries=Vec::new();
 let mut seen_id=HashSet::new();let mut seen_nonce=HashSet::new();
 let mut seen_review=HashSet::new();let mut seen_capture=HashSet::new();
 let mut seen_payload=HashSet::new();
 let mut prior=GENESIS.to_string();
 for line in bytes.split(|x|*x==b'\n').filter(|l|!l.is_empty()){
  let v:Entry=serde_json::from_slice(line).map_err(|_|"CORRUPT_LEDGER_JSON")?;
  let event=Event{event_id:v.event_id.clone(),capture_sha256:v.capture_sha256.clone(),
   challenge_nonce:v.challenge_nonce.clone(),review_id:v.review_id.clone(),
   payload_sha256:v.payload_sha256.clone()};
  validate_event(&event)?;
  if v.seq!=entries.len() as u64+1||v.prev_sha256!=prior
  ||v.entry_sha256!=digest(v.seq,&v.prev_sha256,&event){
   return Err("HASH_CHAIN_OR_SEQUENCE_MISMATCH".into());
  }
  if !seen_id.insert(v.event_id.clone())||!seen_nonce.insert(v.challenge_nonce.clone())
  ||!seen_review.insert(v.review_id.clone())||!seen_capture.insert(v.capture_sha256.clone())
  ||!seen_payload.insert(v.payload_sha256.clone()){return Err("DUPLICATE_REPLAY_ENTRY".into());}
  prior=v.entry_sha256.clone();entries.push(v);
 }
 Ok(entries)
}
struct Lock {path:PathBuf,file:File}
impl Drop for Lock {fn drop(&mut self){let _=self.file.sync_all();let _=fs::remove_file(&self.path);}}
fn lock(path:&Path)->Result<Lock,String>{
 let lock_path=path.with_extension("lock");
 let file=OpenOptions::new().write(true).create_new(true).open(&lock_path)
  .map_err(|e|format!("LOCK_UNAVAILABLE_FAIL_CLOSED: {e}"))?;
 Ok(Lock{path:lock_path,file})
}
fn directory_sync(path:&Path)->Result<(),String>{
 let dir=path.parent().filter(|p|!p.as_os_str().is_empty()).unwrap_or(Path::new("."));
 File::open(dir).and_then(|f|f.sync_all()).map_err(|e|format!("DIR_SYNC: {e}"))
}
fn state(entries:&[Entry])->State{
 State{entries:entries.len() as u64,head_sha256:entries.last().map(|e|e.entry_sha256.clone())
 .unwrap_or_else(||GENESIS.into()),physical_act_allowed:false,operational_authority:"HOLD".into()}
}
pub fn inspect(path:&Path)->Result<State,String>{read_all(path).map(|v|state(&v))}
/// An event is accepted only if both the expected head and expected sequence match.
/// Never recovers an orphan lock by guessing process liveness or a caller-supplied flag.
pub fn append(path:&Path,event:Event,expected_head:&str,expected_entries:u64)->Result<State,String>{
 validate_event(&event)?;
 let _guard=lock(path)?;
 let old=read_all(path)?;
 let prior=state(&old);
 if prior.head_sha256!=expected_head||prior.entries!=expected_entries{return Err("STALE_HEAD".into());}
 if old.iter().any(|v|v.event_id==event.event_id||v.capture_sha256==event.capture_sha256
  ||v.challenge_nonce==event.challenge_nonce||v.review_id==event.review_id
  ||v.payload_sha256==event.payload_sha256){return Err("REPLAY".into());}
 let seq=expected_entries.checked_add(1).ok_or("SEQUENCE_OVERFLOW")?;
 let next=Entry{seq,prev_sha256:prior.head_sha256.clone(),event_id:event.event_id.clone(),
  capture_sha256:event.capture_sha256.clone(),challenge_nonce:event.challenge_nonce.clone(),
  review_id:event.review_id.clone(),payload_sha256:event.payload_sha256.clone(),
  entry_sha256:digest(seq,&prior.head_sha256,&event)};
 let mut f=OpenOptions::new().append(true).create(true).open(path).map_err(|e|format!("APPEND_OPEN: {e}"))?;
 let mut line=serde_json::to_vec(&next).map_err(|e|format!("SERIALIZE: {e}"))?;
 line.push(b'\n');
 f.write_all(&line).map_err(|e|format!("WRITE: {e}"))?;
 f.sync_all().map_err(|e|format!("FSYNC: {e}"))?;
 directory_sync(path)?;
 let rebuilt=read_all(path)?;
 if rebuilt.len()!=old.len()+1||rebuilt.last()!=Some(&next){return Err("READBACK_MISMATCH".into());}
 Ok(state(&rebuilt))
}
