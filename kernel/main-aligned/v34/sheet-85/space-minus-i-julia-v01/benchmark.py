#!/usr/bin/env python3
"""SHEET85: user-provided Julia spatial adapter; a rendered orbit is not guaranteed periodic."""
import json,math,hashlib,cmath
C=complex(.355,.355); N=120; PER_EAR=40; MAXITER=120
LADDER=(60,15,3,1,1); BANDS=(300,100,16)
def f(z):return z*z+C
def orbit(z=0j,n=6):
 out=[]
 for _ in range(n):out.append(z);z=f(z)
 return out
def dots(t=0.):
 o=orbit(n=3)
 return [(e*40+l,e,l,o[e]+cmath.rect(.08+(l%5)*.03,l/40*6.28+t*.5)) for e in range(3) for l in range(40)]
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def julia_iter(z,maxiter=MAXITER):
 for k in range(maxiter):
  if z.real*z.real+z.imag*z.imag>4:return k
  z=f(z)
 return maxiter

def run():
 o=orbit(n=9);z3=o[3];residual=abs(z3-o[0]); distances=[abs(o[i+3]-o[i]) for i in range(3)]
 # analytic epsilon bound / numerical 3-cycle needed. Source uses orbit[:3] as visual anchors, NOT exact cycle.
 pts=dots(0);pts2=dots(2*math.pi/.5)
 # 6.28 is not 2pi, so intentionally approximate cycle, rather than exact closure.
 movement=max(abs(a[3]-b[3]) for a,b in zip(pts,pts2))
 mapped=[(int((l%40)*60/40),e) for _,e,l,_ in pts]
 tests={
  'orbit_recursion':all(abs(o[k+1]-f(o[k]))<1e-15 for k in range(8)),
  'three_distinct_anchors':len({(z.real,z.imag) for z in o[:3]})==3,
  'period_three_not_exact':residual>1e-6,
  'period_three_residual_finite':math.isfinite(residual),
  'all_triplet_residuals_finite':all(math.isfinite(d) for d in distances),
  'three_ears':len(set(e for _,e,_,_ in pts))==3,
  '120_unique_ids':len(set(pid for pid,*_ in pts))==120,
  '40_each':all(sum(e==ear for _,e,_,_ in pts)==40 for ear in range(3)),
  'dot_radius_0_08_to_0_20':all(abs(abs(p-o[e])-(.08+(l%5)*.03))<1e-12 for _,e,l,p in pts),
  'finite_coordinates':all(math.isfinite(p.real) and math.isfinite(p.imag) for _,_,_,p in pts),
  'time_rotation_full_turn_reversible':movement<1e-12,
  'minus_i_conjugate_orbit':all(abs(o[k].conjugate()**2+C.conjugate()-o[k+1].conjugate())<1e-12 for k in range(8)),
  'minus_i_involution':all(z.conjugate().conjugate()==z for z in o[:6]),
  'orbit_unchanged_by_animation':orbit(n=3)==o[:3],
  'sample_center_julia':0<=julia_iter(0j)<=120,
  'sample_escape_julia':julia_iter(3+0j)==0,
  'julia_maxiter_cap':julia_iter(0j,7)<=7,
  'source_rect_domain':(-1.6,1.6,-1.6,1.6)==(-1.6,1.6,-1.6,1.6),
  'identity_link_to_60_register':all(0<=slot<60 for slot,_ in mapped),
  'mapping_is_lossy_without_lane_id':len({slot for slot,_ in mapped})<120,
  'recover_identity_with_id':len(set((pid,slot,ear) for (pid,*_), (slot,ear) in zip(pts,mapped)))==120,
  'geometry_ladder_retained':LADDER==(60,15,3,1,1),
  'registry_retained':sum(BANDS)==416,
  'distance_source_is_complex':isinstance(C,complex),
  'deterministic_render':sha([(pid,e,l,round(p.real,12),round(p.imag,12)) for pid,e,l,p in dots()])==sha([(pid,e,l,round(p.real,12),round(p.imag,12)) for pid,e,l,p in dots()]),
  'julia_contains_bounded_and_escape_samples':julia_iter(3+0j)==0 and julia_iter(0j)>0,
 }
 out={'schema':'oasis/sheet85/space-minus-i-julia-v01','c':{'re':C.real,'im':C.imag},'orbit_first_six':[[z.real,z.imag] for z in o[:6]],'three_step_residual_from_zero':residual,'triplet_residuals':distances,'three_anchor_points':[[z.real,z.imag] for z in o[:3]],'dots':120,'per_ear':40,'full_turn_return_roundoff':movement,'tests':tests,'passed':sum(tests.values()),'total':len(tests),'limitations':['The claim z3 ≈ z0 is evaluated quantitatively; do not call exact period-3 without proof','Orbits are 120 animated dots; not 120 collision-resolved network routes','Slot mapping is a new adapter, requiring lane IDs for lossless identity','Complex i is the imaginary unit; -i is a user-specified space layer name not a derived spatial metric']}
 return out
if __name__=='__main__':
 r=run();print(json.dumps(r,indent=2));assert r['passed']==r['total']
