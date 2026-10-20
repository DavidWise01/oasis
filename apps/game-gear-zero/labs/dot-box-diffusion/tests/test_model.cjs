'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script id="dot-box-model">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'Model source script exists');
const window={};vm.runInNewContext(script,{window,Uint8Array,Map,Math,Number,Error,String,Array});
const D=window.DotBox;let passed=0;function test(name,fn){fn();console.log('PASS',name);passed++;}
for(let generation=0;generation<=6;generation++){
 const t=D.makeTree(generation),states=D.timeline(t,16),leaves=4**generation,nodes=(4**(generation+1)-1)/3;
 test('G'+generation+' recursive count',()=>{assert.equal(t.nodes.length,nodes);assert.equal(t.leaves.length,leaves);assert.equal(t.byPath.size,nodes);});
 test('G'+generation+' parent child/sibling rails',()=>{for(const n of t.nodes){if(n.children.length)assert.equal(n.children.length,4);for(const j of n.neighbors)assert.ok(t.nodes[j].neighbors.includes(n.id));if(n.children.length){for(let i=0;i<3;i++)assert.ok(t.nodes[n.children[i]].neighbors.includes(n.children[i+1]));}}});
 test('G'+generation+' RGB masks from three seeds',()=>{assert.ok(states[0].every(x=>x>=0&&x<=7));assert.equal(t.seeds.length,3);assert.equal(D.summaries(t,states[0])[0],7);});
 test('G'+generation+' bitwise monotonic diffusion',()=>{for(let hop=1;hop<states.length;hop++){for(let i=0;i<nodes;i++){assert.equal(states[hop][i]&states[hop-1][i],states[hop-1][i]);}}});
 test('G'+generation+' eventual white saturation',()=>{const s=D.stats(t,states.at(-1));assert.equal(s.white,leaves);assert.equal(s.occupied,leaves);});
 test('G'+generation+' ASCII bounded pagination',()=>{let a=D.ascii(t,states[2],states[1],'letters',999,64);assert.ok(a.pages>=1);assert.ok(a.page>=0&&a.page<a.pages);assert.ok(a.rows.length<=64);if(generation)assert.ok(a.rows.every(r=>r.masks.length===4));});
}
test('G0 one dot, G1 four dot box',()=>{const g0=D.makeTree(0),g1=D.makeTree(1);assert.equal(g0.leaves.length,1);const row=D.ascii(g1,g1.initial,null,'letters').rows[0];assert.equal(row.masks.length,4);assert.equal(row.masks.join(','),'1,2,0,4');});
test('all 8 RGB ASCII representations',()=>{assert.equal(D.SYMBOLS.join(''),'.RGYBMCW');assert.equal(D.glyph(7,'density'),'#');assert.equal(D.glyph(5,'bits'),'101');assert.equal(D.glyph(1,'wave',0),'+');});
test('nested box collapse and focus',()=>{let t=D.makeTree(3),states=D.timeline(t)[1];let f=D.focus(t,'',states),child=D.focus(t,'0',states);assert.equal(f.children.length,4);assert.equal(f.collapsed,7);assert.equal(child.node.path,'0');});
test('invalid depth and focus validation',()=>{assert.throws(()=>D.makeTree(7));assert.throws(()=>D.makeTree(-1));assert.throws(()=>D.focus(D.makeTree(2),'999',D.makeTree(2).initial));});
console.log(passed+'/'+passed+' PASS');