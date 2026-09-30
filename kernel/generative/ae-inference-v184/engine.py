#!/usr/bin/env python3
"""OaSIs Deterministic Inference Engine v184.

Append-only inference layer bolted onto sealed Zero/I Canon v183.

Properties:
- generic finite Horn-style rules with ?variables;
- deterministic forward-chaining to a fixed point;
- no silent guessing: every derived atom requires an explicit rule match;
- exact provenance receipts for every axiom and derivation;
- cycle-safe monotone saturation;
- v183 adapter for the canonical symbolic transform:
      -1 -> 0
       0 -> -1
      +1 -> 0&1
  and its proved inverse.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import argparse
import hashlib
import json

VERSION = "v184"
STATUS = "GENERATIVE / DETERMINISTIC INFERENCE / APPEND-ONLY"
PARENT_VERSION = "v183"
PARENT_SEALED_COMMIT = "78492de2c7fbca398a1dc6460a33e1f88f619020"
ROOT_LITERAL = "{{0::{i::}}}"

HERE = Path(__file__).resolve().parent
PARENT_SEAL = HERE.parent / "ae-zero-i-v183" / "SEAL.json"


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def is_var(term: str) -> bool:
    return term.startswith("?") and len(term) > 1


@dataclass(frozen=True, order=True)
class Atom:
    predicate: str
    args: tuple[str, ...]

    def __post_init__(self):
        if not self.predicate:
            raise ValueError("predicate must be non-empty")
        if any(not isinstance(x, str) or x == "" for x in self.args):
            raise ValueError("atom args must be non-empty strings")

    @property
    def key(self) -> str:
        return f"{self.predicate}(" + ",".join(self.args) + ")"

    def to_obj(self) -> dict:
        return {"predicate": self.predicate, "args": list(self.args)}

    @staticmethod
    def from_obj(obj: Mapping) -> "Atom":
        return Atom(str(obj["predicate"]), tuple(str(x) for x in obj.get("args", [])))


@dataclass(frozen=True)
class Rule:
    rule_id: str
    premises: tuple[Atom, ...]
    conclusion: Atom

    def __post_init__(self):
        if not self.rule_id:
            raise ValueError("rule_id must be non-empty")
        premise_vars = {
            t for atom in self.premises for t in atom.args if is_var(t)
        }
        conclusion_vars = {t for t in self.conclusion.args if is_var(t)}
        if not conclusion_vars.issubset(premise_vars):
            missing = sorted(conclusion_vars - premise_vars)
            raise ValueError(f"unbound conclusion variables: {missing}")

    def to_obj(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "premises": [a.to_obj() for a in self.premises],
            "conclusion": self.conclusion.to_obj(),
        }

    @staticmethod
    def from_obj(obj: Mapping) -> "Rule":
        return Rule(
            str(obj["rule_id"]),
            tuple(Atom.from_obj(x) for x in obj.get("premises", [])),
            Atom.from_obj(obj["conclusion"]),
        )


@dataclass(frozen=True)
class Proof:
    kind: str
    atom: Atom
    source: str
    rule_id: str | None
    premise_atoms: tuple[Atom, ...]
    premise_receipts: tuple[str, ...]
    receipt: str

    def body(self) -> dict:
        return {
            "kind": self.kind,
            "atom": self.atom.to_obj(),
            "source": self.source,
            "rule_id": self.rule_id,
            "premise_atoms": [a.to_obj() for a in self.premise_atoms],
            "premise_receipts": list(self.premise_receipts),
        }


def make_axiom_proof(atom: Atom, source: str) -> Proof:
    body = {
        "kind": "axiom",
        "atom": atom.to_obj(),
        "source": source,
        "rule_id": None,
        "premise_atoms": [],
        "premise_receipts": [],
    }
    return Proof("axiom", atom, source, None, (), (), sha256_obj(body))


def make_derived_proof(atom: Atom, rule: Rule, premises: Sequence[Proof]) -> Proof:
    premise_atoms = tuple(p.atom for p in premises)
    premise_receipts = tuple(p.receipt for p in premises)
    body = {
        "kind": "derived",
        "atom": atom.to_obj(),
        "source": VERSION,
        "rule_id": rule.rule_id,
        "premise_atoms": [a.to_obj() for a in premise_atoms],
        "premise_receipts": list(premise_receipts),
    }
    return Proof(
        "derived", atom, VERSION, rule.rule_id,
        premise_atoms, premise_receipts, sha256_obj(body)
    )


def unify(pattern: Atom, fact: Atom, env: Mapping[str, str]) -> dict[str, str] | None:
    if pattern.predicate != fact.predicate or len(pattern.args) != len(fact.args):
        return None
    out = dict(env)
    for p, f in zip(pattern.args, fact.args):
        if is_var(p):
            prior = out.get(p)
            if prior is None:
                out[p] = f
            elif prior != f:
                return None
        elif p != f:
            return None
    return out


def instantiate(pattern: Atom, env: Mapping[str, str]) -> Atom:
    vals = []
    for term in pattern.args:
        if is_var(term):
            if term not in env:
                raise ValueError(f"unbound variable at instantiate: {term}")
            vals.append(env[term])
        else:
            vals.append(term)
    return Atom(pattern.predicate, tuple(vals))


def verify_parent_seal(path: Path = PARENT_SEAL) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("version") != "v183":
        raise RuntimeError("wrong parent seal version")
    if obj.get("status") != "SEALED / IMMUTABLE / LEAN-PROVED":
        raise RuntimeError("v183 parent is not sealed")
    canon = obj.get("canon", {})
    if canon.get("literal") != ROOT_LITERAL:
        raise RuntimeError("v183 root literal mismatch")
    expected = {"-1": "0", "0": "-1", "+1": "0&1"}
    if canon.get("mapping") != expected:
        raise RuntimeError("v183 mapping mismatch")
    return obj


def v183_rules() -> tuple[Rule, ...]:
    pairs = (
        ("-1", "0", "neg"),
        ("0", "-1", "zero"),
        ("+1", "0&1", "pos"),
    )
    rules: list[Rule] = []
    for source, image, tag in pairs:
        rules.append(Rule(
            f"v183.i.forward.{tag}",
            (Atom("ternary", (source,)),),
            Atom("image", (image,))
        ))
        rules.append(Rule(
            f"v183.i.inverse.{tag}",
            (Atom("image", (image,)),),
            Atom("ternary", (source,))
        ))
    return tuple(rules)


class InferenceEngine:
    def __init__(
        self,
        rules: Iterable[Rule],
        axioms: Iterable[Atom] = (),
        *,
        source: str = "explicit",
    ):
        self.rules = tuple(sorted(tuple(rules), key=lambda r: r.rule_id))
        ids = [r.rule_id for r in self.rules]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate rule_id")
        self.proofs: dict[Atom, Proof] = {}
        for atom in sorted(set(axioms)):
            self.proofs[atom] = make_axiom_proof(atom, source)

    @property
    def facts(self) -> tuple[Atom, ...]:
        return tuple(sorted(self.proofs))

    def add_axiom(self, atom: Atom, source: str = "explicit") -> None:
        self.proofs.setdefault(atom, make_axiom_proof(atom, source))

    def _matches(self, rule: Rule):
        facts = self.facts

        def walk(i: int, env: dict[str, str], chosen: list[Proof]):
            if i == len(rule.premises):
                yield env, tuple(chosen)
                return
            pattern = rule.premises[i]
            for fact in facts:
                env2 = unify(pattern, fact, env)
                if env2 is not None:
                    chosen.append(self.proofs[fact])
                    yield from walk(i + 1, env2, chosen)
                    chosen.pop()

        yield from walk(0, {}, [])

    def step(self) -> int:
        candidates: dict[Atom, tuple[tuple, Proof]] = {}
        for rule in self.rules:
            for env, premise_proofs in self._matches(rule):
                atom = instantiate(rule.conclusion, env)
                if atom in self.proofs:
                    continue
                proof = make_derived_proof(atom, rule, premise_proofs)
                rank = (rule.rule_id, tuple(p.receipt for p in premise_proofs), atom.key)
                prior = candidates.get(atom)
                if prior is None or rank < prior[0]:
                    candidates[atom] = (rank, proof)
        for atom in sorted(candidates):
            self.proofs[atom] = candidates[atom][1]
        return len(candidates)

    def saturate(self, max_rounds: int = 1024) -> int:
        total = 0
        for _ in range(max_rounds):
            n = self.step()
            total += n
            if n == 0:
                return total
        raise RuntimeError("inference did not reach a fixed point")

    def proof(self, atom: Atom) -> Proof | None:
        return self.proofs.get(atom)

    def closure_seal(self) -> str:
        return sha256_obj({
            "version": VERSION,
            "facts": [a.to_obj() for a in self.facts],
            "receipts": [self.proofs[a].receipt for a in self.facts],
        })

    def audit(self) -> dict:
        bad = []
        for atom, proof in sorted(self.proofs.items()):
            if proof.atom != atom or sha256_obj(proof.body()) != proof.receipt:
                bad.append(atom.key)
                continue
            if proof.kind == "derived":
                if proof.rule_id not in {r.rule_id for r in self.rules}:
                    bad.append(atom.key)
                    continue
                for pa, receipt in zip(proof.premise_atoms, proof.premise_receipts):
                    pp = self.proofs.get(pa)
                    if pp is None or pp.receipt != receipt:
                        bad.append(atom.key)
                        break
        return {
            "status": "0e / AUDIT PASS" if not bad else "xe / AUDIT FAIL",
            "facts": len(self.proofs),
            "bad": bad,
            "closure_seal": self.closure_seal(),
        }


def demo() -> dict:
    parent = verify_parent_seal()
    seed = (Atom("ternary", ("+1",)),)
    eng = InferenceEngine(v183_rules(), seed, source="v183-seed")
    derived = eng.saturate()
    target = Atom("image", ("0&1",))
    proof = eng.proof(target)
    assert proof is not None
    audit = eng.audit()
    assert audit["status"] == "0e / AUDIT PASS"
    return {
        "status": "0e / v184 INFERENCE DEMO PASS",
        "parent": parent["designation"],
        "root": ROOT_LITERAL,
        "seed": [a.key for a in seed],
        "derived": derived,
        "closure": [a.key for a in eng.facts],
        "target_proof": asdict(proof),
        "audit": audit,
    }


def problem_from_json(obj: Mapping) -> dict:
    rules = tuple(Rule.from_obj(x) for x in obj.get("rules", []))
    axioms = tuple(Atom.from_obj(x) for x in obj.get("axioms", []))
    eng = InferenceEngine(rules, axioms, source=str(obj.get("source", "json")))
    derived = eng.saturate(int(obj.get("max_rounds", 1024)))
    return {
        "status": "0e / FIXED POINT",
        "derived": derived,
        "facts": [a.to_obj() for a in eng.facts],
        "proofs": [asdict(eng.proofs[a]) for a in eng.facts],
        "audit": eng.audit(),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    p.add_argument("--problem")
    args = p.parse_args()
    if args.problem:
        obj = json.loads(Path(args.problem).read_text(encoding="utf-8"))
        print(json.dumps(problem_from_json(obj), indent=2))
    else:
        print(json.dumps(demo(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
