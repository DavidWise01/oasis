//! UEP-268R: seven indexed tapes extending the sealed 1080-period universe. .dlw
use oasis_uep::{checkpoint,multi_archive,linked_segment::Anchor as LegacyAnchor,indexed_recovery::Tape,working_projection::Projection,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,verification_profile::{self,NAMES}};
use std::{env,fs,path::Path,time::Instant};
const ROOT:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/root.archive");
const CP:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/root.checkpoint");
const A:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/anchors.bin");
const S1:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/segment-720.bin");
const S2:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/segment-1080.bin");
fn main()->Result<(),Box<dyn std::error::Error>>{
 let dir=env::args().nth(1).ok_or("output directory")?;let dir=Path::new(&dir);
 let cp=checkpoint::decode(CP)?;assert_eq!(A.len(),144);
 let legacy:Vec<LegacyAnchor>=A.chunks_exact(72).map(|b|LegacyAnchor{total:u64::from_be_bytes(b[..8].try_into().unwrap()),ancestry:b[8..40].try_into().unwrap(),closing:b[40..72].try_into().unwrap()}).collect();
 let root=multi_archive::recover(ROOT,&cp,&legacy,&legacy[1],|i|Ok(if i==0{S1}else{S2}.to_vec()))?;
 let original=state_hash::encode(root.universe())?;assert_eq!(original.as_slice(),include_bytes!("../../../UEP-259R-integrated-generations/terminal.state"));
 let p=Projection::build(root.universe(),legacy[1].closing)?;let u=p.compact(root.universe())?;let opening=p.commitment(&u)?;
 let mut csv=String::from("scenario,period,path,operation,calls,inclusive_ns,elapsed_ns\n");
 for scenario in ["balanced","scarcity","churn"]{
  let mut tape=Tape::start(&p,&u,&opening)?;let mut current="G_36".to_string();
  for t in 0..120u64{
   let(enter,depart)=if scenario=="churn"||t%30==0{let id=format!("P_{}",t+1);let old=std::mem::replace(&mut current,id.clone());(vec![id],vec![old])}else{(vec![],vec![])};
   let funding=if scenario=="scarcity"{500}else if scenario=="churn"{600}else if t%30<10{500}else{750};
   let s=Step{period:Period{enter,depart,award:100,funding},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:1000,work_ceiling:17}};
   let mut future=s.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;
   let r=Request{present:s,requested:0,complete:0,accept:0,future:vec![future]};
   let start=Instant::now();let (a,ac)=verification_profile::measure(||tape.universe().advance(&r))?;let an=start.elapsed().as_nanos();let a=a?;
   let start=Instant::now();let (b,bc)=verification_profile::measure(||tape.append(&r))?;let bn=start.elapsed().as_nanos();let b=b?;
   assert_eq!(state_hash::encode(&a)?,state_hash::encode(b.universe())?);
   assert_eq!(b,tape.append(&r)?);
   assert_eq!(ac.calls[1],1);assert_eq!(bc.calls[1],3);assert_eq!(bc.calls[4],4);assert_eq!(bc.calls[5],6);assert_eq!(bc.calls[9],1);
   for (path,c,elapsed) in [("reference",ac,an),("indexed",bc,bn)]{for(i,name)in NAMES.iter().enumerate(){csv.push_str(&format!("{scenario},{},{path},{name},{},{},{elapsed}\n",1081+t,c.calls[i],c.inclusive_ns[i]));}}
   tape=b;
  }
 }
 assert_eq!(state_hash::encode(root.universe())?,original);
 fs::write(dir.join("verification271.csv"),csv)?;
 println!("{{\"scenarios\":3,\"pairedTransitions\":360,\"instrumentedPaths\":720,\"canonicalParity\":true,\"instrumentationParity\":true,\"actualPayments\":0}}");Ok(())
}
