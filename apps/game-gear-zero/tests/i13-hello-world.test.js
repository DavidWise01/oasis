/* GG-ZERO x I13 Hello World : executable Z80/VDP RGB dot proof.
 * Run: node tests/i13-hello-world.test.js 
 * Quantum-dot/diffusion is an 8-state classical software metaphor. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const window={};const scope=vm.createContext({window,Uint8Array,Uint8ClampedArray,Float32Array,Math});
for(const file of ['core/z80.js','core/gg.js','games/i13-hello-world.js'])
 vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),scope,{filename:file});
const result=(function(GGMachine,GGHelloWorld){
let n=0;const cases=[];function ok(name,valid){n++;if(!valid)throw Error('FAIL '+name);cases.push(name)}
const rom=GGHelloWorld.create(),info=rom.hello, m=new GGMachine();m.load(rom);
const frames=k=>{for(let i=0;i<k;i++)m.runFrame()};
frames(5);
ok('01 16384-byte cartridge',rom.length===16384);
ok('02 boot success marker from emulated Z80',m.ram[0x125]===165);
ok('03 enabled Game Gear video and IRQ',m.vdpRegs[1]===0x60&&m.ram[0x126]>=2);
ok('04 I+12 metadata exact count',info.sourceWords.length===13);
ok('05 three RGB paired lanes',info.lanes.join('|')==='red -+|green -+|blue -+');
ok('06 signed input/output direction',info.directions.in===-1&&info.directions.out===1);
ok('07 initial dot phase is zero',m.ram[0x120]===0);
ok('08 default OUT+ direction',m.ram[0x121]===1);
ok('09 actual VDP tiles loaded',m.stats.vramWrites>3000);
ok('10 HELLO WORLD name table glyph H',m.vram[0x3800+(8*32+10)*2]===info.characters.H);
ok('11 HELLO WORLD name table glyph D',m.vram[0x3800+(8*32+20)*2]===info.characters.D);
ok('12 central dot is tile 9',m.vram[0x3800+(11*32+15)*2]===9);
ok('13 all eight RGB swatches are VDP tiles',Array.from({length:8},(_,i)=>m.vram[0x3800+(14*32+12+i)*2]===i+1).every(Boolean));
ok('14 rendered LCD has nonbackground lettering',(()=>{let count=0;for(let i=0;i<m.framebuffer.length;i+=4){if(m.framebuffer[i]>80&&m.framebuffer[i+1]>80)count++}return count>100})());
ok('15 Game Gear pixel buffer size',m.framebuffer.length===92160);
ok('16 LUT contains eight distinct RGB channel sets',new Set(Array.from({length:8},(_,i)=>info.colors.slice(i*2,i*2+2).join(','))).size===8);
const observed=[];
for(let v=1;v<=8;v++){frames(12);const phase=m.ram[0x120];observed.push(phase);const cr=info.colors.slice(phase*2,phase*2+2);
 if(m.cram[18]!==cr[0]||m.cram[19]!==cr[1])throw Error('bad CRAM phase '+phase);}
ok('17 eight natural phases 1..7,0',observed.join(',')==='1,2,3,4,5,6,7,0');
ok('18 2^3 cycle logs eight CPU updates',m.ram[0x123]===8);
m.press('left',true);frames(12);
ok('19 IN - reverses to phase 7',m.ram[0x121]===255&&m.ram[0x120]===7);
m.press('left',false);m.press('b1',true);frames(24);
ok('20 holding button1 freezes phase',m.ram[0x120]===7&&m.ram[0x127]===1);
m.press('b1',false);frames(12);
ok('21 releasing freeze resumes IN movement',m.ram[0x120]===6&&m.ram[0x127]===0);
m.press('right',true);frames(12);
ok('22 OUT+ reverses inward trend',m.ram[0x120]===7&&m.ram[0x121]===1);
m.press('right',false);
ok('23 Game Gear I/O bus was read by Z80',m.stats.portReads>=14);
ok('24 emulated VBlank interrupt serviced',m.ram[0x126]>100&&m.stats.irqRequests>100);
ok('25 CRAM writes tracked per diffusion transition',m.stats.cramWrites>80);
return {cases:n,passed:cases,phaseSequence:observed,ram:{phase:m.ram[0x120],direction:m.ram[0x121],steps:m.ram[0x123],irq:m.ram[0x126]},vramWrites:m.stats.vramWrites,cramWrites:m.stats.cramWrites};

})(window.GGMachine,window.GGHelloWorld);
result.passed.forEach(x=>console.log('PASS',x));
console.log(result.cases+'/'+result.cases+' PASSED, phases = '+result.phaseSequence.join(','));
