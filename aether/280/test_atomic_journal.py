import base64,sqlite3,tempfile,threading,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from atomic_journal import SCHEMA,ZERO,canon,sha,bootstrap,commit_bundle,inspect

class TestJournal(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db=Path(temp.name)/"atomic.sqlite"
        self.priv={}
        keys=[]
        for i in range(3):
            source=f"source{i}"
            self.priv[source]=Ed25519PrivateKey.generate()
            pub=self.priv[source].public_key().public_bytes(
                serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
            keys.append({"source_id":source,"controller":f"controller{i}","public_key_pem":pub})
        self.pin=sha(keys)
        bootstrap(self.db,keys,self.pin)
    def bundle(self,number=1,run_id=280):
        challenge={"id":f"challenge-{number}","nonce":f"challenge-nonce-{number}",
                   "run_id":run_id,"source_commit":"a"*40}
        receipts=[]
        for i in range(3):
            source=f"source{i}"
            row={"source_id":source,"session_id":f"session-{number}-{i}",
                 "session_nonce":f"nonce-{number}-{i}","payload_sha256":"b"*64}
            stmt={"schema":SCHEMA,"operation":"SIGNED_RECEIPT","challenge":challenge,
                  "registry_sha256":self.pin,**row}
            row["signature_b64"]=base64.b64encode(self.priv[source].sign(canon(stmt))).decode()
            receipts.append(row)
        return {"challenge":challenge,"receipts":receipts}
    def test_first_atomic_commit(self):
        r=commit_bundle(self.db,self.bundle(),self.pin,ZERO)
        self.assertEqual(r["challenge_count"],1)
        self.assertEqual(r["receipt_count"],3)
        self.assertEqual(inspect(self.db)["checkpoints"],1)
    def test_reopened_commit(self):
        first=commit_bundle(self.db,self.bundle(),self.pin,ZERO)
        r=commit_bundle(self.db,self.bundle(2,281),self.pin,first["highwater_sha256"])
        self.assertEqual(r["seq"],2)
        self.assertEqual(inspect(self.db)["reasons"],["LOCAL_SQLITE_ROLLBACK_POSSIBLE"])
    def test_replay_challenge(self):
        first=commit_bundle(self.db,self.bundle(),self.pin,ZERO)
        with self.assertRaises(ValueError):
            commit_bundle(self.db,self.bundle(),self.pin,first["highwater_sha256"])
        self.assertEqual(inspect(self.db)["checkpoints"],1)
    def test_replay_session_valid_signature(self):
        first=commit_bundle(self.db,self.bundle(),self.pin,ZERO)
        other=self.bundle(2,281)
        row=other["receipts"][0]
        row["session_nonce"]="nonce-1-0"
        stmt={"schema":SCHEMA,"operation":"SIGNED_RECEIPT","challenge":other["challenge"],
              "registry_sha256":self.pin,**{k:row[k] for k in ("source_id","session_id","session_nonce","payload_sha256")}}
        row["signature_b64"]=base64.b64encode(self.priv[row["source_id"]].sign(canon(stmt))).decode()
        with self.assertRaisesRegex(ValueError,"PERSISTED_SESSION_REPLAY"):
            commit_bundle(self.db,other,self.pin,first["highwater_sha256"])
        self.assertEqual(inspect(self.db)["challenges"],1)
    def test_bad_third_signature_does_not_partially_commit(self):
        b=self.bundle()
        b["receipts"][2]["signature_b64"]="AAAA"
        with self.assertRaisesRegex(ValueError,"RECEIPT_SIGNATURE_INVALID"):
            commit_bundle(self.db,b,self.pin,ZERO)
        r=inspect(self.db)
        self.assertEqual((r["challenges"],r["receipts"],r["checkpoints"]),(0,0,0))
    def test_wrong_registry_pin(self):
        with self.assertRaisesRegex(ValueError,"REGISTRY_SEAL_MISMATCH"):
            commit_bundle(self.db,self.bundle(),"f"*64,ZERO)
    def test_wrong_expected_head(self):
        with self.assertRaisesRegex(ValueError,"STALE_CHECKPOINT_HEAD"):
            commit_bundle(self.db,self.bundle(),self.pin,"f"*64)
    def test_missing_receipt(self):
        b=self.bundle();b["receipts"].pop()
        with self.assertRaisesRegex(ValueError,"THREE_RECEIPTS_REQUIRED"):
            commit_bundle(self.db,b,self.pin,ZERO)
    def test_duplicate_source(self):
        b=self.bundle();b["receipts"][1]["source_id"]="source0"
        with self.assertRaises(ValueError):
            commit_bundle(self.db,b,self.pin,ZERO)
    def test_run_id_rollback(self):
        first=commit_bundle(self.db,self.bundle(run_id=281),self.pin,ZERO)
        with self.assertRaisesRegex(ValueError,"RUN_ID_ROLLBACK"):
            commit_bundle(self.db,self.bundle(2,280),self.pin,first["highwater_sha256"])
    def test_receipt_count_tamper_detected(self):
        commit_bundle(self.db,self.bundle(),self.pin,ZERO)
        with sqlite3.connect(self.db) as c:
            c.execute("DELETE FROM receipt WHERE session_nonce='nonce-1-0'")
        self.assertIn("RECEIPT_HIGHWATER_COUNT_DIVERGENCE",inspect(self.db)["reasons"])
    def test_highwater_digest_tamper_detected(self):
        commit_bundle(self.db,self.bundle(),self.pin,ZERO)
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE highwater SET head_sha256=? WHERE seq=1",("f"*64,))
        self.assertIn("HIGHWATER_HASH_INVALID",inspect(self.db)["reasons"])
    def test_double_writer_one_commit(self):
        b=self.bundle()
        barrier=threading.Barrier(2)
        outcomes=[]
        def attempt():
            barrier.wait()
            try:
                commit_bundle(self.db,b,self.pin,ZERO)
                outcomes.append("committed")
            except ValueError:outcomes.append("rejected")
        threads=[threading.Thread(target=attempt) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=10)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertEqual(sorted(outcomes),["committed","rejected"])
        self.assertEqual(inspect(self.db)["checkpoints"],1)
    def test_bootstrap_cannot_repeat(self):
        with self.assertRaisesRegex(ValueError,"REGISTRY_ALREADY_BOOTSTRAPPED"):
            bootstrap(self.db,[dict(source_id=s,controller="controller"+s[-1],
                public_key_pem=self.priv[s].public_key().public_bytes(
                  serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
                ) for s in self.priv],self.pin)
    def test_bad_bootstrap_pin(self):
        with tempfile.TemporaryDirectory() as temp:
            entries=[{"source_id":s,"controller":f"controller{s[-1]}",
                      "public_key_pem":self.priv[s].public_key().public_bytes(
                        serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
                     for s in self.priv]
            with self.assertRaisesRegex(ValueError,"REGISTRY_PIN_MISMATCH"):
                bootstrap(Path(temp)/"db",entries,"f"*64)
    def test_no_external_authority(self):
        report=inspect(self.db)
        self.assertEqual(report["operational_authority"],"HOLD")
        self.assertFalse(report["physical_act_allowed"])
if __name__=="__main__":
    unittest.main()
