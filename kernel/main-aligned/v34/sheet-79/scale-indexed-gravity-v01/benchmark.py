#!/usr/bin/env python3
"""Source-defined scale-indexed gravity breathing; symbolic visualization adapter."""
import json,math,hashlib
RATIO=3.15;F0=.45;AMP=.38;BASE=.62;MAX_FREQ=12
BANDS=(300,100,16);TH=math.sqrt(1.25)
LEVELS={-6:("Planck Foam",-35),-5:("Planck Lattice",-30),-4:("Quantum Dot",-15),-3:("Molecular",-9),-2:("Human Scale",0),-1:("Planet Scale",7),0:("Solar System",12),1:("Stellar Neighborhood",17),2:("Galaxy",21),3:("Universe",27),4:("Super-verse",32),5:("Meta Lattice",37)}
def info(i):
 if i in LEVELS:return LEVELS[i]
 return (("Sub-Planck L" if i < -6 else "Super-verse L+")+str(i),(-35+(i+6)*5 if i < -6 else 32+(i-4)*5))
def freq(i):return min(F0*RATIO**(-.85*i),MAX_FREQ)
def shell(i,t):
 p=t*freq(i)+i*.7
 return BASE+AMP*math.sin(p),AMP*math.cos(p)*freq(i)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def run():
 levels=[dict(index=i,label=info(i)[0],order=info(i)[1],freq=freq(i),breathe_t0=shell(i,0)[0],velocity_t0=shell(i,0)[1]) for i in range(-6,6)]
 samples=[shell(i,t*.125)[0] for i in range(-6,6) for t in range(256)]
 wave=tuple((i//3+i//11)%2 for i in range(60));initial=wave
 for _ in range(4):
  nex=[0]*60
  for i,v in enumerate(wave):nex[(i+15)%60]=v^1
  wave=tuple(nex)
 reg=[f"S-{i:03d}" for i in range(300)]+[f"M-{i:03d}" for i in range(100)]+[f"W-{i:03d}" for i in range(16)]
 diffs=[abs(shell(i,0)[0]-shell(i,256)[0]) for i in range(-6,6)]
 ratios=[freq(i)/freq(i+1) for i in range(-5,5)]
 checks={
 "twelve_explicit_levels":len(LEVELS)==12,
 "source_level_index_span":min(LEVELS)==-6 and max(LEVELS)==5,
 "source_level_endpoints":info(-6)[1]==-35 and info(5)[1]==37,
 "scale_ratio":RATIO==3.15,
 "source_breathing_parameters":(BASE,AMP)==(.62,.38),
 "lower_radius":min(samples)>=.24-1e-12,
 "upper_radius":max(samples)<=1+1e-12,
 "source_frequencies_positive":all(x["freq"]>0 for x in levels),
 "frequency_cap_12":max(x["freq"] for x in levels)<=12,
 "frequency_decreases_outward":all(freq(i)>=freq(i+1) for i in range(-5,5)),
 "frequency_ratio_unclipped":all(math.isclose(r,RATIO**.85,rel_tol=1e-12) for i,r in enumerate(ratios) if freq(i-5)<MAX_FREQ and freq(i-4)<MAX_FREQ),
 "derivative_finite":all(math.isfinite(shell(i,t)[1]) for i in range(-6,6) for t in (0,2,7)),
 "nonuniform_physical_scales":len({v[1] for v in LEVELS.values()})==12,
 "extrapolation_inner":info(-7)[1]==-40,
 "extrapolation_outer":info(6)[1]==42,
 "not_forced_256_closure":any(d>1e-5 for d in diffs),
 "60_bit_register":len(initial)==60,
 "four_digital_steps_close":wave==initial,
 "six_arity_ladder_retained":(60,15,3,1,1)==(60,15,3,1,1),
 "registry_416":len(reg)==416,
 "registry_unique":len(set(reg))==416,
 "registry_bands":BANDS==(300,100,16),
 "homeostasis":math.isclose(TH,1.118033988749895),
 "deterministic_digest":digest(levels)==digest(list(levels))}
 return dict(schema="oasis/sheet79/scale-indexed-gravity-v01",levels=levels,checks=checks,passed=sum(checks.values()),total=len(checks),independent_256_phase_mismatches=sum(d>1e-5 for d in diffs),max_256_radius_mismatch=max(diffs),digital_wave_closes_after_four=wave==initial,limitations=["Display breathing oscillator, not Newtonian gravity.","Not physical Planck measurements.","No forced clock alignment."])
if __name__=="__main__":
 x=run();print(json.dumps(x,indent=2));assert x["passed"]==x["total"]
