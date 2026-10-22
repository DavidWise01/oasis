"""Phase 2.5: record execution evidence; never manufacture release attestations."""
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

def collect(command, output, timeout=180):
    if not command or not all(isinstance(x,str) for x in command):
        raise ValueError('command required')
    started=datetime.now(timezone.utc)
    try:
        p=subprocess.run(command,capture_output=True,text=True,timeout=timeout,check=False)
        rc=p.returncode; stdout=p.stdout; stderr=p.stderr; error=None
    except subprocess.TimeoutExpired as ex:
        rc=124
        stdout=(ex.stdout or b'').decode(errors='replace') if isinstance(ex.stdout,bytes) else ex.stdout or ''
        stderr=(ex.stderr or b'').decode(errors='replace') if isinstance(ex.stderr,bytes) else ex.stderr or ''
        error='timeout'
    except OSError as ex:
        rc=127;stdout='';stderr='';error=type(ex).__name__
    ended=datetime.now(timezone.utc)
    # Logs can contain credentials; review and protect them before sharing.
    logs=(stdout+'\n---STDERR---\n'+stderr).encode()
    report={'schema':'it3-phase2.5-evidence-v1','started_utc':started.isoformat(),
      'ended_utc':ended.isoformat(),'command':command,'exit_code':rc,
      'result':'PASS' if rc==0 and error is None else 'FAIL',
      'error':error,'logs_sha256':hashlib.sha256(logs).hexdigest(),
      'origin':'live-command-execution' if error is None else 'failed-command-execution',
      'release_attestation':False}
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    (output/'run.log').write_bytes(logs)
    (output/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    p.add_argument('--timeout',type=int,default=180)
    p.add_argument('cmd',nargs=argparse.REMAINDER)
    a=p.parse_args();cmd=a.cmd[1:] if a.cmd[:1]==['--'] else a.cmd
    result=collect(cmd,a.output,a.timeout)
    print(json.dumps(result,sort_keys=True))
    return 0 if result['result']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
