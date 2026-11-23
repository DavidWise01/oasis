#!/usr/bin/env python3
"""AETHER-119 stress harness for the frozen AETHER-118 single-controller evaluator."""
import csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'118'/'experiment.py'
if not SOURCE.exists(): SOURCE=Path('/mnt/data/aether118/experiment.py')
SPEC=importlib.util.spec_from_file_location('aether118_frozen',SOURCE)
FROZEN=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(FROZEN)
SOURCE_HASH=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SCENARIOS=('control','burst_loss','long_outage','reordered','intermittent','invalid_signature','counter_discontinuity')
SEEDS=range(119001,119061);T=FROZEN.T;N=FROZEN.N
def risk_curve(rng,sc):
    risk=np.full(T,.003)
    if sc!='control':
        start=int(rng.integers(7,13));duration=int(rng.integers(5,10))
        risk[start:start+duration]=.085
    return risk
def episode(seed,sc):
    rng=np.random.default_rng(seed+1009*SCENARIOS.index(sc))
    risk=risk_curve(rng,sc)
    originals=[FROZEN.sign(dict(source='risk-audit',seq=t,observed_t=t,counter=t,epoch=1,
        valid_until=t+1,independent=True,n=N,errors=int(rng.binomial(N,risk[t])))) for t in range(T)]
    deliveries=[]
    outage_start=int(rng.integers(5,12));short=int(rng.integers(5,9));recovered=[]
    for t in range(T):
        p=dict(originals[t]);arrival=t;drop=False
        if sc=='burst_loss' and outage_start<=t<outage_start+short:drop=True
        if sc=='long_outage' and outage_start<=t<outage_start+int(rng.integers(14,19)):drop=True
        if sc=='reordered' and t>=5 and t<T-4 and t%4 in (1,2):arrival=t+int(rng.integers(1,4))
        if sc=='intermittent' and t>=outage_start and t<T-5 and (t-outage_start)%4!=0:drop=True
        if sc=='invalid_signature' and t>=outage_start and t<T-5 and t%3==0:
            p=dict(p);p['errors']=0
        if sc=='counter_discontinuity' and t>=outage_start and t<T-5 and t%4 in (1,2):
            b={k:v for k,v in p.items() if k!='mac'};b['counter']=max(0,t-3);p=FROZEN.sign(b)
        if not drop and arrival<T:
            deliveries.append((arrival,p))
            if arrival==t and FROZEN.verify(p) and p['seq']==t and p['counter']==t:recovered.append(t)
    return risk,deliveries,recovered
def stress_eval(seed,sc,policy):
    risk,deliveries,recovered=episode(seed,sc)
    FROZEN.episode=lambda s,c:(risk,deliveries)
    rows=FROZEN.evaluate(seed,sc,policy)
    return rows,recovered,risk,deliveries
def expected_safe_opportunities(risk,deliveries):
    expected=set()
    for t in range(T):
        for arrival,p in deliveries:
            if arrival!=t:continue
            if (FROZEN.verify(p) and p.get('seq')==t and p.get('observed_t')==t
                and p.get('counter')==t and p.get('epoch')==1 and p.get('source')=='risk-audit'
                and p.get('independent') is True and p.get('n')==N
                and t<p.get('valid_until',-1)<=t+1 and FROZEN.bound(p['errors'])<=FROZEN.LIMIT):
                expected.add(t)
    return expected
def save(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    seed_rows=[];checks=[];traces=[]
    for sc in SCENARIOS:
        for seed in SEEDS:
            for policy in ('cached','strict'):
                rows,recovered,risk,deliveries=stress_eval(seed,sc,policy)
                rr,_,_,_=stress_eval(seed,sc,policy)
                acceptable=expected_safe_opportunities(risk,deliveries)
                strict_acts={r['tick'] for r in rows if r['action']=='ACT'}
                legal_result=(policy!='strict' or strict_acts==acceptable)
                checks.append(dict(scenario=sc,seed=seed,policy=policy,
                    replay=int(rows==rr),hash_chain=int(FROZEN.verify_chain(rows)),
                    one_action=int(all(r['action'] in ('ACT','HOLD') for r in rows)),
                    reject_invalid=int(all(r['action']=='HOLD' for r in rows if policy=='strict' and not r['accepted'])),
                    source_match=int(legal_result),no_unsafe=int(policy!='strict' or all(r['unsafe']==0 for r in rows))))
                first_eligible=next((t for t in sorted(acceptable) if t>=24),-1)
                resumed=int(first_eligible==-1 or first_eligible in strict_acts) if policy=='strict' else -1
                seed_rows.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in rows),
                    safe_act=sum(r['safe_act'] for r in rows),safe_hold=sum(r['safe_hold'] for r in rows),
                    act=sum(r['action']=='ACT' for r in rows),receipts=sum(r['receipts'] for r in rows),
                    expected_valid_safe=len(acceptable),recovery_opportunity=first_eligible,
                    recovered_on_first_valid=resumed,cost=round(sum(r['cost'] for r in rows),2)))
                if seed==SEEDS.start:traces.extend(rows)
    save('seed_results.csv',seed_rows);save('checks.csv',checks);save('trace_samples.csv',traces)
    totals=[]
    for sc in (*SCENARIOS,'ALL'):
        for policy in ('cached','strict'):
            z=[r for r in seed_rows if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
            totals.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(x['unsafe'] for x in z),
                safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z),
                cost=round(sum(x['cost'] for x in z),2),recovery_cases=sum(x['recovery_opportunity']>=0 for x in z),
                recovered=sum(x['recovered_on_first_valid']==1 for x in z)))
    save('results.csv',totals)
    a={(r['scenario'],r['policy']):r for r in totals}
    gates=dict(no_unsafe=a['ALL','strict']['unsafe']==0,
        strict_fewer_unsafe=a['ALL','strict']['unsafe']<a['ALL','cached']['unsafe'],
        no_clean_regression=a['control','strict']['safe_act']==a['control','cached']['safe_act'],
        recovery_first_valid=all(r['recovered_on_first_valid']==1 for r in seed_rows if r['policy']=='strict'),
        unchanged_controller=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_HASH,
        deterministic=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks))
    manifest=dict(bound='AETHER-119',phase='V',status='PASS' if all(gates.values()) else 'FAIL',
      source_sha256=SOURCE_HASH,cases=len(SCENARIOS)*len(SEEDS),ticks_per_policy=len(SCENARIOS)*len(SEEDS)*T,
      checks=len(checks)*6,gates=gates,seeds=[SEEDS.start,SEEDS.stop-1],
      caveats=['synthetic risk and packets; HMAC key and signing truth are assumed',
       'stress input harness overrides delivery only; policy imported unchanged',
       'no protection against validly signed false science or compromised counter',
       'safe recovery means on first qualifying fresh risk packet, not first network restoration'])
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
if __name__=='__main__':main()
