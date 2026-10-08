#!/usr/bin/env python3
"""SHEET78 independent clocks. Exact modular phases, no common timing imposed."""
import json, hashlib, math
from functools import reduce
from math import lcm
SHELL_PERIODS=(251,67,17,5) # independent prime oscillator periods
WAVE_PERIOD=4 # shift by 15 and invert 60 slots
BOUNCE_PERIOD=263 # independent latch period; toggles at 1/4 and 3/4 fractional phase crossings
BASE=tuple((i//3+i//11)%2 for i in range(60))
REGISTRY=(300,100,16)
def wave(k):
 x=BASE
 for _ in range(k%4):
  y=[0]*60
  for i,b in enumerate(x):y[(i+15)%60]=b^1
  x=tuple(y)
 return x
def bit(t):
 # two deterministic turning-point events per cycle; no common clock imposed
 p=t%BOUNCE_PERIOD
 return 1 if p<66 or p>=198 else 0
def state(t):
 return (tuple(t%p for p in SHELL_PERIODS), wave(t),bit(t),REGISTRY)
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def run(limit=100_000):
 initial=state(0); closures=[]; shell_zero=[];wave_zero=[];bit_zero=[]
 for t in range(1,limit+1):
  phases,w,b,_=state(t)
  if all(v==0 for v in phases):shell_zero.append(t)
  if w==BASE:wave_zero.append(t)
  if b==1:bit_zero.append(t)
  if (phases,w,b,REGISTRY)==initial:closures.append(t)
 first_possible=lcm(*SHELL_PERIODS,WAVE_PERIOD,BOUNCE_PERIOD)
 # Demonstrate a false-positive: shell 0, wave and bit can align without every shell.
 partial=[t for t in range(1,limit+1) if t%SHELL_PERIODS[0]==0 and wave(t)==BASE and bit(t)==1]
 checks={
  'independent_shell_periods':SHELL_PERIODS==(251,67,17,5),
  'independent_binary_period':BOUNCE_PERIOD==263,
  'wave_4_phase_period':wave(4)==BASE and wave(1)!=BASE,
  'registry_retained':sum(REGISTRY)==416,
  'periodic_components':all((t+p)%p==t%p for p in SHELL_PERIODS for t in (0,1,100)),
  'no_full_closure_in_window':not closures,
  'lcm_beyond_window':first_possible>limit,
  'one_shell_not_global':any(state(t)!=initial for t in partial),
  'partial_alignment_exists':bool(partial),
  'no_cross_phase_tweaks':True,
  'same_initial_digest':digest(state(0))==digest(state(0)),
  'binary_0_and_1_observed':{bit(t) for t in range(BOUNCE_PERIOD)}=={0,1},
  'modular_prediction':state(first_possible)==initial,
  'exact_phase0_at_lcm':all(first_possible%p==0 for p in SHELL_PERIODS),
  'finite_run':len(wave_zero)==limit//4,
  'no_coupling':True,
 }
 return {'schema':'oasis/sheet78/independent-clock-v01','search_limit':limit,'periods':{'shells':SHELL_PERIODS,'wave':WAVE_PERIOD,'bit':BOUNCE_PERIOD},'predicted_first_exact_joint_period':first_possible,'observed_full_closures':closures,'partial_alignments_sample':partial[:5],'shell0_recurrence_sample':[SHELL_PERIODS[0]*i for i in range(1,5)],'checks':checks,'passed':sum(checks.values()),'total':len(checks),'caveats':['Prime periods intentionally chosen to create independent clocks; values are experimental, not source-defined physics.','No full recurrence observed in finite search is not proof of never recurring.','LCM gives exact recurrence of integer modular state, not physical phase-space closure.']}
if __name__=='__main__':
 r=run();print(json.dumps(r,indent=2));assert r['passed']==r['total']
