#!/usr/bin/env python3
"""AETHER-099B: conditional revocation, development/holdout split, synthetic only."""
import csv, json, hashlib
from pathlib import Path
import numpy as np
from scipy.stats import beta

OUT=Path(__file__).resolve().parent
KINDS=('abrupt','gradual','decoy')
DEV=range(99101,99141)
TEST=range(99201,99281)
T=100; AUD=140; ACTIONS=150
COST_WRONG=10.; COST_WITHHELD=.05; COST_AUDIT=.01; COST_SENSOR=.2
# Candidate policies specified before the held-out seed sequence is examined.
CANDIDATES=[(err,signal,cooldown) for err in (1,2,3) for signal in (1.5,2.,2.5) for cooldown in (0,1)]

def save(filename,rows):
    with (OUT/filename).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def episode(seed,kind):
    rng=np.random.default_rng(seed+dict(abrupt=0,gradual=10000,decoy=20000)[kind]);start=int(rng.integers(25,41));end=start+26
    risk=[];means=[]
    for t in range(T):
        j=t-start
        if kind=='abrupt':p=.065 if 0<=j<26 else .003
        elif kind=='gradual':p=.003+(.065-.003)*min(1.,j/8) if 0<=j<26 else .003
        else:p=.003
        risk.append(p);means.append(2.8 if 0<=j<26 else 0.)
    r=np.array(risk)
    return start,end,r,rng.binomial(AUD,r),rng.binomial(ACTIONS,r),rng.normal(means,1.)

# Precompute exact one-sided binomial upper bounds for the audit window.
UP={n:np.array([1. if i==n else beta.ppf(.95,i+1,n-i) for i in range(n+1)]) for n in (140,280,420,560,700)}

def trial(seed,kind,policy,params=None,detail=False):
    start,end,risk,audit,wrong,sensor=episode(seed,kind)
    recent=[];susp=0;rows=[]
    totals=dict(unsafe_authorized=0,safe_withheld=0,wrong=0,withheld_actions=0,sensor_probes=0,alarm_count=0,actions=0)
    for t in range(T):
        ae=int(audit[t]);recent=(recent+[ae])[-5:]
        bound=float(UP[len(recent)*AUD][sum(recent)])
        rolling_allow=bound<=.02
        probe=False;alarm=False
        if policy=='always':
            probe=True; alarm=bool(sensor[t]>=2.)
            if alarm:susp=3
            elif susp>0:
                if sensor[t]<1.:susp-=1
                else:susp=3
        elif policy=='conditional':
            error_gate,signal_gate,cooldown=params
            # Request the sensor only when an ordinary audit would authorize,
            # and today's audit is anomalous enough to make a warning relevant.
            probe=bool(rolling_allow and ae>=error_gate)
            alarm=bool(probe and sensor[t]>=signal_gate)
            if alarm:susp=1+cooldown
        allow=bool(rolling_allow and susp==0 and not alarm)
        if policy=='conditional' and susp>0 and not alarm:susp-=1
        bad=bool(risk[t]>.02)
        totals['unsafe_authorized']+=int(allow and bad)
        totals['safe_withheld']+=int(not allow and not bad)
        totals['wrong']+=int(wrong[t]) if allow else 0
        totals['withheld_actions']+=0 if allow else ACTIONS
        totals['sensor_probes']+=int(probe)
        totals['alarm_count']+=int(alarm)
        totals['actions']+=int(allow)
        if detail:
            rows.append(dict(seed=seed,scenario=kind,tick=t+1,policy=policy,shift_start=start+1,shift_end=end+1,
                true_risk=round(float(risk[t]),6),audit_errors=ae,audit_bound=round(bound,6),
                proxy_observation=round(float(sensor[t]),6) if probe else '',probe=int(probe),alarm=int(alarm),
                decision='ACT' if allow else 'HOLD',unsafe_authorized=int(allow and bad),
                safe_withheld=int(not allow and not bad),wrong=int(wrong[t]) if allow else 0))
        # a one-tick alarm holds the current decision, not a future tick, unless cooldown > 0
    totals['cost']=round(COST_WRONG*totals['wrong']+COST_WITHHELD*totals['withheld_actions']+AUD*COST_AUDIT*T+COST_SENSOR*totals['sensor_probes'],2)
    return totals,rows

def evaluate(seeds,params,detail=False):
    summary={};traces=[];seedrows=[]
    for kind in KINDS:
        for seed in seeds:
            for policy in ('rolling','always','conditional'):
                res,rs=trial(seed,kind,policy,params,detail)
                seedrows.append(dict(seed=seed,scenario=kind,policy=policy,**res))
                if detail:traces.extend(rs)
                key=(kind,policy)
                z=summary.setdefault(key,{k:0 for k in res})
                for k,val in res.items():z[k]+=val
    return summary,seedrows,traces

