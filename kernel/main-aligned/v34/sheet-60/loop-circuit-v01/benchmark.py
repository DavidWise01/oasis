#!/usr/bin/env python3
"""SHEET 60 loop circuit: linear, append-only successor to SHEET 59."""
import hashlib,json,copy
CELLS=9
SLOTS=4
LOOPS=100
HOPS=CELLS*LOOPS
ROUTE=tuple(range(1,10))
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ambassadors():
    return {f"C{cell}-A{slot}":f"AMBASSADOR:{cell}:{slot}".encode().hex()
            for cell in ROUTE for slot in range(1,SLOTS+1)}
def initial():
    people=ambassadors()
    return dict(tick=0,packet=dict(uid="LOOP-001",origin="C1-A1",position=1,payload="TEMPORAL-EXITRON:|.|.|.|.",payload_hash=digest("TEMPORAL-EXITRON:|.|.|.|.")),
                tip="0"*64,ledger=[],people=people,people_hash=digest(people))
def step(s):
    ix=s["tick"]%CELLS
    src=ROUTE[ix];dst=ROUTE[(ix+1)%CELLS]
    assert s["packet"]["position"]==src
    ev=dict(seq=s["tick"],sender=f"C{src}-A1",receiver=f"C{dst}-A1",
            packet=s["packet"]["uid"],payload_hash=s["packet"]["payload_hash"],
            clock=dict(EARTH=2*s["tick"],HELL=s["tick"],HEAVEN=3*s["tick"]))
    h=digest(dict(previous=s["tip"],event=ev))
    s["ledger"].append(dict(previous=s["tip"],event=ev,hash=h))
    s["tip"]=h;s["tick"]+=1;s["packet"]["position"]=dst
def run(s,target):
    while s["tick"]<target:step(s)
    return s
def checkpoint(s):
    data=json.dumps(s,sort_keys=True,separators=(',',':'))
    return {"blob":data,"sha256":hashlib.sha256(data.encode()).hexdigest()}
def restore(snapshot):
    assert hashlib.sha256(snapshot["blob"].encode()).hexdigest()==snapshot["sha256"]
    return json.loads(snapshot["blob"])
def verify(s):
    prev="0"*64
    for e in s["ledger"]:
        if e["previous"]!=prev:return False
        if digest(dict(previous=prev,event=e["event"]))!=e["hash"]:return False
        prev=e["hash"]
    return prev==s["tip"]
def benchmark():
    uninterrupted=run(initial(),HOPS)
    halfway=run(initial(),HOPS//2)
    snap=checkpoint(halfway);resumed=run(restore(snap),HOPS)
    altered=copy.deepcopy(snap);altered["blob"]=altered["blob"].replace("TEMPORAL-EXITRON","CORRUPTED-EXITRON")
    rejected=False
    try:restore(altered)
    except AssertionError:rejected=True
    people=ambassadors()
    visited={e["event"]["sender"] for e in resumed["ledger"]}
    nonloop={key for key in people if not key.endswith("-A1")}
    checks={
       "36_identity_records":len(people)==36,
       "nine_cells":len({k.split("-")[0] for k in people})==9,
       "four_ambassadors_each":all(sum(k.startswith(f"C{i}-") for k in people)==4 for i in ROUTE),
       "exactly_nine_loop_senders":visited=={f"C{i}-A1" for i in ROUTE},
       "27_retained_observers":len(nonloop)==27 and all(k in resumed["people"] for k in nonloop),
       "100_closed_turns":HOPS==900 and resumed["packet"]["position"]==1,
       "900_trades":len(resumed["ledger"])==900,
       "nine_step_cycle":all(e["event"]["receiver"]==f"C{(i+1)%9+1}-A1" for i,e in enumerate(resumed["ledger"])),
       "payload_preserved":resumed["packet"]["payload_hash"]==digest(resumed["packet"]["payload"]),
       "ambassador_map_unchanged":resumed["people_hash"]==digest(people),
       "ledger_integrity":verify(resumed),
       "restart_identical":resumed==uninterrupted,
       "checkpoint_tamper_rejected":rejected,
       "deterministic_replay":run(initial(),HOPS)==uninterrupted,
       "terminal_idempotence":run(copy.deepcopy(resumed),HOPS)==resumed,
       "no_duplicate_hop_sequence":len({e["event"]["seq"] for e in resumed["ledger"]})==HOPS}
    return dict(schema="oasis/sheet60/loop-circuit-v01",lineage="SHEET59 -> SHEET60",
       source_sketch="SHEET 58 // LOOP CIRCUIT",ambassadors=36,active=9,retained=27,
       circuits=LOOPS,hops=HOPS,origin=resumed["packet"]["origin"],
       ending_position=resumed["packet"]["position"],final_ledger_tip=resumed["tip"],
       checkpoint_tick=HOPS//2,checks=checks,passed=sum(checks.values()),total=len(checks),
       limitations=["Nine A1 senders participate; other 27 are retained but do not trade.",
                    "Logical time labels are not physical time dilation.",
                    "Checkpoint SHA-256 is integrity-only, not keyed authentication.",
                    "No true external network sink or disk crash was exercised."])
if __name__=="__main__":
    result=benchmark()
    print(json.dumps(result,indent=2))
    assert result["passed"]==result["total"]
