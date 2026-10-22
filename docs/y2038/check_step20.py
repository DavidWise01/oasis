"""Step 20 synthetic release-gate tests; does NOT certify production."""
import hashlib,hmac,json,tempfile
from pathlib import Path
from datetime import datetime,timezone,timedelta
from step20_release import REQUIRED,canonical,check
KEY='fixture-key-only-not-for-production-0000000';NOW=datetime(2026,10,22,tzinfo=timezone.utc)
def fixture(root,name,when=None):
 data=('synthetic fixture for '+name).encode();(root/(name+'.evidence')).write_bytes(data)
 stmt=dict(requirement=name,result='PASS',evidence_sha256=hashlib.sha256(data).hexdigest(),reviewer='synthetic-test-reviewer',completed_utc=(when or NOW).isoformat())
 (root/(name+'.json')).write_text(json.dumps(dict(statement=stmt,mac=hmac.new(KEY.encode(),canonical(stmt),hashlib.sha256).hexdigest())))
def test():
 count=0
 def ok(pred,label):
  nonlocal count
  assert pred,label
  count+=1;print('PASS',label)
 with tempfile.TemporaryDirectory() as d:
  root=Path(d)
  ok(check(root,None,NOW)['decision']=='BLOCKED','no key')
  ok(check(root,KEY,NOW)['decision']=='BLOCKED','empty evidence')
  for name in REQUIRED:fixture(root,name)
  ok(check(root,KEY,NOW)['decision']=='PASS','synthetic complete fixture')
  name=REQUIRED[0];(root/(name+'.evidence')).write_text('tampered')
  ok(check(root,KEY,NOW)['decision']=='BLOCKED','evidence tamper')
  fixture(root,name);x=json.loads((root/(name+'.json')).read_text());x['statement']['reviewer']='forged';(root/(name+'.json')).write_text(json.dumps(x))
  ok(check(root,KEY,NOW)['decision']=='BLOCKED','forged attestation')
  fixture(root,name,when=NOW-timedelta(days=91))
  ok(check(root,KEY,NOW)['decision']=='BLOCKED','expired evidence')
  fixture(root,name);(root/(name+'.json')).unlink()
  ok(check(root,KEY,NOW)['decision']=='BLOCKED','missing attestation')
  fixture(root,name)
  ok(check(root,KEY,NOW)['decision']=='PASS','recovered fixture')
 print(f'RESULT {count}/8 PASS (synthetic only)')
if __name__=='__main__':test()
