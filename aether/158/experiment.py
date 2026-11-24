#!/usr/bin/env python3
"""AETHER-158: deterministic simulated drift/alarm acceptance.
No hardware-connected reference; operational authority remains HOLD.
This exact script can be run from GitHub checkout or evidence archive.
"""
import csv, hashlib, hmac, json
from pathlib import Path

OUT=Path(__file__).resolve().parent
CASES=("clean","legitimate_rotation","slow_drift","abrupt_drift",
       "suppressed_alarm","delayed_alarm","stale_drift_record","baseline_forgery")
KEY=b"AETHER158-MOCK-EXTERNAL-INSTRUMENT"
BENCH=b"AETHER158-MOCK-BENCH"
LIMIT=.025
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def seal(x,key):
    return dict(x,mac=hmac.new(key,canonical(x),hashlib.sha256).hexdigest())
def authentic(x,key):
    if not isinstance(x,dict):return False
    mac=str(x.get("mac",""))
    plain={k:v for k,v in x.items() if k!="mac"}
    return hmac.compare_digest(mac,hmac.new(key,canonical(plain),hashlib.sha256).hexdigest())

def specimen(seed,case,t):
    """Ground truth is only for the test scorer, never a policy parameter."""
    bad=case not in CASES[:2] and 6<=t<14
    truth=.045 if bad else .005
    generation=2 if case=="legitimate_rotation" and t>=10 else 1
    nonce=digest(canonical([seed,case,t]))[:24]
    acquisition=dict(device="REF-158",generation=generation,tick=t,nonce=nonce,
       source="SIMULATED-INSTRUMENT",path="ACQ-A",measured=truth,
       uncertainty=.0005,drift_per_tick=.0003,
       drift_limit=.001,baseline_epoch=t,alarm=int(truth>LIMIT),
       alarm_latency_ms=20,alarm_deadline_ms=50,expires_tick=t+1)
    bench=dict(device="REF-158",generation=generation,tick=t,nonce=nonce,
       observed=truth,alarm=int(truth>LIMIT),alarm_latency_ms=20)
    if bad:
        if case=="slow_drift":
            acquisition["drift_per_tick"]=.002
        elif case=="abrupt_drift":
            acquisition["drift_per_tick"]=.01
        elif case=="suppressed_alarm":
            acquisition["alarm"]=0
        elif case=="delayed_alarm":
            acquisition["alarm_latency_ms"]=120
        elif case=="stale_drift_record":
            acquisition["expires_tick"]=t
        elif case=="baseline_forgery":
            acquisition["baseline_epoch"]=t-1
    return truth,seal(acquisition,KEY),seal(bench,BENCH)

def decide(acquisition,bench):
    """Blind policy: only signed observations, no seed/case/truth labels."""
    if not authentic(acquisition,KEY) or not authentic(bench,BENCH):
        return "HOLD","signature"
    fields=("device","generation","tick","nonce")
    if any(acquisition[k]!=bench[k] for k in fields):
        return "HOLD","binding"
    if acquisition["source"]!="SIMULATED-INSTRUMENT" or acquisition["path"]!="ACQ-A":
        return "HOLD","path"
    t=acquisition["tick"]
    if acquisition["expires_tick"]!=t+1 or acquisition["baseline_epoch"]!=t:
        return "HOLD","stale_baseline"
    if not (0<=acquisition["uncertainty"]<=.001 and
            0<=acquisition["drift_per_tick"]<=acquisition["drift_limit"]<=.001):
        return "HOLD","drift"
    if acquisition["alarm"]!=bench["alarm"]:
        return "HOLD","alarm_disagreement"
    if not (0<=acquisition["alarm_latency_ms"]<=acquisition["alarm_deadline_ms"]<=50):
        return "HOLD","alarm_latency"
    if abs(acquisition["measured"]-bench["observed"])>acquisition["uncertainty"]:
        return "HOLD","reference_disagreement"
    upper=max(acquisition["measured"],bench["observed"])+acquisition["uncertainty"]+acquisition["drift_limit"]
    if acquisition["alarm"] or upper>LIMIT:
        return "HOLD","risk_bound"
    return "ACT","simulated_authorization"

