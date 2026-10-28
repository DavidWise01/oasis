/* OASIS | Bound 09 | moving common Galactocentric reference frame
   The shared boost is a chosen visualization frame, NOT an observed
   absolute velocity of the Milky Way or Sgr A*.
   The 729 points are coordinate sampling stations, not 729 actual orbiting stars.
*/
(function(root){
"use strict";
const R0_KPC=8.277;
const STATIONS=729;
const ORBIT_KM_S=233;
const PC_PER_MYR_PER_KM_S=1.022712165045695;
const KPC_PER_MYR_PER_KM_S=PC_PER_MYR_PER_KM_S/1000;
const AU_TO_KPC=4.84813681109536e-9;
const SOLAR_PERIOD_MYR=2*Math.PI*(R0_KPC*1000)/(ORBIT_KM_S*PC_PER_MYR_PER_KM_S);
const C=Object.freeze({R0_KPC,STATIONS,ORBIT_KM_S,PC_PER_MYR_PER_KM_S,AU_TO_KPC,SOLAR_PERIOD_MYR});
function finite(x,label){if(typeof x!=="number"||!Number.isFinite(x))throw Error("Invalid "+label);return x;}
function axes(headingDeg){
 finite(headingDeg,"headingDeg");const a=headingDeg*Math.PI/180;
 return {forward:[Math.cos(a),Math.sin(a)],side:[-Math.sin(a),Math.cos(a)]};
}
const plus=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const minus=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const times=(k,a)=>[k*a[0],k*a[1]];
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
const len=a=>Math.hypot(a[0],a[1]);
function position({station=0,timeMyr=0,bulkKmS=0,headingDeg=0,mode="orbit"}={}){
 if(!Number.isInteger(station)||station<0||station>=STATIONS)throw Error("station 0..728");
 finite(timeMyr,"timeMyr");finite(bulkKmS,"bulkKmS");
 const {forward,side}=axes(headingDeg);
 if(mode!=="orbit"&&mode!=="rigid")throw Error("mode must be orbit or rigid");
 // Every object/station gets exactly the same center-frame translation.
 const carrierKm=bulkKmS*KPC_PER_MYR_PER_KM_S*timeMyr;
 const center=times(carrierKm,forward);
 // Orbit is one idealized circular Sun track, not a measured orbital solution.
 // The other 728 markers are samples on the rotating Sun->center ray,
 // NOT stars all with the same angular speed.
 const phase=mode==="orbit"?(2*Math.PI*timeMyr/SOLAR_PERIOD_MYR):0;
 const fraction=station/(STATIONS-1),radius=R0_KPC*fraction;
 const trailingVector=plus(times(-radius*Math.cos(phase),forward),
                           times(-radius*Math.sin(phase),side));
 const point=plus(center,trailingVector);
 const trailingDistance=-dot(trailingVector,forward); // + = behind train center
 return {station,pcFromCenter:radius*1000,timeMyr,center,point,
         trailingKpc:trailingDistance,phaseRad:phase,
         bulkKmS,headingDeg,mode};
}
function sun({timeMyr=0,bulkKmS=0,headingDeg=0,mode="orbit"}={}){
 return position({station:728,timeMyr,bulkKmS,headingDeg,mode});
}
function earth({timeMyr=0,bulkKmS=0,headingDeg=0,mode="orbit"}={}){
 const s=sun({timeMyr,bulkKmS,headingDeg,mode}),{forward,side}=axes(headingDeg);
 // Idealized 1-AU circular Earth orbit, only for local bookkeeping.
 // We DO NOT resolve the annual phase when inspecting million-year epochs.
 const annualPhase=2*Math.PI*((timeMyr*1e6)%1);
 const rel=plus(times(AU_TO_KPC*Math.cos(annualPhase),forward),
                times(AU_TO_KPC*Math.sin(annualPhase),side));
 return {...s,point:plus(s.point,rel),orbitalOffsetKpc:rel,
         modelStatus:"idealized Earth 1 AU position; annual phase not survey ephemeris"};
}
function velocity({station=728,timeMyr=0,bulkKmS=0,headingDeg=0,mode="orbit"}={}){
 const p=position({station,timeMyr,bulkKmS,headingDeg,mode});
 const {forward,side}=axes(headingDeg);
 const common=times(bulkKmS,forward);
 const fraction=station/(STATIONS-1);
 const internal=mode==="orbit"?
  plus(times(ORBIT_KM_S*fraction*Math.sin(p.phaseRad),forward),
       times(-ORBIT_KM_S*fraction*Math.cos(p.phaseRad),side)):[0,0];
 return {commonKmS:common,internalKmS:internal,totalKmS:plus(common,internal),
         stationIsPhysicalStar:false};
}
function separation(a,b){return len(minus(a.point,b.point))}
function relativeVelocity(a,b){return minus(a.totalKmS,b.totalKmS)}
function stationForRank(rank){
 const n=typeof rank==="bigint"?rank:BigInt(rank);
 return Number(((n%729n)+729n)%729n);
}
function snapshot(timeMyr,bulkKmS,headingDeg,mode){
 return {center:position({station:0,timeMyr,bulkKmS,headingDeg,mode}),
         sun:sun({timeMyr,bulkKmS,headingDeg,mode}),
         earth:earth({timeMyr,bulkKmS,headingDeg,mode})};
}
function close(a,b,rtol=1e-10){return Math.abs(a-b)<=rtol*Math.max(1,Math.abs(a),Math.abs(b))}
function selfTest(){
 const cases=[0,1,11,242,364,728];
 const timesToCheck=[0,1,10,50,100,200];
 const modes=["rigid","orbit"];
 let checks=0;
 for(const mode of modes)for(const t of timesToCheck)for(const index of cases){
  const a=position({station:index,timeMyr:t,bulkKmS:0,headingDeg:34,mode});
  const b=position({station:index,timeMyr:t,bulkKmS:320,headingDeg:34,mode});
  const c=position({station:0,timeMyr:t,bulkKmS:0,headingDeg:34,mode});
  const d=position({station:0,timeMyr:t,bulkKmS:320,headingDeg:34,mode});
  if(!close(separation(a,c),separation(b,d)))throw Error("Boost changes distance");
  if(!close(separation(a,c),R0_KPC*index/728))throw Error("Station radius altered");
  const diff=minus(b.point,a.point),displaced=minus(d.point,c.point);
  if(!close(diff[0],displaced[0])||!close(diff[1],displaced[1]))throw Error("Unequal boost");
  const va=velocity({station:index,timeMyr:t,bulkKmS:0,headingDeg:34,mode});
  const vb=velocity({station:index,timeMyr:t,bulkKmS:320,headingDeg:34,mode});
  const vc=velocity({station:0,timeMyr:t,bulkKmS:0,headingDeg:34,mode});
  const vd=velocity({station:0,timeMyr:t,bulkKmS:320,headingDeg:34,mode});
  let rel0=relativeVelocity(va,vc),rel1=relativeVelocity(vb,vd);
  if(!close(rel0[0],rel1[0])||!close(rel0[1],rel1[1]))throw Error("Boost changes relative speed");
  checks++;
 }
 const p0=snapshot(0,320,0,"rigid");
 const p10=snapshot(10,320,0,"rigid");
 if(!close(p10.sun.trailingKpc,8.277))throw Error("Not fixed distance behind train");
 if(!close(p10.center.point[0],320*KPC_PER_MYR_PER_KM_S*10))throw Error("Train shift wrong");
 if(!close(separation(p10.sun,p10.center),8.277))throw Error("Rigidity broken");
 if(!close(separation(p0.earth,p0.sun),AU_TO_KPC,1e-9))throw Error("Earth offset wrong");
 const po=snapshot(SOLAR_PERIOD_MYR/4,320,0,"orbit");
 if(Math.abs(po.sun.trailingKpc)>1e-9)throw Error("Orbital side phase fails");
 const ph=snapshot(SOLAR_PERIOD_MYR/2,320,0,"orbit");
 if(!close(ph.sun.trailingKpc,-8.277))throw Error("Orbital forward phase fails");
 const front=sun({timeMyr:0,bulkKmS:320,headingDeg:0,mode:"orbit"});
 if(!close(front.trailingKpc,8.277))throw Error("Behind convention wrong");
 if(stationForRank(0n)!==0||stationForRank(1n)!==1||
 stationForRank(620448401733239439359999n)!==728)throw Error("24! station mapping inconsistent");
 return {pass:true,boostInvariantCases:checks,stationCount:STATIONS,
  rigidBehind_kpc:p10.sun.trailingKpc,orbitQuarterBehind_kpc:po.sun.trailingKpc,
  orbitHalfBehind_kpc:ph.sun.trailingKpc,
  tenMyr_320km_s_translation_kpc:p10.center.point[0],
  solarOrbitPeriodMyr:SOLAR_PERIOD_MYR,
  "earth1AU_offset_test":"PASS",
  "station_rank_000_001_last":"PASS",
  "gravity_unmodified":"PASS: test compares coordinates only",
  "intrinsic_sgra_bulkmotion_measured_here":false};
}
const api=Object.freeze({...C,axes,position,sun,earth,velocity,separation,
 relativeVelocity,stationForRank,snapshot,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound09SharedMotion=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
