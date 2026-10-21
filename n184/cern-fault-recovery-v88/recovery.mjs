// N184 v8.8: synthetic single-field fault detection and recovery on real CMS events.
// CERN education records give redundant track coordinates, NOT four independent detectors.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseCMSCSV} from '../cern-observer-lab-v84/observer_core.mjs';
import {fnv1a32,isHeldOut,DATA_DOI,DATA_URL} from '../cern-heldout-v87/benchmark.mjs';

export const CASES=Object.freeze(['clean','missing_pz1','biased_pz1_plus5']);
export const SOURCE_SHA256='373f0f56120998d4dad626abb1229ceef91523c262e154fb1e1e541bbb8be3a5';
export function caseFor(r){
 return CASES[fnv1a32('fault:'+r.Run+':'+r.Event)%CASES.length];
}
export function mass4(r){
 const keys=['E1','E2','px1','px2','py1','py2','pz1','pz2'];
 if(keys.some(k=>!Number.isFinite(r[k])))return NaN;
 const E=r.E1+r.E2,px=r.px1+r.px2,py=r.py1+r.py2,pz=r.pz1+r.pz2;
 const m2=E*E-px*px-py*py-pz*pz;
 return Number.isFinite(m2)&&m2>=0?Math.sqrt(m2):NaN;
}
export function injectFault(r,kind){
 if(!CASES.includes(kind))throw Error('Unknown fault '+kind);
 const dirty={...r};
 if(kind==='missing_pz1')dirty.pz1=null;
 if(kind==='biased_pz1_plus5')dirty.pz1+=5;
 return dirty;
}
export function estimatePz(r){
 if(!Number.isFinite(r.pt1)||r.pt1<0||!Number.isFinite(r.eta1))return NaN;
 return r.pt1*Math.sinh(r.eta1);
}
export function witness(r){
 const expected=estimatePz(r);
 const hasReported=Number.isFinite(r.pz1);
 const threshold=Number.isFinite(expected)?0.05+0.005*Math.abs(expected):NaN;
 const residual=hasReported&&Number.isFinite(expected)?Math.abs(r.pz1-expected):NaN;
 const alarm=!hasReported||(Number.isFinite(residual)&&residual>threshold);
 const canRepair=alarm&&Number.isFinite(expected);
 const repaired={...r};
 if(canRepair)repaired.pz1=expected;
 return {alarm,missing:!hasReported,canRepair,expectedPz:expected,threshold,residual,
  modified:canRepair,repaired};
}
export function naiveMass(r){
 // Deliberately inadequate operational baseline: zero fill for missing pz1.
 return mass4({...r,pz1:r.pz1===null?0:r.pz1});
}
function summary(a){
 const v=a.map(Math.abs).sort((x,y)=>x-y),n=v.length;
 if(!n)return {valid:0,maeGeV:null,rmseGeV:null,medianAbsGeV:null,p95AbsGeV:null};
 const at=Math.floor(n/2);
 return {valid:n,maeGeV:v.reduce((x,y)=>x+y,0)/n,
  rmseGeV:Math.sqrt(v.reduce((x,y)=>x+y*y,0)/n),
  medianAbsGeV:n%2?v[at]:(v[at]+v[at-1])/2,
  p95AbsGeV:v[Math.max(0,Math.ceil(.95*n)-1)]};
}
function createCounter(){
 return {n:0,alarm:0,trueAlarm:0,falseAlarm:0,missedFault:0,
  naiveInvalid:0,repairedInvalid:0,
  naiveErrorsToClean:[],repairedErrorsToClean:[],
  naiveErrorsToStoredM:[],repairedErrorsToStoredM:[],
  pairedDeltaAbsToClean:[],recoveryBetter:0,recoveryWorse:0,recoveryTied:0,
  recoveryWithin01GeV:0,comparisonPairs:0};
}
export function evaluate(records,{maxRows=100000}={}){
 if(!Array.isArray(records))throw TypeError('Expected record array');
 if(!Number.isInteger(maxRows)||maxRows<1||maxRows>100000)throw RangeError('maxRows must be 1..100000');
 const cases=Object.fromEntries(CASES.map(k=>[k,createCounter()]));
 const overall=createCounter();
 let reserved=0,held=0,cleanMassInvalid=0;
 const examples=[],missedFaultExamples=[],invalidRepairedExamples=[],falseAlarmExamples=[];
 function mark(bucket,entry){
  bucket.n++;
  if(entry.obs.alarm){
   bucket.alarm++;
   if(entry.kind==='clean')bucket.falseAlarm++;else bucket.trueAlarm++;
  }else if(entry.kind!=='clean')bucket.missedFault++;
  if(!Number.isFinite(entry.baseline))bucket.naiveInvalid++;
  if(!Number.isFinite(entry.repairedMass))bucket.repairedInvalid++;
  if(Number.isFinite(entry.cleanMass)){
   if(Number.isFinite(entry.baseline))bucket.naiveErrorsToClean.push(entry.baseline-entry.cleanMass);
   if(Number.isFinite(entry.repairedMass))bucket.repairedErrorsToClean.push(entry.repairedMass-entry.cleanMass);
   if(Number.isFinite(entry.baseline)&&Number.isFinite(entry.repairedMass)){
    const d=Math.abs(entry.baseline-entry.cleanMass)-Math.abs(entry.repairedMass-entry.cleanMass);
    bucket.pairedDeltaAbsToClean.push(d);bucket.comparisonPairs++;
    if(d>1e-9)bucket.recoveryBetter++;
    else if(d< -1e-9)bucket.recoveryWorse++;
    else bucket.recoveryTied++;
   }
   if(Number.isFinite(entry.repairedMass)&&Math.abs(entry.repairedMass-entry.cleanMass)<0.01)
    bucket.recoveryWithin01GeV++;
  }
  if(Number.isFinite(entry.baseline))bucket.naiveErrorsToStoredM.push(entry.baseline-entry.row.M);
  if(Number.isFinite(entry.repairedMass))bucket.repairedErrorsToStoredM.push(entry.repairedMass-entry.row.M);
 }
 for(const row of records.slice(0,maxRows)){
  if(!isHeldOut(row)){reserved++;continue}
  held++;
  const kind=caseFor(row),cleanMass=mass4(row),fault=injectFault(row,kind),obs=witness(fault);
  const baseline=naiveMass(fault),repairedMass=mass4(obs.repaired);
  if(!Number.isFinite(cleanMass))cleanMassInvalid++;
  const e={kind,row,obs,baseline,repairedMass,cleanMass};
  mark(cases[kind],e);mark(overall,e);
  const diagnostic={run:row.Run,event:row.Event,case:kind,originalPz1GeV:row.pz1,
   faultedPz1GeV:fault.pz1,expectedPz1GeV:obs.expectedPz,
   residualPz1GeV:obs.residual,alarmThresholdGeV:obs.threshold,
   detectionAlarm:obs.alarm,repairApplied:obs.modified,
   cleanMassGeV:cleanMass,recoveredMassGeV:repairedMass,naiveMassGeV:baseline};
  if(kind!=='clean'&&!obs.alarm&&missedFaultExamples.length<12)missedFaultExamples.push(diagnostic);
  if(kind==='clean'&&obs.alarm&&falseAlarmExamples.length<12)falseAlarmExamples.push(diagnostic);
  if(!Number.isFinite(repairedMass)&&invalidRepairedExamples.length<12)invalidRepairedExamples.push(diagnostic);
  if(examples.length<18)examples.push({run:row.Run,event:row.Event,case:kind,
   originalPz1GeV:row.pz1,faultedPz1GeV:fault.pz1,estimatedPz1GeV:obs.expectedPz,
   detected:obs.alarm,recovered:obs.modified,storedMassGeV:row.M,
   cleanMassGeV:cleanMass,naiveMassGeV:baseline,repairedMassGeV:repairedMass});
 }
 const finalize=b=>({n:b.n,alarms:b.alarm,trueAlarms:b.trueAlarm,falseAlarms:b.falseAlarm,
  missedFaults:b.missedFault,naiveValid:b.n-b.naiveInvalid,repairedValid:b.n-b.repairedInvalid,
  naiveCoverage:b.n?(b.n-b.naiveInvalid)/b.n:null,
  recoveredCoverage:b.n?(b.n-b.repairedInvalid)/b.n:null,
  recoveryWithin0p01GeV:b.recoveryWithin01GeV,
  onPairedComparison:{count:b.comparisonPairs,better:b.recoveryBetter,worse:b.recoveryWorse,tied:b.recoveryTied},
  naiveVsClean:summary(b.naiveErrorsToClean),recoveredVsClean:summary(b.repairedErrorsToClean),
  naiveVsRecordedMass:summary(b.naiveErrorsToStoredM),recoveredVsRecordedMass:summary(b.repairedErrorsToStoredM)});
 return {schema:'oasis/n184/cern-fault-recovery-result/v88',
  processed:Math.min(records.length,maxRows),heldout:held,reserved,cleanMassInvalid,
  faultPolicy:{split:'existing v8.7 FNV-1a holdout',injection:'FNV-1a("fault:"+Run+":"+Event)%3',
   scenarios:CASES,driftGeV:5,threshold:'0.05+0.005*abs(pt1*sinh(eta1)) GeV'},
  overall:finalize(overall),
  scenarios:Object.fromEntries(CASES.map(k=>[k,finalize(cases[k])])),
  examples,missedFaultExamples,falseAlarmExamples,invalidRepairedExamples,
  caution:'Internal track-coordinate redundancy under injected single-field faults. Neither actual detector failure nor independent ALICE/ATLAS/CMS/LHCb measurements.'};
}
export function runCSV(text,opts={}){
 const parsed=parseCMSCSV(text,{maxRows:opts.maxRows??100000});
 return {input:{accepted:parsed.records.length,skipped:parsed.skipped,
  truncated:parsed.truncated,errors:parsed.errors},analysis:evaluate(parsed.records,opts)};
}
async function main(){
 const [src,dest,max]=process.argv.slice(2);
 if(!src||src==='--help'){console.log('node recovery.mjs <CMS-CSV> [report.json] [maxRows]');return}
 const text=fs.readFileSync(src,'utf8');
 const hash=crypto.createHash('sha256').update(text).digest('hex');
 const report={provenance:{sourceURL:DATA_URL,doi:DATA_DOI,sourceSha256:hash,
  byteCount:Buffer.byteLength(text),matchesRegisteredSource:hash===SOURCE_SHA256},
  ...runCSV(text,{maxRows:max?Number(max):100000})};
 if(report.analysis.heldout===0)throw Error('No holdout events');
 if(!report.provenance.matchesRegisteredSource)throw Error('Dataset hash differs from recorded 100k-event CERN v8.7 baseline');
 const json=JSON.stringify(report,(key,value)=>typeof value==='number'&&!Number.isFinite(value)?null:value,2)+'\n';
 if(dest)fs.writeFileSync(dest,json);
 console.log(json);
}
if(process.argv[1]&&fileURLToPath(import.meta.url)===process.argv[1])
 main().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
