// UEP-213R: independent exact-integer WASM arithmetic qualification. .dlw
const fs = require('node:fs');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const path = process.argv[2];
if (!path) throw Error('WASM binary path required');
const bytes = fs.readFileSync(path);
const MAX = (1n << 64n)-1n;
function oracle(v,p,n){
 const due=v*BigInt(p)*BigInt(999-n)*2050n/(999n*999n*10000n);
 const carbon=due*80n/100n;
 return [due,carbon,due-carbon];
}
async function main(){
 const {instance}=await WebAssembly.instantiate(bytes,{});
 const e=instance.exports;
 assert.equal(e.uep_abi_version(),209);
 let cases=0, comparisons=0;
 for(const v of [0n,1n,99n,100n,10000n,120000000000n,MAX])
 for(const p of [0,1,250,499,500,750,998,999])
 for(const n of [0,1,250,499,500,750,998,999]){
  const expected=oracle(v,p,n);
  const actual=[0,1,2].map(s=>BigInt.asUintN(64,e.uep_estimate(v,p,n,s)));
  assert.deepEqual(actual,expected);
  assert.equal(actual[0],actual[1]+actual[2]);
  assert(actual[0]*10000n<=v*2050n);
  cases++;comparisons+=3;
 }
 for(const [p,n,s] of [[1000,0,0],[0,1000,0],[999,0,3],[-1,0,0],[0,-1,0],[999,0,-1]])
  assert.equal(BigInt.asUintN(64,e.uep_estimate(10000n,p,n,s)),MAX);
 const report={bound:'UEP-213R',abi:209,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,cases,comparisons,invalidRejected:6,actualPayments:0};
 console.log(JSON.stringify(report,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
