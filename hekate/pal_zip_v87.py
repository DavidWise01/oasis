#!/usr/bin/env python3
"""PAL-ZIP v87 frozen: higher-recovery prefix MERGE2 replay protection."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def consume_authorized_merge(auth_epoch, auth_obj):
    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-CONSUME|"
        + _lp(auth_epoch) + "|"
        + _lp(auth_obj)
    )

def consumed_head(auth_epoch, auth_obj):
    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-CONSUMED-HEAD|"
        + _lp(consume_authorized_merge(auth_epoch, auth_obj))
    )

def next_auth_epoch(consumed_head_value):
    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-AUTH-NEXT|"
        + _lp(consumed_head_value)
    )

def authorize_once(auth_obj, consumed_auths=()):
    if auth_obj in set(consumed_auths):
        raise ValueError("authorized higher-recovery merge already consumed")
    return auth_obj
