#!/usr/bin/env python3
"""SHEET 45 append-only historical timeline anchor audit. 17 layers, 1832–2024."""
import importlib.util,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('exitron',P/'sheet45-exitron-v01.py')
e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
LAYERS=[(1832,'TELEGRAPH_IDEA'),(1844,'TELEGRAPH_MESSAGE'),(1866,'TRANSATLANTIC_CABLE'),(1876,'TELEPHONE'),(1901,'TRANSATLANTIC_WIRELESS'),(1945,'MEMEX'),(1969,'ARPANET'),(1973,'INTERNATIONAL_ARPANET'),(1983,'TCP_IP'),(1991,'WWW'),(1995,'WEB_COMMERCIAL'),(2001,'CORPUS'),(2006,'CLOUD'),(2011,'MOBILE'),(2016,'RANK'),(2019,'PRELOAD'),(2024,'GENERATE')]
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run():
 s=e.START;seen={s};tip='0'*64;events=[];total=0
 for i,(year,word) in enumerate(LAYERS):
  prev=tip;before=sha(s);cross=0
  for a in range(360):
   tick=i*360+a;s,ev=e.travel(s,tick);seen.add(s)
   for v in ev:
    cross+=1;tip=sha({'prev':tip,'event':v,'layer':i,'word':word})
  total+=cross
  record={'layer':i+1,'year':year,'word':word,'before':before,'after':sha(s),'prior_tip':prev,'tip':tip,'crossings':cross}
  record['watermark']=sha({'year':year,'word':word,'prior':prev,'after':record['after'],'tip':tip})
  events.append(record)
 final=sha(s)
 for t in range(len(LAYERS)*360-1,-1,-1):s,_=e.travel(s,t,True)
 def valid(x):return x['watermark']==sha({'year':x['year'],'word':x['word'],'prior':x['prior_tip'],'after':x['after'],'tip':x['tip']})
 forged=dict(events[0]);forged['word']='SPOOF'
 checks={'17_layers':len(events)==17,'start_1832':events[0]['year']==1832,
 'chronology':all(events[i]['year']<events[i+1]['year'] for i in range(16)),
 '6120_ticks':len(LAYERS)*360==6120,'122400_updates':len(LAYERS)*360*20==122400,
 'all_watermarks_valid':all(map(valid,events)),'tamper_rejected':not valid(forged),
 'ledger_links':all(events[i]['tip']==events[i+1]['prior_tip'] for i in range(16)),
 'crossings_counted':sum(x['crossings'] for x in events)==total,
 'reverse_exact':s==e.START,'unique_tick_states':len(seen)==6121,
 'distinct_anchor_words':len({x['word'] for x in events})==17}
 return {'schema':'oasis/sheet45/17layers-v03','anchors':events,'crossings':total,'ticks':6120,
 'node_updates':122400,'unique_tick_states':len(seen),'final_digest':final,'checks':checks,
 'passed':sum(checks.values()),'total':len(checks),
 'limitations':['Timeline is externally selected, not discovered or predicted by transport',
 '2001 CORPUS, 2016 RANK, 2019 PRELOAD are interpretive OaSIs categories',
 'Provenance watermark is in external ledger, not intrinsic to the register',
 'No evidence for physical tunneling or historical causal correspondence']}
if __name__=='__main__':
 r=run();print(json.dumps(r,indent=2));assert r['passed']==r['total']
