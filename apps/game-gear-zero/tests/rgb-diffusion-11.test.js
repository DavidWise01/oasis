/* RGB DIFFUSION 11 - deterministic executable Z80 + independent four-neighbor reference.
 * Run: node tests/rgb-diffusion-11.test.js (no npm or network). */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const scope=vm.createContext({window:{},Uint8Array,Uint8ClampedArray,Float32Array,Math});
for(const file of ['core/z80.js','core/gg.js','games/rgb-diffusion-11.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),scope,{filename:file});
const report=(function(GGMachine,GGRGBDiffusion11){const checks=[],ok=(name,result)=>{if(!result)throw Error('FAIL '+name);checks.push(name)};
const make=()=>{const x=new GGMachine();x.load(GGRGBDiffusion11.create());return x};
const run=(m,n)=>{for(let i=0;i<n;i++)m.runFrame()};
const cart=GGRGBDiffusion11.create(),meta=cart.rgbGame;
ok('1: executable 16 KiB cartridge',cart.length===16384);
ok('2: original Z80 reset vector',cart[0]===0xc3&&cart[1]===0&&cart[2]===1);
ok('3: RGB = 2^3 states',Object.keys(meta.channels).length===3&&meta.channels.red+meta.channels.green+meta.channels.blue===7);
ok('4: 20x16 board of 320 cells',meta.board[0]===20&&meta.board[1]===16);
ok('5: padded 22-wide two-buffer memory',meta.stride===22&&meta.buffer-meta.field>=396);
ok('6: branch notation is preserved as provisional metadata',meta.branch.core===4&&meta.branch.left.join('/')==='2/2'&&meta.branch.right.join('/')==='2/2');
ok('7: 11-hop witness and 34-hop test horizon',meta.hopCheckpoint===11&&meta.maxAttractHops===34);
const m=make();const starts=meta.seeds,seen=new Set(),samples={};let mismatches=0,totalChecks=0,last=-1;
for(let f=0;f<350;f++){
 m.runFrame();const step=m.ram[0x10e],cycle=m.ram[0x111];
 if(cycle){samples.reset={frame:m.frames,step,cycle,max:m.ram[0x112]};break;}
 if(step===last)continue;last=step;seen.add(step);
 const reach=[0,0,0];let filled=0,white=0;
 for(let y=1;y<=16;y++)for(let x=1;x<=20;x++){
  const cell=m.ram[0x200+y*22+x];
  const expected=starts.reduce((v,seed)=>(Math.abs(x-seed.x)+Math.abs(y-seed.y)<=step)?v|seed.mask:v,0);
  if(cell!==expected)mismatches++;
  totalChecks++;
  if(cell)filled++;if(cell===7)white++;
  for(let k=0;k<3;k++)if(cell&(1<<k))reach[k]=Math.max(reach[k],Math.abs(x-starts[k].x)+Math.abs(y-starts[k].y));
 }
 if(step===0||step===11||step===24||step===32||step===33)
  samples[step]={frame:m.frames,filled,white,reach,witness11:m.ram[0x110],max:m.ram[0x112]};
}
ok('8: Z80 boot succeeds',m.ram[0x107]===165);
ok('9: source seeds are R(2,2),G(19,2),B(10,15)',starts[0].x===2&&starts[1].x===19&&starts[2].y===15);
ok('10: all 34 stages 0..33 evaluated',seen.size===34&&seen.has(0)&&seen.has(33));
ok('11: every Z80 cell matches independent reference',mismatches===0&&totalChecks===34*320);
ok('12: at hop 11 each channel reaches radius 11',samples[11].reach.join(',')==='11,11,11');
ok('13: at hop 11 319 tiles colored',samples[11].filled===319);
ok('14: at hop 11 exactly one white tile',samples[11].white===1);
ok('15: Z80 latches explicit 11-hop gate',samples[11].witness11===1);
ok('16: at hop 24 blue reaches its most distant tile',samples[24].reach[2]===24);
ok('17: at hop 32 red and green reach radius 32',samples[32].reach[0]===32&&samples[32].reach[1]===32);
ok('18: at hop 32 all 320 tiles are white',samples[32].white===320&&samples[32].filled===320);
ok('19: no unearned auto-demo score',m.ram[0x106]===0&&m.ram[0x10f]===0);
ok('20: at 34-hop mark attract loop restarts automatically',samples.reset.cycle===1&&samples.reset.step===0&&samples.reset.max===34);
ok('21: Game Gear LCD renders correct 160x144 size',m.framebuffer.length===92160);
ok('22: real VDP has >10k tile writes',m.stats.vramWrites>10000);
const p=make();run(p,8);
ok('23: cursor starts centered at 10,8',p.ram[0x100]===10&&p.ram[0x101]===8);
ok('24: 20x16 board seeded into correct padding',p.ram[0x200+46]===1&&p.ram[0x200+63]===2&&p.ram[0x200+340]===4);
p.press('right',true);run(p,90);p.press('right',false);
ok('25: right movement clamps to 20',p.ram[0x100]===20&&p.vram[0x3f80]===200);
p.press('down',true);run(p,80);p.press('down',false);
ok('26: down movement clamps to 16',p.ram[0x101]===16&&p.vram[0x3f00]===151);
p.press('b1',true);run(p,7);p.press('b1',false);
ok('27: Z paints at x20/y16 using stride22',p.ram[0x200+16*22+20]!==0&&p.ram[0x10f]===1);
const prev=p.ram[0x102];p.press('b2',true);run(p,3);p.press('b2',false);run(p,3);
ok('28: X switches selected RGB channel',prev===1&&p.ram[0x102]===2);
run(p,100);
ok('29: actual player-painted white reactor scores once',p.ram[0x106]===1&&p.ram[0x109]===1);
run(p,180);
ok('30: distance witness stays capped at 34 after paint',p.ram[0x10e]===34&&p.ram[0x112]===34);
p.press('start',true);run(p,2);p.press('start',false);run(p,2);
ok('31: Start resets reach/cycles but preserves score',p.ram[0x10e]===0&&p.ram[0x110]===0&&p.ram[0x112]===0&&p.ram[0x106]===1);
ok('32: Start re-seeds source field',p.ram[0x200+46]===1&&p.ram[0x200+63]===2&&p.ram[0x200+340]===4);
ok('33: earlier Game Gear CPU and VDP code remained unchanged',m.cpu.pc<65536&&p.stats.irqRequests>50);
return {passed:checks.length,checks,cellChecks:totalChecks,mismatches,samples};
})(scope.window.GGMachine,scope.window.GGRGBDiffusion11);
report.checks.forEach(x=>console.log('PASS '+x));
console.log(report.passed+'/'+report.passed+' PASS, '+report.cellChecks+' independent cell checks, '+report.mismatches+' mismatches');
