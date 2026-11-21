"""AETHER-087: tail-aware transfer, independent conditional-risk audit.
Requires numpy. Deterministic synthetic experiment; no real-world certification.
"""
import numpy as np, csv, math
from pathlib import Path
OUT=Path(__file__).resolve().parent
REGIMES=['familiar','gain_drift','timing_shift','asymmetric_outliers','heteroskedastic','bimodal_bias']
POLICIES=['local_only','median_gate','tail_aware']
def errors(r,g,x,n):
    if g=='familiar': return r.normal(0,.018,n)
    if g=='gain_drift': return .07*x+r.normal(0,.025,n)
    if g=='timing_shift': return r.normal(.045,.042,n)
    if g=='asymmetric_outliers': return r.normal(0,.021,n)+(r.random(n)<.08)*r.exponential(.28,n)
    if g=='heteroskedastic': return r.normal(0,.013+.075*np.abs(x),n)
    return r.normal(0,.018,n)+r.choice([-.11,.11],size=n)
def draw(r,g,n):
    x=r.uniform(-1,1,n);e=errors(r,g,x,n);return x,x+e,e
def features(e):
    return np.array([np.median(np.abs(e)),np.quantile(np.abs(e),.90),np.quantile(np.abs(e),.98),np.mean(e),np.mean(e>.07),np.mean(e<-.07)])
def tail_match(a,b):
    d=abs(features(a)-features(b))
    return bool(np.all(d<=[.005,.018,.055,.016,.035,.035]))
def upper(w,n,z=2.394):
    if not n:return 1.
    p=w/n;return (p+z*z/(2*n)+z*np.sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)
def counts(x,y,rad):
    yes=np.abs(y)>rad
    return int(yes.sum()),int((yes&(np.sign(x)!=np.sign(y))).sum())
def certify(x,y,base):
    for mult in [1.,1.25,1.5,2.,3.,4.]:
        rad=base*mult;authorized,wrong=counts(x,y,rad)
        if authorized>=90 and upper(wrong,authorized)<=.02:return rad,upper(wrong,authorized),authorized,wrong
    return float('inf'),1.,0,0
rows=[]
for seed in range(87000,87012):
    rng=np.random.default_rng(seed)
    bank={g:draw(rng,g,600)[2] for g in REGIMES[:3]}
    for regime in REGIMES:
        for batch in range(16):
            _,_,cal=draw(rng,regime,160)
            cx,cy,_=draw(rng,regime,650)
            tx,ty,_=draw(rng,regime,350)
            dist={k:abs(features(cal)[0]-features(v)[0]) for k,v in bank.items()}
            nearest=min(dist,key=dist.get);ref=bank[nearest]
            for policy in POLICIES:
                used=(policy=='median_gate' and dist[nearest]<=.005) or (policy=='tail_aware' and tail_match(cal,ref))
                values=np.r_[cal,ref] if used else cal
                radius=float(np.quantile(abs(values),.98,method='higher'))
                rad,bound,ca,cw=certify(cx,cy,radius)
                au,wr=counts(tx,ty,rad)
                rows.append(dict(seed=seed,regime=regime,batch=batch,policy=policy,transfer=int(used),radius=round(rad,6) if np.isfinite(rad) else 'abstain',certificate_bound=round(bound,5),certificate_authorized=ca,certificate_wrong=cw,authorized=au,wrong=wr,observations=350))
def save(name,data):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('batch_results.csv',rows)
summary=[]
for regime in ['ALL']+REGIMES:
    for policy in POLICIES:
        s=[r for r in rows if r['policy']==policy and (regime=='ALL' or r['regime']==regime)]
        n=sum(r['observations'] for r in s);a=sum(r['authorized'] for r in s);w=sum(r['wrong'] for r in s)
        summary.append(dict(regime=regime,policy=policy,observations=n,authorized=a,wrong=w,authorization_pct=round(100*a/n,3),conditional_error_pct=round(100*w/a,3) if a else '',unconditional_error_pct=round(100*w/n,3),transferred_batches=sum(r['transfer'] for r in s),abstained_batches=sum(r['radius']=='abstain' for r in s)))
save('results.csv',summary)
print(summary)
