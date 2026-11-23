#!/usr/bin/env python3
"""AETHER-114: epoch-bound credential expiry and rotation. Synthetic only."""
import csv, hashlib, hmac, json
from pathlib import Path
import numpy as np
from scipy.stats import beta
HERE=Path(__file__).resolve().parent
SEEDS=range(114001,114061)
SCENARIOS=('clean_rotation','expired_key','epoch_rollback','revoked_key','unknown_key','tampered_epoch','delayed_packet')
TICKS=24; ROTATE=12; N=560; LIMIT=.025
KEYS={'K0':b'fixture-old-key-not-deployable','K1':b'fixture-new-key-not-deployable','KX':b'fixture-untrusted-key'}
SCHEDULE={'K0':(0,12,0),'K1':(12,24,1)}
BODY=('stream','seq','tick','errors','n','certified','epoch','key_id')
def digest(p,key):
    body={k:p[k] for k in BODY}
    return hmac.new(key,json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def pack(t,errors,n=N,certified=True,epoch=None,key_id=None,delay=0):
    key_id=key_id or ('K0' if t<ROTATE else 'K1')
    epoch=(0 if key_id=='K0' else 1) if epoch is None else epoch
    p=dict(stream='sensor-A',seq=t,tick=t,errors=int(errors),n=n,certified=bool(certified),epoch=epoch,key_id=key_id,arrival=t+delay)
    p['tag']=digest(p,KEYS[key_id]);return p
def upper(errors,n):
    return 1. if n<=0 or errors>=n else float(beta.ppf(.95,errors+1,n-errors))
def episode(seed,scenario):
    rng=np.random.default_rng(seed+100000*SCENARIOS.index(scenario))
    risk=[.003 if t<8 or t>=16 else .06 for t in range(TICKS)]
    packets=[pack(t,rng.binomial(N,risk[t])) for t in range(TICKS)]
    for t in range(12,16):
        if scenario=='expired_key':packets[t]=pack(t,0,key_id='K0')
        elif scenario=='epoch_rollback':packets[t]=pack(t,0,key_id='K0',epoch=0)
        elif scenario=='revoked_key':packets[t]=pack(t,0,key_id='K0')
        elif scenario=='unknown_key':packets[t]=pack(t,0,key_id='KX',epoch=1)
        elif scenario=='tampered_epoch':packets[t]['epoch']=0
        elif scenario=='delayed_packet':packets[t]=pack(t-8,0,key_id='K0',delay=8)
    return risk,packets
def validate(p,t,policy,seen):
    if p is None:return 'missing'
    if p['arrival']!=t or p['tick']!=t or p['seq']!=t:return 'stale_or_replay'
    if (p['stream'],p['seq']) in seen:return 'duplicate'
    if p['stream']!='sensor-A' or not p['certified'] or p['n']!=N or not 0<=p['errors']<=N:return 'invalid_packet'
    if p['key_id'] not in SCHEDULE:return 'unknown_key'
    if not hmac.compare_digest(p['tag'],digest(p,KEYS[p['key_id']])):return 'bad_mac'
    if policy=='epoch_bound':
        start,end,epoch=SCHEDULE[p['key_id']]
        if p['epoch']!=epoch:return 'wrong_epoch'
        if not start<=t<end:return 'expired_or_revoked'
        if p['epoch']<int(t>=ROTATE):return 'rollback'
    return 'valid'
def run(seed,scenario,policy):
    risk,packets=episode(seed,scenario)
    seen=set();chain='0'*64;rows=[]
    for t,p in enumerate(packets):
        status=validate(p,t,policy,seen)
        if status=='valid':seen.add((p['stream'],p['seq']))
        bound=upper(p['errors'],p['n']) if status=='valid' else 1.
        action='ACT' if bound<=LIMIT else 'HOLD'
        row=dict(seed=seed,scenario=scenario,tick=t,policy=policy,key_id=p['key_id'] if p else '',epoch=p['epoch'] if p else '',status=status,
            action=action,upper=round(bound,9),actual_hazard=int(risk[t]>LIMIT),unsafe=int(action=='ACT' and risk[t]>LIMIT),
            safe_action=int(action=='ACT' and risk[t]<=LIMIT),cost=round((7.5 if action=='HOLD' else 10*N*risk[t])+.06,3))
        chain=hashlib.sha256((chain+json.dumps(row,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
        row['hash']=chain;rows.append(row)
    return rows
def save(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    rows=[];checks=[]
    for scenario in SCENARIOS:
      for seed in SEEDS:
       for policy in ('keyring_only','epoch_bound'):
        trace=run(seed,scenario,policy);rows.extend(trace)
        replay=trace==run(seed,scenario,policy)
        last='0'*64;chain_ok=True
        for r in trace:
            body={k:v for k,v in r.items() if k!='hash'}
            last=hashlib.sha256((last+json.dumps(body,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
            chain_ok &= last==r['hash']
        fail_closed=all(r['action']=='HOLD' for r in trace if r['status']!='valid')
        admissible=all(r['action']=='HOLD' or r['upper']<=LIMIT for r in trace)
        checks.append(dict(seed=seed,scenario=scenario,policy=policy,replay=replay,hash_chain=chain_ok,fail_closed=fail_closed,admissible=admissible))
    summaries=[]
    for scenario in (*SCENARIOS,'ALL'):
      for policy in ('keyring_only','epoch_bound'):
        z=[r for r in rows if r['policy']==policy and (scenario=='ALL' or r['scenario']==scenario)]
        summaries.append(dict(scenario=scenario,policy=policy,ticks=len(z),acts=sum(r['action']=='ACT' for r in z),unsafe=sum(r['unsafe'] for r in z),safe_acts=sum(r['safe_action'] for r in z),rejected=sum(r['status']!='valid' for r in z),cost=round(sum(r['cost'] for r in z),2)))
    def get(s,p):return next(r for r in summaries if r['scenario']==s and r['policy']==p)
    checks_ok=all(all(c[k] for k in ('replay','hash_chain','fail_closed','admissible')) for c in checks)
    clean=get('clean_rotation','epoch_bound');baseline=get('clean_rotation','keyring_only')
    risky=[s for s in SCENARIOS if s!='clean_rotation']
    accepted=(checks_ok and clean['safe_acts']>=.95*baseline['safe_acts'] and clean['safe_acts']>0
      and all(get(s,'epoch_bound')['unsafe']==0 for s in risky)
      and all(get(s,'epoch_bound')['unsafe']<=get(s,'keyring_only')['unsafe'] for s in SCENARIOS))
    save('checks.csv',checks);save('results.csv',summaries)
    save('trace_samples.csv',[r for r in rows if r['seed']==min(SEEDS) and r['policy']=='epoch_bound'])
    seed_rows=[]
    for scenario in SCENARIOS:
      for seed in SEEDS:
       for policy in ('keyring_only','epoch_bound'):
        z=[r for r in rows if r['scenario']==scenario and r['seed']==seed and r['policy']==policy]
        seed_rows.append(dict(scenario=scenario,seed=seed,policy=policy,acts=sum(r['action']=='ACT' for r in z),unsafe=sum(r['unsafe'] for r in z),safe_acts=sum(r['safe_action'] for r in z),rejected=sum(r['status']!='valid' for r in z)))
    save('seed_results.csv',seed_rows)
    manifest=dict(bound='AETHER-114',phase='V',status='PASS' if accepted else 'FAIL',phase_percent=25 if accepted else 12.5,
        seeds=[min(SEEDS),max(SEEDS)],rotation_tick=ROTATE,scenarios=list(SCENARIOS),cases=len(checks),
        checks_passed=sum(sum(bool(c[k]) for k in ('replay','hash_chain','fail_closed','admissible')) for c in checks),
        possible_checks=4*len(checks),assumption='Trusted key schedule, authentic key metadata and retirement notifications; no detection of compromised active signing key.',
        warning='Test keys are public fixtures. HMAC key possession is not proof of origin or independence.')
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(manifest=manifest,results=summaries),indent=2))
    if not accepted:raise SystemExit(1)
if __name__=='__main__':main()
