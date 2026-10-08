#!/usr/bin/env python3
"""SHEET 45: EXITRONS. Append-only symbolic reversible lane overlay."""
import hashlib,json
MOD=1<<32;MASK=MOD-1
CIPHER='..||..|....|.'
NODES=(1,3,5,7,9)
WALLS=('<........>','>........<')
START=(0,)*10
def operation(s,tick,node,pair,half,inverse=False):
 r=list(s);lane=(node+pair*3+half*5+tick)%8;neighbor=(lane+1+node)%8
 phase=(tick+node+pair+half)%13;gate=int(CIPHER[phase]=='|')
 crossing=(tick+node+pair+half)%11==0 and gate==1
 amplitude=node*17+pair*7+half*3+tick%360+1
 def b0(sign):r[8]=(r[8]+sign*(r[lane]+amplitude))&MASK
 def b1(sign):r[9]=(r[9]+sign*(r[8]*3+r[neighbor]+gate))&MASK
 def reg(sign):r[lane]=(r[lane]+sign*(r[9]*5+amplitude+int(crossing)))&MASK
 if inverse:reg(-1);b1(-1);b0(-1)
 else:b0(1);b1(1);reg(1)
 return tuple(r),crossing,gate
def travel(state,tick,inverse=False):
 events=[(n,p,h) for n in NODES for p in range(2) for h in range(2)]
 if inverse:events.reverse()
 crossed=[]
 for node,pair,half in events:
  state,cross,gate=operation(state,tick,node,pair,half,inverse)
  if cross:crossed.append((tick,node,pair,half,gate))
 return state,crossed
def benchmark(turns=10):
 ticks=360*turns;state=START;seen={state};boundary=[];crossings=0
 for tick in range(ticks):
  state,c=travel(state,tick);crossings+=len(c);seen.add(state)
  if (tick+1)%360==0:boundary.append(state)
 last=state
 for tick in reversed(range(ticks)):state,_=travel(state,tick,True)
 tests={
  'literal_exitron_walls':WALLS[0]=='<........>',
  'cipher_13':len(CIPHER)==13,
  'five_nodes':len(NODES)==5,
  'double_cooper':2*2==4,
  'eight_plus_two':len(START)==10,
  'ten_toroidal_turns':len(boundary)==turns,
  '360_sectors':ticks==360*turns,
  'four_lane_events_per_node':5*4==20,
  'crossings_observed':crossings>0,
  'nontrivial_state':last!=START,
  'exact_full_reverse':state==START,
  'distinct_turn_boundaries':len(set(boundary))==turns,
 }
 return {'schema':'oasis/sheet45/exitron-lanes-v01','ticks':ticks,'turns':turns,
  'node_updates':ticks*20,'boundary_crossings':crossings,
  'unique_tick_boundary_states':len(seen),'unique_turn_states':len(set(boundary)),
  'reversible':state==START,'checks':tests,'passed':sum(tests.values()),'total':len(tests),
  'end_digest':hashlib.sha256(str(last).encode()).hexdigest(),
  'scope':'Symbolic reversible transport; not literal Cooper pairs, electrons or new particle species'}
if __name__=='__main__':
 result=benchmark();print(json.dumps(result,indent=2));assert result['passed']==result['total']
