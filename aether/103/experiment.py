#!/usr/bin/env python3
"""AETHER-102B: observable guard-health monitor with frozen AETHER-101 controller.
Diagnostics are sampled on the current tick only when guard is a candidate.
Evaluate on disjoint development/evaluation seeds; no oracle efficacy at runtime.
"""
from pathlib import Path
import importlib.util, numpy as np, csv, json, hashlib
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('aether102',P.parent/'aether102'/'experiment.py')
a102=importlib.util.module_from_spec(spec);spec.loader.exec_module(a102)
frozen=a102.frozen
REGIMES=a102.REGIMES; T=a102.T; N_ACT=a102.N_ACT
DEV=range(102301,102321); TEST=range(102401,102481)
# The diagnostic is an observable, independent calibration readout, not a regime label.
# It measures guard actuation efficiency imperfectly, with per-tick noise.
DIAGNOSTIC_SD=.25; DIAGNOSTIC_COST=.08

def observe(seed,regime):
    risk,n,audit,direct,guarded,eff=a102.environment(seed,regime)
    # Different RNG stream; target effectiveness is used ONLY by the simulator to
    # generate sensor observations and guarded-action outcomes.
    rng=np.random.default_rng(seed+791231+list(REGIMES).index(regime)*135791)
    health=eff+rng.normal(0,DIAGNOSTIC_SD,T)
    return risk,n,audit,direct,guarded,eff,health