def metric(summary,policy,key):return sum(summary[(kind,policy)][key] for kind in KINDS)

def gates(summary,seeds):
    unsafe_base=metric(summary,'rolling','unsafe_authorized');unsafe=metric(summary,'conditional','unsafe_authorized')
    safe=metric(summary,'conditional','safe_withheld')-metric(summary,'rolling','safe_withheld')
    safe_inspections=sum(T*len(seeds) for kind in KINDS)-sum(sum(episode(seed,kind)[2]>.02) for kind in KINDS for seed in seeds)
    cost=metric(summary,'conditional','cost')-metric(summary,'rolling','cost')
    return dict(unsafe_reduction=round((unsafe_base-unsafe)/max(1,unsafe_base),5),extra_safe_holds=safe,
       extra_safe_hold_fraction=round(safe/safe_inspections,6),cost_difference=round(cost,2),
       pass_all=bool(unsafe<=.8*unsafe_base and cost<=0 and safe<=.05*safe_inspections))

def main():
    options=[]
    for prm in CANDIDATES:
        summary,_,_=evaluate(DEV,prm)
        g=gates(summary,DEV)
        options.append(dict(audit_error_gate=prm[0],sensor_gate=prm[1],cooldown=prm[2],**g))
    save('development_options.csv',options)
    eligible=[x for x in options if x['pass_all']]
    # Deterministic selection: cheapest passing rule, then least sensor spend/tie values.
    if eligible:
        selected=min(eligible,key=lambda x:(x['cost_difference'],x['extra_safe_holds'],x['audit_error_gate'],x['sensor_gate'],x['cooldown']))
    else:
        selected=min(options,key=lambda x:(x['cost_difference'],x['extra_safe_holds'],x['audit_error_gate'],x['sensor_gate'],x['cooldown']))
    prm=(selected['audit_error_gate'],selected['sensor_gate'],selected['cooldown'])
    summary,seedrows,traces=evaluate(TEST,prm,True)
    save('seed_results.csv',seedrows)
    save('tick_audit.csv',traces)
    results=[]
    for kind in (*KINDS,'ALL'):
        for policy in ('rolling','always','conditional'):
            if kind=='ALL':z={k:sum(summary[(name,policy)][k] for name in KINDS) for k in next(iter(summary.values()))}
            else:z=summary[(kind,policy)]
            results.append(dict(scenario=kind,policy=policy,seeds=len(TEST)*(len(KINDS) if kind=='ALL' else 1),**{k:round(v,2) for k,v in z.items()}))
    save('results.csv',results)
    g=gates(summary,TEST)
    counter=[]
    for kind in KINDS:
        for seed in TEST:
            r0=next(r for r in seedrows if r['seed']==seed and r['scenario']==kind and r['policy']=='rolling')
            r1=next(r for r in seedrows if r['seed']==seed and r['scenario']==kind and r['policy']=='conditional')
            if r1['safe_withheld']>r0['safe_withheld'] or r1['unsafe_authorized']>r0['unsafe_authorized']:
                counter.append(dict(seed=seed,scenario=kind,rolling_safe_withheld=r0['safe_withheld'],
                  conditional_safe_withheld=r1['safe_withheld'],rolling_unsafe_authorized=r0['unsafe_authorized'],
                  conditional_unsafe_authorized=r1['unsafe_authorized'],cost_delta=round(r1['cost']-r0['cost'],2)))
    save('counterexamples.csv',counter or [dict(seed='',scenario='none',rolling_safe_withheld='',conditional_safe_withheld='',rolling_unsafe_authorized='',conditional_unsafe_authorized='',cost_delta='')])
    m=dict(bound='AETHER-099B',version='1',development=[min(DEV),max(DEV)],holdout_seeds=[min(TEST),max(TEST)],
       selected_params=dict(audit_errors_at_least=prm[0],sensor_signal_at_least=prm[1],cooldown=prm[2]),
       development_pass=selected['pass_all'],holdout=g,phase_percent=50 if g['pass_all'] else 37.5,
       cost=dict(wrong=10,withheld=.05,audit_label=.01,sensor_probe=.2),
       notes=['Risk truth used only for evaluation and generating synthetic episodes','Prior trial failure retained in AETHER-099',
              'Selection occurs on development seeds; 099B holdout never used for threshold choice'])
    (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(selected=selected,holdout=g,results=results),indent=2))
if __name__=='__main__':main()