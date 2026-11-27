//! UEP-258R: extend the published root through two complete compacted successors. .dlw
use oasis_uep::{checkpoint,replay_archive,linked_segment::{Segment,Anchor},capacity_inheritance,multi_archive,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
use std::{fs,env,path::Path};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let dir=env::args().nth(1).ok_or("output directory")?;let dir=Path::new(&dir);
 let root_bytes=include_bytes!("../../../UEP-249R-integrated-release/generation.archive");
 let root=checkpoint::decode(include_bytes!("../../../UEP-249R-integrated-release/generation.checkpoint"))?;
 let a=replay_archive::decode(root_bytes,&root)?;
 let mut uninterrupted=a.universe().clone();let mut s=Segment::compact_root(&a,&root)?;
 let mut anchors:Vec<Anchor>=vec![];let mut paths=vec![];
 let mut csv=String::from("period,population,due,funded,arrears,retired,work,completed,accepted,harm,rate,water,food,energy,materials,active_records\n");
 let mut current="G_12".to_string();let mut turnovers=0;let mut shortages=0;let mut reserved=0u64;let mut peak=0;
 for t in 360..1080{
  let shock=t%30<10;let(enter,depart)=if t%30==0{let next=format!("G_{}",t/30+1);let old=std::mem::replace(&mut current,next.clone());turnovers+=1;(vec![next],vec![old])}else{(vec![],vec![])};
  let p=Step{period:Period{enter,depart,award:100,funding:if shock{500}else{750}},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:if shock{[0;4]}else{[100;4]},essential:[20;4],decay_bps:1000,work_ceiling:17}};
  let mut future=p.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;future.resources.inflow=[100;4];
  let r=Request{present:p,requested:17,complete:0,accept:0,future:vec![future]};
  let(n,audit,life)=capacity_inheritance::append(&s,&r)?;uninterrupted=uninterrupted.advance(&r)?;
  assert_eq!(state_hash::encode(n.universe())?,state_hash::encode(&uninterrupted)?);
  let o=n.universe().observations().last().ok_or("observation")?;assert_eq!(Some(o),uninterrupted.observations().last());assert_eq!(life.accepted,17);assert_eq!(o.work,0);
  if audit.current_funded<audit.due{shortages+=1;}reserved+=audit.historical_reserved;peak=peak.max(audit.closing);
  let len=n.universe().observations().len();assert!(len<=360);
  csv.push_str(&[t+1,n.universe().population_count() as u64,o.due,o.funded,o.arrears,o.historical_reserved,o.work,o.completed,o.accepted,o.residual_harm,o.rate,o.stock[0],o.stock[1],o.stock[2],o.stock[3],len as u64].iter().map(|v|v.to_string()).collect::<Vec<_>>().join(","));csv.push('\n');
  s=n;
  if (t+1)%360==0{let c=s.anchor()?;let path=dir.join(format!("segment-{}.bin",c.total));fs::write(&path,s.encode()?)?;paths.push(path);anchors.push(c.clone());if t+1<1080{s=capacity_inheritance::boundary(&s,&c)?;}}
 }
 let terminal=anchors.last().ok_or("terminal")?;
 let recovered=multi_archive::recover(root_bytes,&root,&anchors,terminal,|i|fs::read(&paths[i]).map_err(|_|"read segment"))?;
 assert_eq!(recovered,s);assert_eq!(state_hash::encode(recovered.universe())?,state_hash::encode(&uninterrupted)?);
 assert_eq!(turnovers,24);assert_eq!(shortages,240);assert_eq!(reserved,24000);assert_eq!(peak,1400);assert_eq!(s.universe().population_ledger().outstanding()?,400);
 assert_eq!(s.universe().total_observations(),1080);assert_eq!(s.universe().observations().len(),360);
 let mut manifest=Vec::new();for c in &anchors{manifest.extend_from_slice(&c.total.to_be_bytes());manifest.extend_from_slice(&c.ancestry);manifest.extend_from_slice(&c.closing);}
 fs::write(dir.join("anchors.bin"),manifest)?;fs::write(dir.join("generation258.csv"),csv)?;fs::write(dir.join("terminal.state"),state_hash::encode(s.universe())?)?;
 println!("{{\"periods\":1080,\"successorPeriods\":720,\"successorTurnovers\":{turnovers},\"successorShortfalls\":{shortages},\"successorHistoricalReserved\":{reserved},\"peakArrears\":{peak},\"closingArrears\":400,\"accepted\":17,\"activeRecords\":360,\"exactStateParity\":true,\"replayEqual\":true,\"actualPayments\":0}}");Ok(())
}
