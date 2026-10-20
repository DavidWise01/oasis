/* GG-ZERO / I-13 HELLO WORLD / RGB DIFFUSION DOT
 * From-scratch generated Game Gear cartridge: real Z80 draws text/dots to VDP.
 * Three RGB signs {-1,+1} give 2^3 = 8 software states.
 * LEFT = IN (-1), RIGHT = OUT (+1), Z = hold/freeze.
 * No quantum hardware claim; this is a classical 3-bit RGB diffusion illustration.
 */
(function(root){'use strict';
function create(){
 const bytes=new Uint8Array(16384),labels=new Map(),fixups=[];let pc=0;
 const M=Object.freeze({phase:0xc120,direction:0xc121,divider:0xc122,steps:0xc123,input:0xc124,boot:0xc125,irq:0xc126,freeze:0xc127});
 const emit=(...xx)=>{for(const x of xx){if(pc>=0x1000)throw Error('program too big');bytes[pc++]=x&255;}};
 const word=x=>emit(x&255,x>>8),here=x=>{pc=x},label=n=>{if(labels.has(n))throw Error('duplicate '+n);labels.set(n,pc)};
 const target=(op,n)=>{emit(op);fixups.push([pc,n]);word(0)};
 const jump=n=>target(0xc3,n),call=n=>target(0xcd,n),jz=n=>target(0xca,n),jnz=n=>target(0xc2,n),jc=n=>target(0xda,n);
 const LD=x=>emit(0x3e,x),load=x=>{emit(0x3a);word(x)},store=x=>{emit(0x32);word(x)};
 const out=(port,value)=>{LD(value);emit(0xd3,port)};
 const reg=(id,value)=>{out(0xbf,value);out(0xbf,0x80|id)};
 const addr=(value,code)=>{out(0xbf,value&255);out(0xbf,(value>>8&63)|code<<6)};
 function copy(id,dest,mode,n){addr(dest,mode);target(0x21,id);emit(0x01);word(n);
  label('COPY_'+id);emit(0x7e,0xd3,0xbe,0x23,0x0b,0x78,0xb1);jnz('COPY_'+id);
 }
 here(0);target(0xc3,'BOOT');
 here(0x38);emit(0xf5);load(M.irq);emit(0x3c);store(M.irq);emit(0xf1,0xed,0x4d);
 here(0x100);label('BOOT');
 emit(0xf3,0x31,0xf0,0xdf); // DI ; SP=DFF0
 LD(0);store(M.phase);store(M.divider);store(M.steps);store(M.irq);store(M.freeze);
 LD(1);store(M.direction);
 reg(0,4);reg(1,0x60);reg(2,14);reg(5,126);reg(6,0);reg(7,0);reg(8,0);reg(9,0);
 copy('PALETTE',0,3,64);
 copy('TILES',0,1,0x780);
 copy('NAMETABLE',0x3800,1,1536);
 addr(0x3f00,1);out(0xbe,0xd0); // stop sprite evaluation
 call('PAINT');
 LD(0xa5);store(M.boot);
 label('LOOP');emit(0xfb,0x76);call('TICK');jump('LOOP');
 label('TICK');
 emit(0xdb,0xdc);store(M.input);
 load(M.input);emit(0xcb,0x57);jnz('TRY_OUT');LD(255);store(M.direction);jump('TICK_FRAME');
 label('TRY_OUT');load(M.input);emit(0xcb,0x5f);jnz('TICK_FRAME');LD(1);store(M.direction);
 label('TICK_FRAME');
 load(M.divider);emit(0x3c);store(M.divider);emit(0xfe,12);jc('DONE');
 emit(0xaf);store(M.divider);
 // Z / button1 holds the current dot without modifying state.
 load(M.input);emit(0xcb,0x67);jz('PAUSED');
 LD(0);store(M.freeze);
 load(M.direction);emit(0xfe,255);jz('INWARD');
 load(M.phase);emit(0x3c,0xe6,7);store(M.phase);jump('EMIT');
 label('INWARD');load(M.phase);emit(0x3d,0xe6,7);store(M.phase);
 label('EMIT');load(M.steps);emit(0x3c);store(M.steps);call('PAINT');jump('DONE');
 label('PAUSED');LD(1);store(M.freeze);
 label('DONE');emit(0xc9);
 // Dynamic CRAM #9 draws the central dot from a Z80 phase LUT.
 label('PAINT');
 load(M.phase);emit(0x87,0x6f,0x26,0);target(0x11,'COLORS');emit(0x19);
 addr(18,3);emit(0x7e,0xd3,0xbe,0x23,0x7e,0xd3,0xbe,0xc9);
 // Palette: 0 background, 1..8 RGB dot states, 9 animated dot,
 // 10 fixed Hello World glyph color, 15 diamond edge/border.
 const palette=new Uint8Array(64),colors=new Uint8Array(16);
 function setColor(i,r,g,b){palette[i*2]=r|(g<<4);palette[i*2+1]=b}
 setColor(0,0,0,1);
 for(let phase=0;phase<8;phase++){
  const red=phase&1?15:0,green=phase&2?15:0,blue=phase&4?15:0;
  setColor(phase+1,red,green,blue);
  colors[phase*2]=red|(green<<4);colors[phase*2+1]=blue;
 }
 setColor(9,0,0,0);setColor(10,11,14,15);setColor(15,14,15,15);
 labels.set('PALETTE',0x1000);bytes.set(palette,0x1000);
 labels.set('COLORS',0x1080);bytes.set(colors,0x1080);
 // 0 blank + 8 indexed swatches + 1 center 'dot' + uppercase font.
 const font={
  A:['01110','10001','10001','11111','10001','10001','10001'],
  B:['11110','10001','11110','10001','10001','10001','11110'],
  D:['11110','10001','10001','10001','10001','10001','11110'],
  E:['11111','10000','11110','10000','10000','10000','11111'],
  G:['01111','10000','10000','10111','10001','10001','01111'],
  H:['10001','10001','10001','11111','10001','10001','10001'],
  I:['11111','00100','00100','00100','00100','00100','11111'],
  L:['10000','10000','10000','10000','10000','10000','11111'],
  N:['10001','11001','10101','10101','10011','10001','10001'],
  O:['01110','10001','10001','10001','10001','10001','01110'],
  R:['11110','10001','10001','11110','10100','10010','10001'],
  T:['11111','00100','00100','00100','00100','00100','00100'],
  U:['10001','10001','10001','10001','10001','10001','01110'],
  W:['10001','10001','10001','10101','10101','10101','01010'],
  '-':['00000','00000','00000','11111','00000','00000','00000'],
  '+':['00000','00100','00100','11111','00100','00100','00000']
 };
 const glyphChars=Object.keys(font),mapping={},tileCount=10+glyphChars.length;
 const tiles=new Uint8Array(0x780);if(tileCount*32>tiles.length)throw Error('too many font glyphs');
 function putTile(index,y,mask,color){
  const base=index*32+y*4;for(let bit=0;bit<4;bit++)tiles[base+bit]=(color>>bit&1)?mask:0;
 }
 // Diamond swatches with color center and white edging (CRAM #15).
 const outer=[0x18,0x3c,0x7e,0xff,0xff,0x7e,0x3c,0x18],
       inner=[0,0x18,0x3c,0x7e,0x7e,0x3c,0x18,0];
 for(let index=1;index<=9;index++)for(let y=0;y<8;y++){
  const o=outer[y],inmask=inner[y],edge=o&~inmask,shade=index===9?9:index;
  const base=index*32+y*4;for(let bit=0;bit<4;bit++)tiles[base+bit]=((15>>bit&1)?edge:0)|((shade>>bit&1)?inmask:0);
 }
 for(let j=0;j<glyphChars.length;j++){
  const ch=glyphChars[j],tile=10+j;mapping[ch]=tile;
  for(let y=0;y<7;y++){const mask=parseInt(font[ch][y],2)<<2;putTile(tile,y,mask,10);}
 }
 labels.set('TILES',0x1100);bytes.set(tiles,0x1100);
 const table=new Uint8Array(1536),atTile=(x,y,tile)=>{const pos=(y*32+x)*2;table[pos]=tile;table[pos+1]=0};
 function writeText(x,y,text){for(const ch of text){atTile(x++,y,ch===' '?0:mapping[ch]);if(ch!==' '&&mapping[ch]===undefined)throw Error('missing font '+ch);}}
 // 160 px wide cropped hardware window: x = 6..25, y=3..20.
 writeText(10,8,'HELLO WORLD');
 atTile(15,11,9);
 for(let i=0;i<8;i++)atTile(12+i,14,1+i);
 writeText(11,17,'IN - OUT +');
 writeText(12,19,'RGB -+');
 labels.set('NAMETABLE',0x2000);bytes.set(table,0x2000);
 for(const [pos,key]of fixups){const address=labels.get(key);if(address==null)throw Error('unresolved '+key);bytes[pos]=address&255;bytes[pos+1]=address>>8;}
 const schema={name:'I13 HELLO WORLD RGB DOT',quantumDotAnalogy:'.=2^3',lanes:['red -+','green -+','blue -+'],directions:{in:-1,out:+1},code:'3-bit classical RGB/8 states',colors:Array.from(colors),ram:M,characters:{...mapping},table:{helloStart:[10,8],dot:[15,11],swatches:[12,14]},sourceWords:['I','Name','Constant','Attribute','Assign','Arg','Return','Expr','If','Compare','Call','FunctionDef','BinOp']};
 Object.defineProperty(bytes,'hello',{value:schema});return bytes;
}
root.GGHelloWorld={create};
})(typeof window!=='undefined'?window:globalThis);