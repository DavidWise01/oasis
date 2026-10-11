import {spawnSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=dirname(fileURLToPath(import.meta.url));
const suites=[['KET','test_ket.mjs',13],['KernelZero','test_kernel0.mjs',11]];
let total=0;const evidence=[];
for(const [name,file,expected] of suites){
 const r=spawnSync(process.execPath,[join(dir,file)],{encoding:'utf8',timeout:20000});
 let data;try{data=JSON.parse(r.stdout.trim())}catch{}
 const ok=r.status===0&&data?.status==='PASS'&&data?.assertions===expected;
 evidence.push({name,status:ok?'PASS':'FAIL',expected,actual:data?.assertions??null,elapsedMs:data?.elapsedMs??null,reason:ok?undefined:(r.stderr||r.error?.message||'invalid result').slice(0,300)});
 if(ok)total+=expected;
}
const pass=total===24;
const report={release:'KET-R0',status:pass?'PASS':'FAIL',assertions:total,expected:24,hostedCiVerified:false,independentHostVerified:false,productionReady:false,suites:evidence};
console.log(JSON.stringify(report,null,2));if(!pass)process.exitCode=1;