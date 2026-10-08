#!/usr/bin/env python3
"""SHEET50 schedule-period audit: no historical years used. Requires unmodified SHEET45 v01 beside this file."""
import math,json,hashlib,time
from sheet45_exitron_v01 import START,travel,CIPHER,NODES
P=math.lcm(360,8,13,11)
def signature(t):
 out=[]
 for n in NODES:
  for p in range(2):
   for h in range(2):
    lane=(n+3*p+5*h+t)%8
    gate=int(CIPHER[(t+n+p+h)%13]=='|')
    cross=int((t+n+p+h)%11==0 and gate==1)
    out.append((lane,(lane+1+n)%8,gate,cross,n*17+p*7+h*3+t%360+1))
 return tuple(out)
def run():
 start=time.perf_counter()
 divisors=[d for d in range(1,P) if P%d==0]
 smaller=[d for d in divisors if signature(0)==signature(d) and all(signature(i)==signature(i+d) for i in range(P))]
 state=START;seen={state};turns=[];crossings=0;collision=None
 for t in range(P):
  state,c=travel(state,t);crossings+=len(c)
  if collision is None and state in seen:collision=t+1
  seen.add(state)
  if (t+1)%360==0:turns.append(state)
 last=state
 for t in range(P-1,-1,-1):state,_=travel(state,t,True)
 checks={'lcm_51480':P==51480,'143_turns':len(turns)==143,
 'operator_wrap':all(signature(t)==signature(t+P) for t in (0,1,7,12,359,360,P-1)),
 'no_smaller_operator_period':not smaller,'inverse_exact':state==START,
 'crossings_recorded':crossings>0,'state_not_returned':last!=START,
 'no_state_repeat_in_window':collision is None,
 '8_vector_2_workers':len(last)==10,
 'cipher_unchanged':CIPHER=='..||..|....|.',
 'all_32_bit':all(0<=w<2**32 for w in last),
 '143_unique_turn_states':len(set(turns))==143}
 result={'schema':'oasis/sheet50/period-v01','ticks':P,'turns':143,
 'updates':P*20,'crossings':crossings,'unique_states':len(seen),
 'proper_periods':smaller,'first_state_collision':collision,
 'returns_initial':last==START,'reverse_exact':state==START,
 'digest':hashlib.sha256(str(last).encode()).hexdigest(),
 'checks':checks,'passed':sum(checks.values()),'total':len(checks),
 'seconds':round(time.perf_counter()-start,3)}
 return result
if __name__=='__main__':
 r=run();print(json.dumps(r,indent=2));assert r['passed']==r['total']
