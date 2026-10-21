// OASIS CERN v8.7 — blinded-label, training-free mass ablation.
// Source: CERN Open Data DOI 10.7483/OPENDATA.CMS.CB8H.MFFA.
// This is kinematic reconstruction, not an independently trained predictor.
// Large dataset can be supplied as a local CSV path; it is not committed.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseCMSCSV} from '../cern-observer-lab-v84/observer_core.mjs';

export const DATA_URL='https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv';
export const DATA_DOI='10.7483/OPENDATA.CMS.CB8H.MFFA';

export function fnv1a32(value){
 let hash=0x811c9dc5;
 for(const byte of new TextEncoder().encode(String(value))){
  hash=Math.imul(hash^byte,0x01000193)>>>0;
 }
 return hash>>>0;
}
export function isHeldOut(r){
 return fnv1a32(String(r.Run)+':'+String(r.Event))%5===0;
}
export function predictMass(r,mode){
 // Notice that M is absent from every branch below; it is only used by score().
 const pt1=r.pt1,pt2=r.pt2,dPhi=r.phi1-r.phi2,dEta=r.eta1-r.eta2;
 let m2;
 if(mode==='transverse'){
  m2=2*pt1*pt2*(1-Math.cos(dPhi));
 }else if(mode==='angular'||mode==='fourPort'){
  m2=2*pt1*pt2*(Math.cosh(dEta)-Math.cos(dPhi));
 }else if(mode==='fourVector'){
  const E=r.E1+r.E2,x=r.px1+r.px2,y=r.py1+r.py2,z=r.pz1+r.pz2;
  m2=E*E-x*x-y*y-z*z;
 }else throw Error('Unknown benchmark method: '+mode);
 return Number.isFinite(m2)&&m2>=0?Math.sqrt(m2):Number.NaN;
}
function score(samples){
 const abs=samples.map(Math.abs).sort((a,b)=>a-b),n=abs.length;
 if(!n)return {n:0,maeGeV:null,rmseGeV:null,medianAbsGeV:null,p95AbsGeV:null};
 const mid=Math.floor(n/2);
 return {n,maeGeV:abs.reduce((a,b)=>a+b,0)/n,
  rmseGeV:Math.sqrt(abs.reduce((a,b)=>a+b*b,0)/n),
  medianAbsGeV:n%2?abs[mid]:(abs[mid-1]+abs[mid])/2,
  p95AbsGeV:abs[Math.min(n-1,Math.ceil(.95*n)-1)]};
}
export function evaluate(records,{maxRows=100000}={}){
 if(!Array.isArray(records))throw TypeError('Expected parsed record array');
 if(!Number.isInteger(maxRows)||maxRows<1||maxRows>100000)throw RangeError('maxRows must be integer 1..100000');
 const methods=['transverse','angular','fourPort','fourVector'];
 const errs=Object.fromEntries(methods.map(m=>[m,[]]));
 let evalCount=0,reservedCount=0,nonfinite=0,chargeOpposite=0;
 const perEventExamples=[];
 for(const r of records.slice(0,maxRows)){
  if(!isHeldOut(r)){reservedCount++;continue}
  evalCount++;
  if(r.Q1*r.Q2===-1)chargeOpposite++;
  const estimated=Object.fromEntries(methods.map(m=>[m,predictMass(r,m)]));
  for(const m of methods){
   if(Number.isFinite(estimated[m]))errs[m].push(estimated[m]-r.M);
   else nonfinite++;
  }
  if(perEventExamples.length<10){
   perEventExamples.push({run:r.Run,event:r.Event,referenceMGeV:r.M,
    transverseGeV:estimated.transverse,angularGeV:estimated.angular,
    fourVectorGeV:estimated.fourVector});
  }
 }
 const metrics=Object.fromEntries(methods.map(m=>[m,score(errs[m])]));
 return {schema:'oasis/n184/cern-heldout-result/v87',rowsProcessed:Math.min(records.length,maxRows),
  heldOutCount:evalCount,reservedCount,holdoutRule:'fnv1a32(Run+":"+Event)%5===0',
  nonfinitePredictions:nonfinite,oppositeSignHoldoutCount:chargeOpposite,
  metrics,
  comparisons:{
   angularVsTransverseMAEGeV:metrics.transverse.maeGeV!==null&&metrics.angular.maeGeV!==null?metrics.transverse.maeGeV-metrics.angular.maeGeV:null,
   fourPortVsAngularMAEGeV:metrics.fourPort.maeGeV!==null&&metrics.angular.maeGeV!==null?metrics.angular.maeGeV-metrics.fourPort.maeGeV:null,
   fourVectorVsAngularMAEGeV:metrics.angular.maeGeV!==null&&metrics.fourVector.maeGeV!==null?metrics.angular.maeGeV-metrics.fourVector.maeGeV:null
  },sampleOfHoldout:perEventExamples,
  interpretation:'Reference label M is withheld until per-row evaluation, but M originates from the same underlying reconstructed kinematics. Extra four-port fields do not alter angular estimator. This tests formula ablation, not emergence or generalization beyond CMS.'};
}
export function runCsv(text,opts={}){
 const parsed=parseCMSCSV(text,{maxRows:opts.maxRows??100000});
 const analysis=evaluate(parsed.records,opts);
 return {input:{accepted:parsed.records.length,skipped:parsed.skipped,
  truncated:parsed.truncated,header:parsed.header,errors:parsed.errors},analysis};
}
async function main(){
 const args=process.argv.slice(2);
 if(!args.length||args.includes('--help')){
  console.log('Usage: node benchmark.mjs <local-CMS-dimuon-CSV> [result-json-path] [maxRows]');
  process.exit(args.length?0:2);
 }
 const source=args[0],dest=args[1],maxRows=args[2]?Number(args[2]):100000;
 if(!fs.existsSync(source))throw Error('CSV not found: '+source);
 const text=fs.readFileSync(source,'utf8'),bytes=Buffer.byteLength(text);
 const sha256=crypto.createHash('sha256').update(text).digest('hex');
 const report={provenance:{sourceFileName:source.split(/[\\/]/).at(-1),sourceURL:DATA_URL,
  doi:DATA_DOI,sizeBytes:bytes,sha256,repositorySample:false},
  ...runCsv(text,{maxRows})};
 if(!report.analysis.heldOutCount)throw Error('No hash-split holdout rows in input');
 const json=JSON.stringify(report,null,2)+'\n';
 if(dest)fs.writeFileSync(dest,json);
 console.log(json);
}
if(process.argv[1]&&fileURLToPath(import.meta.url)===process.argv[1])main().catch(e=>{console.error(String(e.stack||e));process.exitCode=1});
