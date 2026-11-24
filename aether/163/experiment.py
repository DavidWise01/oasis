#!/usr/bin/env python3
"""AETHER-163 GitHub checkout companion — SYNTHETIC ONLY.
The exact fully audited 3200-check program is separately packaged in the
AETHER-163 local evidence ZIP as experiment.py; SHA-256
f7f97695000d4cb20f1f1daee7aeabfcc28adb25dcad46bd43b6a61b2736f04c.
This companion is independently authored and NOT the executed audit.
"""
import hashlib,hmac,json
SC=("clean_mock","valid_clock_rotation","missing_original_bytes","altered_capture_bytes",
    "sample_counter_gap","clock_rollback","forged_timebase_anchor","capture_source_swap")
KEY=b"AETHER163-MOCK-REFERENCE"
def encode(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def sign(o):return dict(o,mac=hmac.new(KEY,encode(o),hashlib.sha256).hexdigest())
def authentic(o):
 return hmac.compare_digest(o.get("mac",""),hmac.new(KEY,encode({k:v for k,v in o.items() if k!="mac"}),hashlib.sha256).hexdigest())
def create(seed,case,t):
 bad=case not in SC[:2] and 6<=t<14
 truth=.045 if bad else .005
 gen=2 if case=="valid_clock_rotation" and t>=10 else 1
 nonce=sha(encode([seed,case,t]))[:24]
 start=1700000000000000000+t*1000000000
 sample=[dict(counter=3*t+i,stamp_ns=start+10000000*i,reading=truth) for i in range(3)]
 obj=dict(serial="DUT163-1",reference="REF163-1",tick=t,nonce=nonce,generation=gen,clock="MOCK-PTP-163",samples=sample)
 raw=encode(obj)
 receipt=dict(serial="DUT163-1",reference="REF163-1",generation=gen,
    tick=t,nonce=nonce,raw_sha=sha(raw),start_ns=start,first_counter=t*3,
    interval_ns=10000000,clock="MOCK-PTP-163",measured=truth,uncertainty=.0005)
 if bad:
  if case=="missing_original_bytes":raw=b""
  elif case=="altered_capture_bytes":raw+=b"\n"
  elif case=="sample_counter_gap":
   sample[1]["counter"]+=2;raw=encode(obj);receipt["raw_sha"]=sha(raw)
  elif case=="clock_rollback":
   sample[2]["stamp_ns"]=start-10000000;raw=encode(obj);receipt["raw_sha"]=sha(raw)
  elif case=="forged_timebase_anchor":receipt["start_ns"]+=10000000
  elif case=="capture_source_swap":
   obj["serial"]="IMPOSTOR";raw=encode(obj);receipt["raw_sha"]=sha(raw)
 return truth,raw,sign(receipt)
def permit(raw,r):
 if not raw or not authentic(r) or sha(raw)!=r["raw_sha"]:return False
 if r["serial"]!="DUT163-1" or r["reference"]!="REF163-1" or r["clock"]!="MOCK-PTP-163":return False
 if r["start_ns"]!=1700000000000000000+r["tick"]*1000000000 or r["first_counter"]!=r["tick"]*3 or r["interval_ns"]!=10000000:return False
 try:
  d=json.loads(raw)
  if encode(d)!=raw or any(d[k]!=r[k] for k in ("serial","reference","tick","nonce","generation","clock")):return False
  rows=d["samples"]
  if len(rows)!=3 or [x["counter"] for x in rows]!=[r["first_counter"]+i for i in range(3)]:return False
  if [x["stamp_ns"] for x in rows]!=[r["start_ns"]+i*r["interval_ns"] for i in range(3)]:return False
  if any(abs(x["reading"]-r["measured"])>r["uncertainty"] for x in rows):return False
  return max(x["reading"] for x in rows)+r["uncertainty"]<=.025
 except (KeyError,ValueError,TypeError):return False
def main():
 base=unsafe=safe=0
 for case in SC:
  for seed in range(163001,163026):
   for tick in range(20):
    truth,raw,receipt=create(seed,case,tick)
    allowed=permit(raw,receipt)
    base+=int(truth>.025);unsafe+=int(allowed and truth>.025);safe+=int(allowed and truth<=.025)
 assert (base,unsafe,safe)==(1200,0,2800),(base,unsafe,safe)
 print(json.dumps(dict(bound="AETHER-163",synthetic=True,baseline_unsafe=base,
  guarded_unsafe=unsafe,guarded_safe=safe,physical_qualification_percent=0,
  operational_ACT=0),indent=2))
if __name__=="__main__":main()
