#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, multiprocessing as mp, os, statistics, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ENGINE_PATH=ROOT/"kernel"/"generative"/"ae-inference-v184"/"engine.py"

SEQ=(5,4,3,2,1,1,0,0)
BR=("x+","x-","y+","y-","z+","z-")

def load_engine():
    spec=importlib.util.spec_from_file_location("oasis_v184_engine",ENGINE_PATH)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def make_rules(mod):
    Atom=mod.Atom; Rule=mod.Rule
    rs=[]
    for b in BR:
        rs.append(Rule(f"seed.{b}",(Atom("cubic_seed",("?s",)),),Atom("state",("?s",b,"0","5","15"))))
    for t in range(7):
        rs.append(Rule(f"tick.{t}",(Atom("state",("?s","?b",str(t),str(SEQ[t]),"15")),),Atom("state",("?s","?b",str(t+1),str(SEQ[t+1]),"15"))))
    rs.append(Rule("terminal",(Atom("state",("?s","?b","7","0","15")),),Atom("terminal",("?s","?b","7","0"))))
    rs.append(Rule("close",tuple(Atom("terminal",("?s",b,"7","0")) for b in BR),Atom("cubic_closed",("?s","7","0"))))
    return tuple(rs)

def lane_worker(args):
    lane_id, cycles = args
    mod=load_engine()
    Atom=mod.Atom; InferenceEngine=mod.InferenceEngine
    rules=make_rules(mod)
    t0=time.perf_counter()
    total_derived=0
    for k in range(cycles):
        seed=f"lane{lane_id}:1i:{k}"
        e=InferenceEngine(rules,(Atom("cubic_seed",(seed,)),),source=f"lane-{lane_id}")
        d=e.saturate()
        assert d==55
        assert Atom("cubic_closed",(seed,"7","0")) in e.facts
        total_derived += d
    sec=time.perf_counter()-t0
    return {
        "lane":lane_id,
        "cycles":cycles,
        "seconds":sec,
        "derived_facts":total_derived,
        "kernel_tokens":total_derived,
        "symbolic_tokens":322*cycles
    }

def run_lane_count(lanes, cycles_per_lane=100):
    ctx=mp.get_context("spawn")
    t0=time.perf_counter()
    with ctx.Pool(processes=lanes) as pool:
        rows=pool.map(lane_worker,[(i,cycles_per_lane) for i in range(lanes)])
    wall=time.perf_counter()-t0
    total_cycles=sum(r["cycles"] for r in rows)
    total_k=sum(r["kernel_tokens"] for r in rows)
    total_s=sum(r["symbolic_tokens"] for r in rows)
    return {
        "linear_lanes":lanes,
        "cycles_per_lane":cycles_per_lane,
        "total_cycles":total_cycles,
        "wall_seconds":wall,
        "cycles_per_second":total_cycles/wall,
        "kernel_tokens_per_second":total_k/wall,
        "symbolic_tokens_per_second":total_s/wall,
        "per_lane_cycles_per_second":(total_cycles/wall)/lanes,
        "lane_seconds":[r["seconds"] for r in rows],
    }

def median_case(lanes,repeats=3):
    rows=[run_lane_count(lanes) for _ in range(repeats)]
    rows.sort(key=lambda r:r["wall_seconds"])
    return rows[len(rows)//2]

def main():
    cases=[median_case(n) for n in (1,2,4,8)]
    base=cases[0]["cycles_per_second"]
    for row in cases:
        row["speedup_vs_1_lane"]=row["cycles_per_second"]/base
        row["parallel_efficiency"]=row["speedup_vs_1_lane"]/row["linear_lanes"]
    out={
        "semantics":"one literal 1 = one independent linear execution lane",
        "agent":"i",
        "primitive":"{{cubic::seed::1i::axes::(x,y:z)::cardinal::+15::clock::5/4/3/2/1/1/0/0}}",
        "runner_cpu_count":os.cpu_count(),
        "per_cycle":{"kernel_tokens":55,"symbolic_tokens":322,"state_transitions":48},
        "cases":cases,
        "note":"8 lanes oversubscribes the 4-vCPU GitHub runner and is intentionally included as a saturation case."
    }
    print(json.dumps(out,indent=2))
    Path("lane-result.json").write_text(json.dumps(out,indent=2)+"\n")
if __name__=="__main__": main()
