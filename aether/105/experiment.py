#!/usr/bin/env python3
"""AETHER-105: Phase IV single-controller observational economy benchmark.
No consensus, voter count, provenance quorum, or Byzantine assumptions.
"""
import csv, json, math, random, hashlib
from pathlib import Path
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SCENARIOS=('stable','abrupt','oscillation','sensor_noise')
SEEDS=range(105001,105081)
T=80
ACTION=150
LIMIT=.025

def upper(errors,n):
    return 1. if errors==n else float(beta.ppf(.95,errors+1,n-errors))

def risk(kind,t):
    if kind=='stable':return .003
    if kind=='abrupt':return .075 if 25<=t<48 else .003
    if kind=='oscillation':return .052 if t%17<5 else .003
    return .003

def trials(seed,kind):
    r=random.Random(f'{seed}|{kind}|AETHER-105')
    observations=[]
    for t in range(T):
        p=risk(kind,t)
        # Sensor-noise case is correlated in 10-sample blocks, but held-out action errors are independent.
        blocks=[int(r.random()<p) for _ in range(14)] if kind=='sensor_noise' else None
        audit=[blocks[i//10] if blocks else int(r.random()<p) for i in range(140)]
        outcomes=[int(r.random()<p) for _ in range(ACTION)]
        observations.append((p,audit,outcomes))
    return observations

def choose(audit,policy):
    if policy=='fixed':
        n=140;f=sum(audit);u=upper(f,n)
    else:
        # Cheap first stage; more measurements only near the authorization boundary.
        n=40;f=sum(audit[:n]);u=upper(f,n)
        if .015 <= u <= .11:
            n=140;f=sum(audit);u=upper(f,n)
    return ('ACT' if u<=LIMIT else 'HOLD',n,u)

def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    rows=[];traces=[]
    for kind in SCENARIOS:
        for seed in SEEDS:
            obs=trials(seed,kind)
            for policy in ('fixed','adaptive'):
                digest='GENESIS';cost=0;bad=unsafe=holds=labels=acts=0
                for t,(p,audit,outcomes) in enumerate(obs):
                    action,n,bound=choose(audit,policy)
                    wrong=sum(outcomes) if action=='ACT' else 0
                    withheld=0 if action=='ACT' else ACTION
                    bad+=wrong;unsafe+=int(action=='ACT' and p>.02);holds+=int(action=='HOLD' and p<=.02)
                    labels+=n;acts+=int(action=='ACT');cost+=10*wrong+.05*withheld+.01*n
                    content=f'{seed}|{kind}|{policy}|{t}|{action}|{n}|{round(bound,9)}|{digest}'
                    digest=hashlib.sha256(content.encode()).hexdigest()
                    if t in (0,24,25,47,48,79):traces.append(dict(seed=seed,scenario=kind,policy=policy,tick=t,action=action,labels=n,bound=round(bound,5),prior_record=content.split('|')[-1],hash=digest))
                rows.append(dict(seed=seed,scenario=kind,policy=policy,acts=acts,safe_holds=holds,unsafe_acts=unsafe,wrong=bad,labels=labels,cost=round(cost,3),final_hash=digest))
    save('seed_results.csv',rows);save('trace_samples.csv',traces)
    summary=[]
    for scenario in (*SCENARIOS,'ALL'):
        for policy in ('fixed','adaptive'):
            a=[x for x in rows if x['policy']==policy and (scenario=='ALL' or x['scenario']==scenario)]
            summary.append(dict(scenario=scenario,policy=policy,cases=len(a),ticks=len(a)*T,acts=sum(x['acts'] for x in a),safe_holds=sum(x['safe_holds'] for x in a),unsafe_acts=sum(x['unsafe_acts'] for x in a),wrong=sum(x['wrong'] for x in a),labels=sum(x['labels'] for x in a),cost=round(sum(x['cost'] for x in a),3)))
    save('results.csv',summary)
    d={x['policy']:x for x in summary if x['scenario']=='ALL'}
    # Eligibility: no increase in unsafe ACT; evidence reduced 10%; overall cost not worse.
    pairwise_identical=all(next(x for x in rows if x['seed']==seed and x['scenario']==kind and x['policy']=='fixed')['acts']==next(x for x in rows if x['seed']==seed and x['scenario']==kind and x['policy']=='adaptive')['acts'] for seed in SEEDS for kind in SCENARIOS)
    checks={'per_case_action_count_identical':pairwise_identical,'unsafe_not_increased':d['adaptive']['unsafe_acts']<=d['fixed']['unsafe_acts'],
            'labels_reduced_10_pct':d['adaptive']['labels']<=.9*d['fixed']['labels'],
            'cost_not_increased':d['adaptive']['cost']<=d['fixed']['cost']}
    manifest={'bound':'AETHER-105','phase':'IV','status':'ACCEPTED' if all(checks.values()) else 'FAILED_ACCEPTANCE','checks':checks,'phase_completion_pct':12.5 if all(checks.values()) else 0,
      'seed_range':[min(SEEDS),max(SEEDS)],'scenarios':SCENARIOS,'policy_order':['fixed','adaptive'],
      'online_rule':'observe 40; extend to 140 if initial one-sided risk upper bound in [.015,.11]; authorize iff final upper bound <=.025',
      'limitations':['Synthetic trials, not production evidence','Correlated audit errors invalidate binomial confidence interpretation','Hidden true risk used for evaluation only']}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'summary':summary},indent=2))
if __name__=='__main__':main()
