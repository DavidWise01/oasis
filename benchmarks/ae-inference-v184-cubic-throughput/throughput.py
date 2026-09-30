#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, statistics, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ENGINE_PATH=ROOT/"kernel"/"generative"/"ae-inference-v184"/"engine.py"
spec=importlib.util.spec_from_file_location("oasis_v184_engine",ENGINE_PATH)
engine=importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name]=engine
spec.loader.exec_module(engine)

Atom=engine.Atom
Rule=engine.Rule
InferenceEngine=engine.InferenceEngine

SEQ=(5,4,3,2,1,1,0,0)
BRANCHES=("x+","x-","y+","y-","z+","z-")
CARDINAL="15"

def shared_rules():
    rs=[]
    for b in BRANCHES:
        rs.append(Rule(
            f"seed.{b}",
            (Atom("cubic_seed",("?s",)),),
            Atom("state",("?s",b,"0","5",CARDINAL))
        ))
    for t in range(7):
        rs.append(Rule(
            f"tick.{t}.{t+1}",
            (Atom("state",("?s","?b",str(t),str(SEQ[t]),CARDINAL)),),
            Atom("state",("?s","?b",str(t+1),str(SEQ[t+1]),CARDINAL))
        ))
    rs.append(Rule(
        "terminal.branch",
        (Atom("state",("?s","?b","7","0",CARDINAL)),),
        Atom("terminal",("?s","?b","7","0"))
    ))
    rs.append(Rule(
        "terminal.all6.sync",
        tuple(Atom("terminal",("?s",b,"7","0")) for b in BRANCHES),
        Atom("cubic_closed",("?s","7","0"))
    ))
    return tuple(rs)

RULES=shared_rules()

def run_batch(n):
    seeds=tuple(Atom("cubic_seed",(f"1i#{k}",)) for k in range(n))
    e=InferenceEngine(RULES,seeds,source="throughput")
    t0=time.perf_counter()
    derived=e.saturate()
    sec=time.perf_counter()-t0

    expected=55*n
    assert derived==expected,(derived,expected)
    for k in (0,n-1):
        assert Atom("cubic_closed",(f"1i#{k}","7","0")) in e.facts

    derived_proofs=[p for p in e.proofs.values() if p.kind=="derived"]
    logical_tokens=sum(1+len(p.atom.args) for p in derived_proofs)
    symbolic_bytes=sum(len(p.atom.key.encode("utf-8")) for p in derived_proofs)

    return {
        "cycles":n,
        "seconds":sec,
        "derived_facts":derived,
        "state_transitions":48*n,
        "terminal_facts":6*n,
        "closure_facts":n,
        "logical_tokens":logical_tokens,
        "symbolic_bytes":symbolic_bytes,
        "cycles_per_second":n/sec,
        "derived_facts_per_second":derived/sec,
        "state_transitions_per_second":(48*n)/sec,
        "logical_tokens_per_second":logical_tokens/sec,
        "symbolic_bytes_per_second":symbolic_bytes/sec,
    }

def median_case(n,repeats):
    rows=[run_batch(n) for _ in range(repeats)]
    rows.sort(key=lambda r:r["seconds"])
    return rows[len(rows)//2]

def main():
    sizes=(1,10,50,100,250,500,1000)
    out=[]
    for n in sizes:
        repeats=7 if n<=10 else 3
        row=median_case(n,repeats)
        row["repeats"]=repeats
        out.append(row)
        if row["seconds"]>=8.0:
            break

    result={
        "engine":"OaSIs v184 sealed inference",
        "sealed_head":"107ba5911f3a38d2f661e096789c22aca7fb1521",
        "primitive":"{{cubic::seed::1i::axes::(x,y:z)::cardinal::+15::clock::5/4/3/2/1/1/0/0}}",
        "definition_of_logical_token":"one predicate or one atom argument; this is an engine-local symbolic token, not an LLM/BPE token",
        "per_cycle":{
            "derived_facts":55,
            "state_transitions":48,
            "logical_tokens":322
        },
        "cases":out
    }
    print(json.dumps(result,indent=2))
    Path("result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
