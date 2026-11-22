#!/usr/bin/env python3
"""AETHER-111 stress-test of frozen AETHER-110 controller, no retuning.
Requires NumPy, SciPy; run from a checkout of the oasis repository.
"""
from pathlib import Path
import csv,hashlib,importlib.util,json
import numpy as np
HERE=Path(__file__).resolve().parent
UP=HERE.parent/'110'/'experiment.py'
spec=importlib.util.spec_from_file_location('frozen_aether110',UP)
frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)
KINDS=('price_shock','sensor_dropout','hidden_correlation','abrupt_spike','moving_oscillation')
SEEDS=range(111101,111181);BUDGET=11000;T=frozen.T

def episode(seed,kind):
    rng=np.random.default_rng(int.from_bytes(hashlib.sha256(f'111:{seed}:{kind}'.encode()).digest()[:8],'big'))
    data=[]
    for t in range(T):
        if kind=='price_shock':p=.003 if t<12 else .007
        elif kind=='sensor_dropout':p=.003
        elif kind=='hidden_correlation':p=.003 if t<8 or t>=17 else .048
        elif kind=='abrupt_spike':p=.003 if t<9 or t>=17 else .11
        else:p=.003 if (t%5)<2 else .057
        if kind=='hidden_correlation':
            x=np.repeat(rng.binomial(1,p,56).astype(np.int8),10)
        elif kind=='sensor_dropout' and 8<=t<19:
            x=np.zeros(560,dtype=np.int8)
        else:x=rng.binomial(1,p,560).astype(np.int8)
        data.append((p,x,int(rng.binomial(150,p))))
    return data

def stress(seed,kind,policy):
    data=episode(seed,kind)
    result,trace=frozen.run(seed,kind,policy,BUDGET,data,trace=True)
    multiplier=6.0 if kind=='price_shock' else 1.0
    realized=10*result['wrong']+7.5*result['holds']+.01*multiplier*result['roots']
    result.update(realized_cost=round(realized,2),scenario=kind)
    replay,_=frozen.run(seed,kind,policy,BUDGET,data,trace=False)
    assert replay['final_hash']==result['final_hash']
    assert result['acts']+result['holds']==T
    assert sum(x['roots_bought'] for x in trace)<=BUDGET
    perturb=list(data)
    rng=np.random.default_rng(seed+4512)
    for t in range(12,T):
        p,x,w=perturb[t];perturb[t]=(p,rng.binomial(1,.5,560).astype(np.int8),w)
    _,changed=frozen.run(seed,kind,policy,BUDGET,perturb,trace=True)
    assert [x['hash'] for x in trace[:12]]==[x['hash'] for x in changed[:12]]
    return result,trace

def write(filename,rows):
    with (HERE/filename).open('w',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    rows=[];samples=[]
    for kind in KINDS:
        for seed in SEEDS:
            for policy in ('fixed','adaptive'):
                row,trace=stress(seed,kind,policy)
                rows.append(row)
                if seed==min(SEEDS):samples.extend(trace)
    summary=[]
    for kind in (*KINDS,'ALL'):
        for policy in ('fixed','adaptive'):
            r=[v for v in rows if v['policy']==policy and (kind=='ALL' or v['scenario']==kind)]
            summary.append(dict(scenario=kind,policy=policy,cases=len(r),acts=sum(x['acts'] for x in r),holds=sum(x['holds'] for x in r),roots=sum(x['roots'] for x in r),wrong=sum(x['wrong'] for x in r),unsafe_authorized=sum(x['unsafe_authorized'] for x in r),safe_holds=sum(x['safe_holds'] for x in r),realized_cost=round(sum(x['realized_cost'] for x in r),2)))
    comparisons=[]
    for kind in KINDS:
        f=next(x for x in summary if x['scenario']==kind and x['policy']=='fixed')
        a=next(x for x in summary if x['scenario']==kind and x['policy']=='adaptive')
        comparisons.append(dict(scenario=kind,cost_savings=round(f['realized_cost']-a['realized_cost'],2),unsafe_delta=a['unsafe_authorized']-f['unsafe_authorized'],act_delta=a['acts']-f['acts'],pass_cost=a['realized_cost']<=f['realized_cost'],pass_unsafe=a['unsafe_authorized']<=f['unsafe_authorized']))
    accepted=all(x['pass_cost'] and x['pass_unsafe'] for x in comparisons)
    write('results.csv',summary);write('comparisons.csv',comparisons)
    write('seed_results.csv',rows);write('trace_samples.csv',samples)
    manifest=dict(bound='AETHER-111',phase='IV',status='PASS' if accepted else 'FAILED_STRESS_GATE',phase_pct=87.5 if accepted else 75,seed_range=[min(SEEDS),max(SEEDS)],budget=BUDGET,total_cases=len(rows),replay_and_causal_prefix_checks=len(rows)*2,criteria='No added unsafe authorizations and no cost regression in each unseen scenario',limits=['Unknown correlation and missing packets intentionally have no lineage/availability metadata','Frozen controller is imported unchanged from aether110/experiment.py','Unseen observation tariffs included in realized cost','Synthetic data only'])
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'comparisons':comparisons,'totals':[x for x in summary if x['scenario']=='ALL']},indent=2))
if __name__=='__main__':main()
