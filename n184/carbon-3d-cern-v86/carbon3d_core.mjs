import {parseCMSCSV} from '../cern-observer-lab-v84/observer_core.mjs';

export const CARBON_LAYER=Object.freeze({symbol:'C',atomicNumber:6,
 modelLayer:'3D',axes:['px','py','pz'],outerSectors:6,phaseSteps:80,
 microticks:240,fourSoftwarePorts:['ATLAS','ALICE','CMS','LHCb']});

export function massesForEvent(r){
 const E=r.E1+r.E2;
 const p={x:r.px1+r.px2,y:r.py1+r.py2,z:r.pz1+r.pz2};
 const squared2=E*E-p.x*p.x-p.y*p.y;
 const squared3=squared2-p.z*p.z;
 const xy=squared2>=0?Math.sqrt(squared2):Number.NaN;
 const xyz=squared3>=0?Math.sqrt(squared3):Number.NaN;
 return {energy:E,totalMomentum:p,massXY:xy,mass3D:xyz,massRecorded:r.M,
   errorXY:Number.isFinite(xy)?xy-r.M:null,
   error3D:Number.isFinite(xyz)?xyz-r.M:null,
   longitudinalMassSquaredContribution:p.z*p.z,
   massSquared2D:squared2,massSquared3D:squared3};
}
function statistics(arr){
 if(!arr.length)return {count:0,mae:null,rmse:null,maxAbs:null,medianAbs:null};
 const absolute=arr.map(Math.abs).sort((a,b)=>a-b);
 const mid=absolute.length>>1;
 return {count:arr.length,
  mae:absolute.reduce((a,b)=>a+b,0)/absolute.length,
  rmse:Math.sqrt(arr.reduce((a,b)=>a+b*b,0)/arr.length),
  maxAbs:absolute.at(-1),
  medianAbs:absolute.length%2?absolute[mid]:(absolute[mid-1]+absolute[mid])/2};
}
export function analyzeCarbon3D(records,{sampleMax=25000,detailLimit=500}={}){
 if(!Array.isArray(records))throw new TypeError('records must be an array');
 if(!Number.isInteger(sampleMax)||sampleMax<1||sampleMax>100000)throw new RangeError('sampleMax out of range');
 const rows=[],e2=[],e3=[];let invalidXY=0,invalid3D=0,improved=0,tied=0,worse=0;
 let meanMomentumZSum=0;
 for(const r of records.slice(0,sampleMax)){
   const x=massesForEvent(r);
   if(!Number.isFinite(x.massXY))invalidXY++;
   else e2.push(x.errorXY);
   if(!Number.isFinite(x.mass3D))invalid3D++;
   else e3.push(x.error3D);
   if(Number.isFinite(x.massXY)&&Number.isFinite(x.mass3D)){
     const delta=Math.abs(x.errorXY)-Math.abs(x.error3D);
     if(delta>1e-9)improved++;
     else if(delta< -1e-9)worse++;
     else tied++;
   }
   meanMomentumZSum+=x.totalMomentum.z;
   if(rows.length<detailLimit)rows.push({run:r.Run,event:r.Event,chargeProduct:r.Q1*r.Q2,
      ...x});
 }
 const two=statistics(e2),three=statistics(e3);
 return {schema:'oasis/n184/carbon3d-result/v86',inputRecords:Math.min(records.length,sampleMax),
  comparisonLabel:'Mass consistency with existing recorded M (NOT held-out prediction)',
  baseline2D:two,full3D:three,invalidMass2D:invalidXY,invalidMass3D:invalid3D,
  improvedCount:improved,tiedCount:tied,worseCount:worse,
  meanCombinedPzGeV:records.length?meanMomentumZSum/Math.min(records.length,sampleMax):null,
  maeImprovementGeV:two.mae!==null&&three.mae!==null?two.mae-three.mae:null,
  maeRatio2Dover3D:three.mae>0&&two.mae!==null?two.mae/three.mae:null,
  detailCount:rows.length,detailRows:rows,
  methodologicalWarning:'Dropping pz from otherwise unchanged four-vector makes XY-only mass a deliberately incomplete projection. The M reference derives from related four-vectors, so close 3D agreement is expected; this is not an independent discovery or trained-model gain.'};
}
export function runFromCSV(csvText,opts={}){
 const parsed=parseCMSCSV(csvText,{maxRows:opts.sampleMax||25000});
 return {ingestion:{accepted:parsed.records.length,skipped:parsed.skipped,truncated:parsed.truncated,
    errors:parsed.errors},analysis:analyzeCarbon3D(parsed.records,opts)};
}
export function carbonPhaseIndex(index){
 if(!Number.isInteger(index)||index<0)throw new RangeError('nonnegative integer microtick required');
 const phase=index%240;
 return {cycle:Math.floor(index/240),microtick:phase,sector:Math.floor(phase/40),
  phaseStep:Math.floor(phase/3),angleDegrees:phase*1.5,
  carbonLayer:'3D',carbonAtomicNumber:6};
}
export function projection3DTo2D(x,y,z,{azimuth=0.4,tilt=0.48,scale=1}={}){
 // Camera rotation; display only, NOT Lorentz transformation.
 const c=Math.cos(azimuth),s=Math.sin(azimuth),ct=Math.cos(tilt),st=Math.sin(tilt);
 const rx=c*x-s*y,ry=s*x+c*y;
 return {x:scale*rx,y:scale*(ct*ry-st*z),depth:st*ry+ct*z};
}
