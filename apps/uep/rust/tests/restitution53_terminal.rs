//! RESTITUTION-53: full terminal-state and per-epoch conservation gate. .dlw
use oasis_uep::{run,Input,State};
#[test]
fn terminal_state_and_conservation() {
    let root=State::genesis();
    let frame=Input{inflow:20,demand:20,ubi_funds:400,repair_funds:10,new_harm:1,decay_bps:1000};
    let rows=run(&root,&[frame;360]).unwrap();
    assert_eq!(rows.len(),360);
    let mut prior=&root;
    for row in &rows {
        assert_eq!(&row.opening,prior);
        assert_eq!(row.closing.epoch,prior.epoch+1);
        assert_eq!(row.opening.arrears+row.current_due,row.closing.arrears+row.current_paid+row.backpay);
        assert_eq!(row.current_paid+row.backpay,400);
        prior=&row.closing;
    }
    assert_eq!(*prior,State{epoch:366,stock:[[80;4],[80;4],[70;4]],population:6,harm:377,arrears:72400,repair_funds:3926,gain:0});
}
