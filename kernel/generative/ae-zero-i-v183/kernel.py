#!/usr/bin/env python3
"""OaSIs Zero/I Canon v183.

Append-only descendant of sealed v182.

Canonical root:
    {{0::{i::}}}

Model-local ternary transform:
    -1 -> 0
     0 -> -1
    +1 -> 0&1

This is an information transform, not ordinary arithmetic equality.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib, json

VERSION="v183"
STATUS="CANON / ZERO-I ROOT / APPEND-ONLY"
CANON_LITERAL="{{0::{i::}}}"
SOURCE_LITERAL=("-1","0","+1")
IMAGE_LITERAL=("0","-1","0&1")

class Ternary(str,Enum):
    NEG="-1"
    ZERO="0"
    POS="+1"

class Image(str,Enum):
    ZERO="0"
    NEGONE="-1"
    ZERO_AND_ONE="0&1"

def i(x:Ternary)->Image:
    return {
        Ternary.NEG:Image.ZERO,
        Ternary.ZERO:Image.NEGONE,
        Ternary.POS:Image.ZERO_AND_ONE,
    }[x]

def i_inv(y:Image)->Ternary:
    return {
        Image.ZERO:Ternary.NEG,
        Image.NEGONE:Ternary.ZERO,
        Image.ZERO_AND_ONE:Ternary.POS,
    }[y]

@dataclass(frozen=True)
class RootTransform:
    referent:str
    transform:str
    literal:str

ROOT=RootTransform("0","i",CANON_LITERAL)

def exhaustive_report()->dict:
    rows=[]
    for x in Ternary:
        y=i(x)
        back=i_inv(y)
        assert back==x
        rows.append({"source":x.value,"image":y.value,"roundtrip":back.value})
    for y in Image:
        assert i(i_inv(y))==y
    assert len({i(x) for x in Ternary})==3
    blob=json.dumps(rows,sort_keys=True,separators=(",",":")).encode()
    return {
        "status":"0e / v183 ZERO-I TRANSFORM PASS",
        "version":VERSION,
        "canon":CANON_LITERAL,
        "root":asdict(ROOT),
        "mapping":rows,
        "injective":True,
        "surjective":True,
        "bijective":True,
        "source_states":3,
        "image_states":3,
        "mapping_sha256":hashlib.sha256(blob).hexdigest(),
    }

if __name__=="__main__":
    print(json.dumps(exhaustive_report(),indent=2))
