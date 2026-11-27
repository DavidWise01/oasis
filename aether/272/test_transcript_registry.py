import base64,copy,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from transcript_registry import (SCHEMA,canonical,sha_bytes,register,seal,inspect,consume_bundle)

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"trust.sqlite"
        self.keys=[]
        for i in range(3):
            key=Ed25519PrivateKey.generate();self.keys.append(key)
            pem=key.public_key().public_bytes(serialization.Encoding.PEM,
                                               serialization.PublicFormat.SubjectPublicKeyInfo).decode()
            register(self.db,"key"+str(i),"source"+str(i),"controller"+str(i),pem)
        self.pin=seal(self.db)
    def bundle(self,n=1):
        challenge={"challenge_id":"c"+str(n),"nonce":"nonce"+str(n),
                   "source_commit":"a"*40,"run_id":272}
        transcripts=[]
        for i,key in enumerate(self.keys):
            raw=("immutable raw "+str(i)).encode()
            row={"key_id":"key"+str(i),"source_id":"source"+str(i),
                 "controller_id":"controller"+str(i),"session_id":"session"+str(n)+"-"+str(i),
                 "session_nonce":"receipt"+str(n)+"-"+str(i),"requested_url":"https://example.org/item",
                 "raw_b64":base64.b64encode(raw).decode(),"raw_sha256":sha_bytes(raw)}
            statement={"schema":SCHEMA,"challenge":challenge,
                       **{k:v for k,v in row.items() if k not in ("raw_b64",)}}
            row["signature_b64"]=base64.b64encode(key.sign(canonical(statement))).decode()
            transcripts.append(row)
        return {"challenge":challenge,"transcripts":transcripts}
    def test_valid_signatures_still_hold(self):
        result=consume_bundle(self.db,self.bundle(),self.pin)
        self.assertEqual(result["locally_accepted_signed_transcripts"],3)
        self.assertFalse(result["independent_transport_verified"])
        self.assertEqual(inspect(self.db)["used_receipts"],3)
    def test_challenge_persists_across_reopen(self):
        consume_bundle(self.db,self.bundle(),self.pin)
        with self.assertRaisesRegex(ValueError,"CHALLENGE_REPLAY"):
            consume_bundle(self.db,self.bundle(),self.pin)
    def test_receipt_persists_across_restart(self):
        consume_bundle(self.db,self.bundle(),self.pin)
        replacement=self.bundle(2)
        replacement["transcripts"][0]["session_nonce"]="receipt1-0"
        with self.assertRaises(ValueError):consume_bundle(self.db,replacement,self.pin)
    def test_atomic_rollback_on_signature_failure(self):
        bundle=self.bundle()
        bundle["transcripts"][2]["signature_b64"]=base64.b64encode(b"x"*64).decode()
        with self.assertRaisesRegex(ValueError,"SIGNATURE_INVALID"):
            consume_bundle(self.db,bundle,self.pin)
        self.assertEqual(inspect(self.db)["used_receipts"],0)
        self.assertEqual(inspect(self.db)["used_challenges"],0)
    def test_wrong_out_of_band_pin(self):
        with self.assertRaisesRegex(ValueError,"SEALED_REGISTRY_PIN_MISMATCH"):
            consume_bundle(self.db,self.bundle(),"f"*64)
    def test_bad_raw_body(self):
        bundle=self.bundle();bundle["transcripts"][0]["raw_b64"]=base64.b64encode(b"tampered").decode()
        with self.assertRaisesRegex(ValueError,"RAW_BODY_HASH_INVALID"):
            consume_bundle(self.db,bundle,self.pin)
    def test_unknown_signer(self):
        bundle=self.bundle();bundle["transcripts"][0]["key_id"]="other"
        with self.assertRaisesRegex(ValueError,"PINNED_SIGNER_MISMATCH"):
            consume_bundle(self.db,bundle,self.pin)
    def test_duplicate_controller(self):
        bundle=self.bundle();bundle["transcripts"][1]["controller_id"]="controller0"
        with self.assertRaises(ValueError):consume_bundle(self.db,bundle,self.pin)
    def test_duplicate_nonce(self):
        bundle=self.bundle();bundle["transcripts"][1]["session_nonce"]=bundle["transcripts"][0]["session_nonce"]
        with self.assertRaisesRegex(ValueError,"SESSION_NONCE_REPLAY"):
            consume_bundle(self.db,bundle,self.pin)
    def test_duplicate_session(self):
        bundle=self.bundle();bundle["transcripts"][1]["session_id"]=bundle["transcripts"][0]["session_id"]
        with self.assertRaisesRegex(ValueError,"SESSION_ID_REPLAY"):
            consume_bundle(self.db,bundle,self.pin)
    def test_missing_receipt(self):
        bundle=self.bundle();bundle["transcripts"].pop()
        with self.assertRaisesRegex(ValueError,"THREE_TRANSCRIPTS_REQUIRED"):
            consume_bundle(self.db,bundle,self.pin)
    def test_registry_cannot_change_after_seal(self):
        with self.assertRaisesRegex(ValueError,"REGISTRY_ALREADY_SEALED"):
            register(self.db,"key9","source9","controller9","pem")
    def test_registry_pin_is_stable(self):
        self.assertEqual(seal(self.db),self.pin)
        self.assertEqual(inspect(self.db)["registry_digest"],self.pin)
    def test_bad_source_commit(self):
        bundle=self.bundle();bundle["challenge"]["source_commit"]="bad"
        with self.assertRaisesRegex(ValueError,"COMMIT_INVALID"):
            consume_bundle(self.db,bundle,self.pin)
    def test_boolean_run_rejected(self):
        bundle=self.bundle();bundle["challenge"]["run_id"]=True
        with self.assertRaisesRegex(ValueError,"RUN_INVALID"):
            consume_bundle(self.db,bundle,self.pin)
    def test_all_local_evidence_still_hold(self):
        result=consume_bundle(self.db,self.bundle(),self.pin)
        self.assertEqual(result["operational_authority"],"HOLD")
        self.assertFalse(result["physical_act_allowed"])
if __name__=="__main__":unittest.main()