def run_episode(seed,case,policy):
    events=[];previous="0"*64
    for t in range(20):
        truth,observation,bench=specimen(seed,case,t)
        if policy=="signed_only":
            action="ACT" if authentic(observation,KEY) else "HOLD"
            reason="signed_only"
        else:
            action,reason=decide(observation,bench)
        r=dict(seed=seed,scenario=case,policy=policy,tick=t,action=action,reason=reason,
          unsafe=int(action=="ACT" and truth>LIMIT),safe_act=int(action=="ACT" and truth<=LIMIT),
          operational_action="HOLD")
        r["previous"]=previous
        r["digest"]=digest(previous.encode()+canonical(r))
        previous=r["digest"]
        events.append(r)
    return events

def chain_is_valid(events):
    previous="0"*64
    for r in events:
        if r["previous"]!=previous:return False
        body={k:v for k,v in r.items() if k!="digest"}
        if digest(previous.encode()+canonical(body))!=r["digest"]:return False
        previous=r["digest"]
    return True

def csv_write(name,records):
    with (OUT/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)

def main():
    checks=[];seeds=[];trace=[]
    for case in CASES:
        for seed in range(158001,158026):
            for policy in ("signed_only","drift_alarm_gated"):
                r=run_episode(seed,case,policy)
                replay=run_episode(seed,case,policy)
                predicates=dict(
                    deterministic_replay=(r==replay),
                    evidence_chain=chain_is_valid(r),
                    tick_order=all(x["tick"]==i for i,x in enumerate(r)),
                    action_bound=len(r)==20 and all(x["action"] in ("ACT","HOLD") for x in r),
                    modeled_safety=(policy!="drift_alarm_gated" or all(x["unsafe"]==0 for x in r)),
                    physical_hold=all(x["operational_action"]=="HOLD" for x in r),
                    safe_fixture_preserved=(case not in CASES[:2] or all(x["safe_act"]==1 for x in r)),
                    blind_policy=("truth" not in decide.__code__.co_varnames and "case" not in decide.__code__.co_varnames))
                checks.extend(dict(seed=seed,scenario=case,policy=policy,gate=k,passed=int(v))
                              for k,v in predicates.items())
                seeds.append(dict(seed=seed,scenario=case,policy=policy,
                  unsafe=sum(x["unsafe"] for x in r),safe_act=sum(x["safe_act"] for x in r)))
                if seed==158001:trace.extend(r)
    results=[]
    for case in (*CASES,"ALL"):
        for policy in ("signed_only","drift_alarm_gated"):
            rs=[x for x in seeds if x["policy"]==policy and (case=="ALL" or case==x["scenario"])]
            results.append(dict(scenario=case,policy=policy,episodes=len(rs),
                  unsafe=sum(x["unsafe"] for x in rs),
                  safe_act=sum(x["safe_act"] for x in rs),operational_act=0))
    csv_write("checks.csv",checks)
    csv_write("seed_results.csv",seeds)
    csv_write("trace_samples.csv",trace)
    csv_write("results.csv",results)
    score={(r["scenario"],r["policy"]):r for r in results}
    passed=(len(checks)==3200 and all(x["passed"] for x in checks)
      and score["ALL","signed_only"]["unsafe"]==1200
      and score["ALL","drift_alarm_gated"]["unsafe"]==0
      and score["ALL","drift_alarm_gated"]["safe_act"]==2800
      and score["clean","drift_alarm_gated"]["safe_act"]==500
      and score["legitimate_rotation","drift_alarm_gated"]["safe_act"]==500)
    manifest=dict(bound="AETHER-158",phase="X",status="PASS" if passed else "FAIL",
      mode="SYNTHETIC ONLY",checks=len(checks),checks_passed=sum(x["passed"] for x in checks),
      episodes_per_policy=200,decisions_per_policy=4000,baseline_unsafe=1200,
      gated_unsafe=0 if passed else score["ALL","drift_alarm_gated"]["unsafe"],
      safe_dry_run=score["ALL","drift_alarm_gated"]["safe_act"],operational_act=0,
      synthetic_setup_readiness_percent=75 if passed else 62.5,
      physical_qualification_percent=0,physical_measurements=0,
      limits=["Software fixtures know truth; no physical instrument was connected",
      "Simulated alarm latency cannot certify physical response time",
      "Mock HMAC credentials cannot establish independent metrological traceability"])
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
    if not passed:raise SystemExit(1)
if __name__=="__main__":main()
