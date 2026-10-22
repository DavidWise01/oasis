"""Fail-closed release attestation gate. No certification implied."""
import argparse,hashlib,hmac,json,os,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
REQUIRED=('consensus_multi_leader_safety','durable_wal_restart','quorum_partition_recovery','mtls_membership_replay','snapshot_restore_backup_drill','multi_host_chaos_test','formal_protocol_verification','operations_runbook_and_monitoring')
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def check(evidence_dir,key=None,now=None):
 now=now or datetime.now(timezone.utc);root=Path(evidence_dir);approved=[];blocked=[]
 if not key or len(key)<32:return dict(decision='BLOCKED',approved=[],blocked=['release attestation key is absent/short']+list(REQUIRED))
 for name in REQUIRED:
  try:
   obj=json.loads((root/(name+'.json')).read_text(encoding='utf-8'))
   if set(obj)!={'statement','mac'}:raise ValueError('invalid envelope')
   s=obj['statement']
   if set(s)!={'requirement','result','evidence_sha256','reviewer','completed_utc'}:raise ValueError('invalid statement')
   if s['requirement']!=name or s['result']!='PASS':raise ValueError('not passed')
   if not isinstance(s['reviewer'],str) or not s['reviewer'].strip():raise ValueError('reviewer absent')
   mac=hmac.new(key.encode(),canonical(s),hashlib.sha256).hexdigest()
   if not isinstance(obj['mac'],str) or not hmac.compare_digest(mac,obj['mac']):raise ValueError('unauthenticated')
   t=datetime.fromisoformat(s['completed_utc'].replace('Z','+00:00'))
   if t.tzinfo is None or t>now or now-t>timedelta(days=90):raise ValueError('stale or future')
   evidence=(root/(name+'.evidence')).read_bytes()
   if not evidence or hashlib.sha256(evidence).hexdigest()!=s['evidence_sha256']:raise ValueError('missing or mismatched evidence')
   approved.append(name)
  except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:blocked.append(name+': '+str(exc))
 return dict(decision='BLOCKED' if blocked else 'PASS',approved=approved,blocked=blocked)
def main():
 p=argparse.ArgumentParser();p.add_argument('--evidence-dir',default='docs/y2038/release-evidence');p.add_argument('--output')
 a=p.parse_args();r=check(a.evidence_dir,os.environ.get('Y2038_RELEASE_ATTESTATION_KEY'))
 out=json.dumps(r,sort_keys=True,indent=2);print(out)
 if a.output:Path(a.output).write_text(out+'\n',encoding='utf-8')
 return 0 if r['decision']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
