#!/usr/bin/env python3
"""AETHER-151: blind adversarial intake rehearsal; exact GitHub source.

The policy sees only submitted evidence, NOT scenario labels or hidden truth.
Scenario truth is used ONLY after decisions for scoring. The 'independent'
bench is a software oracle, NOT physically independent calibration.
No real-world ACT is permitted. One deterministic controller, no quorum.
"""
import csv,hashlib,hmac,json
from pathlib import Path

OUT=Path(__file__).resolve().parent
SEEDS=range(151001,151031)
SCENARIOS=("clean","legitimate_rotation","missing_raw","counter_replay",
           "route_substitution","self_signed_reference","false_reference",
           "unbound_bench")
TICKS=20
LIMIT=.025
DUT_KEY=b"AETHER151_SIMULATED_DUT_ISSUER"
REF_KEY=b"AETHER151_SIMULATED_EXTERNAL_REFERENCE"
BENCH_KEY=b"AETHER151_SIMULATED_BENCH"

def raw(o): return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(o): return hashlib.sha256(o).hexdigest()
def sign(payload,key): return dict(payload,mac=hmac.new(key,raw(payload),hashlib.sha256).hexdigest())
def authentic(receipt,key):
    if not isinstance(receipt,dict): return False
    body={k:v for k,v in receipt.items() if k!="mac"}
    return hmac.compare_digest(str(receipt.get("mac","")),hmac.new(key,raw(body),hashlib.sha256).hexdigest())

def generate(seed,scenario,t):
    # The generator alone knows whether this tick is unsafe.
    adverse=scenario not in SCENARIOS[:2] and 6<=t<14
    actual=.045 if adverse else .005
    gen=2 if scenario=="legitimate_rotation" and t>=10 else 1
    nonce=sha(raw((seed,scenario,t)))[:24]
    common=dict(serial="DUT-151",generation=gen,tick=t,counter=t,
                nonce=nonce,path="MEASURE-A")
    sample=raw(dict(serial="REF-151",tick=t,nonce=nonce,reading=actual))
    dut=sign(dict(common,reported=.005),DUT_KEY)
    refdata=dict(common,root="EXTERNAL-ROOT-MOCK",source_serial="REF-151",
       measured=actual,uncertainty=.0004,expires=t+1,
       raw_sha=sha(sample),calibration_root="TRACEABLE-MOCK")
    benchdata=dict(common,source_serial="BENCH-151",observed=actual,
       uncertainty=.0004,expires=t+1)
    if adverse:
        if scenario=="missing_raw": sample=b""
        elif scenario=="counter_replay": refdata["counter"]=t-1
        elif scenario=="route_substitution": refdata["path"]="BYPASS-B"
        elif scenario=="self_signed_reference": refdata["root"]="DUT-SELF-ISSUED"
        elif scenario=="false_reference": refdata["measured"]=.005
        elif scenario=="unbound_bench": benchdata["nonce"]="WRONG-CHALLENGE"
    return actual,dict(dut=dut,ref=sign(refdata,REF_KEY),
                       bench=sign(benchdata,BENCH_KEY),sample=sample)

def decide(submission):
    """Blind controller: no seed, scenario, fault label, or hidden truth argument."""
    d,r,b,s=(submission[k] for k in ("dut","ref","bench","sample"))
    if not (authentic(d,DUT_KEY) and authentic(r,REF_KEY) and authentic(b,BENCH_KEY)):
        return "HOLD","issuer"
    if not s or sha(s)!=r["raw_sha"]: return "HOLD","raw"
    for field in ("serial","generation","tick","counter","nonce","path"):
        if not(d[field]==r[field]==b[field]): return "HOLD","binding"
    if d["serial"]!="DUT-151" or d["path"]!="MEASURE-A":
        return "HOLD","device"
    if r["root"]!="EXTERNAL-ROOT-MOCK" or r["calibration_root"]!="TRACEABLE-MOCK":
        return "HOLD","reference_root"
    if r["source_serial"]!="REF-151" or b["source_serial"]!="BENCH-151":
        return "HOLD","source"
    if r["expires"]!=r["tick"]+1 or b["expires"]!=b["tick"]+1:
        return "HOLD","expiry"
    if not(0<=r["uncertainty"]<=.001 and 0<=b["uncertainty"]<=.001):
        return "HOLD","uncertainty"
    if abs(r["measured"]-b["observed"])>r["uncertainty"]+b["uncertainty"]:
        return "HOLD","contradiction"
    if max(r["measured"]+r["uncertainty"],b["observed"]+b["uncertainty"])>LIMIT:
        return "HOLD","upper_bound"
    return "ACT","synthetic_authorization"

