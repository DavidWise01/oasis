/* RGB DIFFUSION ARENA · Original Game Gear cartridge assembler.
 * All game simulation, input, RGB neighbor propagation, score and rendering
 * run as Z80 machine code through GG-ZERO's Game Gear VRAM/CRAM I/O ports.
 * Classical binary channel propagation (OR automaton), not physical diffusion.
 */
(function(root){'use strict';
function create(){
 const out=new Uint8Array(16384), labels=new Map(),fixups=[];let pc=0;
 const S={x:0xc100,y:0xc101,ink:0xc102,selectLatch:0xc103,moveTimer:0xc104,tick:0xc105,score:0xc106,boot:0xc107,irq:0xc108,win:0xc109,drawlo:0xc10a,drawhi:0xc10b,keys:0xc10c,startLatch:0xc10d,steps:0xc10e,playerPaint:0xc10f};
 const FIELD=0xc200,NEXT=0xc300,COUNT=252, W=16,H=12;
 const emit=(...xs)=>{for(const x of xs){if(pc>=0x1000)throw Error('game code exceeds reserved region');out[pc++]=x&255}};
 const ww=n=>emit(n&255,n>>>8),label=k=>{if(labels.has(k))throw Error('duplicate '+k);labels.set(k,pc)},at=n=>pc=n,
       abs=(op,name)=>{emit(op);fixups.push({pos:pc,name});ww(0)},jp=name=>abs(0xc3,name),call=name=>abs(0xcd,name),jz=name=>abs(0xca,name),jnz=name=>abs(0xc2,name),jc=name=>abs(0xda,name),jnc=name=>abs(0xd2,name);
 const imm=n=>emit(0x3e,n),load=adr=>{emit(0x3a);ww(adr)},store=adr=>{emit(0x32);ww(adr)},outp=(port,val)=>{imm(val);emit(0xd3,port)};
 const reg=(n,v)=>{outp(0xbf,v);outp(0xbf,0x80|n)},vaddr=(a,mode)=>{outp(0xbf,a&255);outp(0xbf,(a>>8&63)|mode<<6)};
 const copy=(name,location,mode,length)=>{vaddr(location,mode);abs(0x21,name);emit(0x01);ww(length);label('COPY_'+name);emit(0x7e,0xd3,0xbe,0x23,0x0b,0x78,0xb1);jnz('COPY_'+name)};
 at(0);abs(0xc3,'BOOT');
 at(0x38);emit(0xf5);load(S.irq);emit(0x3c);store(S.irq);emit(0xf1,0xed,0x4d);
 at(0x100);label('BOOT');
 emit(0xf3,0x31,0xf0,0xdf);  // DI, stack DFF0
 imm(8);store(S.x);imm(6);store(S.y);imm(1);store(S.ink);
 emit(0xaf);for(const addr of [S.selectLatch,S.moveTimer,S.tick,S.score,S.irq,S.win,S.startLatch,S.steps,S.playerPaint])store(addr);
 call('CLEAR');
 // Three initial Z80-written pulses ensure diffusion is visible on boot.
 // The player's own Z injection is still required before any point scores.
 imm(1);store(FIELD+38);   // Red at x=2,y=2
 imm(2);store(FIELD+51);   // Green at x=15,y=2
 imm(4);store(FIELD+206);  // Blue at x=8,y=11
 reg(0,4);reg(1,0x60);reg(2,14);reg(5,126);reg(6,0);reg(7,0);reg(8,0);reg(9,0);
 copy('PALETTE',0,3,64);
 copy('TILES',0,1,0x400);
 copy('NAMETABLE',0x3800,1,1536);
 vaddr(0x3f01,1);outp(0xbe,0xd0);
 call('DRAW_SPRITE');call('DRAW_FIELD');
 imm(0xa5);store(S.boot);
 label('MAIN');emit(0xfb,0x76);call('TICK');jp('MAIN');
 label('TICK');
 emit(0xdb,0xdc);store(S.keys);
 // Button 2 / X (bit 5 active-low) cycles 1:R -> 2:G -> 4:B -> 1:R.
 load(S.keys);emit(0xcb,0x6f);jnz('COLOR_RELEASE');
 load(S.selectLatch);emit(0xb7);jnz('COLOR_DONE');
 load(S.ink);emit(0xfe,1);jnz('COLOR_2');imm(2);jp('COLOR_SAVE');
 label('COLOR_2');emit(0xfe,2);jnz('COLOR_4');imm(4);jp('COLOR_SAVE');
 label('COLOR_4');imm(1);
 label('COLOR_SAVE');store(S.ink);imm(1);store(S.selectLatch);jp('COLOR_DONE');
 label('COLOR_RELEASE');emit(0xaf);store(S.selectLatch);
 label('COLOR_DONE');
 // START is an active-low bit7 on GG port 00, edge-gated: clear board.
 emit(0xdb,0x00,0xcb,0x7f);jnz('START_RELEASE');
 load(S.startLatch);emit(0xb7);jnz('AFTER_START');
 imm(1);store(S.startLatch);call('CLEAR');emit(0xaf);store(S.win);store(S.playerPaint);call('DRAW_FIELD');jp('AFTER_START');
 label('START_RELEASE');emit(0xaf);store(S.startLatch);
 label('AFTER_START');
 // Button1 / Z (bit4) adds selected channel to the field at cursor.
 load(S.keys);emit(0xcb,0x67);jnz('NO_EMIT');call('INJECT');
 label('NO_EMIT');
 // Movement is throttled; no page-side position updates.
 load(S.moveTimer);emit(0x3c);store(S.moveTimer);emit(0xfe,6);jc('MOVE_DONE');
 emit(0xaf);store(S.moveTimer);
 load(S.keys);emit(0xcb,0x47);jnz('TRY_DOWN');
 load(S.y);emit(0xfe,1);jz('MOVE_DONE');emit(0x3d);store(S.y);jp('MOVE_SPRITE');
 label('TRY_DOWN');load(S.keys);emit(0xcb,0x4f);jnz('TRY_LEFT');
 load(S.y);emit(0xfe,12);jz('MOVE_DONE');emit(0x3c);store(S.y);jp('MOVE_SPRITE');
 label('TRY_LEFT');load(S.keys);emit(0xcb,0x57);jnz('TRY_RIGHT');
 load(S.x);emit(0xfe,1);jz('MOVE_DONE');emit(0x3d);store(S.x);jp('MOVE_SPRITE');
 label('TRY_RIGHT');load(S.keys);emit(0xcb,0x5f);jnz('MOVE_DONE');
 load(S.x);emit(0xfe,16);jz('MOVE_DONE');emit(0x3c);store(S.x);
 label('MOVE_SPRITE');call('DRAW_SPRITE');
 label('MOVE_DONE');
 load(S.tick);emit(0x3c);store(S.tick);emit(0xfe,6);jc('TICK_END');
 emit(0xaf);store(S.tick);
 call('SPREAD');call('DRAW_FIELD');call('CHECK_REACTOR');
 load(S.steps);emit(0x3c);store(S.steps);
 label('TICK_END');emit(0xc9);
 label('CLEAR');
 // Clear both zero-bordered 18x14 RGB bitmask buffers.
 emit(0x21);ww(FIELD);emit(0x11);ww(FIELD+1);emit(0xaf,0x77,0x01);ww(511);emit(0xed,0xb0,0xc9);
 label('INJECT');
 imm(1);store(S.playerPaint);
 // offset = y * 18 + x; x=[1,16], y=[1,12], padded field stride 18.
 load(S.y);emit(0x5f,0x16,0,0x6f,0x26,0);
 emit(0x29,0x29,0x29,0x29,0x19,0x19); // 16*y + y + y
 load(S.x);emit(0x5f,0x16,0,0x19);
 emit(0x11);ww(FIELD);emit(0x19);
 emit(0x7e,0x47);load(S.ink);emit(0xb0,0x77,0xc9);
 label('SPREAD');
 // Core Z80 spatial algorithm. In each interior cell, compute:
 // next(x,y) = cur(x,y) | cur(x-1,y) | cur(x+1,y) | cur(x,y-1) | cur(x,y+1)
 // Padded borders remain zero; 3 bits represent 2^3 RGB occupancies.
 emit(0x21);ww(FIELD+19);emit(0x11);ww(NEXT+19);emit(0x06,12);
 label('SPREAD_ROW');emit(0x0e,16);
 label('SPREAD_COL');
 emit(0xc5,0xe5,0xd5);   // PUSH BC, HL, DE
 emit(0x7e,0x2b,0xb6,0x23,0x23,0xb6); // center | left | right
 emit(0x01);ww(0x10000-19);emit(0x09,0xb6); // north
 emit(0x01);ww(36);emit(0x09,0xb6); // south
 emit(0xd1,0x12,0x13,0xe1,0x23,0xc1,0x0d); // POP DE, store, INC DE, POP HL INC HL, POP BC DEC C
 jnz('SPREAD_COL');
 emit(0x23,0x23,0x13,0x13,0x05);jnz('SPREAD_ROW'); // skip 2 border cells, DEC B
 // Copy 252 bytes into current; edges remain zero
 emit(0x21);ww(NEXT);emit(0x11);ww(FIELD);emit(0x01);ww(COUNT);emit(0xed,0xb0,0xc9);
 label('DRAW_FIELD');
 // VDP tile map row starting at 3990; each of 12 rows 16 tiles (cell RGB code).
 imm(0x90);store(S.drawlo);imm(0x39);store(S.drawhi);
 emit(0x21);ww(FIELD+19);emit(0x06,12);
 label('DRAW_ROW');
 emit(0xc5);load(S.drawlo);emit(0xd3,0xbf);load(S.drawhi);emit(0xf6,0x40,0xd3,0xbf);
 emit(0x0e,16);
 label('DRAW_COL');emit(0x7e,0xd3,0xbe,0xaf,0xd3,0xbe,0x23,0x0d);jnz('DRAW_COL');
 emit(0x23,0x23);
 load(S.drawlo);emit(0xc6,0x40);store(S.drawlo);
 load(S.drawhi);emit(0xce,0);store(S.drawhi);
 emit(0xc1,0x05);jnz('DRAW_ROW');emit(0xc9);
 label('DRAW_SPRITE');
 vaddr(0x3f00,1);load(S.y);emit(0xc6,5,0x07,0x07,0x07,0x3d,0xd3,0xbe);
 vaddr(0x3f80,1);load(S.x);emit(0xc6,7,0x07,0x07,0x07,0xd3,0xbe);
 outp(0xbe,8);emit(0xc9);
 label('CHECK_REACTOR');
 // Reactor tile 8,6 / field offset 116. Reaching WHITE (7) scores one mix.
 load(S.playerPaint);emit(0xb7);jz('REACTOR_DONE');
 load(S.win);emit(0xb7);jnz('REACTOR_DONE');
 load(FIELD+116);emit(0xfe,7);jnz('REACTOR_DONE');
 imm(1);store(S.win);load(S.score);emit(0x3c);store(S.score);
 label('REACTOR_DONE');emit(0xc9);
 // Data. Tile 0..7 = colored wave tiles; 8 = silver cursor sprite;
 // 9.. font glyphs for Game Gear title and short control legend.
 const palette=new Uint8Array(64);
 const setColor=(n,r,g,b)=>{palette[n*2]=r|(g<<4);palette[n*2+1]=b};
 setColor(0,0,0,1);
 for(let i=1;i<8;i++)setColor(i,(i&1)?15:0,(i&2)?15:0,(i&4)?15:0);
 setColor(8,1,2,3);setColor(9,3,4,5);setColor(10,7,8,9);
 setColor(15,10,14,15);
 setColor(16,0,0,0);setColor(17,0,0,0);setColor(18,15,15,15);setColor(19,9,15,15);
 labels.set('PALETTE',0x1000);out.set(palette,0x1000);
 const font={
 'A':['01110','10001','10001','11111','10001','10001','10001'],
 'B':['11110','10001','11110','10001','10001','10001','11110'],
 'C':['01111','10000','10000','10000','10000','10000','01111'],
 'D':['11110','10001','10001','10001','10001','10001','11110'],
 'E':['11111','10000','11110','10000','10000','10000','11111'],
 'F':['11111','10000','11110','10000','10000','10000','10000'],
 'G':['01111','10000','10000','10111','10001','10001','01111'],
 'I':['11111','00100','00100','00100','00100','00100','11111'],
 'L':['10000','10000','10000','10000','10000','10000','11111'],
 'M':['10001','11011','10101','10101','10001','10001','10001'],
 'N':['10001','11001','10101','10101','10011','10001','10001'],
 'O':['01110','10001','10001','10001','10001','10001','01110'],
 'P':['11110','10001','10001','11110','10000','10000','10000'],
 'R':['11110','10001','10001','11110','10100','10010','10001'],
 'S':['01111','10000','01110','00001','00001','10001','11110'],
 'T':['11111','00100','00100','00100','00100','00100','00100'],
 'U':['10001','10001','10001','10001','10001','10001','01110'],
 'V':['10001','10001','10001','10001','10001','01010','00100'],
 'W':['10001','10001','10001','10101','10101','10101','01010'],
 'X':['10001','01010','00100','00100','00100','01010','10001'],
 'Z':['11111','00001','00010','00100','01000','10000','11111'],
 '+':['00000','00100','00100','11111','00100','00100','00000'],
 '-':['00000','00000','00000','11111','00000','00000','00000']
 };
 const glyph=Object.keys(font),charMap={};
 const tiles=new Uint8Array(0x400);
 const pix=(tile,row,mask,color)=>{const a=tile*32+row*4;for(let b=0;b<4;b++)tiles[a+b]|=(color&(1<<b))?mask:0;};
 for(let k=0;k<8;k++)for(let y=0;y<8;y++){// subtle edge inset (32x sprite palette remains separate)
  pix(k,y,(y===0||y===7)?0xff:0x7e,k);
 }
 const diamond=[0x18,0x3c,0x7e,0xff,0xff,0x7e,0x3c,0x18];
 for(let y=0;y<8;y++)pix(8,y,diamond[y],2); // sprite uses +16 palette
 for(let k=0;k<glyph.length;k++){const ch=glyph[k],tile=9+k;charMap[ch]=tile;for(let y=0;y<7;y++)pix(tile,y,parseInt(font[ch][y],2)<<2,15);}
 if((9+glyph.length)*32>tiles.length)throw Error('tiles overflow');
 labels.set('TILES',0x1100);out.set(tiles,0x1100);
 const names=new Uint8Array(1536);
 const stamp=(x,y,tile)=>{names[(y*32+x)*2]=tile;};
 function text(x,y,line){for(const ch of line){if(ch!==' ')stamp(x,y,charMap[ch]??(()=>{throw Error('unknown glyph '+ch)})());x++;}}
 text(9,4,'RGB DIFFUSION');
 text(8,19,'Z PAINT X COLOR');
 text(10,20,'START RESET');
 // fixed tile 7 white reactor at world x8,y6 (VDP x15,y11), initially white marker
 // overwritten by dynamic field when gameplay begins. Goal remains in UI.
 labels.set('NAMETABLE',0x1800);out.set(names,0x1800);
 for(const {pos,name} of fixups){const a=labels.get(name);if(a===undefined)throw Error('unresolved '+name);out[pos]=a&255;out[pos+1]=a>>8;}
 const info={name:'RGB DIFFUSION ARENA',bytes:out.length,model:'classical 3-channel 4-neighbor binary OR propagation',source:'hand assembled Z80',board:[W,H],stride:18,channels:{red:1,green:2,blue:4},ram:S,field:FIELD,buffer:NEXT,font:charMap,target:{x:8,y:6,offset:116},sourceWords:['I','Name','Constant','Attribute','Assign','Arg','Return','Expr','If','Compare','Call','FunctionDef','BinOp'],programBytes:pc};
 Object.defineProperty(out,'rgbGame',{value:info});return out;
}
root.GGRGBDiffusion={create};
})(typeof window!=='undefined'?window:globalThis);