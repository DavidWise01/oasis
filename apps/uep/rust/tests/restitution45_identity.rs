//! RESTITUTION-45: exact arithmetic identity qualification. .dlw
#[path = "../src/restitution.rs"]
mod restitution;
use restitution::estimate;

#[test]
fn heterogeneous_score_grid_matches_independent_factored_reference() {
    let mut seed = 45u64;
    for value in [0,1,99,100,120_000_000_000,u64::MAX] {
        for _ in 0..256 {
            let mut next = || { seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1); ((seed >> 32)%1000) as u16 };
            let p = std::array::from_fn(|_| next());
            let n = std::array::from_fn(|_| next());
            let d = 21978u128;
            let ps: u128 = p.iter().map(|&v| u128::from(v)).sum();
            let ns: u128 = n.iter().map(|&v| u128::from(999-v)).sum();
            let numerator = u128::from(value)*ps*ns*41;
            let denominator = d*d*200;
            let expected = numerator/denominator;
            let got = estimate(value,p,n).unwrap();
            assert_eq!(u128::from(got.due_cents),expected);
            assert_eq!(u128::from(got.carbon_cents),expected*4/5);
            assert_eq!(got.ai_cents,got.due_cents-got.carbon_cents);
        }
    }
}
