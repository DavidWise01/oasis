#!/usr/bin/env python3
"""SHEET 53 finite center buffer benchmark; append-only successor to SHEET52."""
from collections import deque
import hashlib,json
TICKS=720;ARRIVALS=12;SERVICE=2;BUF=64;QUAR=128;MOD=2**32
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def op(s,k,l,inverse=False):
 x=list(s);i=l%8;j=(i+3)%8;a=k*7+l*13+1
 def f(t):x[8]=(x[8]+t*(x[i]+a))%MOD
 def g(t):x[9]=(x[9]+t*(x[8]+x[j]))%MOD
 def h(t):x[i]=(x[i]+t*(x[9]+a))%MOD
 if inverse:h(-1);g(-1);f(-1)
 else:f(1);g(1);h(1)
 return tuple(x)
def run(mode):
 center=deque();quarantine=deque();source=deque();state=(0,)*10
 seen=set();history=[];ledger=[];tip='0'*64;peakcenter=peakquar=peaksource=0
 spills=blocked=released=0;waits=[]
 for t in range(10000):
  if t<TICKS:
   for n in range(ARRIVALS):
    uid=f'{t}:{n}';source.append((t,uid,sha({'uid':uid,'word':'EXITRON'})))
  while quarantine and len(center)<BUF:center.append(quarantine.popleft());released+=1
  if mode=='baseline':
   while source:center.append(source.popleft())
  elif mode=='quarantine':
   for _ in range(min(ARRIVALS,len(source))):
    if len(center)<BUF:center.append(source.popleft())
    elif len(quarantine)<QUAR:quarantine.append(source.popleft());spills+=1
    else:blocked+=1;break
  else:
   while source and len(center)<BUF:center.append(source.popleft())
   if source:blocked+=len(source)
  for _ in range(min(SERVICE,len(center))):
   born,uid,mark=center.popleft();seq=len(history);lane=seq%8
   state=op(state,seq,lane);history.append((seq,lane));seen.add(uid);waits.append(t-born)
   event={'uid':uid,'mark':mark,'seq':seq,'lane':lane,'wait':t-born}
   h=sha({'prev':tip,'event':event});ledger.append((tip,event,h));tip=h
  peakcenter=max(peakcenter,len(center));peakquar=max(peakquar,len(quarantine));peaksource=max(peaksource,len(source))
  if t>=TICKS-1 and not center and not quarantine and not source:break
 final=sha(state)
 for seq,lane in reversed(history):state=op(state,seq,lane,True)
 valid=all(rec[0]==(ledger[i-1][2] if i else '0'*64) and rec[2]==sha({'prev':rec[0],'event':rec[1]}) and rec[1]['mark']==sha({'uid':rec[1]['uid'],'word':'EXITRON'}) for i,rec in enumerate(ledger))
 fake=dict(ledger[0][1]);fake['mark']='FORGED'
 return dict(mode=mode,arrivals=TICKS*ARRIVALS,delivered=len(history),unique=len(seen),pending=len(center)+len(quarantine)+len(source),peak_center=peakcenter,peak_quarantine=peakquar,peak_source=peaksource,spill_count=spills,blocked=blocked,released=released,finish_tick=t,max_wait=max(waits),mean_wait=sum(waits)/len(waits),reverse_exact=state==(0,)*10,ledger_valid=valid,tamper_rejected=sha({'prev':ledger[0][0],'event':fake})!=ledger[0][2],end_hash=final,ledger_tip=tip)
def test():
 a=run('baseline');b=run('quarantine');c=run('backpressure');rs=[a,b,c]
 checks={
 'arrivals':all(r['arrivals']==8640 for r in rs),
 'delivered':all(r['delivered']==8640 for r in rs),
 'unique':all(r['unique']==8640 for r in rs),
 'empty_final':all(r['pending']==0 for r in rs),
 'finite_center':b['peak_center']<=BUF and c['peak_center']<=BUF,
 'finite_quarantine':b['peak_quarantine']<=QUAR,
 'quarantine_fills':b['spill_count']>0,
 'backpressure':c['blocked']>0,
 'quarantine_releases':b['released']>0,
 'same_state':len({r['end_hash'] for r in rs})==1,
 'same_provenance':len({r['ledger_tip'] for r in rs})==1,
 'reverse_exact':all(r['reverse_exact'] for r in rs),
 'watermark_integrity':all(r['ledger_valid'] for r in rs),
 'tamper_rejected':all(r['tamper_rejected'] for r in rs)}
 return dict(schema='oasis/sheet53/finite-buffer-v01',lineage='SHEET52 -> SHEET53',baseline=a,quarantine=b,backpressure=c,checks=checks,passed=sum(checks.values()),total=len(checks),limitation='Upstream source queue remains unbounded; this is not end-to-end bounded memory.')
if __name__=='__main__':
 out=test();print(json.dumps(out,indent=2));assert out['passed']==out['total']
