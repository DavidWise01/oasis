//! UEP-295R: qualified execution attribution with sealed byte parity. .dlw
use oasis_uep::{checkpoint,multi_archive,linked_segment::Anchor as LegacyAnchor,authenticated_state::State,qualified_recovery,qualified_delta::Qualified,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input,verification_profile::{self,NAMES}};
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
 let s=State::build(root.universe(),legacy[1].closing)?;let u=s.compact(root.universe(),&s.root())?;
 let qualified=Qualified::import(&s,&u,&s.root())?;
 let mut csv=String::from("scenario,period,opening_known,closing_known,opening_lots,closing_lots,operation,calls,inclusive_ns,profiled_ns,plain_ns\n");
 for scenario in ["balanced","scarcity","churn"]{
 let mut tape=qualified_recovery::Tape::start(&qualified,qualified.root())?;let mut current="G_36".to_string();
 for t in 0..360u64{
 let (enter,depart)=if scenario=="churn"||t%30==0{let id=format!("P_{}",t+1);let old=std::mem::replace(&mut current,id.clone());(vec![id],vec![old])}else{(vec![],vec![])};
 let funding=if scenario=="scarcity"{500}else if scenario=="churn"{600}else if t%30<10{500}else{750};
 let st=Step{period:Period{enter,depart,award:100,funding},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:[100;4],essential:[20;4],decay_bps:1000,work_ceiling:17}};
 let mut future=st.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;
 let r=Request{present:st,requested:0,complete:0,accept:0,future:vec![future]};
 let run_plain=||{let start=Instant::now();let v=tape.append(&r);(v,start.elapsed().as_nanos())};
 let run_profile=||{let start=Instant::now();let v=verification_profile::measure(||tape.append(&r));(v,start.elapsed().as_nanos())};
 let ((plain,pn),(profiled,tn))=if t%2==0{let a=run_plain();let b=run_profile();(a,b)}else{let b=run_profile();let a=run_plain();(a,b)};
 let plain=plain?;let (v,c)=profiled?;let v=v?;assert_eq!(plain,v);assert_eq!(state_hash::encode(v.universe())?,state_hash::encode(&tape.universe().advance(&r)?)?);
 let p=tape.universe().population_ledger();let q=v.universe().population_ledger();
 assert_eq!((c.calls[1],c.calls[10],c.calls[11],c.calls[12]),(1,0,0,0));
 assert_eq!((c.calls[22],c.calls[23],c.calls[24],c.calls[25],c.calls[26],c.calls[27],c.calls[28],c.calls[29],c.calls[30]),(1,1,1,1,1,2,0,1,1));assert_eq!(c.calls[9],1);
 for(i,name)in NAMES.iter().enumerate(){csv.push_str(&format!("{scenario},{},{},{},{},{},{name},{},{},{tn},{pn}\n",1081+t,p.known.len(),q.known.len(),p.lots.len(),q.lots.len(),c.calls[i],c.inclusive_ns[i]));}
 tape=v;
 }
 let a=tape.anchor()?;assert_eq!(a.total,1440);let sealed=match scenario{"balanced"=>include_bytes!("../../../UEP-289R-integrated-changed-path/balanced-authenticated.bin").as_slice(),"scarcity"=>include_bytes!("../../../UEP-289R-integrated-changed-path/scarcity-authenticated.bin").as_slice(),_=>include_bytes!("../../../UEP-289R-integrated-changed-path/churn-authenticated.bin").as_slice()};assert_eq!(tape.encode()?.as_slice(),sealed);fs::write(dir.join(format!("{scenario}-terminal.commitment")),a.closing.encode())?;
 }
 assert_eq!(state_hash::encode(root.universe())?,original);fs::write(dir.join("attribution295.csv"),csv)?;
 println!("{{\"scenarios\":3,\"matchedTransitions\":1080,\"channels\":31,\"rows\":33480,\"exactParity\":true,\"actualPayments\":0}}");Ok(())
}
