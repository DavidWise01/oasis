/* OASIS Bound 10: 000 -> 001 Planck reference -> 728 Sun.
   729 labeled positions: 000 CENTER_SENTINEL (r=0), 001..728
   logarithmic areal-radius reference levels. No physical path inside horizon
   claimed; only an algebraic Schwarzschild, nonrotating approximation.

   CODATA 2022: lp = 1.616255(18)×10^-35 m, NIST.
   GRAVITY Collaboration (2022): Sgr A* M=4.297×10^6 Msolar,
   Sun to Galactic Center 8277 pc.
*/
(function(root){
"use strict";
const N=729;
const LP=1.616255e-35;
const C=299792458;
const GM_SUN=1.3271244e20;
const M_BH_SUN=4.297e6;
const PC=3.0856775814913673e16;
const R0=8277*PC;
const RS=2*GM_SUN*M_BH_SUN/(C*C);
const R_PHOTON=1.5*RS;
const R_ISCO=3*RS;
const R_KCRIT=Math.pow(12*RS*RS*LP**4,1/6);
const LOGSPAN=Math.log10(R0/LP);
const LOGSTEP=LOGSPAN/(N-2);
const RATIO=10**LOGSTEP;
const CONST=Object.freeze({N,LP,C,GM_SUN,M_BH_SUN,PC,R0,RS,R_PHOTON,R_ISCO,R_KCRIT,LOGSPAN,LOGSTEP,RATIO});
function log10(v){return Math.log10(v);}
function posToRadius(i){
 if(!Number.isInteger(i)||i<0||i>=N)throw Error("Station must be 000..728");
 if(i===0)return 0;
 return LP*10**((i-1)*LOGSTEP);
}
function radiusToFractionalStation(radius){
 if(!Number.isFinite(radius)||radius<=0||radius>R0*(1+1e-12))throw Error("Radius must be positive and <= Sun");
 return 1+log10(radius/LP)/LOGSTEP;
}
function logKlp4(r){
 if(!(r>0))return null;
 return log10(12)+2*log10(RS/LP)-6*log10(r/LP);
}
function externalSchwarzschildSliceProperLength(r){
 // Proper radial *length* from the horizon to areal radius r
 // at constant Schwarzschild t, only defined on exterior t=const slice.
 if(r<RS)return null;
 if(r===RS)return 0;
 const x=r/RS;
 return Math.sqrt(r*(r-RS))+RS*Math.acosh(Math.sqrt(x));
}
function classification(r){
 if(r===0)return "CENTER_SENTINEL_NO_CONTINUUM_VALUE";
 if(r<LP)return "BELOW_PLANCK_REFERENCE_NOT_SAMPLED";
 if(r<R_KCRIT)return "FORMAL_HIGH_CURVATURE_INSIDE_HORIZON_UNVERIFIED";
 if(r<RS)return "FORMAL_CLASSICAL_INTERIOR_NOT_A_SPATIAL_RADIAL_PATH";
 if(r===RS)return "HORIZON_ANCHOR";
 return "SCHWARZSCHILD_EXTERIOR_SPHERICALLY_SYMMETRIC_APPROXIMATION";
}
function station(i){
 const r=posToRadius(i);
 return {index:i,label:String(i).padStart(3,"0"),
  radius_m:r,ratio_to_planck:i===0?null:r/LP,
  log10_radius_to_planck:i===0?null:log10(r/LP),
  ratio_to_horizon:i===0?null:r/RS,
  log10_planck_normalized_K:i===0?null:logKlp4(r),
  external_slice_proper_m:i===0?null:externalSchwarzschildSliceProperLength(r),
  classification:classification(r),physical_observation:false};
}
function milestones(){
 return [
  {name:"Mathematical center sentinel",r:0,index:0,label:"000"},
  {name:"Planck length reference",r:LP,index:1,label:"001"},
  {name:"Formal Planck curvature (K lp^4 = 1)",r:R_KCRIT,index:radiusToFractionalStation(R_KCRIT),label:"not an exact station"},
  {name:"Schwarzschild event horizon",r:RS,index:radiusToFractionalStation(RS),label:"not an exact station"},
  {name:"Schwarzschild photon sphere",r:R_PHOTON,index:radiusToFractionalStation(R_PHOTON),label:"not an exact station"},
  {name:"Schwarzschild ISCO",r:R_ISCO,index:radiusToFractionalStation(R_ISCO),label:"not an exact station"},
  {name:"Sun galactocentric radius",r:R0,index:728,label:"728"}];
}
function counts(){
 const out={};
 for(let i=0;i<N;i++){let c=classification(posToRadius(i));out[c]=(out[c]||0)+1}
 return out;
}
function selfTest(){
 if(N!==729)throw Error("Wrong station count");
 if(Math.abs(posToRadius(1)/LP-1)>1e-12)throw Error("Planck anchor wrong");
 if(Math.abs(posToRadius(728)/R0-1)>1e-12)throw Error("Solar anchor wrong");
 if(posToRadius(0)!==0)throw Error("Zero sentinel wrong");
 let previous=0;
 for(let i=1;i<N;i++){
  const r=posToRadius(i);
  if(!Number.isFinite(r)||r<=previous)throw Error("Station ordering fails: "+i);
  if(Math.abs(radiusToFractionalStation(r)-i)>1e-10)throw Error("Reverse log rank fails: "+i);
  previous=r;
 }
 if(Math.abs(radiusToFractionalStation(RS)-592.29335905074)>1e-7)throw Error("Horizon anchor wrong");
 if(Math.abs(radiusToFractionalStation(R_KCRIT)-200.46669652477183)>1e-7)throw Error("Curvature anchor wrong");
 if(Math.abs(logKlp4(R_KCRIT))>1e-10)throw Error("Planck curvature equation failed");
 if(externalSchwarzschildSliceProperLength(RS)!==0)throw Error("Exterior horizon proper limit wrong");
 if(externalSchwarzschildSliceProperLength(RS/2)!==null)throw Error("Improper interior Schwarzschild slice");
 if(externalSchwarzschildSliceProperLength(R0)<=0)throw Error("Exterior proper length wrong");
 const v=milestones();
 if(v.length!==7)throw Error("Anchor count wrong");
 return {
  test:"PASS: all 729 stations strictly ordered; source anchors, inverse index, curvature, exterior slice",
  station000:"r=0 named mathematical sentinel, not a physical Planck region",
  station001:"r=1.616255e-35 m CODATA Planck reference",
  station728:"r=8,277 pc model solar radius",
  Schwarzschild_horizon_m:RS,
  classical_Klp4_unity_radius_m:R_KCRIT,
  decades_from_sun_to_Planck:LOGSPAN,
  exterior_radial_slices_only:true,
  center_gravity_field:"UNKNOWN/UNDEFINED",
  counts:counts()
 };
}
const API=Object.freeze({...CONST,posToRadius,radiusToFractionalStation,
 logKlp4,externalSchwarzschildSliceProperLength,classification,station,milestones,counts,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=API;
root.Bound10InvariantZero=API;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
