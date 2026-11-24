#!/usr/bin/env python3
"""AETHER-164 checkout companion — simulated calibration evidence only.
The EXACT locally executed 3200-check source is in the AETHER-164 evidence ZIP,
SHA256 93f5d7d536209ff7b1ac079b2e27c4b4417f6519e9828390e665b4181602f798.
This shorter GitHub variant has not been independently executed from checkout.
"""
import hashlib,hmac,json,math
CASES=("clean_mock","legitimate_reference_rotation","missing_uncertainty_component",
"shared_ancestry","expired_calibration","understated_resolution",
"unsupported_coverage","contradictory_reference")
KEY=b'AETHER164-REFERENCE';BENCH=b'AETHER164-BENCH'
COMP={"calibration":.001,"repeatability":.0005,"resolution":.0004,"drift":.0006}
def enc(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def sha(v):return hashlib.sha256(v).hexdigest()
def seal(v,k):return dict(v,mac=hmac.new(k,enc(v),hashlib.sha256).hexdigest())
def valid(v,k):return hmac.compare_digest(v.get("mac",""),hmac.new(k,enc({x:y for x,y in v.items() if x!="mac"}),hashlib.sha256).hexdigest())
def lower(h,n):
 z=1.6448536269514722;p=h/n;z2=z*z
 return (p+z2/(2*n)-z*math.sqrt((p*(1-p)+z2/(4*n))/n))/(1+z2/n)
def fixture(seed,case,t):
 fault=case not in CASES[:2] and 6<=t<14
 truth=.045 if fault else .005
 g=2 if case=="legitimate_reference_rotation" and t>=10 else 1
 nonce=sha(enc([seed,case,t]))[:24]
 raw=enc(dict(device="DUT-164",reference="REF-164",tick=t,nonce=nonce,generation=g,reading=truth))
 c=dict(serial="REF-164",dut="DUT-164",tick=t,nonce=nonce,generation=g,
   issuer="MOCK-LAB",parent="MOCK-INDEPENDENT-ROOT",expiry=t+1,
   uncertainty_components=dict(COMP),factor=2,coverage=.95,n=120,hits=120,
   raw_sha=sha(raw),reading=truth)
 b=dict(reference="REF-164",device="DUT-164",tick=t,nonce=nonce,generation=g,
   observed=truth,uncertainty=.0003)
 if fault:
  if case=="missing_uncertainty_component":del c["uncertainty_components"]["drift"]
  elif case=="shared_ancestry":c["parent"]="DUT-164"
  elif case=="expired_calibration":c["expiry"]=t
  elif case=="understated_resolution":c["uncertainty_components"]["resolution"]=.00001
  elif case=="unsupported_coverage":c["hits"]=100
  elif case=="contradictory_reference":c["reading"]=.005
 return truth,raw,seal(c,KEY),seal(b,BENCH)
def admit(raw,c,b):
 if not (valid(c,KEY) and valid(b,BENCH)):return False
 if c["issuer"]!="MOCK-LAB" or c["parent"]!="MOCK-INDEPENDENT-ROOT":return False
 if not (c["serial"]==b["reference"]=="REF-164" and c["dut"]==b["device"]=="DUT-164"):return False
 if any(c[k]!=b[k] for k in ("tick","nonce","generation")):return False
 if c["expiry"]!=c["tick"]+1 or sha(raw)!=c["raw_sha"]:return False
 u=c["uncertainty_components"]
 if set(u)!=set(COMP) or any(u[k]<v for k,v in COMP.items()):return False
 if c["factor"]!=2 or c["coverage"]!=.95 or c["n"]!=120 or lower(c["hits"],120)<.95:return False
 try:
  x=json.loads(raw)
  if enc(x)!=raw or x["device"]!=c["dut"] or x["reference"]!=c["serial"] or x["tick"]!=c["tick"] or x["nonce"]!=c["nonce"] or x["generation"]!=c["generation"]:return False
  expanded=2*math.sqrt(sum(v*v for v in u.values()))
  return abs(x["reading"]-c["reading"])<=expanded and abs(c["reading"]-b["observed"])<=expanded+b["uncertainty"] and max(x["reading"],c["reading"],b["observed"])+expanded+b["uncertainty"]<=.025
 except (KeyError,TypeError,ValueError):return False
def main():
 baseline=unsafe=safe=0
 for case in CASES:
  for seed in range(164001,164026):
   for t in range(20):
    truth,raw,c,b=fixture(seed,case,t)
    action=admit(raw,c,b)
    baseline+=int(truth>.025);unsafe+=int(action and truth>.025);safe+=int(action and truth<=.025)
 assert (baseline,unsafe,safe)==(1200,0,2800),(baseline,unsafe,safe)
 print(json.dumps({"bound":"AETHER-164","synthetic":True,"signed_only_unsafe":baseline,"gated_unsafe":unsafe,"safe_dry_run":safe,"physical_samples":0,"operational_ACT":"HOLD"},indent=2))
if __name__=="__main__":main()
