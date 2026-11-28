import base64,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from retained_journal import ZERO,SCHEMA,bootstrap,append,examine,canon,sha,receipt_statement

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/"retained.db"
        self.keys={f"s{i}":Ed25519PrivateKey.generate() for i in range(3)}
        entries=[{"source_id":s,"controller":"controller"+s[-1],
                  "pem":key.public_key().public_bytes(serialization.Encoding.PEM,
                        serialization.PublicFormat.SubjectPublicKeyInfo).decode()} for s,key in self.keys.items()]
        self.pin=sha(entries);bootstrap(self.path,entries,self.pin)
    def bundle(self,n):
        c={"id":"c"+str(n),"nonce":"challenge"+str(n),"run_id":282+n,
           "source_commit":"a"*40}
        receipts=[]
        for i in range(3):
            s=f"s{i}";sid=f"session{n}-{i}";nonce=f"nonce{n}-{i}";payload="b"*64
            st=receipt_statement(c,self.pin,s,sid,nonce,payload)
            receipts.append({"source_id":s,"session_id":sid,"session_nonce":nonce,
                 "payload_sha256":payload,
                 "signature_b64":base64.b64encode(self.keys[s].sign(canon(st))).decode()})
        return {"challenge":c,"receipts":receipts}
    def test_signatures_reverified_after_restart(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        r=examine(self.path)
        self.assertTrue(r["observed"]["all_receipt_signatures_rechecked"])
        self.assertNotIn("STORED_RECEIPT_SIGNATURE_INVALID",r["reasons"])
    def test_original_challenge_retained(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        with sqlite3.connect(self.path) as db:
            raw=db.execute("SELECT original_json FROM challenge").fetchone()[0]
        self.assertEqual(__import__("json").loads(raw)["nonce"],"challenge1")
    def test_second_head_and_prefix(self):
        one=append(self.path,self.bundle(1),self.pin,ZERO)
        append(self.path,self.bundle(2),self.pin,one["head_sha256"])
        self.assertNotIn("HISTORICAL_PREFIX_CHANGED",
                         examine(self.path,1,one["head_sha256"])["reasons"])
    def test_historical_prefix_wrong(self):
        one=append(self.path,self.bundle(1),self.pin,ZERO)
        append(self.path,self.bundle(2),self.pin,one["head_sha256"])
        self.assertIn("HISTORICAL_PREFIX_CHANGED",examine(self.path,1,"f"*64)["reasons"])
    def test_missing_historical_prefix(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        self.assertIn("HISTORICAL_PREFIX_REMOVED",examine(self.path,2,"f"*64)["reasons"])
    def test_receipt_signature_tamper(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE receipt SET signature_b64='AAAA' WHERE source_id='s0'")
        self.assertIn("STORED_RECEIPT_SIGNATURE_INVALID",examine(self.path)["reasons"])
    def test_original_challenge_tamper(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE challenge SET original_json='{}'")
        self.assertIn("ORIGINAL_CHALLENGE_UNREADABLE",examine(self.path)["reasons"])
    def test_receipt_payload_tamper(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE receipt SET payload_sha='f'||substr(payload_sha,2)")
        self.assertIn("STORED_RECEIPT_SIGNATURE_INVALID",examine(self.path)["reasons"])
    def test_atomic_reject_bad_third_signature(self):
        b=self.bundle(1);b["receipts"][2]["signature_b64"]="AAAA"
        with self.assertRaisesRegex(ValueError,"SIGNATURE_INVALID"):
            append(self.path,b,self.pin,ZERO)
        self.assertEqual(examine(self.path)["observed"]["heads"],0)
    def test_replayed_challenge(self):
        h=append(self.path,self.bundle(1),self.pin,ZERO)["head_sha256"]
        with self.assertRaises(ValueError):
            append(self.path,self.bundle(1),self.pin,h)
    def test_stale_head(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        with self.assertRaisesRegex(ValueError,"STALE_HEAD"):
            append(self.path,self.bundle(2),self.pin,ZERO)
    def test_wrong_pin(self):
        with self.assertRaisesRegex(ValueError,"REGISTRY_SEAL_INVALID"):
            append(self.path,self.bundle(1),"f"*64,ZERO)
    def test_count_corruption(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        with sqlite3.connect(self.path) as db:
            db.execute("DELETE FROM receipt WHERE source_id='s0'")
        self.assertIn("COUNT_CONSERVATION_INVALID",examine(self.path)["reasons"])
    def test_bad_source_set(self):
        b=self.bundle(1);b["receipts"][1]["source_id"]="s0"
        with self.assertRaises(ValueError):append(self.path,b,self.pin,ZERO)
    def test_no_physical_act(self):
        append(self.path,self.bundle(1),self.pin,ZERO)
        self.assertFalse(examine(self.path)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
