/* Repeatable GG-ZERO regression suite. Requires Node.js; no emulator packages. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const w={};const scope=vm.createContext({window:w,Uint8Array,Uint8ClampedArray,Float32Array,Math});
for(const file of ['core/z80.js','core/gg.js','core/selftest.js'])
 vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),scope,{filename:file});
let count=0;function test(name,fn){fn();console.log('PASS',name);count++}
function cpu(program,steps){const ram=new Uint8Array(65536),outs=[];ram.set(program);const z=new w.GGZ80({read:a=>ram[a],write:(a,v)=>ram[a]=v,input:()=>255,output:(p,v)=>outs.push([p,v])});for(let i=0;i<steps;i++)z.step();return {z,ram,outs}}
test('Z80 immediate load and memory store',()=>{const r=cpu([0x3e,0x42,0x32,0x00,0xc0],2);assert.equal(r.ram[0xc000],0x42)});
test('Z80 arithmetic',()=>assert.equal(cpu([0x3e,0x14,0xc6,0x28],2).z.A,0x3c));
test('Z80 relative jump',()=>assert.equal(cpu([0x18,0x02,0x3e,1,0x3e,0x22],2).z.A,0x22));
test('Z80 OUT',()=>assert.equal(cpu([0x3e,0x77,0xd3,0xbe],2).outs[0][1],0x77));
test('Z80 CB bit set',()=>assert.equal(cpu([0x06,0,0xcb,0xc0,0x78],3).z.A,1));
test('Z80 DJNZ',()=>assert.equal(cpu([0x06,3,0x10,0xfe,0x3e,0x51],5).z.A,0x51));
test('Game Gear RAM mirrored',()=>{const m=new w.GGMachine();m.write(0xc000,23);assert.equal(m.read(0xe000),23)});
test('Sega mapper register',()=>{const m=new w.GGMachine();m.write(0xfffe,5);assert.equal(m.banks[1],5)});
test('Game Gear input active low',()=>{const m=new w.GGMachine();m.press('b1',true);assert.equal(m.input(0xdc)&0x10,0)});
test('Game Gear Start input',()=>{const m=new w.GGMachine();m.press('start',true);assert.equal(m.input(0)&128,0)});
test('VDP register',()=>{const m=new w.GGMachine();m.output(0xbf,64);m.output(0xbf,0x81);assert.equal(m.vdpRegs[1],64)});
test('VDP RAM data writes',()=>{const m=new w.GGMachine();m.output(0xbf,0);m.output(0xbf,0x40);m.output(0xbe,170);assert.equal(m.vram[0],170)});
test('12bit color CRAM',()=>{const m=new w.GGMachine();m.cram[2]=0xf0;m.cram[3]=8;assert.deepEqual(Array.from(m.palette(1)),[0,255,136])});
test('Frame exact dimensions',()=>assert.equal(new w.GGMachine().drawFrame().length,92160));
test('PSG sample buffer',()=>assert.equal(new w.GGMachine().audioSamples(30).length,60));
test('Original diagnostic cartridge boots and executes',()=>{const m=new w.GGMachine();m.load(w.GGTestROM.create());m.runFrame();m.runFrame();assert.equal(m.ram[0],0xa5);assert.equal(m.vram[0],0xaa);assert.equal(m.vdpRegs[1],0x40)});
test('Diagnostic draws real two-color LCD pixels',()=>{const m=new w.GGMachine();m.load(w.GGTestROM.create());m.runFrame();m.runFrame();const seen=new Set();for(let i=0;i<m.framebuffer.length;i+=4)seen.add(Array.from(m.framebuffer.subarray(i,i+3)).join(','));assert.ok(seen.has('255,0,0'));assert.ok(seen.has('0,0,255'));});
console.log(count+' / '+count+' PASS');
