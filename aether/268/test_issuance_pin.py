import base64,copy,sqlite3,tempfile,threading,unittest
from pathlib import Path
from issuance_pin import sha,digest,canon,check_pin,initialize,consume,inspect

def fixture():
    raw=b'{"challenge":"not-secret","nonce":"fresh"}'
    url="https://issuer.example.org/receipts/42"
    retrieval={"requested_url":url,"raw_b64":base64.b64encode(raw).decode(),
               "raw_sha256":digest(raw),"raw_length":len(raw)}
    retrieval["observation_sha256"]=sha(retrieval)
    pin={"challenge_sha256":"a"*64,"raw_sha256":digest(raw),
         "issuer_controller_claim":"issuer-1"}
    pin["pin_sha256"]=sha(pin)
    return {"issuance_url":url,"challenge_sha256":"a"*64,
            "expected_raw_sha256":digest(raw),"retrieval":retrieval,"pin":pin}

class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db=Path(temp.name)/"nonces.db"
    def test_valid_bytes_still_hold(self):
        self.assertEqual(check_pin(fixture()),["PIN_CUSTODIAN_NOT_INDEPENDENTLY_AUTHENTICATED",
            "RETRIEVAL_TRANSPORT_NOT_INDEPENDENTLY_ATTESTED"])
    def test_substituted_body(self):
        b=fixture();b["retrieval"]["raw_b64"]=base64.b64encode(b"forged").decode()
        self.assertIn("EXPECTED_ISSUANCE_PIN_MISMATCH",check_pin(b))
    def test_truncated_body(self):
        b=fixture();b["retrieval"]["raw_length"]-=1
        self.assertIn("RAW_LENGTH_MISMATCH",check_pin(b))
    def test_url_substitution(self):
        b=fixture();b["retrieval"]["requested_url"]="https://evil.example.org"
        self.assertIn("ISSUANCE_URL_SUBSTITUTED",check_pin(b))
    def test_pin_challenge_substitution(self):
        b=fixture();b["pin"]["challenge_sha256"]="b"*64
        self.assertIn("PIN_CHALLENGE_MISMATCH",check_pin(b))
    def test_pin_selfhash_tamper(self):
        b=fixture();b["pin"]["pin_sha256"]="0"*64
        self.assertIn("PIN_SELF_HASH_MISMATCH",check_pin(b))
    def test_retrieval_hash_tamper(self):
        b=fixture();b["retrieval"]["observation_sha256"]="f"*64
        self.assertIn("RETRIEVAL_OBSERVATION_TAMPER",check_pin(b))
    def test_http_not_allowed(self):
        b=fixture();b["issuance_url"]="http://issuer.example.org"
        self.assertIn("ISSUANCE_URL_INVALID",check_pin(b))
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",check_pin(None))
    def test_first_nonce_consumption(self):
        r=consume(self.db,"n1","a"*64,"b"*64)
        self.assertEqual(inspect(self.db)["consumed"],1)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_nonce_replay_after_restart(self):
        consume(self.db,"n1","a"*64,"b"*64)
        with self.assertRaisesRegex(ValueError,"NONCE_REPLAY"):
            consume(self.db,"n1","a"*64,"b"*64)
    def test_same_nonce_different_challenge(self):
        consume(self.db,"n1","a"*64,"b"*64)
        with self.assertRaises(ValueError):
            consume(self.db,"n1","c"*64,"d"*64)
    def test_distinct_nonces(self):
        consume(self.db,"n1","a"*64,"b"*64)
        consume(self.db,"n2","a"*64,"b"*64)
        self.assertEqual(inspect(self.db)["consumed"],2)
    def test_tampered_db_receipt(self):
        consume(self.db,"n1","a"*64,"b"*64)
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE nonce_receipts SET receipt_sha256=? WHERE nonce='n1'",("f"*64,))
        self.assertIn("RECEIPT_TAMPER",inspect(self.db)["reasons"])
    def test_two_thread_competition(self):
        barrier=threading.Barrier(2)
        outcome=[]
        def attempt():
            barrier.wait()
            try:consume(self.db,"racing-nonce","a"*64,"b"*64);outcome.append(True)
            except ValueError:outcome.append(False)
        workers=[threading.Thread(target=attempt) for _ in range(2)]
        for w in workers:w.start()
        for w in workers:w.join(timeout=10)
        self.assertFalse(any(w.is_alive() for w in workers))
        self.assertEqual(sorted(outcome),[False,True])
        self.assertEqual(inspect(self.db)["consumed"],1)
    def test_unsafe_nonce(self):
        with self.assertRaises(ValueError):consume(self.db,"","a"*64,"b"*64)
    def test_invalid_sha256(self):
        with self.assertRaises(ValueError):consume(self.db,"n","bad","b"*64)
    def test_no_external_authority(self):
        self.assertFalse(inspect(self.db)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
