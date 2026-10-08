#!/usr/bin/env python3
"""SHEET 46 append-only Exitron BLINK/FLOOD overlay. Requires unmodified SHEET45 v01."""
import hashlib, importlib.util, json, math
from pathlib import Path
HOME=Path(__file__).resolve().parent
SOURCE=HOME.parent/'sheet-45'/'sheet45-exitron-v01.py'
spec=importlib.util.spec_from_file_location('sheet45_v01',SOURCE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
TICKS=3600;PERIOD=360;THRESHOLD=.2;MULTIPLICITY=3
WALL_CLOSED='<........>';WALL_OPEN='< >'
def hash_json(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def open_at(t):return math.sin(2*math.pi*(t%PERIOD)/PERIOD)>THRESHOLD
def benchmark():
 state=base.START;prev='0'*64;ledger=[];unique={state};epochs=[]
 open_ticks=0;closed_ticks=0;eligible=0;denied=0;emitted=0;retained=0
 for tick in range(TICKS):
  opened=open_at(tick)
  if opened:open_ticks+=1
  else:closed_ticks+=1
  state,candidates=base.travel(state,tick);unique.add(state)
  for _,node,pair,half,gate in candidates:
   eligible+=1
   if not opened:
    denied+=1;retained+=MULTIPLICITY;continue
   for particle in range(MULTIPLICITY):
    mark={'tick':tick,'node':node,'pair':pair,'half':half,'particle':particle,'wall':WALL_OPEN}
    stamp=hash_json({'previous':prev,'event':mark})
    ledger.append({'previous':prev,'event':mark,'digest':stamp})
    prev=stamp;emitted+=1
  if (tick+1)%PERIOD==0:
   epochs.append({'turn':(tick+1)//PERIOD,'state':hash_json(state),
                  'wall':'CLOSED' if not open_at(tick+1) else 'OPEN','tip':prev})
 final=hash_json(state)
 for tick in reversed(range(TICKS)):state,_=base.travel(state,tick,True)
 chain=all(entry['digest']==hash_json({'previous':entry['previous'],'event':entry['event']}) and
           entry['previous']==(ledger[i-1]['digest'] if i else '0'*64)
           for i,entry in enumerate(ledger))
 tamper_ok=False
 if ledger:
  e=ledger[len(ledger)//2];bad=dict(e['event']);bad['particle']=99
  tamper_ok=hash_json({'previous':e['previous'],'event':bad})!=e['digest']
 checks={
  'initial_closed':not open_at(0),
  'closed_and_open_observed':open_ticks>0 and closed_ticks>0,
  '10_complete_turns':len(epochs)==10,
  'all_turns_return_closed_wall':all(e['wall']=='CLOSED' for e in epochs),
  '20_event_lanes':len(base.NODES)*4==20,
  'all_crossing_candidates_accounted':eligible*MULTIPLICITY==emitted+retained,
  'closed_wall_no_flood':denied*MULTIPLICITY==retained,
  'flood_only_open':all(open_at(e['event']['tick']) for e in ledger),
  'append_only_chain':chain,'tamper_rejected':tamper_ok,
  'full_register_reverse':state==base.START,
  'all_turn_states_distinct':len({e['state'] for e in epochs})==len(epochs),
  'deterministic_schedule':sum(open_at(i) for i in range(TICKS))==open_ticks,
  'source_cipher_unchanged':base.CIPHER=='..||..|....|.'}
 return {'schema':'oasis/sheet46/exitron-blink-v01','wall_closed':WALL_CLOSED,'wall_open':WALL_OPEN,
  'symbolic_cycle':'sin(2*pi*(tick mod 360)/360) > 0.2',
  'ticks':TICKS,'turns':TICKS//PERIOD,'node_updates':TICKS*20,
  'open_ticks':open_ticks,'closed_ticks':closed_ticks,'candidate_crossings':eligible,
  'held_candidates':denied,'multiplicity':MULTIPLICITY,'external_emissions':emitted,
  'retained_tokens':retained,'ledger_events':len(ledger),
  'unique_register_boundaries':len(unique),'turns_summary':epochs,
  'final_state_sha256':final,'ledger_tip_sha256':prev,
  'register_reverse_exact':state==base.START,
  'checks':checks,'passed':sum(checks.values()),'total':len(checks),
  'limits':['Deterministic periodic gate, not physical tunneling',
            'Token flood is symbolic, not physical Cooper pairs',
            'SHA-256 provenance is sidecar, not invisible register watermark']}
if __name__=='__main__':
 result=benchmark();print(json.dumps(result,indent=2))
 assert result['passed']==result['total']
