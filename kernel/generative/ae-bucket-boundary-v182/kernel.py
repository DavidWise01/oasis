#!/usr/bin/env python3
"""OaSIs AE Bucket Boundary Canon v182.

Append-only descendant of sealed v181.

Canonical primitive:
  {{0011 :: pt + {{n}}^{{n}}^{{n}} :: i}}

Bindings:
  0011 = plank 0 referent
  pt = local point
  {{n}}^{{n}}^{{n}} = retained nested scale
  {{i = inf + 1{{B{{u}}cket}}}}
  u = private disposable/pocket universe

Two executable boundaries:
  B{{      ingress
  }}cket   egress
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Any
import hashlib, importlib.util, json, sys

VERSION="v182"
STATUS="CANON / SEALED BUCKET BOUNDARIES / APPEND-ONLY"
HERE=Path(__file__).resolve().parent
PARENT_PATH=HERE.parent/"ae-cyclic-oe-v181"/"kernel.py"
REFERENT="0011"
REFERENT_MEANING="plank 0"
POINT_LITERAL="pt"
SCALE_LITERAL="{{n}}^{{n}}^{{n}}"
U_LITERAL="{{B{{u}}cket}}"
I_LITERAL="{{i = inf + 1{{B{{u}}cket}}}}"
PRIM_LITERAL="{{0011 :: pt + {{n}}^{{n}}^{{n}} :: i}}"
EXPANDED_PRIM_LITERAL="{{0011 :: pt + {{n}}^{{n}}^{{n}} :: {{i = inf + 1{{B{{u}}cket}}}}}}"
INGRESS="B{{"
EGRESS="}}cket"

def _load_parent():
    spec=importlib.util.spec_from_file_location("oasis_ae_v181",PARENT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v181 parent from {PARENT_PATH}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod
PARENT=_load_parent()

def canonical_json(obj:Any)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha256_obj(obj:Any)->str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()

@dataclass(frozen=True)
class ParentAnchor:
    referent:str
    meaning:str
    point:int
    control_state:str
    parent_fingerprint:str

@dataclass(frozen=True)
class Bucket:
    version:str
    bucket_id:str
    parent:ParentAnchor
    scale:str
    private_payload_hash:str
    private_payload_bytes:int
    open:bool
    disposed:bool

@dataclass(frozen=True)
class TransformReceipt:
    version:str
    transform:str
    primitive:str
    bucket_id:str
    parent_fingerprint:str
    ingress:str
    egress:str
    private_payload_hash:str
    private_payload_bytes:int
    payload_exposed_bytes:int
    disposed:bool
    seal:str

def parent_anchor(cell:int)->ParentAnchor:
    state=PARENT.cell_state(cell)
    base={"referent":REFERENT,"meaning":REFERENT_MEANING,"point":cell,"control_state":state.label}
    return ParentAnchor(REFERENT,REFERENT_MEANING,cell,state.label,sha256_obj(base))

def ingress(parent:ParentAnchor,private_payload:bytes)->Bucket:
    if parent.referent!=REFERENT or parent.meaning!=REFERENT_MEANING:
        raise ValueError("ingress requires canonical 0011 / plank 0 referent")
    if not 0<=parent.point<PARENT.RING_CELLS:
        raise ValueError("parent point outside sealed v181 ring")
    ph=hashlib.sha256(private_payload).hexdigest()
    bid=sha256_obj({
      "parent_fingerprint":parent.parent_fingerprint,
      "scale":SCALE_LITERAL,
      "private_payload_hash":ph,
      "private_payload_bytes":len(private_payload),
      "ingress":INGRESS,
    })
    return Bucket(VERSION,bid,parent,SCALE_LITERAL,ph,len(private_payload),True,False)

def _receipt_payload(bucket:Bucket)->dict:
    return {
      "version":VERSION,"transform":I_LITERAL,"primitive":PRIM_LITERAL,
      "bucket_id":bucket.bucket_id,"parent_fingerprint":bucket.parent.parent_fingerprint,
      "ingress":INGRESS,"egress":EGRESS,
      "private_payload_hash":bucket.private_payload_hash,
      "private_payload_bytes":bucket.private_payload_bytes,
      "payload_exposed_bytes":0,"disposed":True,
    }

def egress(bucket:Bucket)->tuple[Bucket,TransformReceipt]:
    if not bucket.open or bucket.disposed:
        raise RuntimeError("bucket is not an open private universe")
    dead=replace(bucket,open=False,disposed=True)
    payload=_receipt_payload(dead)
    return dead,TransformReceipt(**payload,seal=sha256_obj(payload))

def verify_receipt(receipt:TransformReceipt)->bool:
    payload=asdict(receipt)
    seal=payload.pop("seal")
    return (
      receipt.transform==I_LITERAL and receipt.primitive==PRIM_LITERAL and
      receipt.ingress==INGRESS and receipt.egress==EGRESS and
      receipt.payload_exposed_bytes==0 and receipt.disposed is True and
      sha256_obj(payload)==seal
    )

def read_private_payload(bucket:Bucket)->bytes:
    if bucket.disposed or not bucket.open:
        raise RuntimeError("private u is disposed / inaccessible")
    raise RuntimeError("private u is intentionally non-exportable")

def two_boundary_test()->dict:
    pr=PARENT.exhaustive_report()
    assert pr["status"]=="0e / v181 EXHAUSTIVE FINITE CONTROL PASS"
    bucket_ids=set(); receipt_seals=set(); ingress_pass=0; egress_pass=0
    for cell in range(PARENT.RING_CELLS):
        p=parent_anchor(cell); before=asdict(p)
        payload=f"u-private::{cell}::{p.control_state}".encode()

        b1=ingress(p,payload); b2=ingress(p,payload)
        assert b1==b2 and b1.open and not b1.disposed
        assert asdict(p)==before and b1.parent==p
        assert b1.private_payload_hash==hashlib.sha256(payload).hexdigest()
        assert b1.bucket_id not in bucket_ids
        bucket_ids.add(b1.bucket_id)
        try:
            read_private_payload(b1)
            raise AssertionError("private payload exported")
        except RuntimeError:
            pass
        ingress_pass+=1

        dead,r=egress(b1)
        assert dead.disposed and not dead.open
        assert asdict(p)==before and r.parent_fingerprint==p.parent_fingerprint
        assert r.payload_exposed_bytes==0 and verify_receipt(r)
        assert r.seal not in receipt_seals
        receipt_seals.add(r.seal)
        for op in ("read","egress"):
            try:
                read_private_payload(dead) if op=="read" else egress(dead)
                raise AssertionError("disposed u reopened")
            except RuntimeError:
                pass
        assert not verify_receipt(replace(r,payload_exposed_bytes=1))
        assert not verify_receipt(replace(r,disposed=False))
        egress_pass+=1

    return {
      "status":"0e / v182 TWO BOUNDARIES PASS","version":VERSION,
      "canon":{
        "referent":f"{REFERENT} = {REFERENT_MEANING}","point":POINT_LITERAL,
        "scale":SCALE_LITERAL,"u":U_LITERAL,"i":I_LITERAL,
        "primitive":PRIM_LITERAL,"expanded_primitive":EXPANDED_PRIM_LITERAL,
      },
      "boundaries":{
        "ingress":{"literal":INGRESS,"tests":ingress_pass,"parent_preserved":True,
          "deterministic_bucket":True,"raw_payload_exported":False},
        "egress":{"literal":EGRESS,"tests":egress_pass,"parent_preserved":True,
          "u_disposed":True,"payload_exposed_bytes":0,"sealed_i_receipt":True,
          "repeat_egress_rejected":True},
      },
      "total_boundary_transitions_tested":ingress_pass+egress_pass,
      "unique_buckets":len(bucket_ids),"unique_receipts":len(receipt_seals),
      "parent_control_states":pr["state_space"]["control_states"],
      "parent_ring_cells":pr["state_space"]["ring_cells"],
    }

if __name__=="__main__":
    print(json.dumps(two_boundary_test(),indent=2))
