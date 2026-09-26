#!/usr/bin/env python3
"""PAL-ZIP v32 frozen: exit authorization certificate."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def proposal_id(halt_head, action, target):
    return (
        "EXIT-PROPOSAL|"
        + _lp(halt_head)
        + "|"
        + _lp(action)
        + "|"
        + _lp(target)
    )

def authorized_exit_event(halt_head, action, target, cert):
    proposal = proposal_id(halt_head, action, target)

    if proposal not in cert:
        raise ValueError("certificate not bound to exact exit proposal")

    return (
        "AUTHORIZED-EXIT|"
        + _lp(halt_head)
        + "|"
        + _lp(action)
        + "|"
        + _lp(target)
        + "|"
        + _lp(cert)
    )
