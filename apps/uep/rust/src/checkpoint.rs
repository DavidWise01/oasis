//! UEP-244R: immutable checkpoint publication in a trusted local directory. .dlw
use crate::replay_archive::{Checkpoint,MAX_STEPS};
use sha2::{Digest,Sha256};
const MAGIC:&[u8;8]=b"UEP244R\0";
pub const SIZE:usize=112;
pub fn encode(c:&Checkpoint)->Result<Vec<u8>,&'static str>{
 if c.count>MAX_STEPS as u64{return Err("count")}
 let mut b=MAGIC.to_vec();b.extend_from_slice(&c.count.to_be_bytes());b.extend_from_slice(&c.archive_digest);b.extend_from_slice(&c.closing);
 let mut h=Sha256::new();h.update(b"OASIS-UEP-244R-checkpoint-v1");h.update(&b);b.extend_from_slice(&h.finalize());Ok(b)
}
pub fn decode(b:&[u8])->Result<Checkpoint,&'static str>{
 if b.len()!=SIZE||&b[..8]!=MAGIC{return Err("checkpoint format")}
 let c=Checkpoint{count:u64::from_be_bytes(b[8..16].try_into().map_err(|_|"count")?),archive_digest:b[16..48].try_into().map_err(|_|"archive")?,closing:b[48..80].try_into().map_err(|_|"closing")?};
 if encode(&c)?!=b{return Err("checkpoint integrity")}Ok(c)
}
#[cfg(target_os="linux")]
pub mod disk{
 use super::*;use crate::replay_archive::{self,Archive};use std::{fs::{self,File,OpenOptions},io::{Read,Write},path::Path};
 type Result<T>=std::result::Result<T,Box<dyn std::error::Error>>;
 fn name(c:&Checkpoint)->String{format!("{:03}-{}",c.count,c.archive_digest.iter().map(|v|format!("{v:02x}")).collect::<String>())}
 fn put(dir:&Path,name:&str,bytes:&[u8])->Result<()>{
  let stage=dir.join(format!("{name}.stage"));let final_path=dir.join(name);
  let mut f=OpenOptions::new().write(true).create_new(true).open(&stage)?;
  f.write_all(bytes)?;f.sync_all()?;drop(f);
  fs::hard_link(&stage,&final_path)?;File::open(dir)?.sync_all()?;
  fs::remove_file(stage)?;File::open(dir)?.sync_all()?;Ok(())
 }
 pub fn publish(dir:&Path,prior:&Archive,next:&Archive)->Result<Checkpoint>{
  if !next.extends(prior)||next.checkpoint()?.count!=prior.checkpoint()?.count+1{return Err("not immediate successor".into())}
  let c=next.checkpoint()?;let n=name(&c);
  put(dir,&format!("{n}.archive"),&next.encode()?)?;
  put(dir,&format!("{n}.checkpoint"),&encode(&c)?)?;Ok(c)
 }
 pub fn recover(dir:&Path,expected:&Checkpoint)->Result<Archive>{
  let n=name(expected);let mut b=Vec::new();File::open(dir.join(format!("{n}.checkpoint")))?.take((SIZE+1) as u64).read_to_end(&mut b)?;
  if decode(&b)?!=*expected{return Err("external checkpoint mismatch".into())}
  Ok(replay_archive::recover(&dir.join(format!("{n}.archive")),expected)?)
 }
}
#[cfg(test)]
mod tests{
 use super::*;
 fn sample()->Checkpoint{Checkpoint{count:1,archive_digest:[2;32],closing:[3;32]}}
 #[test]fn roundtrip(){let c=sample();assert_eq!(decode(&encode(&c).unwrap()).unwrap(),c);}
 #[test]fn truncation(){let b=encode(&sample()).unwrap();for n in 0..b.len(){assert!(decode(&b[..n]).is_err())}}
 #[test]fn mutation(){let b=encode(&sample()).unwrap();for n in 0..b.len(){let mut x=b.clone();x[n]^=1;assert!(decode(&x).is_err())}}
 #[test]fn limits(){let mut c=sample();c.count=361;assert!(encode(&c).is_err());let mut b=encode(&sample()).unwrap();b.push(0);assert!(decode(&b).is_err())}
 #[cfg(target_os="linux")]
 #[test]fn interrupted_publication(){
 use crate::{replay_archive::Archive,evidence::Ledger,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
 let dir=std::env::temp_dir().join(format!("uep244-{}-{:?}",std::process::id(),std::thread::current().id()));std::fs::create_dir(&dir).unwrap();
 let a=Archive::new(Ledger::default(),[0;32]).unwrap();
 let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:600},restitution:Shares::default(),revenue:Revenue{public_equity:0,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:0,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:0,work_ceiling:17}};
 let r=Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]};
 let b=a.append(&r).unwrap();let c=disk::publish(&dir,&a,&b).unwrap();assert_eq!(disk::recover(&dir,&c).unwrap(),b);
 assert!(disk::publish(&dir,&a,&b).is_err());let d=b.append(&r).unwrap();let dc=d.checkpoint().unwrap();
 let name=format!("{:03}-{}",dc.count,dc.archive_digest.iter().map(|v|format!("{v:02x}")).collect::<String>());
 std::fs::write(dir.join(format!("{name}.archive")),d.encode().unwrap()).unwrap();
 assert!(disk::recover(&dir,&dc).is_err());assert_eq!(disk::recover(&dir,&c).unwrap(),b);
 std::fs::remove_dir_all(dir).unwrap();
 }
}