def chain(records):
    prev="0"*64
    for item in records:
        stripped={k:v for k,v in item.items() if k not in ("previous","digest")}
        d=sha(prev.encode()+raw(stripped))
        if item["previous"]!=prev or item["digest"]!=d: return False
        prev=d
    return True

def save(name,records):
    with (OUT/name).open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader();writer.writerows(records)

def episode(seed,scenario,policy):
    records=[];prev="0"*64
    for t in range(TICKS):
        truth,submitted=generate(seed,scenario,t)
        if policy=="signed_only":
            act="ACT" if authentic(submitted["dut"],DUT_KEY) and submitted["dut"]["reported"]<=LIMIT else "HOLD"
            reason="transport_only"
        else:
            act,reason=decide(submitted)
        row=dict(seed=seed,scenario=scenario,policy=policy,tick=t,action=act,
            reason=reason,unsafe=int(act=="ACT" and truth>LIMIT),
            safe_act=int(act=="ACT" and truth<=LIMIT),
            safe_hold=int(act=="HOLD" and truth<=LIMIT),
            operational_action="HOLD")
        digest=sha(prev.encode()+raw(row))
        row["previous"]=prev;row["digest"]=digest;prev=digest
        records.append(row)
    return records

def main():
    checkrows=[];cases=[];samples=[]
    for scenario in SCENARIOS:
        for seed in SEEDS:
            for policy in ("signed_only","blind_intake"):
                a=episode(seed,scenario,policy)
                b=episode(seed,scenario,policy)
                gates=dict(replay=a==b,chain=chain(a),
                  tick_order=all(r["tick"]==i for i,r in enumerate(a)),
                  single_action=len(a)==TICKS and all(r["action"] in ("ACT","HOLD") for r in a),
                  zero_unsafe=policy!="blind_intake" or all(r["unsafe"]==0 for r in a),
                  no_operational_act=all(r["operational_action"]=="HOLD" for r in a),
                  clean_availability=scenario not in SCENARIOS[:2] or all(r["safe_act"]==1 for r in a),
                  no_label_in_policy="scenario" not in decide.__code__.co_varnames and "truth" not in decide.__code__.co_varnames)
                checkrows.extend(dict(scenario=scenario,seed=seed,policy=policy,gate=g,passed=int(v)) for g,v in gates.items())
                cases.append(dict(scenario=scenario,seed=seed,policy=policy,
                     unsafe=sum(r["unsafe"] for r in a),
                     safe_act=sum(r["safe_act"] for r in a),
                     safe_hold=sum(r["safe_hold"] for r in a)))
                if seed==SEEDS.start:samples.extend(a)
    save("checks.csv",checkrows);save("seed_results.csv",cases);save("trace_samples.csv",samples)
    totals=[]
    for sc in (*SCENARIOS,"ALL"):
        for policy in ("signed_only","blind_intake"):
            z=[r for r in cases if r["policy"]==policy and (sc=="ALL" or r["scenario"]==sc)]
            totals.append(dict(scenario=sc,policy=policy,cases=len(z),
                unsafe=sum(r["unsafe"] for r in z),
                safe_act=sum(r["safe_act"] for r in z),safe_hold=sum(r["safe_hold"] for r in z),
                operational_act=0))
    save("results.csv",totals)
    summary={(x["scenario"],x["policy"]):x for x in totals}
    gates=dict(all_checks_pass=all(x["passed"] for x in checkrows),
       baseline_exposes_faults=summary["ALL","signed_only"]["unsafe"]==1440,
       zero_guarded_unsafe=summary["ALL","blind_intake"]["unsafe"]==0,
       clean_retained=summary["clean","blind_intake"]["safe_act"]==600,
       rotation_retained=summary["legitimate_rotation","blind_intake"]["safe_act"]==600,
       operational_hold=all(x["operational_act"]==0 for x in totals))
    manifest=dict(bound="AETHER-151",phase="IX",status="PASS" if all(gates.values()) else "FAIL",
       episodes_per_policy=240,decisions_per_policy=4800,checks=len(checkrows),
       gates=gates,software_readiness_percent=87.5,physical_qualification_percent=0,
       physical_validation="NOT PERFORMED",
       distinction="Policy sees signed submissions only; test scorer sees hidden truth after decision.",
       limits=["Bench reference oracle is software-generated synthetic truth",
               "Mock HMAC roots do not demonstrate hardware independence",
               "Adversarial generator cannot represent unknown physical failure modes",
               "No operational action authorized"])
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(dict(manifest=manifest,overall=[x for x in totals if x["scenario"]=="ALL"]),indent=2))
    if manifest["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
