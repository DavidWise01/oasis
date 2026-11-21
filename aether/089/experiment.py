#!/usr/bin/env python3
"""AETHER-089 — lineage-aware certification under abrupt risk drift.
Synthetic experiment; independent Bernoulli roots, six copies per root.
Requires numpy and scipy. Run: python aether/089/experiment.py
"""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import beta

OUT=Path(__file__).resolve().parent
SEED=89089; TRIALS=500; LOOKS=30; ROOTS_PER_LOOK=60; COPIES=6
ALPHA=.05; RISK_BUDGET=.02; WINDOW_LOOKS=8; CHANGE_LOOK=15
SCENARIOS={'stable_safe':(.0025,.0025),'stable_unsafe':(.06,.06),'abrupt_drift':(.0025,.06)}
POLICIES=('naive_repeated_records','root_aware_cumulative','root_aware_rolling')
def upper(fails,n,alpha):
    if n<=0 or fails>=n:return 1.
    return float(beta.ppf(1-alpha,fails+1,n-fails))
def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rng=np.random.default_rng(SEED);records=[]
for scenario,(before,after) in SCENARIOS.items():
    for trial in range(TRIALS):
        probabilities=[before if k<CHANGE_LOOK else after for k in range(LOOKS) for _ in range(ROOTS_PER_LOOK)]
        outcomes=rng.binomial(1,probabilities)
        for look in range(1,LOOKS+1):
            hi=look*ROOTS_PER_LOOK
            count=int(outcomes[:hi].sum())
            wstart=max(0,look-WINDOW_LOOKS)*ROOTS_PER_LOOK
            window=outcomes[wstart:hi]
            bounds=(upper(COPIES*count,COPIES*hi,ALPHA),
                    upper(count,hi,ALPHA/LOOKS),
                    upper(int(window.sum()),len(window),ALPHA/LOOKS))
            for policy,bound in zip(POLICIES,bounds):
                records.append(dict(scenario=scenario,trial=trial,look=look,
                    true_risk=before if look<=CHANGE_LOOK else after,
                    policy=policy,unique_roots_seen=hi,
                    claimed_records=hi*COPIES if policy==POLICIES[0] else hi,
                    bound=round(bound,6),authorized=int(bound<=RISK_BUDGET)))
save('look_audit.csv',records)
results=[]
for scenario in SCENARIOS:
    for policy in POLICIES:
        rs=[r for r in records if r['scenario']==scenario and r['policy']==policy]
        pre=[r for r in rs if r['look']<=CHANGE_LOOK]
        post=[r for r in rs if r['look']>CHANGE_LOOK]
        rate=lambda a:round(100*sum(r['authorized'] for r in a)/len(a),2)
        ever=round(100*len({r['trial'] for r in post if r['authorized']})/TRIALS,2)
        results.append(dict(scenario=scenario,policy=policy,trials=TRIALS,looks=LOOKS,
            pre_authorization_pct=rate(pre),post_authorization_pct=rate(post),
            post_trials_ever_authorized_pct=ever,
            unsafe_post_authorizations=sum(r['authorized'] for r in post) if scenario!='stable_safe' else 0,
            total_authorized_looks=sum(r['authorized'] for r in rs)))
save('results.csv',results)
manifest=dict(bound='AETHER-089',seed=SEED,trials=TRIALS,looks=LOOKS,
    roots_per_look=ROOTS_PER_LOOK,copies_per_root=COPIES,
    alpha=ALPHA,risk_budget=RISK_BUDGET,rolling_window_looks=WINDOW_LOOKS,
    change_after_look=CHANGE_LOOK,scenarios=SCENARIOS,
    limitations=['Synthetic independent Bernoulli roots only',
        'Copied records are exact duplicates, not partially shared ancestry',
        'A window bound concerns historical window-average risk, not instantaneous future risk',
        'Alpha spending does not resolve temporal nonstationarity'])
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(*results,sep='\n')
