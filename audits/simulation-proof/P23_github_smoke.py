#!/usr/bin/env python3
"""P2.3 Git CI smoke: exact frozen v92 source; two 2^3 direction policies."""
from pathlib import Path
import sys,subprocess,hashlib,json,math
HERE=Path(__file__).resolve().parent
F=HERE if (HERE/'kernel.py').is_file() else HERE.parents[1]/'kernel'/'frozen'/'ae-generative-first-v92'
sys.path.insert(0,str(F))
import kernel
assert subprocess.check_output(['git','hash-object',str(F/'kernel.py')],text=True).strip()=='bf84cfc8746ccaf35c0204050ada8c3980817cb8'
assert hashlib.sha256((F/'CANON.json').read_bytes()).hexdigest()==kernel.CANON_SHA256
kernel.load_and_verify_canon(F/'CANON.json')
N=12288
D=lambda b:tuple(1 if (b>>i)&1==0 else -1 for i in range(3))
assert len({D(i) for i in range(8)})==8
assert [sum(D(i)[j] for i in range(8)) for j in range(3)]==[0,0,0]
sa=sb=kernel.genesis();pa=pb=(0,0,0);a=b=0
ha=hb='0'*64
for n in range(1,N+1):
    na=kernel.advance(sa);nb=kernel.advance(sb)
    assert na==nb and na.parent_seal==sa.seal() and nb.parent_seal==sb.seal()
    assert n==12*na.generation+na.q
    da,db=D(a),D(b)
    pa=tuple(x+y for x,y in zip(pa,da)); pb=tuple(x+y for x,y in zip(pb,db))
    assert sum(i*i for i in da)==sum(i*i for i in db)==3
    ha=hashlib.sha256((ha+na.seal()+str(pa)+str(a)).encode()).hexdigest()
    hb=hashlib.sha256((hb+nb.seal()+str(pb)+str(b)).encode()).hexdigest()
    if n>1: assert ha!=hb
    sa,sb=na,nb;b=(b+1)%8
assert pa==(N,N,N) and pb==(0,0,0) and sa.generation==1024 and sa.q==0
for start in range(8):
    assert [sum(D((start+i)%8)[j] for i in range(8)) for j in range(3)]==[0,0,0]
assert all(D(i)[0]!=0 for i in range(8))
print(json.dumps({'gate':'P2.3','source':'v92 exact','ticks_each':N,'straight':pa,'rotate8':pb,
  'equal_frozen_lineage':True,'different_transport_lineage':True,'eight_orbits_closed':True,
  'local_step_norm_sq':3,'external_calibration_required':True,'physical_simulation_proven':False,'status':'PASS'},indent=2))
