/* I13 x GG-ZERO · executable Z80 TECH-001 trit-kernel cartridge.
   Reference: DavidWise01/I13-H1.1 examples/e1_tech_trit.i13.
   This is a strict signed-trit subset, NOT the full I13 f64/15-opcode VM.
   All evaluation, input validation, witnesses and LCD palette are Z80-executed. */
(function(root){'use strict';
function create(){
 const rom=new Uint8Array(0x4000),marks=new Map(),fixups=[];let pc=0;
 const M=Object.freeze({evidence:0xc100,debt:0xc101,verdict:0xc102,guard:0xc103,lastPaint:0xc104,evalCount:0xc105,raw:0xc106,boot:0xc10f,irq:0xc10e});
 const emit=(...bytes)=>{for(const n of bytes){if(pc>=0x1000)throw Error('program exceeds 4 KiB');rom[pc++]=n&255}};
 const here=(address)=>{pc=address},label=name=>{if(marks.has(name))throw Error('duplicate '+name);marks.set(name,pc)};
 const w=x=>emit(x&255,x>>>8),ref=(opcode,name)=>{emit(opcode);fixups.push([pc,name]);w(0)};
 const jp=name=>ref(0xc3,name),call=name=>ref(0xcd,name),jz=name=>ref(0xca,name),jnz=name=>ref(0xc2,name),jnc=name=>ref(0xd2,name);
 const imm=x=>emit(0x3e,x),get=address=>{emit(0x3a);w(address)},put=address=>{emit(0x32);w(address)},out=(port,value)=>{imm(value);emit(0xd3,port)};
 const reg=(i,value)=>{out(0xbf,value);out(0xbf,0x80|i)};
 const addr=(n,mode)=>{out(0xbf,n&255);out(0xbf,((n>>8)&63)|mode<<6)};
 const copy=(name,location,mode,size)=>{addr(location,mode);ref(0x21,name);emit(0x01);w(size);
  label('COPY_'+name);emit(0x7e,0xd3,0xbe,0x23,0x0b,0x78,0xb1);jnz('COPY_'+name);
 };
 // Program reset and VBlank handler.
 here(0);ref(0xc3,'START');
 here(0x38);emit(0xf5);get(M.irq);emit(0x3c);put(M.irq);emit(0xf1,0xed,0x4d);
 here(0x100);label('START');
 emit(0xf3,0x31,0xf0,0xdf); // DI; SP=DFF0
 imm(0);put(M.evidence);put(M.debt);put(M.verdict);put(M.guard);put(M.evalCount);put(M.irq);
 imm(127);put(M.lastPaint); // force first paint
 reg(0,4);reg(1,0x60);reg(2,14);reg(5,126);reg(6,0);reg(7,0);reg(8,0);reg(9,0);
 copy('PALETTE',0,3,64);
 copy('TILES',0,1,64);
 copy('NAMETABLE',0x3800,1,1536);
 addr(0x3f00,1);out(0xbe,0xd0); // disable sprites
 call('EVAL');imm(0xa5);put(M.boot);
 label('LOOP');emit(0xfb,0x76);call('SAMPLE');call('EVAL');jp('LOOP');
 // Live on-cartridge input: Left -> n1; Up -> p0; Right -> p1;
 // Button1 -> question debt++ (bounded <=3); Button2 -> clear; Down -> decrement.
 label('SAMPLE');emit(0xdb,0xdc);put(M.raw);
 get(M.raw);emit(0xcb,0x57);jnz('CHK_UP');imm(255);put(M.evidence);jp('CHK_DEBT');
 label('CHK_UP');get(M.raw);emit(0xcb,0x47);jnz('CHK_RIGHT');imm(0);put(M.evidence);jp('CHK_DEBT');
 label('CHK_RIGHT');get(M.raw);emit(0xcb,0x5f);jnz('CHK_DEBT');imm(1);put(M.evidence);
 label('CHK_DEBT');get(M.raw);emit(0xcb,0x67);jnz('CHK_CLEAR');
 get(M.debt);emit(0xfe,3);jnc('SAMPLE_DONE');emit(0x3c);put(M.debt);jp('SAMPLE_DONE');
 label('CHK_CLEAR');get(M.raw);emit(0xcb,0x6f);jnz('CHK_DEC');
 imm(0);put(M.debt);jp('SAMPLE_DONE');
 label('CHK_DEC');get(M.raw);emit(0xcb,0x4f);jnz('SAMPLE_DONE');
 get(M.debt);emit(0xb7);jz('SAMPLE_DONE');emit(0x3d);put(M.debt);
 label('SAMPLE_DONE');emit(0xc9);
 // I13 TECH-001 exact authority: invalid evidence is HOLD with a veto witness;
 // valid -1 HOLD; question_debt>0 FLAY; valid +1 PROCEED; otherwise FLAY.
 label('EVAL');
 get(M.evidence);emit(0xfe,255);jz('VALID_NEG');
 get(M.evidence);emit(0xfe,0);jz('VALID');
 get(M.evidence);emit(0xfe,1);jz('VALID');
 imm(255);put(M.guard);jp('NEG');
 label('VALID_NEG');imm(1);put(M.guard);jp('NEG');
 label('VALID');imm(1);put(M.guard);
 get(M.debt);emit(0xb7);jnz('ZERO');
 get(M.evidence);emit(0xfe,1);jz('POS');
 jp('ZERO');
 label('NEG');imm(255);put(M.verdict);jp('REC');
 label('ZERO');imm(0);put(M.verdict);jp('REC');
 label('POS');imm(1);put(M.verdict);
 label('REC');get(M.evalCount);emit(0x3c);put(M.evalCount);call('PAINT');emit(0xc9);
 // Color generated solely through actual VDP CRAM writes by the Z80.
 label('PAINT');get(M.verdict);emit(0x47);get(M.lastPaint);emit(0xb8);jz('PAINT_END');
 emit(0x78);put(M.lastPaint);emit(0xfe,255);jz('RED');emit(0xfe,1);jz('GREEN');
 label('AMBER');addr(2,3);out(0xbe,0xcf);out(0xbe,3);jp('PAINT_END');
 label('RED');addr(2,3);out(0xbe,0x0f);out(0xbe,2);jp('PAINT_END');
 label('GREEN');addr(2,3);out(0xbe,0xf3);out(0xbe,4);
 label('PAINT_END');emit(0xc9);
 const data=(name,place,b)=>{if(marks.has(name))throw Error('data collision');marks.set(name,place);rom.set(b,place)};
 const palette=new Uint8Array(64),setColor=(i,r,g,b)=>{palette[i*2]=r|g<<4;palette[i*2+1]=b};
 setColor(0,0,0,1);setColor(1,15,12,3);setColor(2,4,6,8);
 data('PALETTE',0x1000,palette);
 const tiles=new Uint8Array(64);
 // Tile 0 dark noise; tile 1 intense color 1 checker / 4-bitplane.
 for(let y=0;y<8;y++){tiles[y*4]=y&1?0x22:0x88;tiles[y*4+1]=0;tiles[32+y*4]=y&1?0xaa:0x55;tiles[32+y*4+1]=0;}
 data('TILES',0x1080,tiles);
 const names=new Uint8Array(1536);for(let y=0;y<24;y++)for(let x=0;x<32;x++)names[(y*32+x)*2]=(y===0||y===23||x===0||x===31)?0:1;
 data('NAMETABLE',0x1200,names);
 for(const [location,key]of fixups){const address=marks.get(key);if(address===undefined)throw Error('unresolved '+key);rom[location]=address&255;rom[location+1]=address>>8;}
 const words=['I','Name','Constant','Attribute','Assign','Arg','Return','Expr','If','Compare','Call','FunctionDef','BinOp'];
 Object.defineProperty(rom,'i13',{value:{mode:'TECH-001-SIGNED-TRIT-SUBSET',words,opcodes:['Const','Ask','Attr','Ret','Answer','Drop','Bin','Cmp','If','Call','Block','Else','End','Func','Halt'],ram:M,programBytes:pc,reference:'I13-H1.1/examples/e1_tech_trit.i13'}});
 return rom;
}
root.GGI13={create};
})(typeof window!=='undefined'?window:globalThis);