#!/usr/bin/env python3
"""PAL-ZIP v28 frozen: pre-anchor timing."""

def authority_registration(source_name: str) -> str:
    return f"AUTH-REGISTER|{len(source_name)}:{source_name}"

def source_is_preanchored(entries, source_name: str, halt_index: int) -> bool:
    target = authority_registration(source_name)
    try:
        first = entries.index(target)
    except ValueError:
        return False
    return first < halt_index
