//! RESTITUTION-46: recovered checkpoint differential test. .dlw
#[path = "fixtures/restitution46_pinned.rs"]
mod pinned;
use oasis_uep::restitution as live;

#[test]
fn differential_checkpoint() {
    let mut seed=46u64;
    for value in [0,1,99,100,120_000_000_000,u64::MAX] {
        for i in 0..1024 {
            let mut next=|| {seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1); ((seed>>32)%1000) as u16};
            let mut p=std::array::from_fn(|_| next());
            let mut n=std::array::from_fn(|_| next());
            if i%16==0 {p[i%22]=1000;}
            if i%16==1 {n[i%22]=u16::MAX;}
            let a=pinned::estimate(value,p,n).map(|x|(x.due_cents,x.carbon_cents,x.ai_cents));
            let b=live::estimate(value,p,n).map(|x|(x.due_cents,x.carbon_cents,x.ai_cents));
            assert_eq!(a,b);
        }
    }
}