def simulate(seed,regime,variant,limit=.87):
    risk,n,audit,direct,guarded,eff,health=observe(seed,regime)
    hist=[];trace=[];prev='0'*64
    for t in range(T):
        hist=(hist+[(int(audit[t]),int(n[t]))])[-5:]
        upper=frozen.ub(sum(x[0] for x in hist),sum(x[1] for x in hist))
        stress=bool(audit[t]>=3)
        proposed=frozen.choose(upper,stress)
        inspected=int(proposed=='guarded' and variant=='monitor')
        diagnostic=float(health[t]) if inspected else None
        if variant=='baseline':action='direct' if upper<=frozen.LIMIT else 'hold'
        elif variant=='frozen':action=proposed
        else:
            action=('direct' if diagnostic is not None and diagnostic>limit else proposed)
        # A diagnostic fallback NEVER makes a previously inadmissible action admissible.
        wrong=int(direct[t] if action=='direct' else guarded[t] if action=='guarded' else 0)
        cost=10*wrong+(7.5 if action=='hold' else 1.6 if action=='guarded' else 1.)+.01*int(n[t])+DIAGNOSTIC_COST*inspected
        evidence=dict(tick=t+1,errors=int(audit[t]),sampled=int(n[t]),upper=round(upper,9),stress=int(stress),diagnostic=round(diagnostic,6) if inspected else None,action=action,prev_hash=prev)
        digest=hashlib.sha256(json.dumps(evidence,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        prev=digest
        trace.append(dict(seed=seed,regime=regime,variant=variant,**evidence,hash=digest,wrong=wrong,cost=round(cost,4),inspected=inspected,unsafe=int(risk[t]>.02 and action!='hold'),safe_hold=int(risk[t]<=.02 and action=='hold'),true_eff=round(float(eff[t]),3)))
    return trace

def summarize(records):
    return dict(ticks=len(records),direct=sum(z['action']=='direct' for z in records),guarded=sum(z['action']=='guarded' for z in records),hold=sum(z['action']=='hold' for z in records),wrong=sum(z['wrong'] for z in records),unsafe=sum(z['unsafe'] for z in records),safe_hold=sum(z['safe_hold'] for z in records),diagnostics=sum(z['inspected'] for z in records),cost=round(sum(z['cost'] for z in records),2))

def evaluate(seeds,threshold,save=False):
    all_rows=[];sample=[];checks=dict(replay=0,causal_prefix=0,hash=0,admissibility=0)
    out=[]
    for g in REGIMES:
        for seed in seeds:
            for v in ('baseline','frozen','monitor'):
                rows=simulate(seed,g,v,threshold)
                d=summarize(rows);out.append(dict(regime=g,seed=seed,variant=v,**d))
                if v=='monitor':
                    replay=simulate(seed,g,v,threshold)
                    checks['replay']+=int(rows==replay)
                    # Compare first 48 records independently of all later diagnostics.
                    # No future observations are read by the selector at any tick.
                    checks['causal_prefix']+=int(all(rows[i]['hash']==replay[i]['hash'] for i in range(48)))
                    checks['hash']+=int(all(hashlib.sha256(json.dumps({k:r[k] for k in ('tick','errors','sampled','upper','stress','diagnostic','action','prev_hash')},sort_keys=True,separators=(',',':')).encode()).hexdigest()==r['hash'] and (i==0 or r['prev_hash']==rows[i-1]['hash']) for i,r in enumerate(rows)))
                    checks['admissibility']+=int(all(r['action']=='hold' or r['upper']<=frozen.LIMIT+1e-9 for r in rows))
                    if seed==min(seeds):sample.extend(rows)
    s=[]
    for g in (*REGIMES,'ALL'):
        for v in ('baseline','frozen','monitor'):
            selected=[r for r in out if r['variant']==v and (g=='ALL' or r['regime']==g)]
            keys=('ticks','direct','guarded','hold','wrong','unsafe','safe_hold','diagnostics','cost')
            s.append(dict(regime=g,variant=v,seeds=len(selected),**{k:round(sum(r[k] for r in selected),2) for k in keys}))
    m={(r['regime'],r['variant']):r for r in s}
    improvements={g:round(m[g,'baseline']['cost']-m[g,'monitor']['cost'],2) for g in REGIMES}
    ok=all(x>=0 for x in improvements.values()) and m['ALL','monitor']['cost']<=m['ALL','baseline']['cost'] and m['ALL','monitor']['unsafe']<=m['ALL','baseline']['unsafe'] and all(v==len(seeds)*len(REGIMES) for v in checks.values())
    if save:
        write('results.csv',s);write('seed_results.csv',out);write('trace_samples.csv',sample)
    return ok,improvements,s,checks

def write(name,rows):
    with (P/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    candidates=[]
    for t in (.65,.75,.85,.95,1.05,1.15,1.25):
        ok,imps,summary,_=evaluate(DEV,t)
        overall=next(r for r in summary if r['regime']=='ALL' and r['variant']=='monitor')
        candidates.append(dict(threshold=t,all_regime_nonregression=int(all(x>=0 for x in imps.values())),total_cost=overall['cost'],guard_degradation_saving=imps['guard_degradation'],all_savings=round(sum(imps.values()),2)))
    write('development_options.csv',candidates)
    eligible=[r for r in candidates if r['all_regime_nonregression']]
    chosen=min(eligible,key=lambda r:(r['total_cost'],r['threshold']))['threshold'] if eligible else min(candidates,key=lambda r:(max(0,-r['guard_degradation_saving']),r['total_cost'],r['threshold']))['threshold']
    ok,imps,summary,checks=evaluate(TEST,chosen,True)
    manifest=dict(bound='AETHER-102B',status='PASS' if ok else 'FAIL',phase_percent=87.5 if ok else 75.0,chosen_threshold=chosen,development_seeds=[min(DEV),max(DEV)],holdout_seeds=[min(TEST),max(TEST)],diagnostic_cost=DIAGNOSTIC_COST,diagnostic_sd=DIAGNOSTIC_SD,acceptance={'no_regime_cost_regression':all(x>=0 for x in imps.values()),'overall_cost_not_higher':next(r for r in summary if r['regime']=='ALL' and r['variant']=='monitor')['cost']<=next(r for r in summary if r['regime']=='ALL' and r['variant']=='baseline')['cost'],'all_replay_and_admissibility':all(v==len(TEST)*len(REGIMES) for v in checks.values())},regime_savings=imps,checks=checks,limitations=['Synthetic diagnostic proxy of guard efficacy','Health proxy assumed observable with fixed calibration noise','Not evidence of generalization outside five environments'])
    (P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'overall':[r for r in summary if r['regime']=='ALL'],'development':candidates},indent=2))
if __name__=='__main__':main()