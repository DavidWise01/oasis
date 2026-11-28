//! RESTITUTION-47: adversarial monetary boundaries. .dlw
use oasis_uep::restitution::estimate;
#[test]
fn extreme_values_and_scores() {
    for v in [0,1,4,5,99,100,199,200,u64::MAX-1,u64::MAX] {
        for p in [0,1,998,999] {
            for n in [0,1,998,999] {
                let e=estimate(v,[p;22],[n;22]).unwrap();
                let expected=u128::from(v)*u128::from(p)*u128::from(999-n)*41/(999u128*999*200);
                assert_eq!(u128::from(e.due_cents),expected);
                assert_eq!(e.carbon_cents.checked_add(e.ai_cents),Some(e.due_cents));
                assert!(e.due_cents<=v);
                if v<u64::MAX {
                    assert!(estimate(v+1,[p;22],[n;22]).unwrap().due_cents>=e.due_cents);
                }
            }
        }
    }
}
#[test]
fn every_score_position_rejects_out_of_range() {
    for i in 0..22 {
        for bad in [1000,u16::MAX] {
            let mut p=[999;22]; p[i]=bad;
            assert_eq!(estimate(u64::MAX,p,[0;22]),Err("score out of range"));
            let mut n=[0;22]; n[i]=bad;
            assert_eq!(estimate(0,[999;22],n),Err("score out of range"));
        }
    }
}
