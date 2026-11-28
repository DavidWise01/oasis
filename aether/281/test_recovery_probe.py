import base64,copy,os,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"280"))
from atomic_journal import bootstrap,commit_bundle,canon,sha,ZERO,connect
from recovery_probe import readback,validate,snapshot,assess

def build():
    private=[Ed25519PrivateKey.generate() for _ in range(3)]
    keys=[{"source_id":f"source{i}","controller":f"controller{i}",
           "public_key_pem":private[i].public_key().public_bytes(
             serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
          for i in range(3)]
    return private,keys,sha(keys)

def bundle(private,pin,n=1):
    challenge={"id":f"challenge-{n}","nonce":f"cn{n}","run_id":281,"source_commit":"a"*40}
    receipts=[]
    for i,k in enumerate(private):
        r={"source_id":f"source{i}","session_id":f"session-{n}-{i}",
           "session_nonce":f"nonce-{n}-{i}","payload_sha256":"b"*64}
        stmt={"schema":"AETHER-280/atomic-journal-v1","operation":"SIGNED_RECEIPT",
              "challenge":challenge,"registry_sha256":pin,**r}
        r["signature_b64"]=base64.b64encode(k.sign(canon(stmt))).decode()
        receipts.append(r)
    return {"challenge":challenge,"receipts":receipts}

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"journal.sqlite"
        self.private,self.keys,self.pin=build()
        bootstrap(self.db,self.keys,self.pin)
    def commit(self,n=1,head=ZERO):
        return commit_bundle(self.db,bundle(self.private,self.pin,n),self.pin,head)
    def check(self,change,reason):
        self.commit()
        view=readback(self.db)
        baseline=snapshot(view)
        change()
        report=assess(readback(self.db),baseline,sha(baseline))
        self.assertIn(reason,report["reasons"],report)
        self.assertEqual(report["operational_authority"],"HOLD")
    def test_empty_restart_read(self):
        v=readback(self.db);self.assertEqual(v["challenges"],[])
        self.assertEqual(validate(v),[])
    def test_committed_restart_recovers_all_four_tables(self):
        self.commit()
        v=readback(self.db)
        self.assertEqual((len(v["challenges"]),len(v["receipts"]),len(v["highwater"])),(1,3,1))
        self.assertEqual(validate(v),[])
    def test_precommit_process_exit_rolls_back(self):
        script="import sqlite3,os,sys;d=sqlite3.connect(sys.argv[1]);d.execute('BEGIN IMMEDIATE');d.execute('INSERT INTO challenge VALUES (?,?,?)',('uncommitted','a'*64,'b'*64));os._exit(17)"
        r=subprocess.run([sys.executable,"-c",script,str(self.db)],timeout=10)
        self.assertEqual(r.returncode,17)
        v=readback(self.db)
        self.assertEqual((len(v["challenges"]),len(v["receipts"]),len(v["highwater"])),(0,0,0))
    def test_postcommit_process_exit_recovers(self):
        # A subprocess commits an atomic transaction and terminates without closing.
        script="import sqlite3,os,sys;d=sqlite3.connect(sys.argv[1]);d.execute('BEGIN IMMEDIATE');d.execute('INSERT INTO challenge VALUES (?,?,?)',('committed','a'*64,'b'*64));d.commit();os._exit(18)"
        r=subprocess.run([sys.executable,"-c",script,str(self.db)],timeout=10)
        self.assertEqual(r.returncode,18)
        self.assertEqual(len(readback(self.db)["challenges"]),1)
    def test_receipt_deleted_same_counts_anchor(self):
        self.check(lambda:self.db_write("DELETE FROM receipt WHERE session_nonce='nonce-1-0'"),"RECOVERY_RECEIPT_COUNT_ROLLBACK")
    def test_payload_changed_same_count(self):
        self.check(lambda:self.db_write("UPDATE receipt SET payload_sha256=? WHERE session_nonce='nonce-1-0'",("f"*64,)),
                   "ANCHORED_JOURNAL_CONTENT_CHANGED")
    def test_signature_changed_same_count(self):
        self.check(lambda:self.db_write("UPDATE receipt SET signature_b64=? WHERE session_nonce='nonce-1-0'",("AAAA",)),
                   "ANCHORED_JOURNAL_CONTENT_CHANGED")
    def test_highwater_digest_replaced(self):
        self.check(lambda:self.db_write("UPDATE highwater SET head_sha256=? WHERE seq=1",("f"*64,)),
                   "HIGHWATER_DIGEST_MISMATCH")
    def test_registry_changed(self):
        self.check(lambda:self.db_write("UPDATE signer SET public_key_pem=? WHERE source_id='source0'",("fake",)),
                   "REGISTRY_SEAL_MISMATCH")
    def test_challenge_removed(self):
        # Foreign-key enforcement on the forensic test connection is deliberately off,
        # modeling corrupt/injected storage rather than normal transactions.
        self.check(lambda:self.db_write("DELETE FROM challenge WHERE nonce='cn1'"),"JOURNAL_CONSERVATION_INVALID")
    def test_missing_anchor_pin(self):
        self.commit();self.assertIn("OUT_OF_BAND_ANCHOR_PIN_REQUIRED",assess(readback(self.db))["reasons"])
    def test_wrong_anchor_pin(self):
        self.commit();v=readback(self.db);a=snapshot(v)
        self.assertIn("EXTERNAL_ANCHOR_PIN_MISMATCH",assess(v,a,"f"*64)["reasons"])
    def test_anchor_head_mismatch(self):
        self.commit();a=snapshot(readback(self.db));a["last_head_sha256"]="f"*64
        self.assertIn("ANCHORED_HEAD_SUBSTITUTED",assess(readback(self.db),a,sha(a))["reasons"])
    def test_newer_history_prefix_not_proven(self):
        first=self.commit();a=snapshot(readback(self.db))
        self.commit(2,first["highwater_sha256"])
        self.assertIn("HISTORICAL_PREFIX_NOT_PROVEN_BY_LATEST_HEAD_ONLY",
                      assess(readback(self.db),a,sha(a))["reasons"])
    def test_valid_snapshot_still_hold(self):
        self.commit();v=readback(self.db);a=snapshot(v)
        r=assess(v,a,sha(a))
        self.assertFalse(r["physical_act_allowed"])
        self.assertIn("EXTERNAL_ANCHOR_NOT_INDEPENDENTLY_ACQUIRED",r["reasons"])
    def db_write(self,sql,params=()):
        with sqlite3.connect(self.db) as db:db.execute(sql,params)

if __name__=="__main__":unittest.main()
