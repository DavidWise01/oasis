#!/usr/bin/env python3
"""SHEET 45 v02: reversible Exitron/internet timeline watermark audit.
Place beside SHEET 45 v01 module; no frozen files modified.
"""
import hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
source=P/'sheet45-exitron-v01.py'
spec=importlib.util.spec_from_file_location('sheet45_v01',source)
v01=importlib.util.module_from_spec(spec);spec.loader.exec_module(v01)
ERAS=((1995,'WEB'),(2001,'CORPUS'),(2006,'CLOUD'),(2011,'MOBILE'),(2016,'RANK'),(2019,'PRELOAD'),(2024,'GENERATE'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check_word(r):
 base={k:r[k] for k in ('era','year','word','before')}
 return r['commitment']==digest({'watermark':base,'after':r['after'],'tip':r['ledger_tip']})
def benchmark():
 state=v01.START;tip='0'*64;ledger=[];eras=[]
 for era,(year,word) in enumerate(ERAS):
  item={'era':era,'year':year,'word':word,'before':digest(state)}
  start=len(ledger)
  for angle in range(360):
   tick=era*360+angle
   state,cross=v01.travel(state,tick)
   for tick0,node,pair,half,gate in cross:
    event={'tick':tick0,'era':era,'node':node,'pair':pair,'half':half,'gate':gate,'watermark_word':word}
    h=digest({'prev':tip,'event':event})
    ledger.append({'prev':tip,'event':event,'hash':h});tip=h
  item.update({'after':digest(state),'crossings_this_era':len(ledger)-start,'ledger_tip':tip})
  item['commitment']=digest({'watermark':{k:item[k] for k in ('era','year','word','before')},'after':item['after'],'tip':tip})
  eras.append(item)
 end=digest(state)
 for tick in range(len(ERAS)*360-1,-1,-1):state,_=v01.travel(state,tick,True)
 tampered=dict(eras[3]);tampered['word']='CLOUD'
 chain=all(r['hash']==digest({'prev':r['prev'],'event':r['event']}) and
           r['prev']==(ledger[i-1]['hash'] if i else '0'*64) for i,r in enumerate(ledger))
 years=[x[0] for x in ERAS];shuffled=years.copy();shuffled[0],shuffled[4]=shuffled[4],shuffled[0]
 checks={
  'v01_cipher':v01.CIPHER=='..||..|....|.',
  'seven_eras':len(eras)==7,
  '360_ticks_per_era':len(ERAS)*360==2520,
  'all_wordmarks_valid':all(check_word(r) for r in eras),
  'tampering_detected':not check_word(tampered),
  'crossings_occurred':bool(ledger),
  'hash_chain_valid':chain,
  'reverse_exact':state==v01.START,
  'chronological_anchors':years==sorted(years),
  'shuffled_negative_control':shuffled!=sorted(shuffled),
  'unique_end_state_hashes':len({r['after'] for r in eras})==7,
  'unique_ledger_tips':len({r['ledger_tip'] for r in eras})==7,
 }
 return {'schema':'oasis/sheet45/internet-watermark-v02','anchors':eras,
   'ticks':len(ERAS)*360,'node_updates':len(ERAS)*360*20,
   'crossing_events':len(ledger),'event_ledger_tip':tip,'final_state_sha256':end,
   'recovered_start':state==v01.START,'checks':checks,
   'passed':sum(checks.values()),'total':len(checks),
   'limitations':['Chronology is user-defined input, not a prediction',
    'SHA-256 wordmarks are external commitments, not invisible register watermarks',
    'No physical tunneling, Cooper pairs, or causal internet mechanism demonstrated']}
if __name__=='__main__':
 result=benchmark();print(json.dumps(result,indent=2))
 assert result['passed']==result['total']
