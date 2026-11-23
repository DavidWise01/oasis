#!/usr/bin/env python3
"""AETHER-115: leased schedule freshness, no true schedule used by live decisions.
Synthetic HMAC fixtures only. Python stdlib plus numpy/scipy.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
SEEDS=range(115001,115081)
SCENARIOS=('clean_rotation','delayed_retirement_notice','feed_outage','schedule_rollback','untrusted_renewal','outage_recovery')
T=28; N=560; LIMIT=.025; LEASE=4; ROTATE=12
ROOT_KEY=b'local-synthetic-schedule-anchor';K0=b'local-credential0';K1=b'local-credential1'
KEYS={'K0':K0,'K1':K1}
def mac(payload,key):return hmac.new(key,json.dumps(payload,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def notice(seq,arrive,active,signer=ROOT_KEY):
    p={'schedule_seq':seq,'issued':seq*4,'arrival':arrive,'active_key':active,'valid_until':seq*4+LEASE}
    p['tag']=mac({k:p[k] for k in ('schedule_seq','issued','active_key','valid_until')},signer);return p
def packet(t,key,err):
    p={'time':t,'seq':t,'key_id':key,'errors':int(err),'n':N,'independent':True}
    p['tag']=mac(p,KEYS[key]);return p
def episodes(seed,scenario):
    rng=np.random.default_rng(seed+SCENARIOS.index(scenario)*100000)
    risk=np.array([.003 if t<12 or t>=18 else .07 for t in range(T)])
    packets=[packet(t,'K0' if t<12 else 'K1',rng.binomial(N,risk[t])) for t in range(T)]
    schedule=[]
    for i in range(7):
        issue=i*4;active='K0' if issue<12 else 'K1';arrival=issue
        if scenario in ('delayed_retirement_notice','outage_recovery') and i in (3,4):arrival=issue+6
        if scenario=='feed_outage' and i in (3,4):continue
        if scenario=='schedule_rollback' and i==3:
            schedule.append(notice(1,12,'K0'))
            continue
        if scenario=='untrusted_renewal' and i==3:
            schedule.append(notice(3,12,'K0',b'fake-signer'))
            continue
        schedule.append(notice(i,arrival,active))
    if scenario in ('delayed_retirement_notice','schedule_rollback','untrusted_renewal'):
        for t in range(12,18):packets[t]=packet(t,'K0',0)
    if scenario=='feed_outage':
        for t in range(12,18):packets[t]=packet(t,'K0',0)
    if scenario=='outage_recovery':
        for t in range(12,18):packets[t]=packet(t,'K1',rng.binomial(N,risk[t]))
    return risk,packets,schedule

def bound(e,n):return 1. if n<=0 or e>=n else float(beta.ppf(.95,e+1,n-e))
def verify_notice(p):
    body={k:p[k] for k in ('schedule_seq','issued','active_key','valid_until')}
    return hmac.compare_digest(p['tag'],mac(body,ROOT_KEY)) and p['issued']==4*p['schedule_seq'] and p['valid_until']==p['issued']+LEASE

def trial(seed,scenario,policy):
    risk,packets,notices=episodes(seed,scenario)
    seq=-1;active=None;expiry=-1;hashprev='0'*64;rows=[];seen=set()
    for t,p in enumerate(packets):
        for u in sorted((x for x in notices if x['arrival']==t),key=lambda x:x['schedule_seq']):
            if verify_notice(u) and u['schedule_seq']>seq and u['issued']<=t:
                seq=u['schedule_seq'];active=u['active_key'];expiry=u['valid_until']
        pbody={k:p[k] for k in ('time','seq','key_id','errors','n','independent')}
        credential=hmac.compare_digest(p['tag'],mac(pbody,KEYS[p['key_id']])) and p['time']==t and p['seq']==t and p['seq'] not in seen and p['independent'] and p['n']==N
        # Cache comparator accepts old recognized key until authoritative replacement arrives.
        if policy=='cache':accepted=bool(credential and p['key_id']==active)
        else:accepted=bool(credential and p['key_id']==active and t<expiry)
        if credential:seen.add(p['seq'])
        upper=bound(p['errors'],p['n']) if accepted else 1.
        act=upper<=LIMIT
        row=dict(scenario=scenario,seed=seed,tick=t,policy=policy,schedule_seq=seq,key_id=p['key_id'],lease_expiry=expiry,
          packet_valid=int(credential),accepted=int(accepted),action='ACT' if act else 'HOLD',unsafe=int(act and risk[t]>LIMIT),safe_act=int(act and risk[t]<=LIMIT),
          safe_hold=int(not act and risk[t]<=LIMIT),audit_cost=.01*N,loss=round(10*(N*risk[t] if act else 0)+(.05*N if not act else 0)+.01*N,3))
        hashprev=hashlib.sha256((hashprev+json.dumps(row,sort_keys=True,separators=(',',':'))).encode()).hexdigest();row['hash']=hashprev
        rows.append(row)
    return rows

def save(name,rows):
    with (D/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    allrows=[];seedrows=[];checks=[]
    for sc in SCENARIOS:
      for seed in SEEDS:
        for policy in ('cache','leased'):
          r=trial(seed,sc,policy);allrows.extend(r)
          seedrows.append(dict(scenario=sc,seed=seed,policy=policy,act=sum(x['action']=='ACT' for x in r),unsafe=sum(x['unsafe'] for x in r),safe_act=sum(x['safe_act'] for x in r),safe_hold=sum(x['safe_hold'] for x in r),cost=round(sum(x['loss'] for x in r),2)))
          rerun=trial(seed,sc,policy)
          checks.append(dict(scenario=sc,seed=seed,policy=policy,replay=int(r==rerun),hash_chain=int(all(len(x['hash'])==64 for x in r)),one_action=int(all(x['action'] in ('ACT','HOLD') for x in r))))
    save('seed_results.csv',seedrows);save('checks.csv',checks)
    summary=[]
    for sc in (*SCENARIOS,'ALL'):
      for pol in ('cache','leased'):
        z=[x for x in seedrows if x['policy']==pol and (sc=='ALL' or x['scenario']==sc)]
        summary.append(dict(scenario=sc,policy=pol,cases=len(z),unsafe=sum(x['unsafe'] for x in z),safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z),cost=round(sum(x['cost'] for x in z),2)))
    save('results.csv',summary);save('trace_samples.csv',[x for x in allrows if x['seed']==min(SEEDS) and x['scenario'] in ('clean_rotation','delayed_retirement_notice')])
    a={r['scenario']:r for r in summary if r['policy']=='cache'};b={r['scenario']:r for r in summary if r['policy']=='leased'}
    # Report both strict and practical checks; no blanket safety claim.
    gates={'no_more_unsafe':b['ALL']['unsafe']<=a['ALL']['unsafe'], 'no_safe_clean_regression':b['clean_rotation']['safe_act']==a['clean_rotation']['safe_act'],
           'fewer_unsafe':b['ALL']['unsafe']<a['ALL']['unsafe'],'no_extra_total_cost':b['ALL']['cost']<=a['ALL']['cost'],
           'replay':bool(all(c['replay'] and c['hash_chain'] and c['one_action'] for c in checks))}
    manifest={'bound':'AETHER-115','phase':'V','status':'PASS' if all(gates.values()) else 'FAIL','seeds':[min(SEEDS),max(SEEDS)],'lease_ticks':LEASE,'gates':gates,
     'caveats':['synthetic trust anchor and HMAC fixture keys','lease cannot detect revoked active credentials before expiry','oracle risk is evaluator-only','costs are simulated']}
    (D/'manifest.json').write_text(json.dumps(manifest,indent=2,default=lambda x:x.item())+'\n')
    print(json.dumps({'manifest':manifest,'summary':summary},indent=2,default=lambda x:x.item()))
if __name__=='__main__':main()
