"""AETHER-086: deterministic synthetic comparison of evidence-transfer policies."""
import numpy as np
import csv
from pathlib import Path
OUT=Path(__file__).resolve().parent
REGIMES=['familiar','gain_drift','timing_shift','asymmetric_outliers','heteroskedastic','bimodal_bias']
def errors(rng,regime,x,n):
    if regime=='familiar': return rng.normal(0,.018,n)
    if regime=='gain_drift': return .07*x+rng.normal(0,.025,n)
    if regime=='timing_shift': return rng.normal(.045,.042,n)
    if regime=='asymmetric_outliers': return rng.normal(0,.021,n)+(rng.random(n)<.08)*rng.exponential(.28,n)
    if regime=='heteroskedastic': return rng.normal(0,.013+.075*np.abs(x),n)
    return rng.normal(0,.018,n)+rng.choice([-.11,.11],size=n)
def draw(rng,regime,n):
    x=rng.uniform(-1,1,n);e=errors(rng,regime,x,n);return x,x+e,e
def radius(e): return float(np.quantile(np.abs(e),.98,method='higher'))
def metrics(x,y,r):
    auth=np.abs(y)>r;wrong=auth&(np.sign(x)!=np.sign(y));return int(auth.sum()),int(wrong.sum())
rows=[]
for seed in range(8):
    rng=np.random.default_rng(86000+seed)
    bank={r:draw(rng,r,400)[2] for r in REGIMES[:3]}
    pooled=np.concatenate(list(bank.values()))
    for regime in REGIMES:
        for batch in range(20):
            _,_,audit=draw(rng,regime,80)
            x,y,_=draw(rng,regime,300)
            distances={k:abs(float(np.median(np.abs(audit)))-float(np.median(np.abs(v)))) for k,v in bank.items()}
            nearest=min(distances,key=distances.get)
            matched=distances[nearest]<=.005
            for name,e,used in [('global_transfer',np.r_[pooled,audit],True),('local_only',audit,False),('similarity_gate',np.r_[bank[nearest],audit] if matched else audit,matched)]:
                rad=radius(e);auth,wrong=metrics(x,y,rad)
                rows.append(dict(seed=seed,regime=regime,batch=batch,policy=name,radius=round(rad,6),matched=int(used),authorized=auth,wrong=wrong,total=300))
with (OUT/'batch_results.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=[]
for regime in REGIMES:
    for policy in ['global_transfer','local_only','similarity_gate']:
        z=[a for a in rows if a['regime']==regime and a['policy']==policy]
        t=sum(a['total'] for a in z);au=sum(a['authorized'] for a in z);wr=sum(a['wrong'] for a in z)
        summary.append(dict(regime=regime,policy=policy,observations=t,authorized=au,wrong=wr,authorization_rate=round(au/t,4),conditional_error=round(wr/au,4) if au else None,unconditional_error=round(wr/t,4),transfer_batches=sum(a['matched'] for a in z)))
with (OUT/'results.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
print('Results:',OUT/'results.csv')
