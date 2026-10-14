// OASIS OBF2 v2.5, one exact Rust codec compiled to Linux native and wasm32.
// FROZEN v0.7 operator sequence UUDDLRLRBASS *5, no floor modification.
// No authentication, no quantum effects, no claims of zero propagation delay.
use std::cmp;
pub const MAX: usize = 65536;
pub const OVER: usize = 16;
pub const MAX_WIRE: usize = MAX * 2 + OVER;
const CODE: &[u8] = b"UUDDLRLRBASS";

#[derive(Default)]
pub struct Codec { n: usize, ready: bool, plus: Vec<usize>, minus: Vec<usize> }
fn step(a: &mut [usize], code: u8, inverse: bool) {
    let n=a.len(); if n==0 {return}
    match code {
        b'U'|b'D'|b'A' => {
            let mut k:isize = if code==b'U'{1}else if code==b'D'{-1}else{2};
            if inverse {k=-k}; a.rotate_right(k.rem_euclid(n as isize) as usize);
        },
        b'B'=>a.reverse(),
        b'L'|b'R'=> {let start=if code==b'L'{0}else{1};
            for i in (start..n.saturating_sub(1)).step_by(2){a.swap(i,i+1)}},
        _=>{}
    }
}
impl Codec {
    fn maps(&mut self,n:usize)->Result<(),&'static str>{
        if n>MAX {return Err("frame exceeds MAX")}
        if self.ready&&self.n==n{return Ok(())}
        self.n=n; self.plus=(0..n).collect(); self.minus=(0..n).rev().collect();
        for _ in 0..5 { for &c in CODE {step(&mut self.plus,c,false)} }
        for _ in 0..5 { for &c in CODE.iter().rev(){step(&mut self.minus,c,true)} }
        self.minus.reverse(); self.ready=true; Ok(())
    }
    pub fn encode(&mut self, input:&[u8],out:&mut [u8])->Result<usize,&'static str>{
        let n=input.len();self.maps(n)?;let len=OVER+2*n;
        if out.len()<len{return Err("small output buffer")}
        out[..12].copy_from_slice(b"OBF2\x01\x01\x00\x00\x00\x00\x00\x00");
        out[8..12].copy_from_slice(&(n as u32).to_be_bytes());
        for i in 0..n {out[12+i]=input[self.plus[i]];out[12+n+i]=input[self.minus[i]];}
        let crc=crc32(&out[..len-4]);out[len-4..len].copy_from_slice(&crc.to_be_bytes());
        Ok(len)
    }
    pub fn decode(&mut self,wire:&[u8],out:&mut [u8])->Result<usize,&'static str>{
        let len=wire.len();
        if len<OVER||len>MAX_WIRE{return Err("bad frame length")}
        if &wire[..4]!=b"OBF2"||wire[4]!=1||wire[5]!=1||wire[6]!=0||wire[7]!=0{return Err("bad protocol version")}
        let n=u32::from_be_bytes(wire[8..12].try_into().unwrap()) as usize;
        if n>MAX||len!=OVER+2*n||out.len()<n{return Err("inconsistent length")}
        let expected=u32::from_be_bytes(wire[len-4..len].try_into().unwrap());
        if crc32(&wire[..len-4])!=expected{return Err("bad CRC")}
        self.maps(n)?;
        for i in 0..n {out[self.plus[i]]=wire[12+i];}
        for i in 0..n {if out[self.minus[i]]!=wire[12+n+i]{return Err("rail mismatch")}}
        Ok(n)
    }
}
// Exact IEEE CRC32, computed at compile time. 8 bit operations/byte -> 1 table lookup/byte.
const CRC_TABLE: [u32; 256] = make_crc_table();
const fn make_crc_table() -> [u32; 256] {
    let mut t = [0u32; 256];
    let mut i = 0;
    while i < 256 {
        let mut c = i as u32;
        let mut j = 0;
        while j < 8 {
            c = (c >> 1) ^ if (c & 1) != 0 { 0xedb88320 } else { 0 };
            j += 1;
        }
        t[i] = c;
        i += 1;
    }
    t
}
fn crc32(s: &[u8]) -> u32 {
    let mut c = !0u32;
    for &b in s { c = (c >> 8) ^ CRC_TABLE[((c ^ (b as u32)) & 255) as usize]; }
    !c
}

