#!/usr/bin/env python3
"""AETHER-132 — standalone deterministic synthetic regularity acceptance test.
This repository implementation reproduces the specified experiment but was
authored separately from the local accepted executable. No real hardware.
"""
from pathlib import Path
import csv,hashlib,hmac,json,math
D=Path(__file__).resolve().parent
SC=('clean','smooth_curvature','localized_notch','step_discontinuity','gain_shift','dropout','expired_certificate','valid_rotation')
SEEDS=range(132001,132051);T=24;XS=[round(i/10,1) for i in range(51)]
K=b'AETHER132-SYNTHETIC-REFERENCE-KEY';LIM=.025
def raw(a):return json.dumps(a,sort_keys=True,separators=(',',':')).encode()
def sign(a):return dict(a,signature=hmac.new(K,raw(a),hashlib.sha256).hexdigest())
def verify(a):return hmac.compare_digest(a.get('signature',''),sign({k:v for k,v in a.items() if k!='signature'})['signature'])
def truth(sc,t):return .03 if sc in ('localized_notch','step_discontinuity','gain_shift','dropout') and 8<=t<18 else .004
def sensor(sc,t,x):
 if sc=='smooth_curvature':return x+.012*math.sin(math.pi*x/5)
 if 8<=t<18:
  if sc=='localized_notch':return max(0,x-1.8*math.exp(-((x-3)/.36)**2))
  if sc=='step_discontinuity':return max(0,x-(1.9 if 2.55<=x<=3.65 else 0))
  if sc=='gain_shift' and 1<=x<=4.2:return .48*x
  if sc=='dropout' and 1<=x<=4.2:return 0.
 return x
def evidence(sc,t):
 generation=2 if sc=='valid_rotation' and t>=12 else 1
 cert=sign(dict(device='REFERENCE-1',generation=generation,measurement_t=t,
  valid_until=t if sc=='expired_certificate' and t>=8 else t+1,
  nonce=f'cal-{generation}-{t}',probe_inputs=XS,probe_outputs=[round(sensor(sc,t,x),8) for x in XS],
  reference_root='assumed-reference-standard',uncertainty_percent=.04))
 pkt=sign(dict(device='REFERENCE-1',generation=generation,tick=t,counter=t,nonce=cert['nonce'],
  risk_reported=round(sensor(sc,t,truth(sc,t)*100)/100,8)))
 return pkt,cert
def admissible(p,c,t):
 if not (verify(p) and verify(c) and p['tick']==t and p['counter']==t and c['measurement_t']==t
  and c['valid_until']==t+1 and p['device']==c['device'] and p['generation']==c['generation']
  and p['nonce']==c['nonce']):return False,'invalid_or_stale'
 if c['probe_inputs']!=XS or len(c['probe_outputs'])!=51:return False,'coverage_invalid'
 ys=c['probe_outputs']
 if max(abs(x-y) for x,y in zip(XS,ys))>.08:return False,'response_residual'
 if any(not(.8<=(ys[i+1]-ys[i])/(XS[i+1]-XS[i])<=1.2) for i in range(50)):return False,'response_slope'
 return True,'regularity_certified'
def episode(seed,sc,pol):
 out=[];prev='0'*64
 for t in range(T):
  pkt,cert=evidence(sc,t);good,why=admissible(pkt,cert,t)
  act=verify(pkt) and pkt['tick']==t and pkt['risk_reported']+.0004<=LIM
  if pol=='regularity':act=act and good
  tr=truth(sc,t)
  r=dict(seed=seed,scenario=sc,policy=pol,tick=t,action='ACT' if act else 'HOLD',
   unsafe=int(act and tr>LIM),safe_act=int(act and tr<=LIM),safe_hold=int(not act and tr<=LIM),
   regularity_valid=int(good),reported=pkt['risk_reported'],truth=tr,reason=why,
   probe_count=51 if pol=='regularity' else 2)
  h=hashlib.sha256(prev.encode()+raw(r)).hexdigest()
  r['prev_hash']=prev;r['hash']=h;prev=h;out.append(r)
 return out
def chain(rows):
 prev='0'*64
 for r in rows:
  a={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256(prev.encode()+raw(a)).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True
def csvout(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 per=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for pol in ('endpoint','regularity'):
    a=episode(seed,sc,pol);b=episode(seed,sc,pol)
    rules=dict(replay=a==b,hash_chain=chain(a),one_action=len(a)==T and all(r['action'] in ('ACT','HOLD') for r in a),
     time_order=all(r['tick']==i for i,r in enumerate(a)),no_unsafe=pol!='regularity' or all(r['unsafe']==0 for r in a),
     fail_closed=pol!='regularity' or all(r['action']=='HOLD' for r in a if not r['regularity_valid']),
     signature=all(verify(evidence(sc,t)[0]) and verify(evidence(sc,t)[1]) for t in range(T)))
    checks.append(dict(scenario=sc,seed=seed,policy=pol,**{k:int(v) for k,v in rules.items()}))
    per.append(dict(scenario=sc,seed=seed,policy=pol,
     unsafe=sum(r['unsafe'] for r in a),safe_act=sum(r['safe_act'] for r in a),
     safe_hold=sum(r['safe_hold'] for r in a),probe_count=sum(r['probe_count'] for r in a)))
    if seed==SEEDS.start:traces+=a
 csvout('checks.csv',checks);csvout('seed_results.csv',per);csvout('trace_samples.csv',traces)
 totals=[]
 for sc in (*SC,'ALL'):
  for pol in ('endpoint','regularity'):
   z=[r for r in per if r['policy']==pol and (sc=='ALL' or r['scenario']==sc)]
   totals.append(dict(scenario=sc,policy=pol,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),probe_count=sum(r['probe_count'] for r in z)))
 csvout('results.csv',totals);x={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(zero_unsafe=x['ALL','regularity']['unsafe']==0,
  baseline_counterexample=x['ALL','endpoint']['unsafe']>0,
  clean_availability=x['clean','regularity']['safe_act']==x['clean','endpoint']['safe_act'],
  rotation_availability=x['valid_rotation','regularity']['safe_act']==x['valid_rotation','endpoint']['safe_act'],
  nonlinear_rejection=all(x[s,'regularity']['unsafe']==0 for s in ('localized_notch','step_discontinuity','gain_shift','dropout')),
  deterministic=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks))
 manifest=dict(bound='AETHER-132',phase='VII',status='PASS' if all(gates.values()) else 'FAIL',
  episodes_per_policy=400,decisions_per_policy=9600,check_count=5600,gates=gates,
  seed_range=[132001,132050],challenge_count=51,domain='risk 0..5 percent in 0.1-percent steps',
  limitations=['No physical instrument connected','Trusted challenge truth and same-path response assumed',
  'Finite probes cannot certify arbitrary behavior between them','This is synthetic-only'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
