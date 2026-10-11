import {spawnSync} from 'node:child_process';
import {writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {resolve} from 'node:path';
const root=process.env.P466_ROOT ?? '/mnt/data';
const suites=[
 ['P4.65 deployment preflight',resolve(root,'p465/test_p465.mjs'),19],
 ['P4.64 signed HTTPS high-water',resolve(root,'p464/test_p464.mjs'),15],
 ['P4.46 socket recovery',resolve(root,'p446/test_p446.mjs'),8],
];
const detail=[];let assertions=0;
for(const [name,path,expected] of suites){
 const start=performance.now();
 const run=spawnSync(process.execPath,[path],{encoding:'utf8',timeout:15000,maxBuffer:1024*1024});
 let parsed=null;
 try{const raw=run.stdout.trim();parsed=JSON.parse(raw.slice(raw.indexOf('{')))}catch{}
 const passed=run.status===0&&parsed?.status==='PASS'&&parsed?.assertions===expected&&parsed?.independentHostVerified!==true&&parsed?.independentHost!==true;
 detail.push({name,expected,actual:parsed?.assertions??null,passed,elapsedMs:+(performance.now()-start).toFixed(3),exitCode:run.status,error:run.error?.message??null});
 if(passed)assertions+=expected;
}
const out={gate:'P4.66',status:detail.every(x=>x.passed)?'PASS':'FAIL',assertionsPassed:assertions,assertionsExpected:42,prototypeMilestonesCompleted:15,prototypeMilestonesTotal:20,prototypeCompletionPercent:75,independentHostVerified:false,hostedCiVerified:false,suites:detail};
if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
if(out.status!=='PASS')process.exitCode=1;