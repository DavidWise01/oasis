#!/usr/bin/env python3
from pathlib import Path
import json
import kernel

HERE = Path(__file__).resolve().parent

def test():
    canon = kernel.load_and_verify_canon(HERE / "CANON.json")
    assert canon["status"] == "FROZEN / IMMUTABLE / GENERATIVE-FIRST"

    g1 = kernel.genesis()
    g2 = kernel.genesis()
    assert g1 == g2, "genesis must be deterministic"

    s1 = kernel.run_steps(12)
    s2 = kernel.run_steps(12)
    assert s1 == s2, "same frozen parent/canon must generate same child"
    assert kernel.verify_invariants(s1)

    # q0..q11 retain same identity/v^3.
    assert s1[0].q == 0 and s1[11].q == 11
    assert s1[0].identity == s1[11].identity
    assert s1[0].v3 == s1[11].v3

    # q11 -> q0 creates a new deterministic ID and a fresh v^3.
    child = s1[12]
    assert child.q == 0
    assert child.generation == 1
    assert child.identity != s1[11].identity
    assert child.v3 != s1[11].v3
    assert child.parent_seal == s1[11].seal()

    # No static a/b/c -> i/id/sid table exists in runtime.
    assert not hasattr(kernel, "ABC_TO_IDENTITY_BRANCH")

    # Tamper test: mutated canon must fail hash verification.
    original = (HERE / "CANON.json").read_bytes()
    tampered = HERE / "_tampered_canon.json"
    tampered.write_bytes(original + b"\n")
    failed = False
    try:
        kernel.load_and_verify_canon(tampered)
    except RuntimeError:
        failed = True
    finally:
        tampered.unlink(missing_ok=True)
    assert failed, "tampered frozen canon must fail"

    return {
        "status": "0e / 10 INVARIANT GROUPS PASS",
        "canon_sha256": kernel.CANON_SHA256,
        "genesis_id": g1.identity,
        "child_id": child.identity,
        "child_v3": {
            "vector": child.v3.vector,
            "voxel": child.v3.voxel,
            "vogel": child.v3.vogel,
            "sg": child.v3.sg,
        },
        "child_lineage_seal": child.lineage_seal,
    }

if __name__ == "__main__":
    print(json.dumps(test(), indent=2))
