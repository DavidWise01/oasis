import base64, tempfile, unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from durable_receipts import bootstrap,rotate,consume,inspect,canon,digest,SCHEMA

def pem(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,
                                        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def signature(k,statement):
    return base64.b64encode(k.sign(canon(statement))).decode()

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"journal.sqlite"
        self.keys={f"source{i}":Ed25519PrivateKey.generate() for i in range(3)}
        self.entries=[{"source_id":s,"controller":"controller"+s[-1],
                       "key_pem":pem(k),"version":1} for s,k in self.keys.items()]
        self.pin=digest(self.entries)
        bootstrap(self.db,self.entries,self.pin)
    def bundle(self,n):
        challenge={"nonce":"challenge"+str(n),"id":"c"+str(n),
                   "run_id":276,"source_commit":"a"*40}
        receipts=[]
        for i in range(3):
            source="source"+str(i);sid=f"session{n}-{i}";nonce=f"nonce{n}-{i}"
            payload="b"*64
            stmt={"schema":SCHEMA,"operation":"RECEIPT","challenge":challenge,
                  "registry_sha256":self.pin,"source_id":source,
                  "session_id":sid,"session_nonce":nonce,"payload_sha256":payload}
            receipts.append({"source_id":source,"session_id":sid,"session_nonce":nonce,
                             "payload_sha256":payload,"signature_b64":signature(self.keys[source],stmt)})
        return {"challenge":challenge,"receipts":receipts}
    def test_first_atomic_commit(self):
        r=consume(self.db,self.bundle(1),self.pin)
        self.assertEqual(r["receipts_committed"],3)
        self.assertEqual(inspect(self.db)["challenges"],1)
    def test_persisted_challenge_replay(self):
        consume(self.db,self.bundle(1),self.pin)
        with self.assertRaises(ValueError):consume(self.db,self.bundle(1),self.pin)
    def test_persisted_session_nonce_replay(self):
        consume(self.db,self.bundle(1),self.pin)
        b=self.bundle(2);b["receipts"][0]["session_nonce"]="nonce1-0"
        with self.assertRaises(ValueError):consume(self.db,b,self.pin)
    def test_invalid_signature_atomic_rollback(self):
        b=self.bundle(1);b["receipts"][2]["signature_b64"]="AAAA"
        with self.assertRaisesRegex(ValueError,"RECEIPT_SIGNATURE_INVALID"):consume(self.db,b,self.pin)
        self.assertEqual(inspect(self.db)["challenges"],0)
    def test_missing_receipt(self):
        b=self.bundle(1);b["receipts"].pop()
        with self.assertRaises(ValueError):consume(self.db,b,self.pin)
    def test_duplicate_source(self):
        b=self.bundle(1);b["receipts"][1]["source_id"]="source0"
        with self.assertRaises(ValueError):consume(self.db,b,self.pin)
    def test_stale_registry_pin(self):
        with self.assertRaises(ValueError):consume(self.db,self.bundle(1),"f"*64)
    def test_bootstrap_repeat_rejected(self):
        with self.assertRaises(ValueError):bootstrap(self.db,self.entries,self.pin)
    def test_bootstrap_wrong_pin(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):bootstrap(Path(t)/"db",self.entries,"f"*64)
    def rotation(self,newkey=None,old_sig_override=None):
        replacement=newkey or Ed25519PrivateKey.generate()
        old=self.keys["source0"]
        stmt={"schema":SCHEMA,"operation":"ROTATE","source_id":"source0",
              "controller":"controller0","previous_registry_sha256":self.pin,
              "old_key_sha256":__import__("hashlib").sha256(pem(old).encode()).hexdigest(),
              "new_key_sha256":__import__("hashlib").sha256(pem(replacement).encode()).hexdigest(),
              "next_version":2}
        oldsig=old_sig_override if old_sig_override is not None else signature(old,stmt)
        nextsig=signature(replacement,stmt)
        return replacement,oldsig,nextsig
    def test_rotation_two_sided_authorization(self):
        new,oldsig,nextsig=self.rotation()
        r=rotate(self.db,"source0",pem(new),oldsig,nextsig,self.pin)
        self.assertNotEqual(r["registry_sha256"],self.pin)
        self.assertEqual(inspect(self.db)["rotations"],1)
    def test_bad_old_signature_blocks_rotation(self):
        new,old,nextsig=self.rotation(old_sig_override="AAAA")
        with self.assertRaisesRegex(ValueError,"OLD_KEY_AUTHORIZATION_INVALID"):
            rotate(self.db,"source0",pem(new),old,nextsig,self.pin)
        self.assertEqual(inspect(self.db)["rotations"],0)
    def test_bad_new_signature_blocks_rotation(self):
        new,oldsig,nextsig=self.rotation()
        with self.assertRaisesRegex(ValueError,"NEW_KEY_POSSESSION_INVALID"):
            rotate(self.db,"source0",pem(new),oldsig,"AAAA",self.pin)
    def test_rotation_stale_pin(self):
        new,oldsig,nextsig=self.rotation()
        with self.assertRaisesRegex(ValueError,"REGISTRY_PIN_STALE"):
            rotate(self.db,"source0",pem(new),oldsig,nextsig,"f"*64)
    def test_old_receipts_fail_after_rotation(self):
        oldbundle=self.bundle(1)
        new,oldsig,nextsig=self.rotation()
        newpin=rotate(self.db,"source0",pem(new),oldsig,nextsig,self.pin)["registry_sha256"]
        with self.assertRaises(ValueError):consume(self.db,oldbundle,newpin)
    def test_multiple_distinct_challenges(self):
        consume(self.db,self.bundle(1),self.pin);consume(self.db,self.bundle(2),self.pin)
        self.assertEqual(inspect(self.db)["receipts"],6)
    def test_authority_stays_hold(self):
        self.assertFalse(inspect(self.db)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
