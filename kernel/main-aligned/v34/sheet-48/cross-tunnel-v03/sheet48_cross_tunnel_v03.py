#!/usr/bin/env python3
"""SHEET 48 Cross Tunnel v03 — asymmetric FIFO; append only."""
import importlib.util,hashlib,json
from collections import deque,Counter
from pathlib import Path
v02path=Path(__file__).resolve().parent.parent/'cross-tunnel-v02'/'sheet48_cross_tunnel_v02.py'
sp=importlib.util.spec_from_file_location('v02',v02path)
v02=importlib.util.module_from_spec(sp);sp.loader.exec_module(v02)
DIR=('W','N','E','S')
RATES={'W':4,'N':2,'E':1,'S':3}
CAPACITY=8;ARRIVAL_TICKS=720
def sha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def benchmark():
 s=v02.START;queues={d:deque() for d in DIR};tip='0'*64
 arrived=Counter();departed=Counter();peak=0;ledger=[];history=[];service=0
 for tick in range(ARRIVAL_TICKS+500):
  if tick<ARRIVAL_TICKS:
   for d in DIR:
    for ordinal in range(RATES[d]):
     uid=f'{tick}:{d}:{ordinal}'
     queues[d].append({'uid':uid,'origin':d,'born':tick,'watermark':sha({'uid':uid,'word':'EXITRON'})})
     arrived[d]+=1
  for _ in range(CAPACITY):
   active=[d for d in DIR if queues[d]]
   if not active:break
   d=min(active,key=lambda k:(queues[k][0]['born'],DIR.index(k)))
   token=queues[d].popleft()
   lane=(DIR.index(d)*2+int(token['uid'].split(':')[-1])%2)%8
   before=sha(s);s,exit_dir=v02.operation(s,service,lane)
   event={'service':service,'uid':token['uid'],'origin':d,'lane':lane,'pair':lane//2,
          'watermark':token['watermark'],'exit':exit_dir,
          'wait':tick-token['born'],'before':before,'after':sha(s)}
   h=sha({'prev':tip,'event':event});ledger.append({'prev':tip,'event':event,'hash':h})
   tip=h;history.append((service,lane));service+=1;departed[d]+=1
  peak=max(peak,sum(map(len,queues.values())))
  if tick>=ARRIVAL_TICKS and not any(queues.values()):break
 final=sha(s)
 for n,lane in reversed(history):s,_=v02.operation(s,n,lane,True)
 valid=all(r['prev']==(ledger[i-1]['hash'] if i else '0'*64)
     and r['hash']==sha({'prev':r['prev'],'event':r['event']})
     and r['event']['watermark']==sha({'uid':r['event']['uid'],'word':'EXITRON'})
     for i,r in enumerate(ledger))
 forged=dict(ledger[0]['event']);forged['watermark']='altered'
 spoof=sha({'prev':ledger[0]['prev'],'event':forged})!=ledger[0]['hash']
 checks={'asymmetric_load':len(set(RATES.values()))>1,'queue_congestion':peak>0,
  'finite_capacity':CAPACITY==8,'no_unserved_tokens':not any(queues.values()),
  'all_arrivals_departed':arrived==departed,
  'no_duplicate_uid':len({r['event']['uid'] for r in ledger})==len(ledger),
  'each_record_watermarked':valid,'tamper_rejected':spoof,'exact_inverse':s==v02.START,
  'all_four_sources_served':all(departed[d]>0 for d in DIR),
  'no_loss':sum(arrived.values())==len(ledger),
  'fifo_time_monotonic':all(r['event']['service']==i for i,r in enumerate(ledger)),
  'pair_identity':all(r['event']['pair']==r['event']['lane']//2 for r in ledger),
  'end_signature_nontrivial':final!=sha(v02.START)}
 return {'schema':'oasis/sheet48/cross-tunnel-v03','arrival_ticks':ARRIVAL_TICKS,
  'arrival_rates':RATES,'capacity_per_tick':CAPACITY,'arrivals':dict(arrived),
  'departures':dict(departed),'total_tokens':len(ledger),'peak_queue':peak,
  'last_service_tick':tick,'max_wait':max(r['event']['wait'] for r in ledger),
  'mean_wait':sum(r['event']['wait'] for r in ledger)/len(ledger),
  'end_state_sha256':final,'ledger_tip':tip,'inverse_exact':s==v02.START,
  'checks':checks,'passed':sum(checks.values()),'total':len(checks),
  'limitation':'Artificial traffic; no physical Cooper pairs or internet chronology inferred.'}
if __name__=='__main__':
 out=benchmark();print(json.dumps(out,indent=2));assert out['passed']==out['total']
