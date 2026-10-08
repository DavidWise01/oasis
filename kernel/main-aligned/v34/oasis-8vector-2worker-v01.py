#!/usr/bin/env python3
"""OaSIs 8-vector plus 2 worker bees, reversible ordered 24-label processing."""
import random,math,json,time
MOD=2**32;MASK=MOD-1
LABELS=[(s,p) for s in (-3,-2,-1,1,2,3) for p in range(4)]
INIT=(0,)*10
def step(state,k,inverse=False):
 s,ph=LABELS[k];v=list(state);i=(k*5+ph)%8;j=(i+1+ph)%8
 a=abs(s)*11+ph*3+1;b=ph*7+abs(s)*5+1;c=s*13+ph*17+1
 def b0(d):v[8]=(v[8]+d*(v[i]*a+k+1))&MASK
 def b1(d):v[9]=(v[9]+d*(v[8]*b+v[j]+s))&MASK
 def reg(d):v[i]=(v[i]+d*(v[9]*c+v[j]+1))&MASK
 if inverse:reg(-1);b1(-1);b0(-1)
 else:b0(1);b1(1);reg(1)
 return tuple(v)
def run(seq,start=INIT):
 v=start
 for k in seq:v=step(v,k)
 return v
def undo(seq,end):
 v=end
 for k in reversed(seq):v=step(v,k,True)
 return v
def benchmark():
 rng=random.Random(340424);seq=tuple(range(24));out=run(seq);sw=list(seq);sw[0],sw[1]=sw[1],sw[0]
 checks={'8_vector_2_bees':len(out)==10,'24_labels':len(set(LABELS))==24,'canonical_reverse':undo(seq,out)==INIT,'order_sensitivity':run(sw)!=out,'deterministic':out==run(seq)}
 outputs=set();fails=0;start=time.perf_counter()
 for i in range(5000):
  p=list(seq);rng.shuffle(p);p=tuple(p);x=run(p);outputs.add(x)
  if undo(p,x)!=INIT:fails+=1
 checks['reversible_5000']=fails==0;checks['unique_outputs_5000']=len(outputs)==5000
 checks['edge_reversible']=undo(seq,run(seq,(MASK,)*10))==(MASK,)*10
 checks['each_instruction_reversible']=all(step(step((MASK,)*10,k),k,True)==(MASK,)*10 for k in seq)
 checks['all_samples_noncanonical']=out not in outputs
 return {'schema':'oasis/8-vector-2-worker-bees/v01','checks':checks,'passed':sum(checks.values()),'total':len(checks),'sampled_permutations':5000,'unique_outputs':len(outputs),'reverse_failures':fails,'seconds':time.perf_counter()-start,'24_factorial':str(math.factorial(24)),'scope':'modular finite-state simulated scheduler, not physics; full 24! not enumerated'}
if __name__=='__main__':
 r=benchmark();print(json.dumps(r,indent=2));assert r['passed']==r['total']
