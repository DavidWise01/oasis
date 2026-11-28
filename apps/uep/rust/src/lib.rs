//! UEP-201: deterministic long-horizon obligation and capacity kernel.
//! .dlw — synthetic simulation; no actual transactions.
pub const BASELINE_COMMIT: &str = "0bdfb7db06f1eb771c6e1bfc7c61a05ebceb8a6b";
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct State {
    pub epoch: u64,
    pub stock: [[u64; 4]; 3],
    pub population: u64,
    pub harm: u64,
    pub arrears: u64,
    pub repair_funds: u64,
    pub gain: u64,
}
impl State {
    pub fn genesis() -> Self {
        Self { epoch: 6, stock: [[90;4],[80;4],[70;4]], population: 6,
            harm: 17, arrears: 400, repair_funds: 326, gain: 15 }
    }
}
#[derive(Clone, Copy, Debug)]
pub struct Input {
    pub inflow: u64,
    pub demand: u64,
    pub ubi_funds: u64,
    pub repair_funds: u64,
    pub new_harm: u64,
    pub decay_bps: u64,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Epoch {
    pub opening: State,
    pub closing: State,
    pub current_due: u64,
    pub current_paid: u64,
    pub backpay: u64,
    pub unmet: [[u64;4];3],
}
pub fn advance(s: &State, p: Input) -> Result<Epoch, &'static str> {
    if p.decay_bps > 10_000 || s.gain > 30 || s.stock.iter().flatten().any(|&x| x > 100)
        || [p.inflow,p.demand,p.ubi_funds,p.repair_funds,p.new_harm,s.population].iter().any(|&x| x > 1_000_000) {
        return Err("invalid bounded input");
    }
    let mut next = s.clone();
    next.epoch = s.epoch.checked_add(1).ok_or("epoch overflow")?;
    let mut unmet = [[0;4];3];
    for r in 0..3 { for k in 0..4 {
        let gain = if r == 0 && k == 0 { s.gain } else { 0 };
        let available = (s.stock[r][k] + p.inflow + gain).min(100);
        let delivered = p.demand.min(available.saturating_sub(5));
        next.stock[r][k] = available - delivered;
        unmet[r][k] = p.demand - delivered;
    }}
    let due = s.population * 100;
    let paid = due.min(p.ubi_funds);
    let backpay = s.arrears.min(p.ubi_funds - paid);
    next.arrears = (s.arrears - backpay).checked_add(due - paid).ok_or("arrears overflow")?;
    next.harm = s.harm.checked_add(p.new_harm).ok_or("harm overflow")?;
    next.repair_funds = s.repair_funds.checked_add(p.repair_funds).ok_or("fund overflow")?;
    next.gain = s.gain - (s.gain * p.decay_bps + 9_999) / 10_000;
    Ok(Epoch { opening: s.clone(), closing: next, current_due: due, current_paid: paid, backpay, unmet })
}
pub fn run(root: &State, inputs: &[Input]) -> Result<Vec<Epoch>, &'static str> {
    if inputs.len() > 10_000 { return Err("horizon limit"); }
    let mut state = root.clone();
    let mut rows = Vec::with_capacity(inputs.len());
    for &p in inputs {
        let row = advance(&state, p)?;
        state = row.closing.clone();
        rows.push(row);
    }
    Ok(rows)
}
#[cfg(test)]
mod tests {
    use super::*;
    fn frame() -> Input { Input { inflow: 20, demand: 20, ubi_funds: 400, repair_funds: 10, new_harm: 1, decay_bps: 1000 } }
    #[test] fn frozen_genesis() {
        let s = State::genesis();
        assert_eq!(s.stock, [[90;4],[80;4],[70;4]]);
        assert_eq!((s.harm,s.arrears,s.repair_funds,s.gain),(17,400,326,15));
    }
    #[test] fn long_horizon_conservation() {
        let root = State::genesis();
        let rows = run(&root, &[frame(); 360]).unwrap();
        for (i,r) in rows.iter().enumerate() {
            assert_eq!(r.opening, if i == 0 { root.clone() } else { rows[i-1].closing.clone() });
            assert_eq!(r.opening.arrears+r.current_due, r.closing.arrears+r.current_paid+r.backpay);
            assert_eq!(r.closing.harm,r.opening.harm+1);
            assert_eq!(r.closing.repair_funds,r.opening.repair_funds+10);
            assert!(r.closing.gain<=r.opening.gain);
        }
        assert_eq!(rows.last().unwrap().closing.arrears,72400);
        assert_eq!(rows.last().unwrap().closing.harm,377);
    }
    #[test] fn prefix_and_replay() {
        let s=State::genesis(); let p=[frame();24];
        let full=run(&s,&p).unwrap();
        for n in 0..=p.len() { assert_eq!(run(&s,&p[..n]).unwrap(),full[..n]); }
        assert_eq!(s,State::genesis());
    }
    #[test] fn funding_non_offset() {
        let s=State::genesis(); let mut p=frame();
        let a=advance(&s,p).unwrap(); p.repair_funds=0;
        let b=advance(&s,p).unwrap();
        assert_eq!((a.current_paid,a.backpay,a.closing.arrears,a.closing.stock),(b.current_paid,b.backpay,b.closing.arrears,b.closing.stock));
    }
    #[test] fn rejects_bad_input() {
        let mut p=frame();p.decay_bps=10001;
        assert!(advance(&State::genesis(),p).is_err());
    }
}

// UEP-202R: reusable population ledger.
pub mod population;

// UEP-203R: 42-Universe model estimate kernel.
pub mod restitution;

// UEP-204R: hash-linked restitution evidence.
pub mod evidence;

// UEP-205R: independent restitution accounting bridge.
pub mod bridge;

// UEP-206R: systemic case-level prioritization.
pub mod priority;

// UEP-207R: staged restorative infrastructure conversion.
pub mod infrastructure;

// UEP-208R: adaptive forward protection.
pub mod recovery;

// UEP-209R: browser-facing arithmetic ABI.
pub mod browser;

// UEP-216R: complete axiom-vector ABI.
pub mod vector;

// UEP-217R: persistent evidence snapshots.
pub mod journal;

pub mod lifecycle;

pub mod generation;

pub mod capacity;

pub mod dividend;

pub mod entitlement;

pub mod arrears;

pub mod equilibrium;

pub mod stress;

pub mod universe;

pub mod expenditure;

pub mod restoration;

pub mod regeneration;

pub mod adaptive;

pub mod forward;

pub mod executable;

pub mod request_codec;

pub mod state_hash;

pub mod replay_archive;

pub mod checkpoint;

pub mod integrated_abi;

pub mod linked_segment;

pub mod cross_arrears;

pub mod identity_continuity;

pub mod capacity_inheritance;

pub mod multi_archive;

pub mod obligation_index;

pub mod identity_index;

pub mod funding_cursor;

pub mod working_projection;

pub mod indexed_recovery;

pub mod verification_profile;

pub mod balance_tree;

pub mod membership_tree;

pub mod chronology_tree;

pub mod authenticated_state;

pub mod authenticated_recovery;

pub mod compact_membership;

pub mod changed_path;

pub mod incremental_membership;

pub mod incremental_balance;
