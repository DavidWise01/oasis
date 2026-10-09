import assert from 'node:assert/strict';
// Finite carrier from frozen I13 schema, two *synthetic* physical tick policies.
const P=['in','out','vacant','occupied'], A=['3x3','abc','-abc'];
function* states(){for(let n=0;n<1024;n++){let k=n,slots=[];for(let j=0;j<5;j++){slots.push(k%4);k=Math.floor(k/4)}for(let x=0;x<3;x++)for(let y=0;y<3;y++)for(let z=0;z<3;z++)for(const witnessed of [false,true])yield{slots,axes:[x,y,z],witnessed,ledger:['root','tick0']}}}
const observe=s=>({...s,slots:[...s.slots],axes:[...s.axes],witnessed:true,ledger:[...s.ledger,'observed:'+Number(s.witnessed)+'->1']});
const blindTick=s=>({...s,slots:s.slots.map(v=>(v+1)%4),axes:s.axes.map(v=>(v+1)%3),ledger:[...s.ledger]});
const leakyTick=s=>({...s,slots:s.witnessed?s.slots.map((v,i)=>i===0?(v+1)%4:v):[...s.slots],axes:[...s.axes],ledger:[...s.ledger]});
const proj=s=>JSON.stringify([s.slots,s.axes]);
function test(tick){
let checked=0,readOnly=0,commuting=0,physicalCommuting=0,example=null;
for(const s of states()){
const w=observe(s),left=tick(w),right=observe(tick(s)),same=JSON.stringify(left)===JSON.stringify(right);
checked++;if(proj(s)===proj(w))readOnly++;if(same)commuting++;if(proj(left)===proj(right))physicalCommuting++;
if(!same&&!example)example={start:{slots:s.slots.map(i=>P[i]),axes:s.axes.map(i=>A[i]),witnessed:s.witnessed},T_after_W:{slots:left.slots.map(i=>P[i]),ledger:left.ledger},W_after_T:{slots:right.slots.map(i=>P[i]),ledger:right.ledger}};
}
return{checked,readOnly,commuting,physicalCommuting,failures:checked-commuting,example};
}
const blind=test(blindTick),leaky=test(leakyTick);
assert.equal(blind.checked,55296);assert.equal(blind.readOnly,55296);
assert.equal(blind.commuting,55296);assert.equal(blind.physicalCommuting,55296);
assert.equal(leaky.checked,55296);assert.equal(leaky.readOnly,55296);
assert.equal(leaky.failures,27648);assert.equal(leaky.physicalCommuting,27648);
console.log(JSON.stringify({schema:'I13-P1.2-witness-commutation',blind,leaky},null,2));