#[cfg(target_arch="wasm32")]
mod wasm {
    use super::*;
    // Single-threaded wasm ABI. The host owns all network I/O.
    static mut INPUT:[u8;MAX]=[0;MAX];
    static mut FRAME:[u8;MAX_WIRE]=[0;MAX_WIRE];
    static mut RECOVERED:[u8;MAX]=[0;MAX];
    static mut CODEC:Option<Codec>=None;
    #[no_mangle] pub extern "C" fn max_bytes()->u32{MAX as u32}
    #[no_mangle] pub extern "C" fn input_ptr()->u32{std::ptr::addr_of_mut!(INPUT) as u32}
    #[no_mangle] pub extern "C" fn frame_ptr()->u32{std::ptr::addr_of_mut!(FRAME) as u32}
    #[no_mangle] pub extern "C" fn recovered_ptr()->u32{std::ptr::addr_of_mut!(RECOVERED) as u32}
    #[no_mangle] pub extern "C" fn encode(n:u32)->i32{
        if n as usize>MAX{return -1}
        unsafe {
            if CODEC.is_none(){CODEC=Some(Codec::default());}
            let engine=CODEC.as_mut().unwrap();
            let src=std::slice::from_raw_parts(std::ptr::addr_of!(INPUT) as *const u8,n as usize);
            let dst=std::slice::from_raw_parts_mut(std::ptr::addr_of_mut!(FRAME) as *mut u8,MAX_WIRE);
            engine.encode(src,dst).map(|len|len as i32).unwrap_or(-1)
        }
    }
    #[no_mangle] pub extern "C" fn decode(frame_len:u32)->i32{
        if frame_len as usize>MAX_WIRE{return -1}
        unsafe {
            if CODEC.is_none(){CODEC=Some(Codec::default());}
            let engine=CODEC.as_mut().unwrap();
            let src=std::slice::from_raw_parts(std::ptr::addr_of!(FRAME) as *const u8,frame_len as usize);
            let dst=std::slice::from_raw_parts_mut(std::ptr::addr_of_mut!(RECOVERED) as *mut u8,MAX);
            engine.decode(src,dst).map(|n|n as i32).unwrap_or(-1)
        }
    }
}
#[cfg(not(target_arch="wasm32"))]
mod native {
    use super::*;
    use std::{env,io::{Read,Write},net::{TcpListener,TcpStream},time::Instant};
    fn server_conn(mut stream:TcpStream)->std::io::Result<()>{
        stream.set_nodelay(true)?;stream.set_read_timeout(Some(std::time::Duration::from_secs(5)))?;
        let mut c=Codec::default();let mut restored=vec![0u8;MAX];let mut output=vec![0u8;MAX_WIRE];
        loop {
            let mut h=[0u8;4];if stream.read_exact(&mut h).is_err(){return Ok(())}
            let n=u32::from_be_bytes(h) as usize;
            if n<OVER||n>MAX_WIRE{stream.write_all(&[1,0,0,0,0])?;return Ok(())}
            let mut frame=vec![0u8;n];if stream.read_exact(&mut frame).is_err(){return Ok(())}
            let response=if let Ok(count)=c.decode(&frame,&mut restored) {
                c.encode(&restored[..count],&mut output).ok()
            }else{None};
            let k=response.unwrap_or(0);stream.write_all(&[if response.is_some(){0}else{1}])?;
            stream.write_all(&(k as u32).to_be_bytes())?;if k>0{stream.write_all(&output[..k])?}
        }
    }
    fn serve(port:u16)->std::io::Result<()>{
        let listener=TcpListener::bind(("127.0.0.1",port))?;
        println!("READY rust-native {port}");for s in listener.incoming(){if let Ok(s)=s{let _=server_conn(s);}}Ok(())
    }
    pub fn run(){
        let args:Vec<String>=env::args().collect();
        if args.get(1).map(|s|s.as_str())==Some("serve"){
            let port=args.get(2).and_then(|s|s.parse().ok()).unwrap_or(31221);
            serve(port).unwrap();return
        }
        // Native microbenchmark uses the very same Codec and no host-boundary copies.
        let mut c=Codec::default();let mut frame=vec![0;MAX_WIRE];let mut recovered=vec![0;MAX];
        let sizes=[214usize,4096,65536];let iters=[7000usize,1200,140];
        for (&n,&count) in sizes.iter().zip(iters.iter()){
            let src:Vec<u8>=(0..n).map(|i|((i*23)^(i>>3)) as u8).collect();
            let len=c.encode(&src,&mut frame).unwrap();
            if c.decode(&frame[..len],&mut recovered).unwrap()!=n||recovered[..n]!=src[..]{panic!("wrong recovery")}
            let mut times=Vec::new();
            for sweep in 0..5 {
                let start=Instant::now();
                for _ in 0..count {
                    let l=c.encode(&src,&mut frame).unwrap();
                    let x=c.decode(&frame[..l],&mut recovered).unwrap();
                    if x!=n {panic!("size mismatch")}
                    std::hint::black_box(&recovered[0..cmp::min(n,1)]);
                }
                times.push(start.elapsed().as_secs_f64()*1e6/count as f64);
                let _=sweep;
            }
            times.sort_by(|a,b|a.total_cmp(b));
            println!("NATIVE_BENCH size={} median_us={:.4} runs_us={:?}",n,times[2],times);
        }
    }
}
#[cfg(not(target_arch="wasm32"))]
fn main(){native::run()}
