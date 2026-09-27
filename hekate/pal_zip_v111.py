#!/usr/bin/env python3
"""PAL-ZIP v111 frozen: clean higher-recovery prefix MERGE2 replay protection."""

CONSUME_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-CONSUME'
CONSUMED_HEAD_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-CONSUMED-HEAD'
NEXT_EPOCH_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-AUTH-NEXT'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def consume_event(auth_epoch, auth_obj):
    return CONSUME_LABEL + "|" + _lp(auth_epoch) + "|" + _lp(auth_obj)

def consumed_head(auth_epoch, auth_obj):
    return CONSUMED_HEAD_LABEL + "|" + _lp(consume_event(auth_epoch, auth_obj))

def next_auth_epoch(consumed_head_value):
    return NEXT_EPOCH_LABEL + "|" + _lp(consumed_head_value)

def authorize_once(auth_obj, consumed_auths=()):
    if auth_obj in set(consumed_auths):
        raise ValueError("authorized clean higher-recovery prefix merge already consumed")
    return auth_obj
