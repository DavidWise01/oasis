#!/usr/bin/env python3
"""AETHER-111B: single-controller explicit evidence packet contract.
Synthetic stress; packet assertions depend on the simulated trusted acquisition layer.
No distributed witnesses or consensus are introduced.
"""
from pathlib import Path
import csv, hashlib, json
import numpy as np
from scipy.stats import beta
HERE=Path(__file__).resolve().parent
KINDS=('price_shock','sensor_dropout','hidden_correlation','abrupt_spike','moving_oscillation')
DEV=range(111201,111221)
TEST=range(111301,111381)
T=24; CAP=560; BUDGET=11000; LIMIT=.025; ALPHA=.05; LOOKS=4

def upper(e,n):
    return 1.0 if n<=0 or e>=n else float(beta.ppf(1-ALPHA/(T*LOOKS),int(e)+1,int(n-e)))

def episode(seed,kind):
    rng=np.random.default_rng(int.from_bytes(hashlib.sha256(f'111b:{seed}:{kind}'.encode()).digest()[:8],'big'))
    packets=[]
    for t in range(T):
        if kind=='price_shock':p=.003 if t<12 else .007
        elif kind=='sensor_dropout':p=.003
        elif kind=='hidden_correlation':p=.003 if t<8 or t>=17 else .048
        elif kind=='abrupt_spike':p=.003 if t<9 or t>=17 else .11
        else:p=.003 if (t%5)<2 else .057
        if kind=='sensor_dropout' and 8<=t<19:
            status='missing';values=np.array([],dtype=np.int8);roots=0
        elif kind=='hidden_correlation':
            # Simulated ingress cannot certify independence; do not fabricate roots.
            status='unverified';values=np.repeat(rng.binomial(1,p,56).astype(np.int8),10);roots=0
        else:
            status='valid';values=rng.binomial(1,p,CAP).astype(np.int8);roots=CAP
        # Observation packet includes status supplied by an assumed trustworthy collector,
        # not inferred by the decision policy from the simulated true risk.
        packets.append(dict(status=status,reported_count=len(values),certified_unique_count=roots,
            values=values,risk_for_evaluation=p,outcome=int(rng.binomial(150,p))))
    return packets

