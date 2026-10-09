#!/usr/bin/env node
// ROOT0 P2.0: CONDITIONAL 3D scalar-lattice physical candidate, NOT an I13-derived law.
// Local wave recurrence: u(n+1)-2u(n)+u(n-1) = r^2 * 3D discrete Laplacian(u).
import assert from 'node:assert/strict';
const c=299792458;                         // SI exact, m/s
const hbarC=0.1973269804e-15;              // GeV*m, CODATA
const lp=1.616255e-35;                     // m, CODATA rounded
const tp=lp/c;                             // seconds, rounded Planck length input
const Gpc=3.0856775814913673e25;         // m, 1 Gpc
const nAxis=[1,0,0];
const nDiag=Array(3).fill(1/Math.sqrt(3));
const scalar=(x,y)=>Math.abs(x-y)<1e-11*Math.max(1,Math.abs(x),Math.abs(y));
const sum4=n=>n.reduce((z,v)=>z+v**4,0);
const sqr=x=>x*x;
const rFor=a=>c*tp/a;
const axisSpeed=(x,r)=>Math.cos(x/2)/Math.sqrt(1-r*r*sqr(Math.sin(x/2)));
const speed=(x,r,n)=>{
  const s=n.reduce((z,v)=>z+sqr(Math.sin(x*v/2)),0);
  return n.reduce((z,v)=>z+v*Math.sin(x*v),0)/(2*Math.sqrt(s)*Math.sqrt(1-r*r*s));
};
const delay=(a,n,high=30,low=1)=>(Gpc/c)*(sqr(a)/(8*sqr(hbarC)))*
  (sum4(n)-sqr(rFor(a)))*(sqr(high)-sqr(low));
function oscillatorMaxRhs(r){return 3*r*r}
const naivePitch=lp,naiveCourant=rFor(naivePitch);
assert.equal(naiveCourant,1);
assert.equal(oscillatorMaxRhs(naiveCourant),3);
assert(oscillatorMaxRhs(naiveCourant)>1);
const growingRootMagnitude=5+Math.sqrt(24);
assert(growingRootMagnitude>9.8&&growingRootMagnitude<10);
// Marginal (boundary) stability r^2=1/3; not robust strict stability.
const criticalPitch=Math.sqrt(3)*lp,rCritical=rFor(criticalPitch);
assert(oscillatorMaxRhs(rCritical)<=1+1e-12);
assert(scalar(sqr(rCritical),1/3));
const convergence=[.1,.01,.001,.0001].map(x=>{
  const va=axisSpeed(x,rCritical);
  const vd=speed(x,rCritical,nDiag);
  const leading=1-x*x/12;
  assert(Math.abs(va-leading)<x**4/15+1e-14);
  assert(Math.abs(vd-1)<1e-12);
  return {ka:x,axis_v_over_c:va,diagonal_v_over_c:vd,axis_quadratic_approx:leading};
});
const timingAxis=delay(criticalPitch,nAxis);
const timingDiag=delay(criticalPitch,nDiag);
assert(Math.abs(timingDiag)<1e-32);
assert(timingAxis>1e-19&&timingAxis<2e-19);
const interiorPitch=2*lp,rInterior=rFor(interiorPitch);
assert(scalar(rInterior,.5)&&oscillatorMaxRhs(rInterior)<1);
const timingAxisInterior=delay(interiorPitch,nAxis);
const timingDiagInterior=delay(interiorPitch,nDiag);
assert(scalar(timingAxisInterior/timingAxis,1.5));
assert(scalar(timingDiagInterior/timingAxis,1/6));
const assumedResolution=1e-3; // Hypothetical 1ms, not observation.
const thresholdCell_m=Math.sqrt(12*assumedResolution*(c/Gpc)*
  sqr(hbarC)/(sqr(30)-sqr(1)));
const thresholdRatio=assumedResolution/timingAxis;
assert(thresholdRatio>1e15);
// Alternative spacings show physical hypotheses underdetermined by 'one Planck tick'.
const output={
  schema:'ROOT0-P2.0-source-linked-conditional-wave-test',
  model:'3D centered-difference scalar wave; extra hypothetical coupling, not frozen ROOT0',
  naive:{a_m:naivePitch,tau_s:tp,CFL_rhs_max:3,stable:false,amplification_per_tick:growingRootMagnitude},
  marginal:{a_m:criticalPitch,tau_s:tp,CFL_rhs_max:oscillatorMaxRhs(rCritical),axis_delay_30vs1_GeV_1Gpc_s:timingAxis,diagonal_delay_s:timingDiag},
  interior:{a_m:interiorPitch,tau_s:tp,CFL_rhs_max:oscillatorMaxRhs(rInterior),axis_delay_s:timingAxisInterior,diagonal_delay_s:timingDiagInterior},
  hypothetical_one_ms:{required_axis_cell_m:thresholdCell_m,ratio_to_marginal_prediction:thresholdRatio},
  convergent_speed_tests:convergence,
  linear_vacuum_dispersion_baseline:'zero',
  source_emission_and_redshift:'not modeled',
  scalar_not_Maxwell:true,
  simulationTheoryProven:false,
  tests:'PASS'
};
console.log(JSON.stringify(output,null,2));
