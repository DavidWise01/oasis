#!/usr/bin/env python3
from dataclasses import replace
import itertools
import json

import engine


def expected_closure(seed):
    pairs = (
        {engine.Atom("ternary", ("-1",)), engine.Atom("image", ("0",))},
        {engine.Atom("ternary", ("0",)), engine.Atom("image", ("-1",))},
        {engine.Atom("ternary", ("+1",)), engine.Atom("image", ("0&1",))},
    )
    out = set(seed)
    for pair in pairs:
        if out & pair:
            out |= pair
    return out


def test_all():
    parent = engine.verify_parent_seal()
    assert parent["canon"]["literal"] == "{{0::{i::}}}"

    core = (
        engine.Atom("ternary", ("-1",)),
        engine.Atom("image", ("0",)),
        engine.Atom("ternary", ("0",)),
        engine.Atom("image", ("-1",)),
        engine.Atom("ternary", ("+1",)),
        engine.Atom("image", ("0&1",)),
    )

    closures = 0
    for mask in range(1 << len(core)):
        seed = tuple(core[i] for i in range(len(core)) if mask & (1 << i))
        e = engine.InferenceEngine(engine.v183_rules(), seed, source="exhaustive")
        e.saturate()
        assert set(e.facts) == expected_closure(seed)
        assert e.audit()["status"] == "0e / AUDIT PASS"

        # Determinism under reversed rule/axiom input order.
        e2 = engine.InferenceEngine(reversed(engine.v183_rules()), reversed(seed), source="exhaustive")
        e2.saturate()
        assert e2.facts == e.facts
        assert e2.closure_seal() == e.closure_seal()
        closures += 1

    # Generic variable rule test: parent(x,y) & parent(y,z) -> grandparent(x,z)
    rules = (
        engine.Rule(
            "grandparent",
            (
                engine.Atom("parent", ("?x", "?y")),
                engine.Atom("parent", ("?y", "?z")),
            ),
            engine.Atom("grandparent", ("?x", "?z")),
        ),
    )
    axioms = (
        engine.Atom("parent", ("a", "b")),
        engine.Atom("parent", ("b", "c")),
        engine.Atom("parent", ("x", "y")),
    )
    g = engine.InferenceEngine(rules, axioms)
    assert g.saturate() == 1
    assert engine.Atom("grandparent", ("a", "c")) in g.facts
    assert g.audit()["status"] == "0e / AUDIT PASS"

    # Unbound conclusion variables fail closed.
    failed = False
    try:
        engine.Rule(
            "bad",
            (engine.Atom("p", ("?x",)),),
            engine.Atom("q", ("?z",)),
        )
    except ValueError:
        failed = True
    assert failed

    # Tampering breaks proof audit.
    target = engine.Atom("grandparent", ("a", "c"))
    original = g.proofs[target]
    g.proofs[target] = replace(original, receipt="0" * 64)
    assert g.audit()["status"] == "xe / AUDIT FAIL"

    demo = engine.demo()
    assert demo["status"] == "0e / v184 INFERENCE DEMO PASS"

    return {
        "status": "0e / v184 INFERENCE ENGINE TESTS PASS",
        "v183_seed_subsets_exhausted": closures,
        "core_atoms": len(core),
        "generic_variable_rule": "PASS",
        "deterministic_order_independence": "PASS",
        "fixed_point": "PASS",
        "unbound_variable_rejection": "PASS",
        "provenance_tamper_rejection": "PASS",
    }


if __name__ == "__main__":
    print(json.dumps(test_all(), indent=2))
