use std::{collections::BTreeMap,env,io::{Read,Write},net::{TcpListener,TcpStream},sync::{Mutex,OnceLock}};
const MAX_N:usize=65536;
fn u32be(a:&[u8])->usize{u32::from_be_bytes(a.try_into().unwrap()) as usize}
fn crc32(a:&[u8])->u32{let mut c:u32=!0;for b in a{c^=*b as u32;for _ in 0..8{c=(c>>1)^if c&1!=0{0xedb88320}else{0};}}!c}
fn op(a:&mut Vec<usize>,c:u8,inverse:bool){let n=a.len();if n==0{return;}
 match c{b'U'|b'D'|b'A'=>{let k=if c==b'U'{1}else if c==b'D'{-1}else{2};let k=if inverse{-k}else{k};a.rotate_right(k.rem_euclid(n as isize) as usize);},b'B'=>a.reverse(),b'L'|b'R'=>{let start=if c==b'L'{0}else{1};for i in (start..n-1).step_by(2){a.swap(i,i+1);}},_=>{}}
}
static MAPS:OnceLock<Mutex<BTreeMap<usize,(Vec<usize>,Vec<usize>)>>>=OnceLock::new();
fn maps(n:usize)->(Vec<usize>,Vec<usize>){let cache=MAPS.get_or_init(||Mutex::new(BTreeMap::new()));let mut c=cache.lock().unwrap();if let Some(x)=c.get(&n){return x.clone()}
 let mut pos:Vec<usize>=(0..n).collect();let mut neg:Vec<usize>=(0..n).rev().collect();const CODE:&[u8]=b"UUDDLRLRBASS";
 for _ in 0..5{for &k in CODE{op(&mut pos,k,false);}for &k in CODE.iter().rev(){op(&mut neg,k,true);}}
 neg.reverse();if c.len()>=16{let k=*c.keys().next().unwrap();c.remove(&k);}c.insert(n,(pos.clone(),neg.clone()));(pos,neg)
}
fn decode(wire:&[u8])->Option<Vec<u8>>{if wire.len()<16||wire.len()>16+2*MAX_N{return None}
 if &wire[0..4]!=b"OBF2"||wire[4]!=1||wire[5]!=1||wire[6]!=0||wire[7]!=0{return None}
 let n=u32be(&wire[8..12]);if n>MAX_N||wire.len()!=16+2*n||crc32(&wire[..wire.len()-4])!=u32be(&wire[wire.len()-4..]) as u32{return None}
 let (p,m)=maps(n);let mut left=vec![0u8;n];let mut right=vec![0u8;n];for i in 0..n{left[p[i]]=wire[12+i];right[m[i]]=wire[12+n+i];}if left!=right{return None}Some(left)
}
fn encode(bytes:&[u8])->Vec<u8>{let n=bytes.len();let(p,m)=maps(n);let mut out=vec![0u8;16+2*n];out[..4].copy_from_slice(b"OBF2");out[4]=1;out[5]=1;out[8..12].copy_from_slice(&(n as u32).to_be_bytes());for i in 0..n{out[12+i]=bytes[p[i]];out[12+n+i]=bytes[m[i]];}let crc=crc32(&out[..out.len()-4]);let end=out.len();out[end-4..].copy_from_slice(&crc.to_be_bytes());out}
fn handle(mut s:TcpStream){let _=s.set_nodelay(true);let _=s.set_read_timeout(Some(std::time::Duration::from_secs(5)));let _=s.set_write_timeout(Some(std::time::Duration::from_secs(5)));loop{
 let mut hdr=[0u8;4];if s.read_exact(&mut hdr).is_err(){break}
 let len=u32be(&hdr);if !(16..=16+2*MAX_N).contains(&len){let _=s.write_all(&[1,0,0,0,0]);break}
 let mut frame=vec![0u8;len];if s.read_exact(&mut frame).is_err(){break}
 let decoded=decode(&frame);let mut payload=decoded.as_ref().map(|bytes|encode(bytes)).unwrap_or_default();let mut response=Vec::with_capacity(5+payload.len());response.push(if decoded.is_some(){0}else{1});response.extend_from_slice(&(payload.len() as u32).to_be_bytes());response.append(&mut payload);
 if s.write_all(&response).is_err(){break}
 }}
fn main(){let port=env::args().nth(1).unwrap_or("31023".into());let listener=TcpListener::bind(format!("127.0.0.1:{port}")).unwrap();println!("READY rust {port}");for incoming in listener.incoming(){if let Ok(s)=incoming{handle(s)}}}
