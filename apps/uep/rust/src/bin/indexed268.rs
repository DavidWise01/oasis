//! UEP-268R: seven indexed tapes extending the sealed 1080-period universe. .dlw
use oasis_uep::{checkpoint,multi_archive,linked_segment::Anchor as LegacyAnchor,indexed_recovery::{self,Tape,Anchor},working_projection::Projection,state_hash,executable::Request,equilibrium::Step,population::Period,bridge::Shares,dividend::Revenue,capacity::Input};
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
 fs::write(dir.join("opening.commitment"),opening.encode())?;
 let mut tape=Tape::start(&p,&u,&opening)?;let mut reference=u.clone();
 let mut anchors:Vec<Anchor>=vec![];let mut paths=vec![];let mut current="G_36".to_string();
 let(mut turnovers,mut shortages,mut reserved,mut peak)=(0u64,0u64,0u64,0u64);
 let mut csv=String::from("period,active,known,beneficiaries,lots,arrears,due,funded,reserved,accepted,water,food,energy,materials,observations,canonical_bytes,tape_append_ns,reference_advance_ns\n");
 for t in 1080..3600u64{
  let shock=t%30<10;let(enter,depart)=if t%30==0{let id=format!("G_{}",t/30+1);let old=std::mem::replace(&mut current,id.clone());turnovers+=1;(vec![id],vec![old])}else{(vec![],vec![])};
  let s=Step{period:Period{enter,depart,award:100,funding:if shock{500}else{750}},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:if shock{[0;4]}else{[100;4]},essential:[20;4],decay_bps:1000,work_ceiling:17}};
  let mut future=s.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;future.resources.inflow=[100;4];
  let r=Request{present:s,requested:17,complete:0,accept:0,future:vec![future]};
  let start=Instant::now();let next=tape.append(&r)?;let append_ns=start.elapsed().as_nanos();
  let start=Instant::now();reference=reference.advance(&r)?;let reference_ns=start.elapsed().as_nanos();
  let v=next.universe();let bytes=state_hash::encode(v)?;assert_eq!(bytes,state_hash::encode(&reference)?);
  let o=v.observations().last().ok_or("observation")?;assert_eq!(Some(o),reference.observations().last());
  let view=next.projection().view(v)?;assert_eq!(view.active,6);assert!(view.observations<=360);assert_eq!(o.accepted,17);assert_eq!(o.work,0);
  assert_eq!(o.funded,o.due.min(r.present.period.funding));assert_eq!(view.outstanding,o.arrears);
  if o.funded<o.due{shortages+=1}reserved+=o.historical_reserved;peak=peak.max(o.arrears);
  csv.push_str(&format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",t+1,view.active,view.known,view.beneficiaries,view.lots,view.outstanding,o.due,o.funded,o.historical_reserved,o.accepted,o.stock[0],o.stock[1],o.stock[2],o.stock[3],view.observations,bytes.len(),append_ns,reference_ns));
  tape=next;
  if (t+1)%360==0{let a=tape.anchor()?;let path=dir.join(format!("tape-{}.bin",a.total));fs::write(&path,tape.encode()?)?;paths.push(path);anchors.push(a.clone());if t+1<3600{tape=tape.successor(&a)?;}}
 }
 let mut recovered=Tape::start(&p,&u,&opening)?;let mut manifest=Vec::new();let mut recovery_csv=String::from("terminal,bytes,recovery_ns\n");
 for(i,a)in anchors.iter().enumerate(){
  let c=recovered.projection().commitment(recovered.universe())?;
  let start=Instant::now();let n=indexed_recovery::recover_file(recovered.projection(),recovered.universe(),&c,&paths[i],a)?;let ns=start.elapsed().as_nanos();
  recovery_csv.push_str(&format!("{},{},{}\n",a.total,fs::metadata(&paths[i])?.len(),ns));
  manifest.extend_from_slice(&a.total.to_be_bytes());manifest.extend_from_slice(&a.digest);manifest.extend_from_slice(&a.closing.encode());
  recovered=if i+1<anchors.len(){n.successor(a)?}else{n};
 }
 assert_eq!(recovered,tape);assert_eq!(state_hash::encode(recovered.universe())?,state_hash::encode(&reference)?);
 assert_eq!(state_hash::encode(root.universe())?,original);
 let v=tape.projection().view(tape.universe())?;
 assert_eq!((turnovers,shortages,reserved,peak),(84,840,84000,1400));
 assert_eq!((v.cumulative,v.observations,v.known,v.lots,v.outstanding),(3600,360,127,0,400));
 assert_eq!(anchors.len(),7);
 fs::write(dir.join("indexed268.csv"),csv)?;fs::write(dir.join("recovery268.csv"),recovery_csv)?;fs::write(dir.join("indexed-anchors.bin"),manifest)?;
 fs::write(dir.join("terminal.state"),state_hash::encode(tape.universe())?)?;fs::write(dir.join("terminal.commitment"),tape.projection().commitment(tape.universe())?.encode())?;
 println!("{{\"periods\":3600,\"newPeriods\":2520,\"tapes\":7,\"newTurnovers\":{turnovers},\"newShortfalls\":{shortages},\"newHistoricalReserved\":{reserved},\"peakArrears\":{peak},\"closingArrears\":400,\"known\":127,\"activeRecords\":360,\"exactStateParity\":true,\"indexedRecoveryEqual\":true,\"actualPayments\":0}}");Ok(())
}
