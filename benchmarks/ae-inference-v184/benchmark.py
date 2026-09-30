#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "kernel" / "generative" / "ae-inference-v184" / "engine.py"

spec = importlib.util.spec_from_file_location("oasis_v184_engine", ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)

Atom = engine.Atom
Rule = engine.Rule
InferenceEngine = engine.InferenceEngine

def timed(fn, repeats=5, warmups=1):
    for _ in range(warmups):
        fn()
    vals=[]
    payload=None
    for _ in range(repeats):
        t0=time.perf_counter()
        payload=fn()
        vals.append(time.perf_counter()-t0)
    return {
        "seconds_median": statistics.median(vals),
        "seconds_min": min(vals),
        "seconds_max": max(vals),
        "repeats": repeats,
        "payload": payload,
    }

def v183_micro(iterations=5000):
    rules=engine.v183_rules()
    seed=(Atom("ternary",("+1",)),)
    nderived=0
    for _ in range(iterations):
        e=InferenceEngine(rules, seed, source="bench")
        nderived += e.saturate()
        assert Atom("image",("0&1",)) in e.facts
    return {"iterations":iterations,"derived":nderived,"final_facts_per_iter":2}

def unary_pipeline(n=10000):
    axioms=tuple(Atom("src",(str(i),)) for i in range(n))
    rules=(
        Rule("r1",(Atom("src",("?x",)),),Atom("seen",("?x",))),
        Rule("r2",(Atom("seen",("?x",)),),Atom("done",("?x",))),
    )
    e=InferenceEngine(rules,axioms,source="bench")
    derived=e.saturate()
    assert derived==2*n
    assert len(e.facts)==3*n
    return {"seed_facts":n,"derived":derived,"final_facts":len(e.facts)}

def binary_join(n=500):
    axioms=tuple(Atom("left",(str(i),)) for i in range(n))+tuple(Atom("right",(str(i),)) for i in range(n))
    rules=(Rule("join",(Atom("left",("?x",)),Atom("right",("?x",))),Atom("joined",("?x",))),)
    e=InferenceEngine(rules,axioms,source="bench")
    derived=e.saturate()
    assert derived==n
    return {"seed_facts":2*n,"derived":derived,"final_facts":len(e.facts)}

def transitive_closure(n=20):
    axioms=tuple(Atom("reach",(str(i),str(i+1))) for i in range(n-1))
    rules=(Rule(
        "transitive",
        (Atom("reach",("?x","?y")),Atom("reach",("?y","?z"))),
        Atom("reach",("?x","?z"))
    ),)
    e=InferenceEngine(rules,axioms,source="bench")
    derived=e.saturate()
    expected=n*(n-1)//2
    assert len(e.facts)==expected, (len(e.facts),expected)
    return {"nodes":n,"seed_facts":n-1,"derived":derived,"final_facts":len(e.facts)}

def run_case(name, fn, unit_count_key, repeats=5, warmups=1):
    r=timed(fn,repeats=repeats,warmups=warmups)
    p=r.pop("payload")
    count=p[unit_count_key]
    sec=r["seconds_median"]
    logical_terms=max(1,p.get("derived",0)*2)
    return {
        "name":name,
        **p,
        **r,
        "throughput_per_second": count/sec if sec else math.inf,
        "logical_terms_per_second_approx": logical_terms/sec if sec else math.inf,
    }

def main():
    cases=[
        run_case("v183_microcycle",lambda:v183_micro(5000),"iterations",repeats=5,warmups=1),
        run_case("unary_two_stage_pipeline",lambda:unary_pipeline(10000),"derived",repeats=5,warmups=1),
        run_case("binary_keyed_join",lambda:binary_join(500),"derived",repeats=5,warmups=1),
        run_case("transitive_closure_n20",lambda:transitive_closure(20),"derived",repeats=3,warmups=1),
    ]
    result={
        "engine":"OaSIs Deterministic Inference Engine v184",
        "sealed_head":"107ba5911f3a38d2f661e096789c22aca7fb1521",
        "benchmark_scope":"single-process CPython; deterministic forward chaining; no network in timed regions",
        "important_note":"logical_terms_per_second_approx is NOT an LLM tokenizer metric; derivations/sec and fixed-point latency are the meaningful engine metrics.",
        "runner":{
            "python":sys.version.split()[0],
            "platform":platform.platform(),
            "machine":platform.machine(),
            "processor":platform.processor(),
            "cpu_count":os.cpu_count(),
        },
        "cases":cases,
    }
    print(json.dumps(result,indent=2))
    Path("benchmark-result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
