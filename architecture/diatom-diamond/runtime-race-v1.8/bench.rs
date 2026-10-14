use std::time::Instant;
const CODE:&[u8;12]=b"UUDDLRLRBASS";
fn op(a:&mut [u8;32],x:u8,inv:bool){match x{b'U'|b'D'|b'A'=>{let mut k=if x==b'U'{1}else if x==b'D'{-1}else{2};if inv{k=-k;}let k=((k%32)+32)%32;let mut tmp=[0u8;32];for i in 0..32{tmp[(i+k as usize)%32]=a[i]}*a=tmp;},b'L'|b'R'=>{let start=if x==b'L'{0}else{1};for i in (start..31).step_by(2){a.swap(i,i+1)}},b'B'=>a.reverse(),_=>{}}}
fn perm(a:&mut [u8;32],inv:bool){for _ in 0..5{for s in 0..12{op(a,CODE[if inv{11-s}else{s}],inv)}}}
fn main(){let n:usize=std::env::args().nth(1).unwrap_or("32768".into()).parse().unwrap();assert!(n>0&&n%32==0);let t=Instant::now();let mut ck:u32=2166136261;for first in (0..n).step_by(32){let mut src=[0u8;32];for j in 0..32{src[j]=((first+j)%44) as u8;}let mut pos=src;let mut neg=src;neg.reverse();perm(&mut pos,false);perm(&mut neg,true);let mut left=pos;let mut right=neg;perm(&mut left,true);perm(&mut right,false);right.reverse();assert_eq!(left,src);assert_eq!(right,src);for &x in pos.iter().chain(neg.iter()){ck=(ck^(x as u32)).wrapping_mul(16777619);}}
println!("{{\"runtime\":\"rust\",\"tokens\":{},\"checksum\":{},\"elapsed_s\":{:.9}}}",n,ck,t.elapsed().as_secs_f64());}
