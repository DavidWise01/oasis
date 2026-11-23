#!/usr/bin/env python3
"""AETHER-120 integration of unchanged 118 risk verifier; synthetic only."""
import csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'118'/'experiment.py'
if not SRC.exists(): SRC=ROOT.parent.parent/'aether118'/'experiment.py'
sp=importlib.util.spec_from_file_location('frozen118',SRC)
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
PIN=hashlib.sha256(SRC.read_bytes()).hexdigest()
SC=('clean','late','tampered','rollback','outage_recovery','mixed')
SEEDS=range(120001,120041);T=M.T;N=M.N
def simulate(seed,sc):
 rng=np.random.default_rng(seed+1007*SC.index(sc))
 truth=np.full(T,.003);truth[13:20]=.085
 packets=[]
 for t in range(T):
  p=M.sign(dict(source='risk-audit',seq=t,observed_t=t,counter=t,epoch=1,valid_until=t+1,independent=True,n=N,errors=int(rng.binomial(N,truth[t]))))
  q=dict(p);arrival=t
  if sc=='late' and t%5==0:arrival=t+2
  if sc=='tampered' and t%4==0:q['errors']=0
  if sc=='rollback' and t in (10,11,12,20,21):
   b={k:v for k,v in q.items() if k!='mac'};b['counter']=t-2;q=M.sign(b)
  if sc=='outage_recovery' and 10<=t<=19:continue
  if sc=='mixed':
   if 9<=t<=14:continue
   if t%7==2:q['errors']=0
   if t%7==3:arrival=t+2
  if arrival<T:packets.append((arrival,q))
 return truth,packets
def eligible(t,delivery):
 for arrival,p in delivery:
  if arrival!=t:continue
  if (M.verify(p) and p.get('source')=='risk-audit' and p.get('independent') is True and p.get('n')==N and p.get('epoch')==1 and p.get('seq')==t and p.get('observed_t')==t and p.get('counter')==t and p.get('valid_until')==t+1 and M.bound(p['errors'])<=M.LIMIT):return True
 return False
def write(name,data):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def main():
 audit=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   truth,delivery=simulate(seed,sc)
   M.episode=lambda _s,_c:(truth,delivery)
   rows=M.evaluate(seed,sc,'strict');replay=M.evaluate(seed,sc,'strict')
   acts={r['tick'] for r in rows if r['action']=='ACT'}
   eligible_ticks={t for t in range(T) if eligible(t,delivery)}
   tests=dict(deterministic_replay=rows==replay,integrity_chain=M.verify_chain(rows),
     unique_action_per_tick=len(rows)==T and [r['tick'] for r in rows]==list(range(T)),
     no_stale_packet_act=all(r['packet_seq']==r['tick'] for r in rows if r['action']=='ACT'),
     matched_oracle_contract=acts==eligible_ticks,
     no_unsafe_act=all(r['unsafe']==0 for r in rows),
     budget_bounded=all(0<=r['receipts']<=T and r['cost']>=0 for r in rows),
     recovery_on_first_eligible=all(t in acts for t in eligible_ticks if t>=20))
   checks.extend(dict(scenario=sc,seed=seed,check=k,pass_=int(v)) for k,v in tests.items())
   audit.append(dict(scenario=sc,seed=seed,decisions=len(rows),act=len(acts),hold=T-len(acts),
     unsafe=sum(r['unsafe'] for r in rows),packets=len(delivery),
     trace_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
     first_safe_post_hazard=min((t for t in eligible_ticks if t>=20),default=-1)))
   if seed==SEEDS.start:traces.extend(rows)
 write('integration_cases.csv',audit);write('checks.csv',checks);write('trace_samples.csv',traces)
 inv=[]
 for b in ('113','114','115','116','117','117b','118','119'):
  p=ROOT.parent/b/'experiment.py'
  if not p.exists(): p=ROOT.parent.parent/('aether'+b)/'experiment.py'
  if p.exists():inv.append(dict(bound=b,file='experiment.py',bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),present=1))
 write('inventory.csv',inv)
 ok=len(checks)==1920 and all(r['pass_'] for r in checks) and len(inv)==8 and PIN==hashlib.sha256(SRC.read_bytes()).hexdigest()
 manifest=dict(bound='AETHER-120',phase='V',status='PASS' if ok else 'FAIL',cases=len(audit),
    checks=len(checks),passed=sum(r['pass_'] for r in checks),decisions=sum(r['decisions'] for r in audit),
    unsafe=sum(r['unsafe'] for r in audit),act=sum(r['act'] for r in audit),hold=sum(r['hold'] for r in audit),
    archive_entries=len(inv),frozen_source_sha256=PIN,scenarios=list(SC),seeds=[SEEDS.start,SEEDS.stop-1],
    limits=['synthetic only','trusted signer and authentic provenance assumed','protected counters and independence not independently proven','older bounds inventoried by presence and hashes, not rerun'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2))
 if not ok:raise SystemExit(2)
if __name__=='__main__':main()
