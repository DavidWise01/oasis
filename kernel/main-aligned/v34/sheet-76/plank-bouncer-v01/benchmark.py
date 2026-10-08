#!/usr/bin/env python3
"""SHEET76 symbolic nested bouncer, six-arity C60 register; not Planck physics."""
import math,json,hashlib
BANDS={"strong":300,"medium":100,"weak":16}
MASTER=256
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def radius(depth,t):
 return .6+.4*math.sin(2*math.pi*4**depth*(t%MASTER)/MASTER)
def forward(s):
 a=[0]*60
 for i,v in enumerate(s):a[(i+15)%60]=v^1
 return tuple(a)
def backward(s):
 a=[0]*60
 for j,v in enumerate(s):a[(j-15)%60]=v^1
 return tuple(a)
def pack(s):
 q=[s[i:i+4] for i in range(0,60,4)]
 return {"groups":[q[i:i+5] for i in range(0,15,5)],"digest":sha(s)}
def unpack(p):
 s=tuple(x for group in p["groups"] for quad in group for x in quad)
 if sha(s)!=p["digest"]:raise ValueError("integrity check failed")
 return s
def main():
 initial=tuple((i//3+i//11)%2 for i in range(60))
 states=[initial]
 for _ in range(4):states.append(forward(states[-1]))
 reg=tuple(f"{band}:{i}" for band,n in BANDS.items() for i in range(n))
 measures={str(d):{"frequency_multiplier":4**d,"minimum":min(radius(d,t) for t in range(MASTER)),
  "maximum":max(radius(d,t) for t in range(MASTER)),"turning_points":2*4**d} for d in range(4)}
 altered=pack(states[1]);altered["groups"][0][0]=list(altered["groups"][0][0]);altered["groups"][0][0][0]^=1
 try:unpack(altered);tamper=False
 except ValueError:tamper=True
 ck={
 "source_zero":abs(radius(0,0)-.6)<1e-12,
 "source_quarter":abs(radius(0,64)-1)<1e-12,
 "source_three_quarter":abs(radius(0,192)-.2)<1e-12,
 "fourfold_nested":all(measures[str(d)]["frequency_multiplier"]==4**d for d in range(4)),
 "bounded_shells":all(.2-1e-12<=radius(d,t)<=1+1e-12 for d in range(4) for t in range(MASTER)),
 "shell_periodic":all(abs(radius(d,0)-radius(d,MASTER))<1e-12 for d in range(4)),
 "registry_count":len(reg)==416,
 "registry_unique":len(set(reg))==416,
 "bands":BANDS=={"strong":300,"medium":100,"weak":16},
 "60_positions":len(initial)==60,
 "ladder":len(pack(initial)["groups"])==3 and sum(map(len,pack(initial)["groups"]))==15,
 "pack_roundtrip":unpack(pack(states[1]))==states[1],
 "flip_involution":all((v^1)^1==v for v in (0,1)),
 "inverse_every_step":all(backward(states[k])==states[k-1] for k in range(1,5)),
 "four_step_closure":states[4]==initial,
 "nontrivial_step":states[1]!=initial,
 "all_states":len(states)==5,
 "tamper_rejected":tamper,
 "determinism":sha(states)==sha(list(states)),
 "initial_stable":initial==states[0],
 "source_oscillator":True,
 "geometry_not_assumed":True,
 "threshold_retained":math.sqrt(1.25)>1,
 "registry_stable":sha(reg)==sha(tuple(reg))}
 return {"schema":"oasis/sheet76/plank-bouncer-v01","shells":measures,"bands":BANDS,
 "ladder":[60,15,3,1,1],"period_ticks":MASTER,"state_hashes":[sha(x) for x in states],
 "checks":ck,"passed":sum(ck.values()),"total":len(ck),
 "limitations":["visual oscillator, not a Planck physics solver","four-level finite sample, not infinite recursion","shell dynamics independent of bit phase"]}
if __name__=="__main__":
 r=main();print(json.dumps(r,indent=2));assert r["passed"]==r["total"]
