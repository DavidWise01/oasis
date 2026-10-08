#!/usr/bin/env python3
"""SHEET 42 symbolic transport. Append-only module; frozen baseline unchanged."""
import math,hashlib,json
MASK=(1<<32)-1
CIPHER="..||..|....|."
SHEETS=((1,-2,3),(1,2,-3),(-1,1,0),(2,1,-1))
START=(0,)*10
def digest(v): return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def carriers(node,phase):
 t=((node*13+phase*7)%112)/112
 return round(1000*math.sin(6*math.pi*t)),(1 if int(8*t)%2==0 else -1),(1 if phase%2==0 else -1)
def step(state,node,phase=0,inverse=False):
 v=list(state);sheet=(node+phase)%4;a,b,c=SHEETS[sheet]
 sine,square,orb=carriers(node,phase);i=node%8;j=(i+3+sheet)%8
 if i==j:j=(j+1)%8
 def proton(s):v[8]=(v[8]+s*(v[i]*a+sine+node+1))&MASK
 def neutron(s):v[9]=(v[9]+s*(v[8]*b+square*17+v[j]))&MASK
 def electron(s):v[i]=(v[i]+s*(v[9]*c+orb*23+v[j]+1))&MASK
 if inverse:electron(-1);neutron(-1);proton(-1)
 else:proton(1);neutron(1);electron(1)
 return tuple(v)
def walk(order=tuple(range(28)),phase=0):
 v=START;ledger=[]
 for idx,node in enumerate(order):
  before=digest(v);v=step(v,node,phase)
  sine,square,orb=carriers(node,phase)
  ledger.append(dict(index=idx,node=node,sheet=(node+phase)%4,sine=sine,square=square,orbital=orb,before=before,after=digest(v)))
 return v,ledger
def reverse(state,order=tuple(range(28)),phase=0):
 for node in reversed(order):state=step(state,node,phase,True)
 return state
def benchmark():
 order=tuple(range(28));out,ledger=walk();variants=[walk(phase=i)[0] for i in range(16)]
 checks={
 '13_cipher':len(CIPHER)==13 and CIPHER.count('.')==9 and CIPHER.count('|')==4,
 '4_sheets':len(SHEETS)==4,
 '28_nodes':len(ledger)==28,
 '8_plus_2':len(out)==10,
 '32bit_bounds':all(0<=x<=MASK for x in out),
 'all_sheets':set(x['sheet'] for x in ledger)==set(range(4)),
 'reverse':reverse(out,order)==START,
 'order_sensitive':walk(tuple(reversed(order)))[0]!=out,
 '16_phase_reverse':all(reverse(v,order,i)==START for i,v in enumerate(variants)),
 '16_phase_distinct':len(set(variants))==16,
 'append_only_indices':all(x['index']==i for i,x in enumerate(ledger)),
 'hash_chain':all(ledger[i]['after']==ledger[i+1]['before'] for i in range(27)),
 'repeatable':walk()[0]==out,
 'complete_ledger':len(ledger)==28}
 return {'name':'SHEET 42','passed':sum(checks.values()),'total':len(checks),'checks':checks,'state_sha256':digest(out)},ledger
if __name__=='__main__':
 result,ledger=benchmark()
 print(json.dumps(result,indent=2))
 assert result['passed']==result['total']
