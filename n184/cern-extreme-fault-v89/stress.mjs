// OASIS v8.9 – prospective-shard synthetic fault robustness on CERN CMS records.
// A mathematical redundancy of ONE reconstructed track is not an independent detector.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseCMSCSV} from '../cern-observer-lab-v84/observer_core.mjs';
import {fnv1a32,DATA_URL,DATA_DOI} from '../cern-heldout-v87/benchmark.mjs';
import {mass4,estimatePz,SOURCE_SHA256} from '../cern-fault-recovery-v88/recovery.mjs';
export const CASES=Object.freeze(['clean','isolated_pz','correlated_pz_eta','coherent_pz_eta_E']);
export const METHODS=Object.freeze(['legacy','capped','guarded']);
export const MUON_MASS_GEV=0.1056583755;
export function shard(r){return fnv1a32(String(r.Run)+':'+String(r.Event))%5}
export function injectionKind(r){return CASES[fnv1a32('v89-fault:'+r.Run+':'+r.Event)%4]}
export function inject(r,kind){
 if(!CASES.includes(kind))throw Error('Unknown fault case: '+kind);
 const x={...r};
 if(kind==='clean')return x;
 x.pz1=r.pz1+5;
 if(kind==='correlated_pz_eta'||kind==='coherent_pz_eta_E'){
  if(!(r.pt1>0))throw Error('Cannot inject coherent eta fault with pt1<=0');
  x.eta1=Math.asinh(x.pz1/r.pt1);
 }
 if(kind==='coherent_pz_eta_E')
  x.E1=Math.hypot(x.px1,x.py1,x.pz1,MUON_MASS_GEV);
 return x;
}
export function energyWitness(r){
 const implied=Math.hypot(r.px1,r.py1,r.pz1,MUON_MASS_GEV);
 const diff=Number.isFinite(r.E1)&&Number.isFinite(implied)?Math.abs(r.E1-implied):Infinity;
 const bound=0.5+0.001*Math.abs(r.E1);
 return {impliedGeV:implied,absoluteDifferenceGeV:diff,toleranceGeV:bound,
  alarm:!Number.isFinite(diff)||diff>bound};
}
export function applyPolicy(r,method){
 if(!METHODS.includes(method))throw Error('Unknown policy '+method);
 const expect=estimatePz(r),missing=!Number.isFinite(r.pz1),
  difference=missing||!Number.isFinite(expect)?Infinity:Math.abs(r.pz1-expect);
 const legacyLimit=0.05+0.005*Math.abs(expect);
 const limit=method==='legacy'?legacyLimit:Math.min(legacyLimit,2);
 const angleAlarm=missing||difference>limit;
 const shell=energyWitness(r);
 const invalidMass=!Number.isFinite(mass4(r));
 const alert=angleAlarm||(method==='guarded'&&(shell.alarm||invalidMass));
 let output={...r},quarantined=false,repaired=false,reason='pass';
 if(angleAlarm){
  if(!Number.isFinite(expect)){quarantined=true;reason='no-redundant-estimate'}
  else{
   output.pz1=expect;repaired=true;reason='angle-repair';
   if(method==='guarded'&&(energyWitness(output).alarm||!Number.isFinite(mass4(output)))){
    quarantined=true;reason='candidate-failed-guard';
   }
  }
 }else if(method==='guarded'&&(shell.alarm||invalidMass)){
  quarantined=true;reason='unattributed-energy-or-mass-conflict';
 }
 const m=quarantined?NaN:mass4(output);
 return {alert,angleAlarm,energyAlarm:shell.alarm,invalidInputMass:invalidMass,
  repaired:repaired&&!quarantined,quarantined,reason,mass:m,estimatedPzGeV:expect,
  absolutePzDifferenceGeV:difference,toleranceGeV:limit,
  energyResidualGeV:shell.absoluteDifferenceGeV,energyToleranceGeV:shell.toleranceGeV};
}
function collector(){
 return {n:0,flags:0,tp:0,fp:0,fn:0,tn:0,quarantine:0,valid:0,invalid:0,repair:0,
  errorsClean:[],errorsCMS:[],detectionMissExamples:[],falseAlarmExamples:[],unrepairedExamples:[],
  detectedButInvalid:0};
}
function accumulate(c,clean,kind,fault,result){
 c.n++;
 const isFault=kind!=='clean';
 if(result.alert){c.flags++;if(isFault)c.tp++;else c.fp++}
 else if(isFault)c.fn++;else c.tn++;
 if(result.quarantined)c.quarantine++;
 if(result.repaired)c.repair++;
 if(Number.isFinite(result.mass)){
  c.valid++;
  if(Number.isFinite(clean.mass))c.errorsClean.push(result.mass-clean.mass);
  c.errorsCMS.push(result.mass-clean.raw.M);
 }else {c.invalid++;if(result.alert)c.detectedButInvalid++}
 const info={run:clean.raw.Run,event:clean.raw.Event,case:kind,
  cleanPz1:clean.raw.pz1,corruptPz1:fault.pz1,cleanEta1:clean.raw.eta1,corruptEta1:fault.eta1,
  alert:result.alert,quarantined:result.quarantined,reason:result.reason,
  estimatePzGeV:result.estimatedPzGeV,differenceGeV:result.absolutePzDifferenceGeV,
  thresholdGeV:result.toleranceGeV,energyDifferenceGeV:result.energyResidualGeV,
  energyThresholdGeV:result.energyToleranceGeV,
  cleanMassGeV:clean.mass,outputMassGeV:result.mass};
 if(isFault&&!result.alert&&c.detectionMissExamples.length<8)c.detectionMissExamples.push(info);
 if(!isFault&&result.alert&&c.falseAlarmExamples.length<8)c.falseAlarmExamples.push(info);
 if(isFault&&!Number.isFinite(result.mass)&&c.unrepairedExamples.length<8)c.unrepairedExamples.push(info);
}
function stats(values){
 const n=values.length;if(!n)return {n:0,maeGeV:null,rmseGeV:null,medianAbsGeV:null,p95AbsGeV:null};
 const a=values.map(Math.abs).sort((x,y)=>x-y),mid=Math.floor(n/2);
 return {n,maeGeV:a.reduce((x,y)=>x+y,0)/n,
  rmseGeV:Math.sqrt(a.reduce((x,y)=>x+y*y,0)/n),
  medianAbsGeV:n%2?a[mid]:(a[mid-1]+a[mid])/2,
  p95AbsGeV:a[Math.max(0,Math.ceil(n*.95)-1)]};
}
function finish(c){
 return {count:c.n,alarm:c.flags,detectedFault:c.tp,missedFault:c.fn,falseAlarm:c.fp,
  trueNegative:c.tn,quarantined:c.quarantine,repairs:c.repair,
  valid:c.valid,invalid:c.invalid,outputCoverage:c.n?c.valid/c.n:null,
  precision:c.tp+c.fp?c.tp/(c.tp+c.fp):null,
  recall:c.tp+c.fn?c.tp/(c.tp+c.fn):null,
  cleanFalseAlarmRate:c.fp+c.tn?c.fp/(c.fp+c.tn):null,
  detectedButInvalid:c.detectedButInvalid,
  versusClean:stats(c.errorsClean),versusCMS:stats(c.errorsCMS),
  missedExamples:c.detectionMissExamples,falseAlarmExamples:c.falseAlarmExamples,
  invalidFaultExamples:c.unrepairedExamples};
}
export function evaluate(records,{maxRows=100000}={}){
 if(!Array.isArray(records))throw TypeError('records must be an array');
 if(!Number.isInteger(maxRows)||maxRows<1||maxRows>100000)throw RangeError('maxRows must be integer 1..100000');
 const shards={retrospective:0,prospective:1},output={};
 for(const label of Object.keys(shards)){
  const bucket=shards[label];
  const buckets=Object.fromEntries(METHODS.map(m=>[m,Object.fromEntries(['all',...CASES].map(k=>[k,collector()]))]));
  let count=0;
  for(const raw of records.slice(0,maxRows)){
   if(shard(raw)!==bucket)continue;
   count++;
   const kind=injectionKind(raw),fault=inject(raw,kind),
   clean={raw,mass:mass4(raw)};
   for(const method of METHODS){
    const result=applyPolicy(fault,method);
    accumulate(buckets[method].all,clean,kind,fault,result);
    accumulate(buckets[method][kind],clean,kind,fault,result);
   }
  }
  output[label]={hashBucket:bucket,events:count,
   methods:Object.fromEntries(METHODS.map(m=>[m,Object.fromEntries(
    ['all',...CASES].map(k=>[k,finish(buckets[m][k])]))]))};
 }
 return {schema:'oasis/n184/cern-extreme-fault-result/v89',rowsProcessed:Math.min(records.length,maxRows),
  prospectiveSeparatedFromEarlierV88:true,shards:output,
  note:'Artificial corruption of authentic CMS input. Retrospective and prospective are disjoint hash buckets of the SAME source file; not independent detector data or datasets.'};
}
export function runCSV(text,opts={}){
 const parsed=parseCMSCSV(text,{maxRows:opts.maxRows??100000});
 return {ingest:{accepted:parsed.records.length,skipped:parsed.skipped,truncated:parsed.truncated,errors:parsed.errors},
  experiment:evaluate(parsed.records,opts)};
}
async function main(){
 const [src,dst,max]=process.argv.slice(2);
 if(!src||src==='--help'){console.log('node stress.mjs <official-source-CSV> [report.json] [maxRows]');return}
 const bytes=fs.readFileSync(src),sha=crypto.createHash('sha256').update(bytes).digest('hex');
 if(sha!==SOURCE_SHA256)throw Error('CSV SHA256 differs from predeclared CERN v8.7/v8.8 input');
 const report={source:{url:DATA_URL,doi:DATA_DOI,sha256:sha,bytes:bytes.byteLength,matchedV87:true},
  ...runCSV(bytes.toString('utf8'),{maxRows:max?Number(max):100000})};
 const json=JSON.stringify(report,(_,v)=>typeof v==='number'&&!Number.isFinite(v)?null:v,2)+'\n';
 if(dst)fs.writeFileSync(dst,json);
 console.log(json);
}
if(process.argv[1]&&fileURLToPath(import.meta.url)===process.argv[1])
 main().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
