/* GAME GEAR FROM ZERO · original machine/bus/VDP/PSG implementation.
   Milestone: SMS/Game Gear Mode-4 background, sprites, Sega mapper,
   buttons, simple SN76489 audio. Unimplemented features documented. */
(function(root){'use strict';
const FRAME_LINES=262, CYCLES_PER_LINE=228;
class Machine {
 constructor(){if(!root.GGZ80)throw Error('GGZ80 must load before GGMachine');
  this.ram=new Uint8Array(8192);this.vram=new Uint8Array(16384);
  this.cram=new Uint8Array(64);this.vdpRegs=new Uint8Array(16);
  this.framebuffer=new Uint8ClampedArray(160*144*4);
  this.rom=new Uint8Array(0x4000);this.banks=[0,1,2];this.mapper=0;
  this.sram=new Uint8Array(16384);this.sramEnabled=false;
  this.keys={up:false,down:false,left:false,right:false,b1:false,b2:false,start:false};
  this.vaddr=0;this.vcode=0;this.vlatch=null;this.readBuffer=0;this.status=0;this.line=0;this.frames=0;
  this.psg={tone:[0x100,0x100,0x100],vol:[15,15,15,15],noise:0,phase:[0,0,0,0],latchCh:0,latchVol:false,stereo:255,lfsr:0x8000,noiseClock:0,rate:22050};
  this.cpu=new root.GGZ80(this);this.reset();}
 reset(){this.ram.fill(0);this.vram.fill(0);this.cram.fill(0);this.vdpRegs.fill(0);this.banks=[0,1,2];this.mapper=0;this.sramEnabled=false;this.vaddr=0;this.vcode=0;this.vlatch=null;this.readBuffer=0;this.status=0;this.line=0;this.frames=0;this.cpu.reset();this.psg.vol=[15,15,15,15];this.psg.phase=[0,0,0,0];this.psg.lfsr=0x8000;}
 load(bytes){const b=bytes instanceof Uint8Array?bytes:new Uint8Array(bytes);if(!b.length)throw Error('Empty Game Gear ROM');
  if(b.length>4*1024*1024)throw Error('ROM exceeds experimental 4 MiB limit');
  this.rom=b;this.reset();return {bytes:b.length,banks:Math.ceil(b.length/16384)};
 }
 romByte(bank,off){const total=Math.max(1,Math.ceil(this.rom.length/16384));const idx=(bank%total*16384+off)%this.rom.length;return this.rom[idx]}
 read(address){const a=address&65535;
  if(a<0x4000)return this.romByte(0,a);
  if(a<0x8000)return this.romByte(this.banks[1],a-0x4000);
  if(a<0xc000)return this.sramEnabled?this.sram[a-0x8000]:this.romByte(this.banks[2],a-0x8000);
  return this.ram[a&8191];
 }
 write(address,value){const a=address&65535,v=value&255;
  if(a>=0xc000){this.ram[a&8191]=v;
   if(a===0xfffc){this.mapper=v;this.sramEnabled=!!(v&8)}
   else if(a===0xfffd)this.banks[0]=v;
   else if(a===0xfffe)this.banks[1]=v;
   else if(a===0xffff)this.banks[2]=v;
  }else if(a>=0x8000&&this.sramEnabled)this.sram[a-0x8000]=v;
 }
 press(name,on){if(name in this.keys)this.keys[name]=!!on;}
 input(port){const p=port&255;
  if(p===0xbe)return this.readData();
  if(p===0xbf)return this.readStatus();
  if(p===0x7e)return this.line&255;
  if(p===0x7f)return ((this.cpu.cycles/2)%228)&255;
  if(p===0x00)return this.keys.start?0x7f:0xff;
  if(p===0xdc||p===0xc0){let v=0xff;const buttons=['up','down','left','right','b1','b2'];buttons.forEach((k,i)=>{if(this.keys[k])v&=~(1<<i)});return v}
  if(p===0xdd||p===0xc1)return 0xff;
  return 0xff;
 }
 output(port,val){const p=port&255,v=val&255;
  if(p===0xbe)this.writeData(v);
  else if(p===0xbf)this.writeControl(v);
  else if(p===0x7f)this.writePSG(v);
  else if(p===0x06)this.psg.stereo=v;
 }
 writeControl(v){if(this.vlatch===null){this.vlatch=v;return}
  const low=this.vlatch;this.vlatch=null;
  this.vcode=v>>6;
  if(this.vcode===2){this.vdpRegs[v&15]=low;return}
  this.vaddr=((v&63)<<8)|low;
  if(this.vcode===0){this.readBuffer=this.vram[this.vaddr];this.vaddr=(this.vaddr+1)&0x3fff}
 }
 writeData(v){if(this.vcode===3){this.cram[this.vaddr&63]=v}else{this.vram[this.vaddr&0x3fff]=v}
  this.vaddr=(this.vaddr+1)&0x3fff;this.vlatch=null;
 }
 readData(){const old=this.readBuffer;this.readBuffer=this.vram[this.vaddr&0x3fff];this.vaddr=(this.vaddr+1)&0x3fff;this.vlatch=null;return old}
 readStatus(){const s=this.status;this.status=0;this.vlatch=null;return s}
 palette(i){i&=31;const lo=this.cram[i*2],hi=this.cram[i*2+1];return [((lo&15)*17),((lo>>4&15)*17),((hi&15)*17)]}
 tileColor(tile,x,y){const a=((tile&511)*32+(y&7)*4)&16383,bit=7-(x&7);return((this.vram[a]>>bit)&1)|(((this.vram[a+1]>>bit)&1)<<1)|(((this.vram[a+2]>>bit)&1)<<2)|(((this.vram[a+3]>>bit)&1)<<3)}
 bgPixel(px,py){const scrollX=this.vdpRegs[8],scrollY=this.vdpRegs[9];
  const x=(px+scrollX)&255,y=(py+scrollY)&255;
  const namebase=(this.vdpRegs[2]&14)<<10;
  const a=(namebase+((y>>3)*32+(x>>3))*2)&0x3fff;
  const word=this.vram[a]|this.vram[(a+1)&0x3fff]<<8;
  const tile=word&511,fx=word&512,fy=word&1024,pal=word&2048,priority=word&4096;
  const ix=fx?7-(x&7):(x&7),iy=fy?7-(y&7):(y&7);
  return {color:this.tileColor(tile,ix,iy)|(pal?16:0),priority:!!priority,solid:this.tileColor(tile,ix,iy)!==0};
 }
 drawFrame(){const rgba=this.framebuffer,display=!!(this.vdpRegs[1]&64),backdrop=this.vdpRegs[7]&15;
  // Genuine GG hardware LCD viewport: SMS 256x192 coordinates cropped
  // x=48..207 and y=24..167, giving exactly 160x144.
  const sprites=this.buildSprites();
  let off=0;
  for(let yy=0;yy<144;yy++)for(let xx=0;xx<160;xx++){
   const vx=xx+48,vy=yy+24;
   const bg=display?this.bgPixel(vx,vy):{color:backdrop,priority:false,solid:false};
   let index=display?bg.color:backdrop;
   if(display){for(const sp of sprites){
    const sx=vx-sp.x,sy=vy-sp.y;if(sx<0||sy<0||sx>=sp.size||sy>=sp.size)continue;
    const localX=sp.scale2?sx>>1:sx,localY=sp.scale2?sy>>1:sy;
    const tile=sp.tile+(localY>=8?1:0);
    const col=this.tileColor(tile,localX&7,localY&7);
    if(col&&! (bg.priority&&bg.solid)){index=16+col;break;}
   }}
   const [r,g,b]=this.palette(index);rgba[off++]=r;rgba[off++]=g;rgba[off++]=b;rgba[off++]=255;
  }return rgba;
 }
 buildSprites(){const sprites=[],base=(this.vdpRegs[5]&0x7e)<<7,large=!!(this.vdpRegs[1]&2),scale2=!!(this.vdpRegs[1]&1);
  for(let i=0;i<64;i++){const rawY=this.vram[(base+i)&16383];if(rawY===0xd0)break;
   const y=(rawY+1)&255,x=this.vram[(base+0x80+i*2)&16383],tile0=this.vram[(base+0x81+i*2)&16383];
   const tile=(this.vdpRegs[6]&4?256:0)+(large?(tile0&254):tile0);
   sprites.push({x,y:y>224?y-256:y,tile,size:(large?16:8)*(scale2?2:1),scale2});}return sprites;
 }
 writePSG(byte){const p=this.psg,v=byte&255;
  if(v&128){p.latchCh=(v>>5)&3;p.latchVol=!!(v&16);if(p.latchVol)p.vol[p.latchCh]=v&15;else if(p.latchCh===3){p.noise=v&7;p.lfsr=0x8000}else p.tone[p.latchCh]=(p.tone[p.latchCh]&0x3f0)|(v&15)}
  else if(p.latchVol)p.vol[p.latchCh]=v&15;
  else if(p.latchCh!==3)p.tone[p.latchCh]=(p.tone[p.latchCh]&15)|((v&63)<<4);
 }
 audioSamples(n=368){const out=new Float32Array(n*2),p=this.psg,clock=3579545/32;
  for(let i=0;i<n;i++){
   let left=0,right=0;
   for(let ch=0;ch<4;ch++){
    let value=0;
    if(ch<3){const frequency=clock/Math.max(1,p.tone[ch]);p.phase[ch]=(p.phase[ch]+frequency/p.rate)%1;value=p.phase[ch]<.5?1:-1}
    else{const freq=clock/(p.noise&3?([16,32,64,64][p.noise&3]):16);p.phase[3]+=(freq/p.rate);if(p.phase[3]>=1){p.phase[3]%=1;const bit=(p.lfsr^(p.lfsr>>((p.noise&4)?3:1)))&1;p.lfsr=(p.lfsr>>1)|bit<<15}value=(p.lfsr&1)?1:-1}
    const vol=Math.pow(10,-2*p.vol[ch]/20)*.10*value;
    if(p.stereo&(1<<(ch+4)))left+=vol;if(p.stereo&(1<<ch))right+=vol;
   }
   out[i*2]=left;out[i*2+1]=right;
  }return out;
 }
 runFrame(){if(!this.rom.length)throw Error('No ROM loaded');
  for(let y=0;y<FRAME_LINES;y++){this.line=y;if(y===192){this.status|=128;if(this.vdpRegs[1]&32)this.cpu.interrupt()}
   let budget=CYCLES_PER_LINE,guard=0;while(budget>0&&guard++<200){budget-=this.cpu.step();}
  }
  this.frames++;return {frame:this.frames,pixels:this.drawFrame(),audio:this.audioSamples()};
 }
}
root.GGMachine=Machine;
})(typeof window!=='undefined'?window:globalThis);