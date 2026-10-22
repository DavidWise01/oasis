import hashlib,json,tempfile,sys
from pathlib import Path
from evidence import collect

def test():
    with tempfile.TemporaryDirectory() as directory:
        p=Path(directory)
        a=collect([sys.executable,'-c','print("verified")'],p/'success')
        assert a['result']=='PASS' and a['release_attestation'] is False
        assert hashlib.sha256((p/'success'/'run.log').read_bytes()).hexdigest()==a['logs_sha256']
        assert json.loads((p/'success'/'report.json').read_text())==a
        b=collect([sys.executable,'-c','raise SystemExit(5)'],p/'error')
        assert b['result']=='FAIL' and b['exit_code']==5
        c=collect([sys.executable,'-c','import time;time.sleep(3)'],p/'timeout',timeout=.01)
        assert c['result']=='FAIL' and c['exit_code']==124
        d=collect(['__missing_executable_fixture__'],p/'missing')
        assert d['result']=='FAIL' and d['exit_code']==127
        assert not any(x.get('release_attestation') for x in (a,b,c,d))
        print('PASS: 7 checks')
if __name__=='__main__':test()
