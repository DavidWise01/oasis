//! UEP-261R: read-only state growth instrumentation, synthetic branches only. .dlw
use oasis_uep::{checkpoint,replay_archive,multi_archive,linked_segment::Anchor,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
use std::{fs,env,path::Path,time::Instant};
const ROOT:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/root.archive");
const CP:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/root.checkpoint");
const A:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/anchors.bin");
const S1:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/segment-720.bin");
const S2:&[u8]=include_bytes!("../../../UEP-259R-integrated-generations/segment-1080.bin");
fn main()->Result<(),Box<dyn std::error::Error>>{
 let dir=env::args().nth(1).ok_or("output directory")?;let dir=Path::new(&dir);
 let cp=checkpoint::decode(CP)?;assert_eq!(A.len(),144);
 let anchors:Vec<Anchor>=A.chunks_exact(72).map(|b|Anchor{total:u64::from_be_bytes(b[..8].try_into().unwrap()),ancestry:b[8..40].try_into().unwrap(),closing:b[40..72].try_into().unwrap()}).collect();
 let root=multi_archive::recover(ROOT,&cp,&anchors,&anchors[1],|i|Ok(if i==0{S1}else{S2}.to_vec()))?;
 let baseline=state_hash::encode(root.universe())?;assert_eq!(baseline.as_slice(),include_bytes!("../../../UEP-259R-integrated-generations/terminal.state"));
 let mut csv=String::from("scenario,period,opening_known,opening_lots,known,active,departed,lots,arrears,observations,canonical_bytes,advance_ns,encode_ns\n");
 for scenario in ["balanced","persistent_shortage","identity_churn"]{
  let mut u=root.universe().compact(anchors[1].closing)?;let mut current="G_36".to_string();
  for t in 0..360u64{
   let (enter,depart)=if scenario=="identity_churn"||t%30==0{let next=format!("P_{}",t+1);let old=std::mem::replace(&mut current,next.clone());(vec![next],vec![old])}else{(vec![],vec![])};
   let funding=if scenario=="persistent_shortage"{500}else if scenario=="identity_churn"{600}else if t%30<10{500}else{750};
   let p=Step{period:Period{enter,depart,award:100,funding},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:1000,work_ceiling:17}};
   let mut future=p.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;
   let r=Request{present:p,requested:0,complete:0,accept:0,future:vec![future]};
   let opening=u.population_ledger();let known=opening.known.len();let lots=opening.lots.len();
   let start=Instant::now();let n=u.advance(&r)?;let elapsed=start.elapsed().as_nanos();
   let start=Instant::now();let bytes=state_hash::encode(&n)?;let encode=start.elapsed().as_nanos();
   let p=n.population_ledger();let o=n.observations().last().ok_or("observation")?;
   assert_eq!(o.funded,o.due.min(funding));assert_eq!(o.accepted,17);assert_eq!(p.unattributed,400);
   assert_eq!(u.population_ledger().outstanding()?+o.due,p.outstanding()?+o.funded+o.historical_reserved);
   csv.push_str(&format!("{scenario},{},{known},{lots},{},{},{},{},{},{},{},{elapsed},{encode}\n",1081+t,p.known.len(),p.active.len(),p.known.len()-p.active.len(),p.lots.len(),p.outstanding()?,n.observations().len(),bytes.len()));
   u=n;
  }
  let p=u.population_ledger();
  match scenario{"balanced"=>assert_eq!((p.known.len(),p.lots.len(),p.outstanding()?),(55,0,400)),"persistent_shortage"=>assert_eq!((p.known.len(),p.lots.len(),p.outstanding()?),(55,2160,36400)),"identity_churn"=>assert_eq!((p.known.len(),p.lots.len(),p.outstanding()?),(403,0,400)),_=>unreachable!()}
 }
 assert_eq!(state_hash::encode(root.universe())?,baseline);
 fs::write(dir.join("growth261.csv"),csv)?;
 println!("{{\"scenarios\":3,\"transitions\":1080,\"branchPeriods\":360,\"sealedRootPreserved\":true,\"actualPayments\":0,\"timing\":\"wall-clock nanoseconds; diagnostic only\"}}");Ok(())
}
