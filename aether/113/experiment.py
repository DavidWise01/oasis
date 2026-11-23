#!/usr/bin/env python3
"""AETHER-113: synthetic authenticated ingress; HMAC does NOT prove independence."""
import csv, hashlib, hmac, json
from pathlib import Path
import numpy as np
from scipy.stats import beta
HERE=Path(__file__).resolve().parent
KEY=b'aether113-simulation-only-not-a-deployment-secret'
SCENARIOS=('clean','replay','tamper','self_signed','count_forgery','missing','uncertified')
SEEDS=range(113001,113051)
TICKS=24;N=560;LIMIT=.025
def digest(p,key=KEY):
    body={k:p[k] for k in ('stream','seq','tick','errors','n','certified')}
    return hmac.new(key,json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def pack(stream,tick,errors,n=N,certified=True,key=KEY):
    p=dict(stream=stream,seq=tick,tick=tick,errors=errors,n=n,certified=certified)
    p['tag']=digest(p,key);return p
def upper(errors,n):
    return 1. if n<=0 or errors>=n else float(beta.ppf(.95,errors+1,n-errors))
def episode(seed,scenario):
    rng=np.random.default_rng(seed+100000*SCENARIOS.index(scenario))
    risk=[.003 if t<8 or t>=16 else .05 for t in range(TICKS)]
    raw=[pack('sensor-A',t,int(rng.binomial(N,p))) for t,p in enumerate(risk)]
    arr=[dict(x) for x in raw]
    for t in range(8,16):
        p=arr[t]
        if scenario=='replay':p.update(raw[3]);p['tick']=raw[3]['tick']
        elif scenario=='tamper':p['errors']=0
        elif scenario=='self_signed':arr[t]=pack('sensor-A',t,0,key=b'untrusted-attacker-key')
        elif scenario=='count_forgery':p['n']=5600;p['errors']=0
        elif scenario=='missing':arr[t]=None
        elif scenario=='uncertified':arr[t]=pack('sensor-A',t,0,certified=False)
    return risk,arr
def run(seed,scenario,policy):
    risk,packets=episode(seed,scenario)
    seen=set();next_seq=0;trace=[];chain='0'*64
    for t,p in enumerate(packets):
        status='valid'
        if p is None:status='missing'
        elif policy=='trusted':
            if not hmac.compare_digest(p.get('tag',''),digest(p)):status='bad_mac'
            elif not p['certified']:status='uncertified'
            elif p['stream']!='sensor-A' or p['tick']!=t or p['seq']!=next_seq:status='stale_or_replay'
            elif (p['stream'],p['seq']) in seen:status='duplicate'
            elif p['n']!=N or not 0<=p['errors']<=p['n']:status='invalid_count'
        if p is not None and policy=='trusted' and status=='valid':
            seen.add((p['stream'],p['seq']));next_seq+=1
        elif p is None or status!='valid':next_seq=t+1
        elif policy=='trusted':next_seq=t+1
        if policy=='naive' and p is not None:status='accepted_without_verification'
        bound=upper(int(p['errors']),int(p['n'])) if p is not None and status in ('valid','accepted_without_verification') else 1.
        action='ACT' if bound<=LIMIT else 'HOLD'
        row=dict(seed=seed,scenario=scenario,tick=t,policy=policy,packet_status=status,
            true_risk=risk[t],upper=round(bound,8),action=action,
            unsafe=int(action=='ACT' and risk[t]>LIMIT),
            valid_safe_act=int(action=='ACT' and risk[t]<=LIMIT),
            cost=round((7.5 if action=='HOLD' else 10*N*risk[t])+.06,3))
        chain=hashlib.sha256((chain+json.dumps(row,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
        row['hash']=chain;trace.append(row)
    return trace
def save(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    rows=[];checks=[]
    for scenario in SCENARIOS:
        for seed in SEEDS:
            for policy in ('naive','trusted'):
                trace=run(seed,scenario,policy);rows+=trace
                replay=run(seed,scenario,policy)
                last='0'*64;chain_ok=True
                for row in trace:
                    content={k:v for k,v in row.items() if k!='hash'}
                    last=hashlib.sha256((last+json.dumps(content,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
                    chain_ok &= last==row['hash']
                fail_closed=all(r['action']=='HOLD' for r in trace if policy=='trusted' and r['packet_status']!='valid')
                admissible=all(r['action']=='HOLD' or r['upper']<=LIMIT for r in trace)
                checks.append(dict(seed=seed,scenario=scenario,policy=policy,
                    replay=trace==replay,hash_chain=chain_ok,fail_closed=fail_closed,admissible=admissible))
    save('tick_audit.csv',rows);save('checks.csv',checks)
    summaries=[]
    for scenario in (*SCENARIOS,'ALL'):
        for policy in ('naive','trusted'):
            z=[r for r in rows if r['policy']==policy and (scenario=='ALL' or r['scenario']==scenario)]
            summaries.append(dict(scenario=scenario,policy=policy,ticks=len(z),
                acts=sum(r['action']=='ACT' for r in z),unsafe_authorizations=sum(r['unsafe'] for r in z),
                safe_acts=sum(r['valid_safe_act'] for r in z),
                rejected_packets=sum(r['packet_status'] not in ('valid','accepted_without_verification') for r in z),
                total_cost=round(sum(r['cost'] for r in z),3)))
    save('results.csv',summaries)
    def get(sc,pol):return next(r for r in summaries if r['scenario']==sc and r['policy']==pol)
    safe_fraction=get('clean','trusted')['safe_acts']/max(1,get('clean','naive')['safe_acts'])
    all_ok=all(all(c[k] for k in ('replay','hash_chain','fail_closed','admissible')) for c in checks)
    accepted=bool(all_ok and get('clean','trusted')['safe_acts']>0 and safe_fraction>=.95
        and get('ALL','trusted')['unsafe_authorizations']<=get('ALL','naive')['unsafe_authorizations']
        and all(get(s,'trusted')['unsafe_authorizations']==0 for s in SCENARIOS))
    manifest=dict(bound='AETHER-113',phase='V',status='PASS' if accepted else 'FAIL',
        phase_percent=12.5 if accepted else 0,seeds=[min(SEEDS),max(SEEDS)],
        scenarios=list(SCENARIOS),ticks_per_episode=TICKS,cases=len(checks),
        test_checks=sum(sum(bool(c[k]) for k in ('replay','hash_chain','fail_closed','admissible')) for c in checks),
        possible_checks=4*len(checks),clean_safe_act_retention=round(safe_fraction,5),
        caveat='A trusted HMAC ingestion key and truthful independent count are explicit assumptions, not outcomes of this test. Simulated errors and costs are illustrative.')
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(manifest=manifest,results=summaries),indent=2))
    if not accepted:raise SystemExit(1)
if __name__=='__main__':main()
