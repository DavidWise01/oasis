#!/usr/bin/env python3
"""AETHER-256-RS: fail-closed ledger append, fork and signer ancestry review."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "AETHER-256/replay-ledger-ancestry-v1"
HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "external_head_authenticated": False,
        "independent_controller_custody_authenticated": False}
HEX = re.compile(r"^[0-9a-f]{64}$")

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def ancestry(node, graph):
    observed, active = set(), set()
    def visit(current):
        if not isinstance(current, str) or not current or len(current) > 128:
            raise ValueError("INVALID_ANCESTRY_NAME")
        if current in active:
            raise ValueError("CONTROLLER_ANCESTRY_CYCLE")
        if current in observed:
            return
        if current not in graph:
            raise ValueError("MISSING_ANCESTRY_NODE")
        parents = graph[current]
        if not isinstance(parents, list) or len(parents) > 16:
            raise ValueError("INVALID_PARENT_LIST")
        active.add(current)
        observed.add(current)
        if len(observed) > 256:
            raise ValueError("ANCESTRY_LIMIT")
        for parent in parents:
            visit(parent)
        active.remove(current)
    visit(node)
    return observed

def chain(events, anchor):
    issues, seen, heads = [], set(), []
    previous = anchor["head_sha256"]
    sequence = anchor["sequence"]
    if not isinstance(events, list) or not 1 <= len(events) <= 128:
        return [], ["EVENT_SET_INVALID"]
    for event in events:
        if not isinstance(event, dict) or set(event) != {
            "sequence", "previous_sha256", "run_id", "challenge_id",
            "nonce", "transcript_sha256", "event_sha256"}:
            issues.append("EVENT_SCHEMA_INVALID")
            break
        seq = event["sequence"]
        if type(seq) is not int or seq != sequence + 1:
            issues.append("NONMONOTONIC_SEQUENCE")
        if type(seq) is int:
            sequence = seq
        if event["previous_sha256"] != previous:
            issues.append("PREVIOUS_HEAD_MISMATCH")
        nonce = event["nonce"]
        if not isinstance(nonce, str) or not nonce or len(nonce) > 128 or nonce in seen:
            issues.append("NONCE_REPLAY")
        if isinstance(nonce, str):
            seen.add(nonce)
        if type(event["run_id"]) is not int or event["run_id"] <= 0:
            issues.append("RUN_INVALID")
        if not isinstance(event["challenge_id"], str) or not event["challenge_id"]:
            issues.append("CHALLENGE_INVALID")
        if not isinstance(event["transcript_sha256"], str) or not HEX.fullmatch(event["transcript_sha256"]):
            issues.append("TRANSCRIPT_INVALID")
        computed = digest({k:v for k,v in event.items() if k != "event_sha256"})
        if event["event_sha256"] != computed:
            issues.append("EVENT_DIGEST_MISMATCH")
        previous = computed
        heads.append(computed)
    return heads, issues

def assess(bundle):
    reasons = []
    observed = {"candidate_heads": [], "controllers": []}
    if not isinstance(bundle, dict):
        return {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
                "reasons": ["BUNDLE_INVALID"], "observed": observed, **HOLD}
    anchor = bundle.get("externally_claimed_anchor")
    candidates = bundle.get("candidate_histories")
    graph = bundle.get("controller_graph")
    signers = bundle.get("signers")
    used = bundle.get("consumed_nonces")
    if not isinstance(anchor, dict) or set(anchor) != {"sequence", "head_sha256"} or (
        type(anchor.get("sequence")) is not int or anchor["sequence"] < 0 or
        not isinstance(anchor.get("head_sha256"), str) or not HEX.fullmatch(anchor["head_sha256"])):
        reasons.append("ANCHOR_INVALID")
        anchor = {"sequence": 0, "head_sha256": "0"*64}
    if not isinstance(candidates, list) or not 2 <= len(candidates) <= 8:
        reasons.append("CANDIDATE_HISTORIES_INVALID")
        candidates = []
    if not isinstance(used, list) or any(not isinstance(x, str) for x in used):
        reasons.append("NONCE_HISTORY_INVALID")
        used = []
    if len(used) != len(set(used)):
        reasons.append("NONCE_HISTORY_DUPLICATES")
    hashes = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != {"source_id", "events", "claimed_head_sha256"}:
            reasons.append("CANDIDATE_SCHEMA_INVALID")
            continue
        heads, failures = chain(candidate["events"], anchor)
        reasons.extend(failures)
        if heads and heads[-1] != candidate["claimed_head_sha256"]:
            reasons.append("CANDIDATE_HEAD_MISMATCH")
        if any(isinstance(event, dict) and event.get("nonce") in used for event in
               candidate["events"] if isinstance(candidate["events"], list)):
            reasons.append("ALREADY_CONSUMED_NONCE")
        hashes.append(heads)
        observed["candidate_heads"].append({"source_id": candidate["source_id"],
                                             "computed_head": heads[-1] if heads else None})
    for i, one in enumerate(hashes):
        for other in hashes[i+1:]:
            shared = min(len(one), len(other))
            if one[:shared] != other[:shared]:
                reasons.append("DIVERGENT_HISTORY")
    if not isinstance(graph, dict):
        reasons.append("GRAPH_INVALID")
        graph = {}
    if not isinstance(signers, list) or len(signers) != 3:
        reasons.append("THREE_SIGNERS_REQUIRED")
        signers = []
    roots = []
    ids = set()
    for signer in signers:
        if not isinstance(signer, dict) or set(signer) != {"key_id", "controller_id"}:
            reasons.append("SIGNER_SCHEMA_INVALID")
            continue
        key, controller = signer["key_id"], signer["controller_id"]
        if not isinstance(key, str) or not key or key in ids:
            reasons.append("SIGNER_KEY_REUSE")
        if isinstance(key, str):
            ids.add(key)
        try:
            ancestors = ancestry(controller, graph)
            roots.append(ancestors)
            observed["controllers"].append({"key_id": key,
                                              "declared_controller": controller,
                                              "ancestry_count": len(ancestors)})
        except ValueError as error:
            reasons.append(str(error))
    for index, ancestry_one in enumerate(roots):
        for ancestry_two in roots[index+1:]:
            if ancestry_one.intersection(ancestry_two):
                reasons.append("SHARED_CONTROLLER_ANCESTRY")
    reasons.extend(["EXTERNAL_ANCHOR_NOT_AUTHENTICATED",
                    "SIGNER_KEYS_AND_CONTROLLER_GRAPH_NOT_EXTERNALLY_ATTESTED",
                    "ATOMIC_LEDGER_CONSUMPTION_NOT_OBSERVED"])
    return {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
            "reasons": sorted(set(reasons)), "observed": observed, **HOLD}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        data = args.bundle.read_bytes()
        if len(data) > 512*1024:
            raise ValueError("INPUT_TOO_LARGE")
        result = assess(json.loads(data))
    except (OSError, ValueError, TypeError, UnicodeError) as error:
        result = {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
                  "reasons": ["INPUT_REJECTED:" + type(error).__name__], **HOLD}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
