//! UEP-202R: individual entitlement and population ledger.
//! Synthetic accounting only. .dlw
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Lot { pub origin: u64, pub id: String, pub amount: u64 }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Population {
    pub epoch: u64,
    pub active: BTreeSet<String>,
    pub known: BTreeSet<String>,
    pub lots: Vec<Lot>,
    pub unattributed: u64,
    pub cursor: Option<String>,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Period {
    pub enter: Vec<String>,
    pub depart: Vec<String>,
    pub award: u64,
    pub funding: u64,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Award { pub id: String, pub due: u64, pub funded: u64 }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Settlement {
    pub closing: Population,
    pub awards: Vec<Award>,
    pub current_due: u64,
    pub current_funded: u64,
    pub historical_reserved: BTreeMap<String,u64>,
    pub unallocated: u64,
}
fn valid(id: &str) -> bool {
    !id.is_empty() && id.len() <= 30 &&
        id.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}
fn total(lots: &[Lot]) -> Result<u64, &'static str> {
    lots.iter().try_fold(0u64, |n,l| n.checked_add(l.amount).ok_or("lot overflow"))
}
impl Population {
    pub fn phase_ix() -> Self {
        let active: BTreeSet<String> = ["A_1","B_0","B_1","C_0","C_1","D_0"]
            .iter().map(|x| x.to_string()).collect();
        let mut known = active.clone(); known.insert("A_0".into());
        Self { epoch: 6, active, known, lots: Vec::new(), unattributed: 400, cursor: None }
    }
    pub fn outstanding(&self) -> Result<u64, &'static str> {
        total(&self.lots)?.checked_add(self.unattributed).ok_or("balance overflow")
    }
}
pub fn settle(s: &Population, p: &Period) -> Result<Settlement, &'static str> {let _profile=crate::verification_profile::span(0);
    if p.award > 1_000_000 || p.funding > 1_000_000 || s.known.len() > 10_000
        || !s.active.is_subset(&s.known) || !s.known.iter().all(|x| valid(x))
        || s.lots.iter().any(|x| !s.known.contains(&x.id) || x.origin > s.epoch || x.amount == 0)
        || s.lots.windows(2).any(|x| x[0].origin > x[1].origin)
        || s.cursor.as_ref().map_or(false, |x| !s.known.contains(x)) {
        return Err("invalid ledger");
    }
    let opening = s.outstanding()?;
    let enter: BTreeSet<_> = p.enter.iter().cloned().collect();
    let depart: BTreeSet<_> = p.depart.iter().cloned().collect();
    if enter.len()!=p.enter.len() || depart.len()!=p.depart.len() ||
        !depart.is_subset(&s.active) || !enter.is_disjoint(&s.known) ||
        !enter.iter().all(|x| valid(x)) || s.known.len()+enter.len()>10_000 {
        return Err("invalid population transition");
    }
    let mut n=s.clone();
    n.epoch=n.epoch.checked_add(1).ok_or("epoch overflow")?;
    for id in depart { n.active.remove(&id); }
    n.active.extend(enter.iter().cloned()); n.known.extend(enter);
    let ids: Vec<_>=n.active.iter().cloned().collect();
    let count=ids.len() as u64;
    let due=count.checked_mul(p.award).ok_or("award overflow")?;
    let paid=due.min(p.funding);
    let base=if count==0 {0} else {paid/count};
    let extra=if count==0 {0} else {paid%count};
    let start=ids.iter().position(|id| n.cursor.as_ref().map_or(true,|c|id>c)).unwrap_or(0);
    let mut rank=ids.clone(); rank.rotate_left(start);
    if extra>0 { n.cursor=Some(rank[extra as usize-1].clone()); }
    let awards: Vec<_>=rank.iter().enumerate().map(|(i,id)|Award{
        id:id.clone(),due:p.award,funded:base+u64::from((i as u64)<extra)
    }).collect();
    let mut left=p.funding-paid;
    let mut reserved=BTreeMap::<String,u64>::new();
    // Do not assign or settle unattributed inherited debt without attribution.
    // Identified lots are served in recorded chronological order.
    for lot in &mut n.lots {
        let a=left.min(lot.amount); lot.amount-=a; left-=a;
        if a>0 { let entry=reserved.entry(lot.id.clone()).or_default();
            *entry=entry.checked_add(a).ok_or("reservation overflow")?; }
    }
    n.lots.retain(|x|x.amount>0);
    for a in &awards { if a.funded<a.due {
        n.lots.push(Lot{origin:n.epoch,id:a.id.clone(),amount:a.due-a.funded});
    }}
    let back=p.funding-paid-left;
    if u128::from(opening)+u128::from(due)!=u128::from(n.outstanding()?)+u128::from(paid)+u128::from(back) {
        return Err("obligation conservation");
    }
    Ok(Settlement{closing:n,awards,current_due:due,current_funded:paid,historical_reserved:reserved,unallocated:left})
}
#[cfg(test)]
mod tests {
    use super::*;
    fn period(funding:u64)->Period{Period{enter:vec![],depart:vec![],award:100,funding}}
    #[test] fn inherited_unknown_is_preserved(){
        let r=settle(&Population::phase_ix(),&period(1000)).unwrap();
        assert_eq!(r.closing.unattributed,400);assert_eq!(r.unallocated,400);
    }
    #[test] fn departure_preserves_identity(){
        let a=settle(&Population::phase_ix(),&period(0)).unwrap();
        let mut p=period(500);p.depart=vec!["A_1".into()];p.enter=vec!["E_0".into()];
        let b=settle(&a.closing,&p).unwrap();
        assert!(b.closing.lots.iter().any(|l|l.id=="A_1"&&l.amount==100));
        assert!(!b.closing.lots.iter().any(|l|l.id=="E_0"&&l.origin<=a.closing.epoch));
        assert_eq!(b.closing.outstanding().unwrap(),1100);
        let c=settle(&b.closing,&period(1300)).unwrap();
        assert_eq!(c.historical_reserved.get("A_1"),Some(&100));
        assert_eq!(c.closing.outstanding().unwrap(),400);
    }
    #[test] fn rotating_cent(){
        let mut s=Population::phase_ix();let mut extra=BTreeMap::new();
        for _ in 0..6 { let r=settle(&s,&period(1)).unwrap();
            for a in r.awards { *extra.entry(a.id).or_insert(0u64)+=a.funded; } s=r.closing; }
        assert!(extra.values().all(|&v|v==1));
    }
    #[test] fn no_active_population(){
        let s=Population::phase_ix();let mut p=period(1000);p.depart=s.active.iter().cloned().collect();
        let r=settle(&s,&p).unwrap();assert_eq!(r.current_due,0);assert_eq!(r.closing.outstanding().unwrap(),400);
    }
    #[test] fn rejects_identity_reuse(){
        let mut p=period(0);p.enter=vec!["A_0".into()];
        assert!(settle(&Population::phase_ix(),&p).is_err());
    }
    #[test] fn grid_conservation(){
        for funding in [0,400,800] {for award in [0,100,200] {for leave in [false,true] {
            let mut s=Population::phase_ix();
            for i in 0..360 {let mut p=period(funding);p.award=award;
                if leave&&i==1 {p.depart=vec!["A_1".into()];p.enter=vec!["E_0".into()];}
                let r=settle(&s,&p).unwrap();
                let back:u64=r.historical_reserved.values().sum();
                assert_eq!(s.outstanding().unwrap()+r.current_due,r.closing.outstanding().unwrap()+r.current_funded+back);
                assert_eq!(funding,r.current_funded+back+r.unallocated);
                assert_eq!(r.closing.unattributed,400);
                s=r.closing;
            }
        }}}
    }
}
