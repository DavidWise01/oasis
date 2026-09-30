#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, sys, time
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

LITERAL="{{0::{i::1i::uniary::binary::ternary::quarterny::cubic::-+}}}"

def rules():
    return (
        Rule("base_to_uniary",
             (Atom("base1i",("?i",)),),
             Atom("uniary",("?i",))),
        Rule("uniary_to_binary",
             (Atom("uniary",("?i",)),),
             Atom("binary",("?i","?i"))),
        Rule("binary_to_ternary",
             (Atom("binary",("?i","?i")),),
             Atom("ternary",("?i","?i","?i"))),
        Rule("ternary_to_quarterny",
             (Atom("ternary",("?i","?i","?i")),),
             Atom("quarterny",("?i","?i","?i","?i"))),
        Rule("quarterny_to_cubic_minus",
             (Atom("quarterny",("?i","?i","?i","?i")),),
             Atom("cubic",("-", "?i"))),
        Rule("quarterny_to_cubic_plus",
             (Atom("quarterny",("?i","?i","?i","?i")),),
             Atom("cubic",("+", "?i"))),
        Rule("cubic_dual_close",
             (Atom("cubic",("-", "?i")), Atom("cubic",("+", "?i"))),
             Atom("cubic_closed",("?i",))),
    )

def expected(i):
    return {
        Atom("base1i",(i,)),
        Atom("uniary",(i,)),
        Atom("binary",(i,i)),
        Atom("ternary",(i,i,i)),
        Atom("quarterny",(i,i,i,i)),
        Atom("cubic",("-",i)),
        Atom("cubic",("+",i)),
        Atom("cubic_closed",(i,)),
    }

def single_exact():
    i="1i"
    e=InferenceEngine(rules(),(Atom("base1i",(i,)),),source="base 1i")
    derived=e.saturate()
    assert derived==7
    assert set(e.facts)==expected(i)
    assert e.audit()["status"]=="0e / AUDIT PASS"
    closed=e.proof(Atom("cubic_closed",(i,)))
    assert closed is not None
    assert closed.rule_id=="cubic_dual_close"
    assert {a.key for a in closed.premise_atoms}=={"cubic(-,1i)","cubic(+,1i)"}
    return {
        "status":"0e / EXACT BASE 1i CUBIC CLOSURE PASS",
        "literal":LITERAL,
        "derived":derived,
        "final_facts":len(e.facts),
        "closure_seal":e.closure_seal(),
        "audit":e.audit(),
        "terminal_receipt":closed.receipt,
    }

def scaled(n):
    axioms=tuple(Atom("base1i",(f"1i#{k}",)) for k in range(n))
    e=InferenceEngine(rules(),axioms,source="synthetic scale")
    t0=time.perf_counter()
    derived=e.saturate()
    sec=time.perf_counter()-t0
    assert derived==7*n
    assert len(e.facts)==8*n
    for k in (0,n-1):
        assert Atom("cubic_closed",(f"1i#{k}",)) in e.facts
    assert e.audit()["status"]=="0e / AUDIT PASS"
    return {
        "carriers":n,
        "seconds":sec,
        "derived":derived,
        "final_facts":len(e.facts),
        "derived_per_second":derived/sec if sec else None,
    }

def determinism():
    seed=(Atom("base1i",("1i",)),)
    a=InferenceEngine(rules(),seed,source="determinism")
    b=InferenceEngine(reversed(rules()),reversed(seed),source="determinism")
    a.saturate(); b.saturate()
    assert a.facts==b.facts
    assert a.closure_seal()==b.closure_seal()
    return {"status":"0e / ORDER-INDEPENDENT","closure_seal":a.closure_seal()}

def main():
    exact=single_exact()
    det=determinism()
    scale=[]
    for n in (1,10,100,250,500,1000,2000,4000):
        row=scaled(n)
        scale.append(row)
        if row["seconds"]>=8.0:
            break
    result={
        "engine":"OaSIs v184 sealed inference",
        "sealed_head":"107ba5911f3a38d2f661e096789c22aca7fb1521",
        "test":"base 1i arity ladder through cubic -+ closure",
        "exact":exact,
        "determinism":det,
        "scale":scale,
        "note":"scaled carriers are synthetic load replicas of the exact 1i structure; they do not redefine the canonical literal."
    }
    print(json.dumps(result,indent=2))
    Path("result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