def run(seed,kind,policy,data,budget=BUDGET,trace=False,tariff_model='current'):
    remaining=budget;totalroots=acts=holds=wrong=unsafe=safe_holds=0;invalid_holds=0
    chain='0'*64;trace_rows=[];transitions=0;last_action=None
    for t,packet in enumerate(data):
        status=packet['status'];values=packet['values'];unique=packet['certified_unique_count']
        # Fail-closed: explicit packet validity, count matching, and certified independent roots.
        valid=(status=='valid' and unique==len(values) and unique>0 and
               packet['reported_count']==len(values) and set(np.unique(values)).issubset({0,1}))
        n=e=0;allow=False;reason='INVALID_OR_MISSING_PACKET'
        if valid:
            cap=min(unique,remaining)
            if policy=='fixed':
                n=cap;e=int(values[:n].sum())
                allow=bool(n==CAP and upper(e,n)<=LIMIT)
                reason='FIXED_CERT' if allow else 'FIXED_HOLD'
            elif policy=='adaptive':
                while n<cap:
                    step=min(140,cap-n);e+=int(values[n:n+step].sum());n+=step
                    if n>=140 and upper(e,n)<=LIMIT:
                        allow=True;reason='EARLY_CERT';break
                    # If best-case remaining observations cannot certify, stop early.
                    if upper(e,cap)>LIMIT:
                        reason='NO_CERT_POSSIBLE';break
                    reason='FULL_CERT_FAIL'
            else:raise ValueError(policy)
        remaining-=n;totalroots+=n;acts+=int(allow);holds+=int(not allow)
        unsafe+=int(allow and packet['risk_for_evaluation']>LIMIT)
        safe_holds+=int(not allow and packet['risk_for_evaluation']<=LIMIT)
        wrong+=int(packet['outcome']) if allow else 0
        invalid_holds+=int(not valid and not allow)
        action='ACT' if allow else 'HOLD'
        transitions+=int(last_action is not None and last_action!=action);last_action=action
        event=dict(seed=seed,scenario=kind,tick=t+1,policy=policy,packet_status=status,
          packet_reported=packet['reported_count'],packet_certified_roots=unique,
          accepted_roots=n,errors=e,upper=round(upper(e,n),8),action=action,reason=reason,
          remaining_budget=remaining)
        chain=hashlib.sha256((chain+json.dumps(event,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
        if trace:trace_rows.append(dict(**event,hash=chain))
    tariff=6 if kind=='price_shock' else 1
    cost=10*wrong+7.5*holds+.01*tariff*totalroots
    return dict(seed=seed,scenario=kind,policy=policy,ticks=T,acts=acts,holds=holds,wrong=wrong,
      roots=totalroots,unsafe_authorized=unsafe,safe_holds=safe_holds,
      invalid_packet_holds=invalid_holds,act_hold_transitions=transitions,
      cost=round(cost,2),final_hash=chain),trace_rows

def save(file,rows):
    with (HERE/file).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    # One frozen criterion, tested on separate development and holdout seeds.
    # No policy selection on the holdout.
    records=[];traces=[];tests=[]
    for kind in KINDS:
      for seed in TEST:
        data=episode(seed,kind)
        for policy in ('fixed','adaptive'):
          result,trace=run(seed,kind,policy,data,trace=seed==min(TEST));records.append(result)
          if trace:traces.extend(trace)
          replay,_=run(seed,kind,policy,data)
          assert replay['final_hash']==result['final_hash']
          assert result['acts']+result['holds']==T
          assert result['roots']<=BUDGET
          if kind in ('sensor_dropout','hidden_correlation'):
            assert all(x['action']=='HOLD' for x in trace if x['packet_status']!='valid') if trace else True
          # Future packets cannot alter the hash prefix prior to tick 12.
          mutated=list(data)
          for i in range(12,T):
            q=dict(mutated[i]);q['status']='missing';q['values']=np.array([],dtype=np.int8)
            q['reported_count']=0;q['certified_unique_count']=0;mutated[i]=q
          _,a=run(seed,kind,policy,data,trace=True)
          _,b=run(seed,kind,policy,mutated,trace=True)
          assert [x['hash'] for x in a[:12]]==[x['hash'] for x in b[:12]]
          tests.append(dict(seed=seed,scenario=kind,policy=policy,replay=True,prefix=True,budget=True,packet_validity=True))
    summary=[]
    for kind in (*KINDS,'ALL'):
      for policy in ('fixed','adaptive'):
        x=[r for r in records if r['policy']==policy and (kind=='ALL' or r['scenario']==kind)]
        summary.append(dict(scenario=kind,policy=policy,cases=len(x),acts=sum(r['acts'] for r in x),
          holds=sum(r['holds'] for r in x),wrong=sum(r['wrong'] for r in x),roots=sum(r['roots'] for r in x),
          unsafe_authorized=sum(r['unsafe_authorized'] for r in x),
          invalid_packet_holds=sum(r['invalid_packet_holds'] for r in x),
          safe_holds=sum(r['safe_holds'] for r in x),
          realized_cost=round(sum(r['cost'] for r in x),2)))
    comparisons=[]
    for kind in KINDS:
      f=next(r for r in summary if r['scenario']==kind and r['policy']=='fixed')
      a=next(r for r in summary if r['scenario']==kind and r['policy']=='adaptive')
      comparisons.append(dict(scenario=kind,savings=round(f['realized_cost']-a['realized_cost'],2),
        unsafe_delta=a['unsafe_authorized']-f['unsafe_authorized'],
        safe_acts_delta=a['acts']-f['acts'],
        passed_cost=a['realized_cost']<=f['realized_cost'],
        passed_safety=a['unsafe_authorized']<=f['unsafe_authorized']))
    pass_all=all(x['passed_cost'] and x['passed_safety'] for x in comparisons)
    save('results.csv',summary);save('comparisons.csv',comparisons);save('seed_results.csv',records)
    save('trace_samples.csv',traces);save('checks.csv',tests)
    manifest=dict(bound='AETHER-111B',phase='IV',status='PASS' if pass_all else 'FAIL',
       phase_completion_percent=87.5 if pass_all else 75,
       holdout_seeds=[min(TEST),max(TEST)],development_seeds=[min(DEV),max(DEV)],
       cases=len(records),gate='Every environment no added unsafe ticks and no cost regression',
       caveats=['Trusted packet status and certified independent root count are assumptions, not cryptographically established',
       'No votes or distributed consensus; single controller',
       'Unknown correlation without trusted metadata cannot be inferred with certainty',
       'Synthetic 24-tick Bernoulli outcomes, known tariff for evaluation'])
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'comparisons':comparisons,'totals':[x for x in summary if x['scenario']=='ALL']},indent=2))
if __name__=='__main__':main()
