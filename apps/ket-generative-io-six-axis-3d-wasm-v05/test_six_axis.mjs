import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const binary=fs.readFileSync(new URL('./vector_toroid.wasm',import.meta.url));
const ex=(await WebAssembly.instantiate(binary,{})).instance.exports;
const places=[[0,0,0],[-1,0,0],[1,0,0],[0,-1,0],[0,1,0],[0,0,-1],[0,0,1]];
let checked=0;
function ck(name,fn){fn();checked++;console.log('PASS',name);}
const vector=t=>[0,1,2].map(k=>ex.get_vector(t,k));
ck('valid wasm',()=>assert.equal(WebAssembly.validate(binary),true));
ck('no imports',()=>assert.equal(WebAssembly.Module.imports(new WebAssembly.Module(binary)).length,0));
ck('real wasm magic',()=>assert.equal(binary.toString('hex',0,4),'0061736d'));
ck('toroid two-cell-volume',()=>assert.equal(ex.configure(1.9,.65,3,4.2,99,355,0,42,90),2160));
ck('366 slots per body',()=>assert.equal(20*18+3+3,366));
ck('default position -X',()=>assert.deepEqual(vector(0),[-1,0,0]));
ck('default position +X',()=>assert.deepEqual(vector(1),[1,0,0]));
ck('all 49 pairs of legal directions',()=>{
  for(let a=0;a<7;a++)for(let b=0;b<7;b++){
    assert.equal(ex.set_directions(a,b),1);
    assert.deepEqual(vector(0),places[a]);
    assert.deepEqual(vector(1),places[b]);
    assert.equal(ex.get_direction(0),a);
    assert.equal(ex.get_direction(1),b);
  }
});
ck('negative code invalid',()=>assert.equal(ex.set_directions(-1,0),0));
ck('positive code 7 invalid',()=>assert.equal(ex.set_directions(0,7),0));
ck('X+Y diagonal disallowed',()=>assert.equal(ex.set_vectors(1,1,0,0,0,0),0));
ck('three-axis diagonal disallowed',()=>assert.equal(ex.set_vectors(-1,-1,-1,0,0,0),0));
ck('mixed-sign diagonal disallowed',()=>assert.equal(ex.set_vectors(0,0,0,1,0,-1),0));
ck('out-of-range vector disallowed',()=>assert.equal(ex.set_vectors(2,0,0,0,0,0),0));
ck('simultaneous shared origin',()=>{assert.equal(ex.set_directions(0,0),1);assert.equal(ex.center_distance_squared(),0);});
ck('coincident toroids do not merge',()=>assert.equal(ex.cell_count(),2160));
ck('gate OFF cannot transmit',()=>{
  ex.configure(1.9,.65,3,4.2,0,180,0,42,0);
  ex.set_directions(0,0);ex.stimulate(0,0);ex.advance();
  assert.equal(ex.get_tx(0)+ex.get_tx(1),0);
});
ck('directional A to B gate',()=>{
  ex.configure(1.9,.65,3,4.2,0,359,1,42,0);
  ex.set_directions(1,6);ex.stimulate(0,0);ex.advance();
  assert.equal(ex.get_tx(0),1);assert.equal(ex.get_tx(1),0);
});
ck('directional B to A gate',()=>{
  ex.configure(1.9,.65,3,4.2,359,99,2,42,0);
  ex.set_directions(6,3);ex.stimulate(1,99);ex.advance();
  assert.equal(ex.get_tx(1),1);assert.equal(ex.get_tx(0),0);
});
ck('forward linear tick increments',()=>assert.equal(ex.get_tick(),1));
function run(){
  ex.configure(1.9,.65,3,4.2,99,355,0,42,50);
  ex.set_directions(5,4);
  for(let i=0;i<360;i++)ex.advance();
  return {tick:ex.get_tick(),phaseA:ex.get_phase(0),phaseB:ex.get_phase(1),speedA:ex.get_speed(0),speedB:ex.get_speed(1),msg:ex.get_tx(0)+ex.get_tx(1),hash:ex.get_checksum()>>>0};
}
const first=run();
ck('360 tick chronological cycle',()=>assert.equal(first.tick,360));
ck('360 degree phase both toroids',()=>{assert.equal(first.phaseA,360);assert.equal(first.phaseB,360);});
ck('initial angular speed recovered',()=>{assert.equal(first.speedA,1);assert.equal(first.speedB,1);});
ck('zero messages with gate OFF across circuit',()=>assert.equal(first.msg,0));
ck('deterministic replay',()=>assert.deepEqual(first,run()));
ck('embedded WASM hash',()=>assert.ok(fs.readFileSync(new URL('./index.html',import.meta.url),'utf8').includes(crypto.createHash('sha256').update(binary).digest('hex'))));
ck('seven-code browser selectors',()=>{
  const html=fs.readFileSync(new URL('./index.template.html',import.meta.url),'utf8');
  assert.ok(html.includes('id="dirA"')&&html.includes('id="dirB"'));
  assert.ok(!html.includes('id="ax"'));
});
console.log(JSON.stringify({checks:checked,expectedDirections:places.length,orderedPlacementPairs:49,result:first},null,2));
