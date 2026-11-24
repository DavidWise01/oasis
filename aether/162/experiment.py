#!/usr/bin/env python3
"""AETHER-162 GitHub compact checkout reproducer (synthetic only).
For exact locally executed 3200-check audit see companion evidence ZIP.
No actual instrument, accredited lab or physical samples were verified.
"""
import hashlib,hmac,json
SC=("clean_mock","valid_mock_rotation","missing_identity","cloned_serial",
"unverified_issuer","false_accreditation","self_rooted_chain","missing_attestation")
DUT=b"162-MOCK-DUT-PROOF";REF=b"162-MOCK-EXTERNAL-CERT-ISSUER";REG=b"162-MOCK-REFERENCE-REGISTRY"
def enc(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def seal(x,k):return dict(x,mac=hmac.new(k,enc(x),hashlib.sha256).hexdigest())
def valid(x,k):
 return isinstance(x,dict) and hmac.compare_digest(str(x.get("mac","")),hmac.new(k,enc({a:b for a,b in x.items() if a!="mac"}),hashlib.sha256).hexdigest())
def fixture(seed,case,t):
 bad=case not in SC[:2] and 6<=t<14;truth=.045 if bad else .005
 gen=2 if case=="valid_mock_rotation" and t>=10 else 1
 nonce=sha(enc([seed,case,t]))[:24]
 raw=enc(dict(serial="DUT162-1",reference="REF162-1",tick=t,nonce=nonce,reading=truth))
 d=dict(serial="DUT162-1",manufacturer="MOCK-MFG",model="MOCK-162",generation=gen,tick=t,nonce=nonce)
 c=dict(serial="REF162-1",issuer="MOCK-EXTERNAL-LAB",parent="MOCK-ROOT-PARENT",
  accreditation="MOCK-ACCREDITED",root="MOCK-EXTERNAL-ROOT",generation=gen,
  tick=t,nonce=nonce,dut_serial="DUT162-1",expiry=t+1,raw_sha=sha(raw),measured=truth,uncertainty=.0005)
 registry=dict(reference="REF162-1",issuer="MOCK-EXTERNAL-LAB",root="MOCK-EXTERNAL-ROOT",accredited=True)
 proof=dict(device="DUT162-1",nonce=nonce,tick=t)
 if bad:
  if case=="missing_identity":d["serial"]=""
  if case=="cloned_serial":proof["device"]="IMPOSTOR"
  if case=="unverified_issuer":c["issuer"]="UNKNOWN-LAB"
  if case=="false_accreditation":c["accreditation"]="SELF-ASSERTED"
  if case=="self_rooted_chain":c["parent"]="DUT162-1"
  if case=="missing_attestation":proof=None
 return truth,raw,seal(d,DUT),seal(c,REF),seal(registry,REG),seal(proof,DUT) if proof else None
def gate(raw,d,c,r,p):
 if not all([valid(d,DUT),valid(c,REF),valid(r,REG),valid(p,DUT)]):return False
 if d["serial"]!="DUT162-1" or d["manufacturer"]!="MOCK-MFG" or d["model"]!="MOCK-162":return False
 if p["device"]!=d["serial"] or p["nonce"]!=d["nonce"] or p["tick"]!=d["tick"]:return False
 if c["serial"]!=r["reference"] or c["issuer"]!=r["issuer"]!="UNKNOWN-LAB" or c["issuer"]!="MOCK-EXTERNAL-LAB":return False
 if c["parent"]!="MOCK-ROOT-PARENT" or c["root"]!=r["root"]!="MOCK-EXTERNAL-ROOT":return False
 if not r["accredited"] or c["accreditation"]!="MOCK-ACCREDITED":return False
 if c["dut_serial"]!=d["serial"] or c["generation"]!=d["generation"] or c["tick"]!=d["tick"] or c["nonce"]!=d["nonce"] or c["expiry"]!=d["tick"]+1:return False
 if sha(raw)!=c["raw_sha"]:return False
 try:
  x=json.loads(raw)
  return enc(x)==raw and x["serial"]==d["serial"] and x["reference"]==c["serial"] and x["nonce"]==d["nonce"] and x["tick"]==d["tick"] and abs(x["reading"]-c["measured"])<=c["uncertainty"] and x["reading"]+c["uncertainty"]<=.025
 except (ValueError,KeyError,TypeError):return False
def main():
 baseline=unsafe=safe=0
 for case in SC:
  for seed in range(162001,162026):
   for t in range(20):
    truth,raw,d,c,r,p=fixture(seed,case,t)
    allowed=gate(raw,d,c,r,p)
    baseline+=int(truth>.025);unsafe+=int(allowed and truth>.025);safe+=int(allowed and truth<=.025)
 assert (baseline,unsafe,safe)==(1200,0,2800),(baseline,unsafe,safe)
 print(json.dumps(dict(bound="AETHER-162",synthetic=True,baseline_unsafe=baseline,gate_unsafe=unsafe,gate_safe=safe,operational_ACT=0,physical_qualification_percent=0),indent=2))
if __name__=="__main__":main()
