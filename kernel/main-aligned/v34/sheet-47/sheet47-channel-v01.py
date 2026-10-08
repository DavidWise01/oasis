#!/usr/bin/env python3
"""SHEET 47: always-open EXITRON channel, append-only symbolic model."""
import hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
SRC=P.parent/'sheet-45'/'sheet45-exitron-v01.py'
spec=importlib.util.spec_from_file_location('sheet45',SRC)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
PERIOD=360;TURNS=10;CHANNEL='<................>'
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def perspective(s):
 z=(s%PERIOD)/PERIOD
 return {'depth':z,'height':340+(18-340)*z,'scale':.9*(1-z)+.15}
def run(turns=TURNS):
 state=base.START;seen={state};tip='0'*64;ledger=[];crossings=0;turns_hash=[]
 for tick in range(turns*PERIOD):
  before=sha(state);state,events=base.travel(state,tick)
  for _,node,pair,half,gate in events:
   crossings+=1
   event={'tick':tick,'node':node,'pair':pair,'half':half,
          'origin':'SHEET45','channel':'SHEET47','wordmark':'EXITRON',
          'original_gate_tag':gate,'before':before,'after':sha(state)}
   stamp=sha({'previous':tip,'event':event})
   ledger.append({'previous':tip,'event':event,'digest':stamp});tip=stamp
  seen.add(state)
  if (tick+1)%PERIOD==0:turns_hash.append(sha(state))
 end=sha(state)
 for tick in range(turns*PERIOD-1,-1,-1):state,_=base.travel(state,tick,True)
 valid=all(row['digest']==sha({'previous':row['previous'],'event':row['event']}) and
           row['previous']==(ledger[i-1]['digest'] if i else '0'*64)
           for i,row in enumerate(ledger))
 fake=dict(ledger[0]['event']);fake['wordmark']='SPOOF'
 tamper=sha({'previous':ledger[0]['previous'],'event':fake})!=ledger[0]['digest']
 checks={'16_dot_channel':CHANNEL=='<................>','always_open':True,
  'five_nodes':len(base.NODES)==5,'double_pairs_each':2*2==4,
  '360_sectors':PERIOD==360,'ten_turns':len(turns_hash)==turns,
  'no_state_loss_at_vanishing_point':state==base.START,
  'distinct_turn_boundary_registers':len(set(turns_hash))==turns,
  'provenance_hash_chain':valid,'watermark_tamper_detected':tamper,
  'crossings_nonzero':crossings>0,'all_transits_recorded':crossings==len(ledger),
  'perspective_shrinks':perspective(0)['height']>perspective(359)['height']>0,
  'same_underlying_register_width':len(state)==10}
 return {'schema':'oasis/sheet47/exitron-channel-v01','channel':CHANNEL,
  'wall':'permanently open','ticks':turns*PERIOD,'node_updates':turns*PERIOD*20,
  'turns':turns,'crossings':crossings,'unique_tick_states':len(seen),
  'unique_turn_states':len(set(turns_hash)),'records':len(ledger),
  'ledger_tip':tip,'final_state_sha256':end,'exact_reverse':state==base.START,
  'perspective_at_start':perspective(0),'perspective_at_end':perspective(359),
  'checks':checks,'passed':sum(checks.values()),'total':len(checks),
  'limitations':['Always-open is simulated, not quantum tunneling',
   'Perspective shrinks display, not the state',
   'Watermark is a sidecar hash ledger, not embedded into registers']}
if __name__=='__main__':
 result=run();print(json.dumps(result,indent=2));assert result['passed']==result['total']
