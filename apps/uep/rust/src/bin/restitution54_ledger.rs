//! RESTITUTION-54 canonical simulation ledger. .dlw
use oasis_uep::{run,Input,State,Epoch};
use sha2::{Digest,Sha256};
fn put(out:&mut Vec<u8>,n:u64){out.extend(n.to_be_bytes());}
fn state(out:&mut Vec<u8>,s:&State){
    put(out,s.epoch);
    for n in s.stock.iter().flatten(){put(out,*n);}
    for n in [s.population,s.harm,s.arrears,s.repair_funds,s.gain]{put(out,n);}
}
fn record(i:u64,p:Input,e:&Epoch)->Vec<u8>{
    let mut b=Vec::new();
    put(&mut b,i);
    for n in [p.inflow,p.demand,p.ubi_funds,p.repair_funds,p.new_harm,p.decay_bps]{put(&mut b,n);}
    state(&mut b,&e.opening);state(&mut b,&e.closing);
    for n in [e.current_due,e.current_paid,e.backpay]{put(&mut b,n);}
    for n in e.unmet.iter().flatten(){put(&mut b,*n);}
    b
}
fn genesis(s:&State)->[u8;32]{
    let mut b=b"RESTITUTION54/GENESIS/v1".to_vec();state(&mut b,s);
    Sha256::digest(b).into()
}
fn link(prev:[u8;32],b:&[u8])->[u8;32]{
    let mut h=Sha256::new();h.update(b"RESTITUTION54/ROW/v1");h.update(prev);h.update(b);h.finalize().into()
}
fn hex(b:&[u8])->String{b.iter().map(|n|format!("{n:02x}")).collect()}
fn main(){
    let root=State::genesis();
    let p=Input{inflow:20,demand:20,ubi_funds:400,repair_funds:10,new_harm:1,decay_bps:1000};
    let rows=run(&root,&[p;360]).expect("bounded simulation");
    let mut prev=genesis(&root);
    println!("{{\"type\":\"genesis\",\"digest\":\"{}\"}}",hex(&prev));
    for (i,e) in rows.iter().enumerate(){
        let b=record(i as u64,p,e);let next=link(prev,&b);
        println!("{{\"type\":\"row\",\"index\":{},\"previous\":\"{}\",\"payload\":\"{}\",\"digest\":\"{}\"}}",i,hex(&prev),hex(&b),hex(&next));
        prev=next;
    }
    println!("{{\"type\":\"terminal\",\"count\":{},\"digest\":\"{}\",\"actual_transactions\":0}}",rows.len(),hex(&prev));
}
#[cfg(test)]
mod tests{
 use super::*;
 #[test]fn canonical_replay_and_mutation(){
 let s=State::genesis();let p=Input{inflow:20,demand:20,ubi_funds:400,repair_funds:10,new_harm:1,decay_bps:1000};
 let rows=run(&s,&[p;360]).unwrap();
 let fold=|rs:&[Epoch]|rs.iter().enumerate().fold(genesis(&s),|h,(i,e)|link(h,&record(i as u64,p,e)));
 assert_eq!(fold(&rows),fold(&run(&s,&[p;360]).unwrap()));
 assert_ne!(fold(&rows),fold(&rows[..359]));
 let mut altered=rows.clone();altered[179].closing.harm+=1;
 assert_ne!(fold(&rows),fold(&altered));
 let mut swapped=rows.clone();swapped.swap(0,1);assert_ne!(fold(&rows),fold(&swapped));
 assert_eq!(record(0,p,&rows[0]).len(),464);
 }
}
