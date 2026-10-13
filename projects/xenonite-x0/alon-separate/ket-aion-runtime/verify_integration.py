#!/usr/bin/env python3
"""Independent regression for K.E.T.-aligned adapter; runs synthetic workloads."""
import json, pathlib, shutil, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parent
SCRIPT=ROOT/'ket_aion.py'

def call(mode,out):
    return subprocess.run([sys.executable,str(SCRIPT),'--module',mode,'--out',str(out)],capture_output=True,text=True,timeout=120)

def check():
    count=0
    with tempfile.TemporaryDirectory(prefix='ket-aion-verification-') as d:
        root=pathlib.Path(d)
        for mode,target in [('all','both'),('crystal','crystal'),('pulse','pulse')]:
            out=root/target
            first=call(mode,out)
            assert first.returncode==0,first.stderr
            r1=json.loads((out/'ket-aion-receipt.json').read_text())
            assert r1['mode']==mode and not r1['tracks']['u.s']['idempotent_replay']
            assert r1['checks_passed']==({'all':11,'crystal':6,'pulse':5}[mode]); count+=3
            second=call(mode,out)
            assert second.returncode==0,second.stderr
            r2=json.loads((out/'ket-aion-receipt.json').read_text())
            assert r2['event_id']==r1['event_id']
            assert r2['outputs_sha256']==r1['outputs_sha256']
            assert r2['tracks']['u.s']['idempotent_replay']
            assert len((out/'ket-aion-ledger.jsonl').read_text().splitlines())==1; count+=4
            if mode=='all':
                original=(out/'ket-aion-ledger.jsonl').read_text()
                with (out/'ket-aion-ledger.jsonl').open('a') as f:f.write('{"sequence":999,"entry_hash":"forged"}\n')
                failed=call(mode,out)
                assert failed.returncode!=0
                assert 'QUARANTINED' in failed.stderr and 'hash-chain invalid' in failed.stderr
                (out/'ket-aion-ledger.jsonl').write_text(original);count+=3
    print(f'INTEGRATION REGRESSION PASS — {count}/{count} independent conditions')

if __name__=='__main__':check()
