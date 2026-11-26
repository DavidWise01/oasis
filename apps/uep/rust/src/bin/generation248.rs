//! UEP-248R: synthetic 360-period generational exercise, actual integrated engine. .dlw
use oasis_uep::{evidence::{Ledger,Event},restitution::Assessment,replay_archive::{self,Archive},executable::Request,equilibrium::Step,population::{Population,Period,settle},bridge::Shares,dividend::Revenue,capacity::Input,checkpoint};
use std::{env,fs,path::Path};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let dir=env::args().nth(1).ok_or("output directory")?;let dir=Path::new(&dir);
 let l=Ledger::default().append(Event::Estimate{id:"e".into(),valuation:10000,assessment:Assessment{target:"synthetic aggregate resource harm".into(),evidence_refs:vec!["synthetic reference".into()],human_observation_ref:"h".into(),ai_observation_ref:"a".into(),positive:[999;22],negative:[0;22]}})?.append(Event::AcceptModel{id:"a".into(),estimate_id:"e".into(),decision_ref:"synthetic only".into()})?;
 let mut archive=Archive::new(l.clone(),l.head())?;let mut shadow=Population::phase_ix();let mut current="A_1".to_owned();let mut turnover=0;let mut short=0;let mut peak=0;let mut retired=0u64;let mut accepted=0;let mut total_work=0;let mut csv=String::from("period,population,due,funded,arrears,retired,work,completed,accepted,harm,rate,water,food,energy,materials,water_gain,food_gain,energy_gain,materials_gain,rejected\n");
 for t in 0..360{
  let shock=t%30<10;
  let (enter,depart)=if t%30==0{let next=format!("G_{}",t/30+1);let old=std::mem::replace(&mut current,next.clone());turnover+=1;(vec![next],vec![old])}else{(vec![],vec![])};
  let p=Step{period:Period{enter,depart,award:100,funding:if shock{500}else{750}},restitution:Shares{carbon:100,ai:25},revenue:Revenue{public_equity:600,licensing:0,automation_royalties:0,infrastructure_return:0},dividend_cap:100,resources:Input{inflow:if shock{[0;4]}else{[100;4]},essential:[20;4],decay_bps:1000,work_ceiling:17}};
  let mut future=p.clone();future.period.enter.clear();future.period.depart.clear();future.period.funding=750;future.resources.inflow=[100;4];
  let baseline=settle(&shadow,&p.period)?;
  let stage=archive.universe().state().state().restoration();
  let req=Request{present:p,requested:17,complete:stage.funded()-stage.completed(),accept:stage.completed()-stage.accepted(),future:vec![future]};
  archive=archive.append(&req)?;
  let o=archive.universe().observations().last().ok_or("observation")?;
  assert_eq!((o.due,o.funded,o.arrears),(baseline.current_due,baseline.current_funded,baseline.closing.outstanding()?));
  assert_eq!(archive.universe().population_count(),baseline.closing.active.len());assert_eq!(o.accepted+o.residual_harm,17);
  if o.funded<o.due{short+=1;assert_eq!(o.work,0);assert_eq!(o.accepted,accepted);}
  assert!(o.accepted>=accepted);accepted=o.accepted;peak=peak.max(o.arrears);retired+=o.historical_reserved;total_work+=o.work;
  csv.push_str(&[t as u64+1,archive.universe().population_count() as u64,o.due,o.funded,o.arrears,o.historical_reserved,o.work,o.completed,o.accepted,o.residual_harm,o.rate,o.stock[0],o.stock[1],o.stock[2],o.stock[3],o.gain[0],o.gain[1],o.gain[2],o.gain[3],u64::from(o.rejected)].iter().map(|v|v.to_string()).collect::<Vec<_>>().join(","));csv.push('\n');
  shadow=baseline.closing;
 }
 let bytes=archive.encode()?;let c=archive.checkpoint()?;assert_eq!(c.count,360);assert_eq!(replay_archive::decode(&bytes,&c)?,archive);
 assert_eq!(turnover,12);assert_eq!(short,120);assert_eq!(accepted,17);assert_eq!(total_work,17);assert_eq!(shadow.outstanding()?,400);assert_eq!(retired,12000);
 fs::write(dir.join("generation.csv"),csv)?;fs::write(dir.join("generation.archive"),&bytes)?;fs::write(dir.join("generation.checkpoint"),checkpoint::encode(&c)?)?;
 println!("{{\"periods\":360,\"turnovers\":{turnover},\"shortfalls\":{short},\"peakArrears\":{peak},\"closingArrears\":{},\"historicalReserved\":{retired},\"accepted\":{accepted},\"archiveBytes\":{},\"replayEqual\":true,\"actualPayments\":0}}",shadow.outstanding()?,bytes.len());Ok(())
}
