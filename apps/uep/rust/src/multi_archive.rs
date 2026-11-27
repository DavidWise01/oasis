//! UEP-257R: ordered multi-archive recovery; synthetic accounting only. .dlw
use crate::{linked_segment::{Anchor,Segment,LIMIT,BYTE_LIMIT},replay_archive::{self,Checkpoint},state_hash};
pub const MAX_SEGMENTS:usize=1024;
/// Recover one successor at a time. The caller supplies trusted root and closing anchors.
/// The final segment may be partial; all earlier segments must be full.
pub fn recover<F>(root_bytes:&[u8],root:&Checkpoint,anchors:&[Anchor],terminal:&Anchor,mut load:F)->Result<Segment,&'static str>
where F:FnMut(usize)->Result<Vec<u8>,&'static str>{
 if root.count!=LIMIT as u64||anchors.is_empty()||anchors.len()>MAX_SEGMENTS||anchors.last()!=Some(terminal){return Err("chain boundary")}
 let mut total=root.count;
 for (i,a) in anchors.iter().enumerate(){
  let count=a.total.checked_sub(total).ok_or("chain order")?;
  if count==0||count>LIMIT as u64||(i+1<anchors.len()&&count!=LIMIT as u64){return Err("chain count")}
  total=a.total;
 }
 let a=replay_archive::decode(root_bytes,root)?;
 if a.encode()?.as_slice()!=root_bytes{return Err("root canonical mismatch")}
 let mut opening=Segment::compact_root(&a,root)?;
 drop(a);
 for (i,expected) in anchors.iter().enumerate(){
  let bytes=load(i)?;
  if bytes.len()>BYTE_LIMIT{return Err("segment size")}
  let next=Segment::recover(&opening,&bytes,expected)?;
  drop(bytes);
  if next.universe().observations().len()>LIMIT||next.universe().total_observations()!=expected.total{return Err("observation boundary")}
  if i+1==anchors.len(){
   if next.anchor()?!=*terminal||state_hash::fingerprint(next.universe())?!=terminal.closing{return Err("terminal mismatch")}
   return Ok(next)
  }
  opening=crate::capacity_inheritance::boundary(&next,expected)?;
 }
 Err("empty chain")
}
/// Bounded file reads for a caller-selected, ordered list of local segment paths.
#[cfg(not(target_arch="wasm32"))]
pub fn recover_files(root_path:&std::path::Path,root:&Checkpoint,paths:&[std::path::PathBuf],anchors:&[Anchor],terminal:&Anchor)->Result<Segment,&'static str>{
 use std::io::Read;
 fn read(path:&std::path::Path,limit:usize)->Result<Vec<u8>,&'static str>{let mut b=Vec::new();std::fs::File::open(path).map_err(|_|"archive open")?.take((limit+1) as u64).read_to_end(&mut b).map_err(|_|"archive read")?;if b.len()>limit{return Err("archive size")}Ok(b)}
 if paths.len()!=anchors.len()||paths.len()>MAX_SEGMENTS{return Err("path count")}
 let bytes=read(root_path,replay_archive::MAX_BYTES)?;
 recover(&bytes,root,anchors,terminal,|i|read(&paths[i],BYTE_LIMIT))
}
#[cfg(test)]mod tests{
 use super::*;use crate::{executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,checkpoint};
 use std::sync::OnceLock;
 const ROOT:&[u8]=include_bytes!("../../UEP-249R-integrated-release/generation.archive");
 const CHECKPOINT:&[u8]=include_bytes!("../../UEP-249R-integrated-release/generation.checkpoint");
 fn req(f:u64)->Request{let s=Step{period:Period{enter:vec![],depart:vec![],award:100,funding:f},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:1000,work_ceiling:17}};Request{present:s.clone(),requested:0,complete:0,accept:0,future:vec![s]}}
 struct Fixture{root:Checkpoint,anchors:Vec<Anchor>,bytes:Vec<Vec<u8>>,final_state:Segment}
 fn fixture()->&'static Fixture{static F:OnceLock<Fixture>=OnceLock::new();F.get_or_init(||{
  let root=checkpoint::decode(CHECKPOINT).unwrap();let a=replay_archive::decode(ROOT,&root).unwrap();
  let mut s=Segment::compact_root(&a,&root).unwrap();
  for i in 0..360{s=s.append(&req(if i==359{0}else{600})).unwrap()}
  let first=s.anchor().unwrap();let b=s.encode().unwrap();let mut n=s.compact_boundary(&first).unwrap();
  n=n.append(&req(700)).unwrap();n=n.append(&req(1100)).unwrap();
  Fixture{root,anchors:vec![first,n.anchor().unwrap()],bytes:vec![b,n.encode().unwrap()],final_state:n}
 })}
 #[test]fn sealed_root_chain(){let f=fixture();let mut order=vec![];let s=recover(ROOT,&f.root,&f.anchors,&f.anchors[1],|i|{order.push(i);Ok(f.bytes[i].clone())}).unwrap();assert_eq!(order,vec![0,1]);assert_eq!(s,f.final_state);assert_eq!(s.universe().total_observations(),722);assert_eq!(s.universe().observations().len(),2);assert_eq!(s.universe().population_ledger().outstanding().unwrap(),400);assert_eq!(s.universe().state().state().restoration().accepted(),17);}
 #[test]fn reordered_or_missing(){let f=fixture();assert!(recover(ROOT,&f.root,&f.anchors,&f.anchors[1],|i|Ok(f.bytes[1-i].clone())).is_err());assert!(recover(ROOT,&f.root,&f.anchors,&f.anchors[1],|i|if i==0{Ok(f.bytes[0].clone())}else{Err("missing")}).is_err());}
 #[test]fn terminal_and_count(){let f=fixture();let mut wrong=f.anchors[1].clone();wrong.closing[0]^=1;assert!(recover(ROOT,&f.root,&f.anchors,&wrong,|_|panic!("must reject before loading")).is_err());let mut list=f.anchors.clone();list[0].total-=1;assert!(recover(ROOT,&f.root,&list,&list[1],|_|panic!("must reject before loading")).is_err());assert!(recover(ROOT,&f.root,&[],&f.anchors[1],|_|panic!("empty")).is_err());}
 #[test]fn tampered_root_or_segment(){let f=fixture();let mut root=ROOT.to_vec();root[100]^=1;assert!(recover(&root,&f.root,&f.anchors,&f.anchors[1],|_|panic!("invalid root")).is_err());assert!(recover(ROOT,&f.root,&f.anchors,&f.anchors[1],|i|{let mut b=f.bytes[i].clone();if i==1{b[100]^=1;}Ok(b)}).is_err());}
 #[test]fn local_files(){let f=fixture();let dir=std::env::temp_dir().join(format!("uep257-{}",std::process::id()));std::fs::create_dir(&dir).unwrap();let root=dir.join("root");let paths=vec![dir.join("first"),dir.join("second")];std::fs::write(&root,ROOT).unwrap();for(i,p)in paths.iter().enumerate(){std::fs::write(p,&f.bytes[i]).unwrap()}let result=recover_files(&root,&f.root,&paths,&f.anchors,&f.anchors[1]);std::fs::remove_dir_all(dir).unwrap();assert_eq!(result.unwrap(),f.final_state);}
}
