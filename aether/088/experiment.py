#!/usr/bin/env python3
"""AETHER-088: exact sequential certification with independent audit roots.

Requires numpy and scipy. One thousand synthetic trials per condition.
The confidence guarantee requires stationary independent Bernoulli roots.
"""
from pathlib import Path
import csv,json
import numpy as np
from scipy.stats import beta
HERE=Path(__file__).resolve().parent
SEED=88001; TRIALS=1000; LOOKS=40; ROOTS_PER_LOOK=30; COPIES=6
ALPHA=.05; BUDGET=.02; RISKS={'safe':.003,'unsafe':.024}
def upper(fails,n,alpha):
    result=beta.ppf(1-alpha,fails+1,n-fails)
    return np.where(fails==n,1.,result)
rng=np.random.default_rng(SEED); summary=[]; audit=[]
for regime,p in RISKS.items():
    for dependence in ('independent','six_copies_one_root'):
        draws=rng.binomial(1,p,size=(TRIALS,LOOKS*ROOTS_PER_LOOK))
        totals=np.cumsum(draws,axis=1)
        stops={k:np.zeros(TRIALS,dtype=int) for k in ('naive_repeated_peeking','anytime_unique_roots','fixed_final_unique_roots')}
        multiplier=COPIES if dependence!='independent' else 1
        for look in range(1,LOOKS+1):
            n=look*ROOTS_PER_LOOK
            f=totals[:,n-1]
            naive=upper(f*multiplier,n*multiplier,ALPHA)
            anytime=upper(f,n,ALPHA/LOOKS)
            fixed=upper(f,n,ALPHA)
            for policy,bounds in (('naive_repeated_peeking',naive),('anytime_unique_roots',anytime)):
                fresh=(stops[policy]==0)&(bounds<=BUDGET)
                stops[policy][fresh]=look
            if look==LOOKS:
                stops['fixed_final_unique_roots'][fixed<=BUDGET]=look
            if look in (1,5,10,20,30,40):
                audit.append(dict(regime=regime,dependence=dependence,look=look,unique_roots=n,raw_records=n*multiplier,naive_ever_certified=int((stops['naive_repeated_peeking']>0).sum()),anytime_ever_certified=int((stops['anytime_unique_roots']>0).sum())))
        for policy,st in stops.items():
            good=st>0
            summary.append(dict(regime=regime,true_wrong_sign_risk=p,dependence=dependence,policy=policy,trials=TRIALS,approved=int(good.sum()),approval_pct=round(100*good.mean(),2),mean_unique_roots_at_first_approval=round(float(np.mean(st[good])*ROOTS_PER_LOOK),1) if good.any() else '',risk_budget=BUDGET,alpha=ALPHA))
def dump(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
dump('results.csv',summary);dump('look_audit.csv',audit)
(HERE/'manifest.json').write_text(json.dumps(dict(bound='AETHER-088',seed=SEED,trials=TRIALS,looks=LOOKS,roots_per_look=ROOTS_PER_LOOK,copies_per_root=COPIES,alpha=ALPHA,risk_budget=BUDGET,risks=RISKS,assumptions='Unique roots are independent stationary Bernoulli samples; copies share root ancestry.'),indent=2)+'\n')
print(json.dumps(summary,indent=2))
