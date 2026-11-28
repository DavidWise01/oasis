import base64,copy,hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from recovery_audit import (audit,read_local,canon,sha,SCHEMA,ROTATION_SCHEMA)

def pem(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def sig(k,obj):
    return base64.b64encode(k.sign(canon(obj))).decode()
def fixture():
    keys=[Ed25519PrivateKey.generate() for _ in range(3)]
    base=[{"source_id":f"source{i}","controller":f"controller{i}",
           "key_pem":pem(keys[i]),"version":1} for i in range(3)]
    previous=sha(base)
    replacement=Ed25519PrivateKey.generate()
    stmt={"schema":ROTATION_SCHEMA,"operation":"ROTATE","source_id":"source0",
          "controller":"controller0","previous_registry_sha256":previous,
          "old_key_sha256":hashlib.sha256(pem(keys[0]).encode()).hexdigest(),
          "new_key_sha256":hashlib.sha256(pem(replacement).encode()).hexdigest(),
          "next_version":2}
    rotation={"source_id":"source0","new_key_pem":pem(replacement),
              "old_signature_b64":sig(keys[0],stmt),"new_signature_b64":sig(replacement,stmt)}
    head=copy.deepcopy(base)
    head[0]["key_pem"]=pem(replacement);head[0]["version"]=2
    next_hash=sha(head)
    log=[{"source_id":"source0","old_key_sha":stmt["old_key_sha256"],
          "new_key_sha":stmt["new_key_sha256"],
          "old_sig_b64":rotation["old_signature_b64"],
          "new_sig_b64":rotation["new_signature_b64"],
          "previous_registry_sha":previous,"next_registry_sha":next_hash}]
    anchor={"schema":SCHEMA,"base_registry_sha256":previous,"head_registry_sha256":next_hash,
            "rotation_count":1,"minimum_challenges":2,"minimum_receipts":6,
            "anchor_nonce":"external-custody-claim-277"}
    custodian=Ed25519PrivateKey.generate()
    bundle={"base_registry":base,"rotation_history":[rotation],"checkpoint":anchor,
            "anchor_public_key_pem":pem(custodian),
            "anchor_signature_b64":sig(custodian,anchor)}
    local={"registry_rows":head,"rotation_log":log,"challenges":2,"receipts":6}
    return bundle,local,sha(anchor)

class Tests(unittest.TestCase):
    def expect(self,edit,reason):
        b,local,pin=fixture();edit(b,local)
        report=audit(b,local,pin)
        self.assertIn(reason,report["reasons"],report)
        self.assertEqual(report["operational_authority"],"HOLD")
    def test_valid_chain_not_external(self):
        b,local,pin=fixture();r=audit(b,local,pin)
        self.assertTrue(r["observed"]["rotation_signatures"][0]["old_valid"])
        self.assertTrue(r["observed"]["rotation_signatures"][0]["new_valid"])
        self.assertIn("ANCHOR_CHECKPOINT_NOT_EXTERNALLY_RETAINED",r["reasons"])
    def test_old_key_forged(self):
        self.expect(lambda b,l:b["rotation_history"][0].update(old_signature_b64="AAAA"),
                    "OLD_ROTATION_SIGNATURE_INVALID")
    def test_new_key_forged(self):
        self.expect(lambda b,l:b["rotation_history"][0].update(new_signature_b64="AAAA"),
                    "NEW_ROTATION_SIGNATURE_INVALID")
    def test_replacement_key_swapped(self):
        self.expect(lambda b,l:b["rotation_history"][0].update(new_key_pem=pem(Ed25519PrivateKey.generate())),
                    "NEW_ROTATION_SIGNATURE_INVALID")
    def test_old_ancestry_key_swapped(self):
        self.expect(lambda b,l:b["base_registry"][0].update(key_pem=pem(Ed25519PrivateKey.generate())),
                    "OLD_ROTATION_SIGNATURE_INVALID")
    def test_external_pin_wrong(self):
        b,l,p=fixture()
        self.assertIn("ANCHOR_PIN_MISMATCH",audit(b,l,"f"*64)["reasons"])
    def test_anchor_signature_corrupted(self):
        self.expect(lambda b,l:b.update(anchor_signature_b64="AAAA"),"ANCHOR_SIGNATURE_INVALID")
    def test_restart_registry_replaced(self):
        self.expect(lambda b,l:l["registry_rows"][0].update(version=3),"RESTART_REGISTRY_MISMATCH")
    def test_local_history_removed(self):
        self.expect(lambda b,l:l["rotation_log"].clear(),"RESTART_ROTATION_LOG_MISMATCH")
    def test_rotation_history_missing(self):
        self.expect(lambda b,l:b["rotation_history"].clear(),"ROTATION_COUNT_ROLLBACK")
    def test_lower_challenge_count(self):
        self.expect(lambda b,l:l.update(challenges=1),"CHALLENGE_COUNT_ROLLBACK")
    def test_lower_receipt_count(self):
        self.expect(lambda b,l:l.update(receipts=3),"RECEIPT_COUNT_ROLLBACK")
    def test_nonconserved_receipts(self):
        self.expect(lambda b,l:l.update(receipts=7),"THREE_RECEIPTS_PER_CHALLENGE_VIOLATED")
    def test_anchor_head_substitution(self):
        self.expect(lambda b,l:b["checkpoint"].update(head_registry_sha256="f"*64),"ANCHORED_HEAD_CONFLICT")
    def test_invalid_bundle(self):
        b,l,p=fixture()
        self.assertIn("AUDIT_BUNDLE_INVALID",audit({},l,p)["reasons"])
    def test_pin_mandatory(self):
        b,l,p=fixture()
        self.assertIn("OUT_OF_BAND_ANCHOR_PIN_REQUIRED",audit(b,l,None)["reasons"])
    def test_readonly_sqlite_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"db.sqlite"
            db=sqlite3.connect(path)
            db.executescript("""
            CREATE TABLE signer(source_id TEXT,controller TEXT,key_pem TEXT,version INTEGER);
            CREATE TABLE rotation(source_id TEXT,old_key_sha TEXT,new_key_sha TEXT,old_sig_b64 TEXT,new_sig_b64 TEXT,previous_registry_sha TEXT,next_registry_sha TEXT);
            CREATE TABLE challenge(challenge_nonce TEXT);
            CREATE TABLE receipt(session_nonce TEXT);
            """)
            db.commit();db.close()
            result=read_local(path)
            self.assertEqual(result["registry_rows"],[])
            self.assertEqual(result["challenges"],0)
    def test_physical_act_never(self):
        b,l,p=fixture()
        self.assertFalse(audit(b,l,p)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
