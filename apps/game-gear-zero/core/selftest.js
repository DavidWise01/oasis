/* Diagnostic Game Gear cartridge generator. No copyrighted ROM bytes.
   It boots at 0000, writes Sega VDP register, CRAM and VRAM through OUT,
   initializes the 32x24 name table, and enters an idle JP loop. */
(function(root){'use strict';
function create(){
 const code=[];
 const emit=(...xs)=>code.push(...xs.map(x=>x&255));
 function out(port,n){emit(0x3e,n,0xd3,port)}
 function reg(i,v){out(0xbf,v);out(0xbf,0x80|i)}
 function addr(a,mode){out(0xbf,a&255);out(0xbf,((a>>8)&63)|(mode<<6))}
 emit(0xf3); // DI
 reg(0,0x04);reg(1,0x40);reg(2,0x0e);reg(5,0x7e);reg(7,0x00);reg(8,0);reg(9,0);
 // Game Gear 12-bit palette. 2 bytes per entry: R:G and B.
 addr(0,3);
 const colors=[[0,0,0],[15,0,0],[0,0,15],[15,15,0],[0,15,15],[15,0,15],[15,15,15]];
 for(let i=0;i<32;i++){const col=colors[i]||[0,0,0];out(0xbe,col[0]|(col[1]<<4));out(0xbe,col[2]);}
 // First two patterns. Each tile row: 4 bitplanes.
 addr(0,1);
 for(let tile=0;tile<2;tile++)for(let row=0;row<8;row++){
   out(0xbe,tile===0?0xaa:(row&1?0x0f:0xf0));
   out(0xbe,tile===0?0x55:(row&1?0xf0:0x0f));
   out(0xbe,0);out(0xbe,0);
 }
 // Populate 32x24 tiles using a deterministic striped sequence.
 addr(0x3800,1);
 emit(0x01,0x00,0x06); // LD BC, 1536 bytes of name entries
 const loop=code.length;
 emit(0x3e,0x00,0xd3,0xbe,0x0b,0x78,0xb1);
 const pos=code.length;emit(0x20,0); // JR NZ, loop
 code[pos+1]=((loop-(pos+2))&255);
 // Sprite attribute table termination marker at 3F00
 addr(0x3f00,1);out(0xbe,0xd0);
 // Mark success in work RAM and idle
 emit(0x3e,0xa5,0x32,0x00,0xc0);
 const idle=code.length;emit(0xc3,idle&255,idle>>8);
 if(code.length>0x4000)throw Error('Selftest code too long');
 const rom=new Uint8Array(0x4000);rom.set(code);
 const word='GG-ZERO ORIGINAL CORE TEST';
 for(let i=0;i<word.length;i++)rom[0x3f00+i]=word.charCodeAt(i)&127; // informational marker not executed
 return rom;
}
root.GGTestROM={create};
})(typeof window!=='undefined'?window:globalThis);