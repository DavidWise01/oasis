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

def once(fn):
    t0=time.perf_counter()
    payload=fn()
    return time.perf_counter()-t0,payload

def unary(n):
    axioms=tuple(Atom("src",(str(i),)) for i in range(n))
    rules=(
        Rule("r1",(Atom("src",("?x",)),),Atom("mid",("?x",))),
        Rule("r2",(Atom("mid",("?x",)),),Atom("done",("?x",))),
    )
    e=InferenceEngine(rules,axioms,source="stress")
    d=e.saturate()
    assert d==2*n
    return {"derived":d,"facts":len(e.facts)}

def join(n):
    axioms=tuple(Atom("left",(str(i),)) for i in range(n))+tuple(Atom("right",(str(i),)) for i in range(n))
    rules=(Rule("join",(Atom("left",("?x",)),Atom("right",("?x",))),Atom("joined",("?x",))),)
    e=InferenceEngine(rules,axioms,source="stress")
    d=e.saturate()
    assert d==n
    return {"derived":d,"facts":len(e.facts)}

def transitive(n):
    axioms=tuple(Atom("reach",(str(i),str(i+1))) for i in range(n-1))
    rules=(Rule("transitive",(Atom("reach",("?x","?y")),Atom("reach",("?y","?z"))),Atom("reach",("?x","?z"))),)
    e=InferenceEngine(rules,axioms,source="stress")
    d=e.saturate()
    expected=n*(n-1)//2
    assert len(e.facts)==expected
    return {"derived":d,"facts":len(e.facts)}

def series(name,sizes,fn,hard_stop_seconds):
    out=[]
    for n in sizes:
        sec,p=once(lambda:fn(n))
        row={"n":n,"seconds":sec,**p}
        row["derived_per_second"]=p["derived"]/sec if sec else None
        out.append(row)
        if sec>=hard_stop_seconds:
            break
    return {"name":name,"hard_stop_seconds":hard_stop_seconds,"rows":out}

def main():
    result={
      "engine":"OaSIs v184 sealed inference",
      "sealed_head":"107ba5911f3a38d2f661e096789c22aca7fb1521",
      "purpose":"scale-to-failure characterization of exhaustive matcher",
      "series":[
        series("unary_pipeline",[1000,5000,10000,25000,50000,100000],unary,8.0),
        series("keyed_join",[100,250,500,1000,2000,4000,8000],join,8.0),
        series("transitive_closure",[10,15,20,25,30,35,40,50],transitive,8.0)
      ]
    }
    print(json.dumps(result,indent=2))
    Path("stress-result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":
    main()
