//! UEP-201R: append-only protection companion to the frozen native kernel.
use oasis_uep::{advance, Input, State};
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Protected {
    pub state: State,
    pub rate: u64,
    pub clear: u64,
    pub candidate: u64,
    pub blocked: bool,
}
pub fn step(s: &Protected, p: Input, ceiling: u64) -> Result<Protected, &'static str> {
    if s.rate > 100 || ceiling > 1_000_000 { return Err("invalid policy"); }
    let row = advance(&s.state, p)?;
    let blocked = row.current_paid < row.current_due
        || row.unmet.iter().flatten().any(|&x| x > 0)
        || row.closing.stock.iter().flatten().any(|&x| x < 10);
    let clear = if blocked { 0 } else { s.clear.saturating_add(1) };
    let rate = if blocked { 0 } else if clear >= 2 { (s.rate + 25).min(100) } else { s.rate };
    let candidate = (ceiling * rate / 100).min(row.closing.harm)
        .min(row.closing.repair_funds / 2)
        .min(row.closing.stock[0][0].saturating_sub(10) / 2);
    Ok(Protected { state: row.closing, rate, clear, candidate, blocked })
}
#[cfg(test)]
mod tests {
    use super::*;
    fn root() -> Protected { Protected { state: State::genesis(), rate: 50, clear: 0, candidate: 0, blocked: false } }
    fn input(funds: u64, inflow: u64) -> Input { Input { inflow, demand: 20, ubi_funds: funds, repair_funds: 10, new_harm: 1, decay_bps: 1000 } }
    #[test] fn grid() {
        for funds in [0,400,800] { for inflow in [0,20,40] { for ceiling in [0,5,20] {
            let mut s = root();
            for _ in 0..360 {
                let next = step(&s,input(funds,inflow),ceiling).unwrap();
                assert!(!next.blocked || next.candidate == 0);
                assert!(next.candidate <= ceiling);
                assert!(next.candidate <= next.state.harm);
                assert!(next.candidate * 2 <= next.state.repair_funds);
                assert!(next.candidate * 2 <= next.state.stock[0][0].saturating_sub(10));
                assert_eq!(next.state, advance(&s.state,input(funds,inflow)).unwrap().closing);
                s=next;
            }
        }}}
    }
    #[test] fn recovery() {
        let a=step(&root(),input(0,40),20).unwrap();
        assert_eq!(a.rate,0);
        let b=step(&a,input(800,40),20).unwrap();
        assert_eq!(b.rate,0);
        let c=step(&b,input(800,40),20).unwrap();
        assert_eq!(c.rate,25);
        assert!(c.candidate>0);
    }
    #[test] fn reject_invalid_policy() {
        let mut s=root(); s.rate=101;
        assert!(step(&s,input(800,40),20).is_err());
    }
}
