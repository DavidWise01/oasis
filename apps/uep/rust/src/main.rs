use oasis_uep::{run, Input, State, BASELINE_COMMIT};
fn main() {
    let root = State::genesis();
    let frame = Input { inflow:20,demand:20,ubi_funds:400,repair_funds:10,new_harm:1,decay_bps:1000 };
    let rows = run(&root, &[frame;360]).expect("valid demo");
    println!("Phase IX source: {BASELINE_COMMIT}");
    println!("Opening: {root:?}");
    println!("Closing: {:?}", rows.last().expect("nonempty").closing);
    println!("Actual transactions: 0");
}
