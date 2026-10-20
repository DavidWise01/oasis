/* FIRST LIGHT - Original Game Gear cartridge generator (Z80 machine code).
   No borrowed game engine or copyrighted ROM: assembles a 16 KiB .gg on demand.
   Walkable maze / CPU-side wall collision / VDP sprites / two PSG/color abilities.
*/
(function(root){'use strict';
function create(){
 const rom=new Uint8Array(0x4000),labels=new Map(),fixups=[];
 let pc=0;
 const emit=(...b)=>{for(const v of b){if(pc>=0x1000)throw Error('First Light program exceeds 0x1000');rom[pc++]=v&255;}};
 const at=n=>{pc=n};
 const label=n=>{if(labels.has(n))throw Error('Duplicate label '+n);labels.set(n,pc)};
 const word=n=>emit(n&255,(n>>>8)&255);
 const ld8=(val)=>emit(0x3e,val);
 const io=(port,n)=>{ld8(n);emit(0xd3,port)};
 const reg=(i,v)=>{io(0xbf,v);io(0xbf,0x80|i)};
 const vaddr=(a,mode)=>{io(0xbf,a&255);io(0xbf,((a>>8)&0x3f)|(mode<<6))};
 const fix=(op,n)=>{emit(op);fixups.push([pc,n]);word(0)};
 const jp=n=>fix(0xc3,n),call=n=>fix(0xcd,n);
 const jcond=(op,n)=>fix(op,n);
 const memLoad=n=>{emit(0x3a);word(n)},memStore=n=>{emit(0x32);word(n)};
 const imm16=(regop,n)=>{emit(regop);word(n)};
 const T={x:0xc001,y:0xc002,steps:0xc003,blocked:0xc004,timer:0xc005,input:0xc006,tryx:0xc007,tryy:0xc008,ability:0xc009,irqcount:0xc00a};
 function stream(addr,mode,name,size){vaddr(addr,mode);fix(0x21,name);imm16(0x01,size);
  const n='copy_'+name;label(n);emit(0x7e,0xd3,0xbe,0x23,0x0b,0x78,0xb1);jcond(0xc2,n);
 }
 // Reset vector and interrupt handler. RETI is executed by OUR Z80 core.
 at(0);emit(0xc3,0,1);at(0x38);emit(0xf5);memLoad(T.irqcount);emit(0x3c);memStore(T.irqcount);emit(0xf1,0xed,0x4d);
 at(0x100);label('BOOT');
 emit(0xf3);imm16(0x31,0xdff0);ld8(8);memStore(T.x);ld8(5);memStore(T.y);
 ld8(0);memStore(T.timer);memStore(T.steps);memStore(T.blocked);memStore(T.ability);
 reg(0,4);reg(1,0x60);reg(2,14);reg(5,126);reg(6,0);reg(7,0);reg(8,0);reg(9,0);
 stream(0,3,'PALETTE',64);
 stream(0,1,'TILES',96);
 stream(0x3800,1,'NAMETABLE',1536);
 vaddr(0x3f01,1);io(0xbe,0xd0);
 call('WRITE_SPRITE');
 ld8(0xa5);memStore(0xc000); // CPU has completed hardware setup
 label('MAIN');emit(0xfb,0x76);call('TICK');jp('MAIN');
 label('TICK');
 memLoad(T.timer);emit(0x3c);memStore(T.timer);emit(0xfe,7);jcond(0xda,'TICK_RETURN');
 emit(0xaf);memStore(T.timer);
 // Read Game Gear joystick port through the emulated bus.
 emit(0xdb,0xdc);memStore(T.input);
 memLoad(T.x);memStore(T.tryx);memLoad(T.y);memStore(T.tryy);
 memLoad(T.input);emit(0xcb,0x47);jcond(0xc2,'TEST_DOWN');
 memLoad(T.tryy);emit(0x3d);memStore(T.tryy);jp('VALIDATE');
 label('TEST_DOWN');memLoad(T.input);emit(0xcb,0x4f);jcond(0xc2,'TEST_LEFT');
 memLoad(T.tryy);emit(0x3c);memStore(T.tryy);jp('VALIDATE');
 label('TEST_LEFT');memLoad(T.input);emit(0xcb,0x57);jcond(0xc2,'TEST_RIGHT');
 memLoad(T.tryx);emit(0x3d);memStore(T.tryx);jp('VALIDATE');
 label('TEST_RIGHT');memLoad(T.input);emit(0xcb,0x5f);jcond(0xc2,'ACTIONS');
 memLoad(T.tryx);emit(0x3c);memStore(T.tryx);jp('VALIDATE');
 label('VALIDATE');
 // Bound world to the 20×18 center viewport.
 memLoad(T.tryx);emit(0xfe,6);jcond(0xda,'BLOCKED');emit(0xfe,26);jcond(0xd2,'BLOCKED');
 memLoad(T.tryy);emit(0xfe,3);jcond(0xda,'BLOCKED');emit(0xfe,21);jcond(0xd2,'BLOCKED');
 // Read 1-byte ROM collision tiles. address = map + y*32 + x.
 memLoad(T.tryy);emit(0x6f,0x26,0);for(let i=0;i<5;i++)emit(0x29);
 memLoad(T.tryx);emit(0x5f,0x16,0,0x19);fix(0x11,'COLLISION');emit(0x19,0x7e,0xb7);jcond(0xc2,'BLOCKED');
 memLoad(T.tryx);memStore(T.x);memLoad(T.tryy);memStore(T.y);
 memLoad(T.steps);emit(0x3c);memStore(T.steps);call('WRITE_SPRITE');jp('ACTIONS');
 label('BLOCKED');memLoad(T.blocked);emit(0x3c);memStore(T.blocked);
 label('ACTIONS');
 // Release synthesized PSG note each tick; B1 and B2 re-trigger it.
 io(0x7f,0x9f);
 memLoad(T.input);emit(0xcb,0x67);jcond(0xc2,'B2_TEST');call('ABILITY_ONE');jp('TICK_RETURN');
 label('B2_TEST');memLoad(T.input);emit(0xcb,0x6f);jcond(0xc2,'TICK_RETURN');call('ABILITY_TWO');
 label('TICK_RETURN');emit(0xc9);
 label('WRITE_SPRITE');
 vaddr(0x3f00,1);memLoad(T.y);emit(0x87,0x87,0x87,0x3d,0xd3,0xbe);
 vaddr(0x3f80,1);memLoad(T.x);emit(0x87,0x87,0x87,0xd3,0xbe);io(0xbe,2);emit(0xc9);
 label('ABILITY_ONE');ld8(1);memStore(T.ability);
 vaddr(2,3);io(0xbe,0xf0);io(0xbe,0x0f);
 io(0x7f,0x84);io(0x7f,0x20);io(0x7f,0x90);emit(0xc9);
 label('ABILITY_TWO');ld8(2);memStore(T.ability);
 vaddr(2,3);io(0xbe,0x0f);io(0xbe,0x0f);
 io(0x7f,0x88);io(0x7f,0x30);io(0x7f,0x90);emit(0xc9);
 // Data can be found in the main ROM's first 16KB by LD HL,addr.
 const dataAt=(name,addr,bytes)=>{labels.set(name,addr);rom.set(bytes,addr)};
 const palette=new Uint8Array(64);const setColor=(n,r,g,b)=>{palette[n*2]=r|(g<<4);palette[n*2+1]=b};
 setColor(0,0,0,1);setColor(1,15,0,2);setColor(2,1,2,4);setColor(3,12,13,15);
 setColor(16,0,0,0);setColor(17,6,14,15);setColor(18,8,8,15);setColor(19,15,15,15);
 dataAt('PALETTE',0x1000,palette);
 const tiles=new Uint8Array(96);
 for(let row=0;row<8;row++){
  // floor: subtle pixel speckles from color 2
  const f=(row%2)?0x11:0x44;tiles[row*4]=0;tiles[row*4+1]=f;
  // wall: crystalline diagonal color 1/3
  tiles[32+row*4]=row%2?0x7e:0xff;tiles[32+row*4+1]=row%2?0x24:0x42;
  // diamond-shaped sprite using palette 3 and 1
  const mask=[0x18,0x3c,0x7e,0xff,0xff,0x7e,0x3c,0x18][row];
  tiles[64+row*4]=mask;tiles[64+row*4+1]=mask;
 }
 dataAt('TILES',0x1080,tiles);
 const cells=new Uint8Array(32*24);
 for(let y=0;y<24;y++)for(let x=0;x<32;x++){
  const rx=x-6,ry=y-3;let wall=0;
  if(rx<0||rx>19||ry<0||ry>17)wall=1;
  else if(rx===0||rx===19||ry===0||ry===17)wall=1;
  else if(rx===7&&ry>=2&&ry<=14&&ry!==8)wall=1;
  else if(rx===13&&ry>=3&&ry<=15&&ry!==6&&ry!==11)wall=1;
  else if(ry===11&&rx>=3&&rx<=11&&rx!==9)wall=1;
  else if(ry===5&&rx>=14&&rx<=18&&rx!==16)wall=1;
  cells[y*32+x]=wall;
 }
 const table=new Uint8Array(1536);
 for(let i=0;i<cells.length;i++){table[i*2]=cells[i];table[i*2+1]=0;}
 dataAt('COLLISION',0x1200,cells);
 dataAt('NAMETABLE',0x1600,table);
 for(const [pos,key] of fixups){const value=labels.get(key);if(value===undefined)throw Error('Unresolved label '+key);rom[pos]=value&255;rom[pos+1]=value>>>8;}
 Object.defineProperty(rom,'firstLightInfo',{value:{labels:Object.fromEntries(labels),cells:Array.from(cells),source:'original-Z80-assembled-in-browser',programBytes:pc}});
 return rom;
}
root.GGFirstLight={create};
})(typeof window!=='undefined'?window:globalThis);