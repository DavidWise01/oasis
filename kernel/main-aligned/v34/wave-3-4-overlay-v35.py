#!/usr/bin/env python3
"""Additive OaSIs 8D wave overlay: sine 3, square 4 cycles/frame; frozen v34 unchanged."""
import math, random, json, time
from pathlib import Path
N=8
ANGLES=[(0,1,.7),(2,3,-.9),(4,5,1.1),(6,7,-.6),(1,2,.8),(3,4,-1.0),(5,6,.5),(0,7,.95),(2,5,-.75),(1,6,.65)]
def eye(): return [[float(i==j) for j in range(N)] for i in range(N)]
def mul(a,b): return [[sum(a[i][k]*b[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
def mv(a,v): return [sum(a[i][j]*v[j] for j in range(N)) for i in range(N)]
def trans(a): return [list(x) for x in zip(*a)]
def g(i,j,t):
 a=eye(); c,s=math.cos(t),math.sin(t)
 a[i][i]=a[j][j]=c; a[i][j]=-s; a[j][i]=s
 return a
def error(a,b):return max(abs(x-y) for x,y in zip(a,b))
def norm(a):return math.sqrt(sum(x*x for x in a))
R=eye()
for i,j,t in ANGLES:R=mul(g(i,j,t),R)
def waves(t):
 return math.sin(6*math.pi*(t%1)),(1 if (4*t)%1<.5 else -1)
def matrix(t):
 sine,square=waves(t)
 return mul(g(2,3,.08*square),mul(g(0,1,.12*sine),R))
checks={}
def check(name,condition):checks[name]=bool(condition)
n=4096
square=[waves((i+.5)/n)[1] for i in range(n)]
sine=[waves((i+.5)/n)[0] for i in range(n)]
check("sine_3_cycles",max(abs(sine[i]-math.sin(6*math.pi*(i+.5)/n)) for i in range(n))<1e-12)
check("square_4_cycles",sum(square[i]!=square[i-1] for i in range(1,n))+(square[0]!=square[-1])==8)
check("square_balanced",sum(square)==0)
check("sine_zero_mean",abs(sum(sine)/n)<1e-12)
check("one_frame_period",all(waves((i+.5)/n)==waves(1+(i+.5)/n) for i in range(0,n,64)))
random.seed(3404)
max_err=max_norm=0.
start=time.perf_counter()
for i in range(600):
 t=(i+.5)/600;v=[random.uniform(-1,1) for _ in range(N)]
 a=matrix(t);w=mv(a,v);u=mv(trans(a),w)
 max_err=max(max_err,error(v,u));max_norm=max(max_norm,abs(norm(v)-norm(w)))
check("random_roundtrips",max_err<1e-12)
check("norm_preservation",max_norm<1e-12)
base=[.62,.18,.85,.34,.71,.09,.55,.28];v=base[:]
for i in range(20000):
 a=matrix((i+.5)/20000)
 v=mv(trans(a),mv(a,v))
drift=error(v,base)
check("20k_cycle_drift",drift<1e-10)
check("nontrivial_components",max(sine)>.5 and set(square)=={-1,1})
report={"target":"OaSIs main-aligned v34, additive sine3/square4 v35", "checks":checks,"passed":sum(checks.values()),"failed":sum(not x for x in checks.values()),"max_roundtrip_error":max_err,"max_norm_error":max_norm,"drift_20000":drift,"seconds":time.perf_counter()-start,"note":"8D numerical fixture only; no full Lean kernel test"}
print(json.dumps(report,indent=2))
if not all(checks.values()):raise SystemExit(1)
