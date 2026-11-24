#!/usr/bin/env python3
"""AETHER-166 compact GitHub reproduction. SYNTHETIC ONLY.
Exact locally run 3200-check source SHA-256:
5c096f560730de2171d5538c842bce3abfc52a7d452ca70db3b9db348cda9613
is retained in the evidence ZIP. This independently authored reproduction is
NOT a confirmed byte-for-byte match to the locally executed audit.
"""
import hashlib,hmac,json,math
CASES=("clean","legitimate_rotation","missing_drift_sample","excess_drift",
 "suppressed_alarm","late_alarm","forged_baseline","clock_regression")
KEY=b"166_SIM_REFERENCE";ALARM=b"166_SIM_ALARM"
def enc(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def sign(x,k):return dict(x,mac=hmac.new(k,enc(x),hashlib.sha256).hexdigest())
def valid(x,k):return bool(x) and hmac.compare_digest(x.get("mac",""),hmac.new(k,enc({a:b for a,b in x.items() if a!="mac"}),hashlib.sha256).hexdigest())
def specimen(seed,scenario,t):
 bad=scenario not in CASES[:2] and 6<=t<14
 truth=.045 if bad else .005
 generation=2 if scenario=="legitimate_rotation" and t>=10 else 1
 nonce=hashlib.sha256(enc([seed,scenario,t])).hexdigest()[:24]
 start=1800000000000000000+t*1000000000
 ref=dict(serial="DUT-166",tick=t,generation=generation,nonce=nonce,
  baseline=t,clock_anchor=start,drift=[.0002,.0003,.0004],
  limit=.001,measured=truth,uncertainty=.0005,expires=t+1,root="SIM-REF")
 alarm=dict(serial="DUT-166",tick=t,generation=generation,nonce=nonce,
  trigger=int(truth>.025),observed=int(truth>.025),
  sent=start+10000000,received=start+30000000)
 if bad:
  if scenario=="missing_drift_sample":ref["drift"]=ref["drift"][:2]
  elif scenario=="excess_drift":ref["drift"][2]=.002
  elif scenario=="suppressed_alarm":alarm["observed"]=0
  elif scenario=="late_alarm":alarm["received"]+=100000000
  elif scenario=="forged_baseline":ref["baseline"]=t-1
  elif scenario=="clock_regression":alarm["sent"]=start-10000000
 return truth,sign(ref,KEY),sign(alarm,ALARM)
def admit(r,a):
 if not valid(r,KEY) or not valid(a,ALARM):return False
 if any(r[k]!=a[k] for k in ("serial","tick","generation","nonce")):return False
 t=r["tick"];start=1800000000000000000+t*1000000000
 if r["serial"]!="DUT-166" or r["root"]!="SIM-REF":return False
 if r["baseline"]!=t or r["expires"]!=t+1 or r["clock_anchor"]!=start:return False
 if len(r["drift"])!=3 or any(not 0<=v<=r["limit"]<=.001 for v in r["drift"]):return False
 if a["sent"]!=start+10000000 or not 0<a["received"]-a["sent"]<=50000000:return False
 if a["trigger"]!=a["observed"] or a["trigger"]!=int(r["measured"]>.025):return False
 return not a["observed"] and r["measured"]+r["uncertainty"]+r["limit"]<=.025
def main():
 baseline=unsafe=safe=0
 for case in CASES:
  for seed in range(166001,166026):
   for t in range(20):
    truth,r,a=specimen(seed,case,t);permission=admit(r,a)
    baseline+=int(truth>.025)
    unsafe+=int(permission and truth>.025)
    safe+=int(permission and truth<=.025)
 assert (baseline,unsafe,safe)==(1200,0,2800),(baseline,unsafe,safe)
 print(json.dumps(dict(bound="AETHER-166",synthetic_only=True,baseline_unsafe=baseline,
  gated_unsafe=unsafe,safe_dry_run=safe,physical_samples=0,operational_act="HOLD"),indent=2))
if __name__=="__main__":main()
