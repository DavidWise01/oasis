#!/usr/bin/env python3
r"""
root_i_contract_v00_frozen.py

Frozen two-channel substrate contract.

Canonical literal:
    {{ -i \::/ { e | r } }}

e = EMPH reference ("what crosses")
r = accountable route ("how / who / authority / provenance / time")

The one-field collapse -i{r} is intentionally NOT frozen here.
"""

from dataclasses import dataclass
from typing import List, Optional
import json

ROOT = "-i"
BIND = r"\::/"
PRIME = "."
HOME0 = "HOME0"

HAMILTON_VISITED = 27
HAMILTON_MOVES = 26
TIME_TAPE = ("00", "11", "22", "33", "22", "11", "00")

VALID_AUTHORITY = {"sovereign", "delegated", "advisory", "observer"}
VALID_CHOICE = {"y", "n"}


@dataclass(frozen=True)
class Edge:
    edge_id: str
    src: str
    dst: str
    actor: str
    authority: str
    parent: Optional[str] = None


@dataclass
class Route:
    edges: List[Edge]
    choice: str
    visited: int = HAMILTON_VISITED
    moves: int = HAMILTON_MOVES
    start: str = PRIME
    return_path: str = HOME0
    time_tape: tuple[str, ...] = TIME_TAPE


@dataclass
class Kernel:
    e: str
    r: Route
    root: str = ROOT
    bind: str = BIND


def validate(kernel: Kernel) -> list[str]:
    errors: list[str] = []

    if kernel.root != ROOT:
        errors.append("V000 root must be -i")
    if kernel.bind != BIND:
        errors.append(r"V001 bind must be \::/")

    if not kernel.e or not kernel.e.strip():
        errors.append("V002 e must contain an EMPH reference")

    r = kernel.r

    if r.start != PRIME:
        errors.append("V010 route must start from prime .")
    if r.visited != HAMILTON_VISITED:
        errors.append("V011 visited positions must be 27")
    if r.moves != HAMILTON_MOVES:
        errors.append("V012 Hamilton path must use 26 moves")
    if r.visited != r.moves + 1:
        errors.append("V013 visited must equal moves + 1")
    if len(r.edges) != r.moves:
        errors.append("V014 edge count must equal 26 moves")

    if r.choice not in VALID_CHOICE:
        errors.append("V020 choice must be y or n")

    if r.return_path != HOME0:
        errors.append("V021 return path must remain HOME0")

    if r.choice == "y" and tuple(r.time_tape) != TIME_TAPE:
        errors.append("V022 y continuation must use 00 11 22 33 22 11 00")

    seen: set[str] = set()
    previous_dst = r.start
    for i, edge in enumerate(r.edges):
        if not edge.edge_id:
            errors.append(f"V03{i} edge id is empty")
            continue
        if edge.edge_id in seen:
            errors.append(f"V03{i} duplicate edge id {edge.edge_id}")
        if not edge.actor:
            errors.append(f"V04{i} edge {edge.edge_id} missing actor")
        if edge.authority not in VALID_AUTHORITY:
            errors.append(f"V05{i} edge {edge.edge_id} has invalid authority")
        if edge.src != previous_dst:
            errors.append(f"V06{i} edge {edge.edge_id} breaks ordered route")
        if i == 0:
            if edge.parent is not None:
                errors.append(f"V07{i} first edge parent must be None")
        else:
            if edge.parent not in seen:
                errors.append(f"V07{i} parent must resolve backward to an earlier edge")
        seen.add(edge.edge_id)
        previous_dst = edge.dst

    return errors


def demo_route(choice: str = "n") -> Route:
    edges: list[Edge] = []
    src = PRIME
    for i in range(HAMILTON_MOVES):
        dst = f"n{i+1:02d}"
        edge_id = f"r{i+1:02d}"
        parent = None if i == 0 else f"r{i:02d}"
        edges.append(
            Edge(
                edge_id=edge_id,
                src=src,
                dst=dst,
                actor="agent-1",
                authority="delegated",
                parent=parent,
            )
        )
        src = dst
    return Route(edges=edges, choice=choice)


def self_test() -> dict[str, bool]:
    tests: dict[str, bool] = {}

    tests["valid_n_stop"] = validate(Kernel(e="emph:demo", r=demo_route("n"))) == []
    tests["valid_y_return"] = validate(Kernel(e="emph:demo", r=demo_route("y"))) == []

    bad_root = Kernel(e="emph:demo", r=demo_route("n"), root="ACI")
    tests["reject_bad_root"] = any("V000" in e for e in validate(bad_root))

    bad_bind = Kernel(e="emph:demo", r=demo_route("n"), bind="::")
    tests["reject_bad_bind"] = any("V001" in e for e in validate(bad_bind))

    bad_count = Kernel(e="emph:demo", r=demo_route("n"))
    bad_count.r.moves = 27
    tests["reject_27_moves"] = any("V012" in e or "V013" in e for e in validate(bad_count))

    bad_auth = Kernel(e="emph:demo", r=demo_route("n"))
    e0 = bad_auth.r.edges[0]
    bad_auth.r.edges[0] = Edge(e0.edge_id, e0.src, e0.dst, e0.actor, "magic", e0.parent)
    tests["reject_invalid_authority"] = any("V050" in e for e in validate(bad_auth))

    bad_tape = Kernel(e="emph:demo", r=demo_route("y"))
    bad_tape.r.time_tape = ("00", "11", "00")
    tests["reject_bad_y_time_tape"] = any("V022" in e for e in validate(bad_tape))

    return tests


if __name__ == "__main__":
    results = self_test()
    print(json.dumps(results, indent=2))
    failed = [name for name, ok in results.items() if not ok]
    if failed:
        raise SystemExit(f"FAIL: {failed}")
    print("0e :: root -i frozen contract self-test PASS")
