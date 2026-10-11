import {spawnSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=dirname(fileURLToPath(import.meta.url));
const suite=[['cross-user witness','test_p445.mjs',13],['socket lifecycle','test_p446.mjs',8]];
const results=[];
for(const [name,file,expected] of suite){
 const cmd=spawnSync(process.execPath,[join(dir,file)],{encoding:'utf8',timeout:30000});
 let data;try{data=JSON.parse(cmd.stdout.trim().slice(cmd.stdout.indexOf('{')))}catch{}
 const pass=cmd.status===0&&data?.status==='PASS'&&data?.assertions===expected;
 results.push({name,assertions:data?.assertions??0,expected,status:pass?'PASS':'FAIL',elapsedMs:data?.elapsedMs??null,stderr:pass?undefined:cmd.stderr?.slice(0,1000)});
}
const ok=results.every(x=>x.status==='PASS');
const report={gate:'P4.67',status:ok?'PASS':'FAIL',assertions:results.reduce((sum,x)=>sum+x.assertions,0),expected:21,hostedCiVerified:false,independentHostVerified:false,roadmapPercent:75,results};
console.log(JSON.stringify(report,null,2));if(!ok)process.exitCode=1;