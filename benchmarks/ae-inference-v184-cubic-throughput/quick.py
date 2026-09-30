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
Atom=engine.Atom; Rule=engine.Rule; InferenceEngine=engine.InferenceEngine
SEQ=(5,4,3,2,1,1,0,0)
BR=("x+","x-","y+","y-","z+","z-")

def rules():
    rs=[]
    for b in BR:
        rs.append(Rule(f"seed.{b}",(Atom("cubic_seed",("?s",)),),Atom("state",("?s",b,"0","5","15"))))
    for t in range(7):
        rs.append(Rule(f"tick.{t}",(Atom("state",("?s","?b",str(t),str(SEQ[t]),"15")),),Atom("state",("?s","?b",str(t+1),str(SEQ[t+1]),"15"))))
    rs.append(Rule("terminal",(Atom("state",("?s","?b","7","0","15")),),Atom("terminal",("?s","?b","7","0"))))
    rs.append(Rule("close",tuple(Atom("terminal",("?s",b,"7","0")) for b in BR),Atom("cubic_closed",("?s","7","0"))))
    return tuple(rs)
RULES=rules()

def run(n):
    seeds=tuple(Atom("cubic_seed",(f"1i#{i}",)) for i in range(n))
    e=InferenceEngine(RULES,seeds,source="quick-throughput")
    t0=time.perf_counter(); d=e.saturate(); sec=time.perf_counter()-t0
    assert d==55*n
    derived=[p.atom for p in e.proofs.values() if p.kind=="derived"]
    logical=sum(1+len(a.args) for a in derived)
    bytes_=sum(len(a.key.encode()) for a in derived)
    return {
      "cycles":n,"seconds":sec,"derived_facts":d,"logical_tokens":logical,
      "cycles_per_second":n/sec,
      "derived_facts_per_second":d/sec,
      "state_transitions_per_second":48*n/sec,
      "logical_tokens_per_second":logical/sec,
      "symbolic_bytes_per_second":bytes_/sec
    }

def main():
    rows=[]
    for n in (1,5,10,25,50,100):
        samples=[run(n) for _ in range(5)]
        samples.sort(key=lambda x:x["seconds"])
        rows.append(samples[2])
    out={
      "definition":"logical token = one predicate or one atom argument; NOT an LLM/BPE token",
      "per_cycle":{"derived_facts":55,"state_transitions":48,"logical_tokens":322},
      "rows":rows
    }
    print(json.dumps(out,indent=2))
    Path("quick-result.json").write_text(json.dumps(out,indent=2)+"\n")
if __name__=="__main__": main()
