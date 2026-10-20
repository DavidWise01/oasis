/* GG-ZERO x I13 TECH-001: executable Z80 cross-product proof
 * Run: node tests/i13-kernel.test.js (no network / no dependencies).
 * The test checks ONLY the bounded signed-trit I13 adapter, not the full H1.1 VM. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const window={};
const sandbox=vm.createContext({window,Uint8Array,Uint8ClampedArray,Float32Array,Math});
for(const filename of ['core/z80.js','core/gg.js','games/i13-kernel.js']){
 vm.runInContext(fs.readFileSync(path.join(__dirname,'..',filename),'utf8'),sandbox,{filename});
}
const report=(function(GGMachine,GGI13){
let count=0;const tested=[];
function check(name,ok){count++;if(!ok)throw new Error('FAIL '+name);tested.push(name);}
const input=(e,d)=>{const m=new GGMachine();m.load(GGI13.create());for(let n=0;n<4;n++)m.runFrame();m.write(0xc100,e&255);m.write(0xc101,d);m.runFrame();return m};
const cart=GGI13.create(),M=cart.i13.ram;
check('16 KiB Game Gear executable cartridge',cart.length===16384);
check('13 canonical surface words, I + 12 semantic words',JSON.stringify(cart.i13.words)===JSON.stringify(['I','Name','Constant','Attribute','Assign','Arg','Return','Expr','If','Compare','Call','FunctionDef','BinOp']));
check('15 VM names are metadata, not a false full interpreter',cart.i13.opcodes.length===15);
check('CPU boot success marker A5',input(0,0).read(M.boot)===0xa5);
for(const e of [-1,0,1])for(const debt of [0,1,3]){
 const expected=e===-1?-1:debt>0?0:e===1?1:0;
 const m=input(e,debt),v=m.read(M.verdict);const want=expected&255;
 check('TECH rule evidence='+e+',debt='+debt+' => '+expected,v===want&&m.read(M.guard)===1);
}
for(const e of [2,42,254]){
 const m=input(e,0);
 check('invalid evidence veto '+e,m.read(M.verdict)===255&&m.read(M.guard)===255);
}
const p=input(1,0);
check('Z80 wrote green palette',p.cram[2]===0xf3&&p.cram[3]===4);
const red=input(255,0);
check('Z80 wrote red palette',red.cram[2]===0x0f&&red.cram[3]===2);
const neutral=input(0,0);
check('Z80 wrote amber palette',neutral.cram[2]===0xcf&&neutral.cram[3]===3);
check('Z80 render pipeline is 160x144xRGBA',p.framebuffer.length===160*144*4&&p.stats.cramWrites>64);
check('IRQ handler operates with real Z80 steps',p.read(M.irq)>=4&&p.stats.irqRequests>=4);
check('guard recovers from invalid value when revalidated -1',(()=>{const m=input(42,0);m.press('left',true);for(let j=0;j<3;j++)m.runFrame();return m.read(M.guard)===1&&m.read(M.verdict)===255})());
check('right switch enters p1 PROCEED',(()=>{const m=input(0,0);m.press('right',true);for(let j=0;j<4;j++)m.runFrame();return m.read(M.evidence)===1&&m.read(M.verdict)===1})());
check('question debt by actual Z80 input cancels p1',(()=>{const m=input(1,0);m.press('b1',true);for(let j=0;j<8;j++)m.runFrame();return m.read(M.debt)===3&&m.read(M.verdict)===0})());
check('B2 clears question debt and restores p1',(()=>{const m=input(1,2);m.press('b2',true);for(let j=0;j<3;j++)m.runFrame();return m.read(M.debt)===0&&m.read(M.verdict)===1})());
return {passed:count,names:tested};

})(window.GGMachine,window.GGI13);
report.names.forEach(n=>console.log('PASS '+n));
console.log(report.passed+'/'+report.passed+' passed');
