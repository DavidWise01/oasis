#!/usr/bin/env python3
"""PAL-ZIP v23 frozen: authority-vacuum recovery."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def committee_anchor(members, threshold):
    members = tuple(sorted(set(members)))
    if threshold < 1 or threshold > len(members):
        raise ValueError("invalid threshold")
    return "COMMITTEE|" + _lp(str(threshold)) + "|" + _lp(";".join(members))

def vacuum_recover(vacuum_root, reserve_cid, implicated, reserve_members,
                   successor_members, successor_threshold):
    successor_members = tuple(sorted(set(successor_members)))

    if set(successor_members) & set(implicated):
        raise ValueError("implicated identity cannot enter vacuum successor")

    if set(successor_members) & set(reserve_members):
        raise ValueError("reserve authority cannot appoint itself")

    successor_cid = committee_anchor(successor_members, successor_threshold)

    return (
        "VACUUM-RECOVER|"
        + _lp(vacuum_root) + "|"
        + _lp(reserve_cid) + "|"
        + _lp(";".join(sorted(set(implicated)))) + "|"
        + _lp(successor_cid)
    )
