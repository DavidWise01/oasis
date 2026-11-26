import base64
import copy
import json
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from receipt_gate import check

def fixture():
    s={"schema":"AETHER-238/receipt-statement-v1","repository":"DavidWise01/oasis",
       "pin_commit":"a"*40,"source_sha256":"b"*64,"challenge_id":"external-challenge-1",
       "nonce":"nonce-1","issued_at":"2026-11-26T18:00:00Z","run_id":123,
       "run_head":"c"*40,"witness_root":"root1"}
    receipts=[]
    trust={}
    for i in range(3):
        t=copy.deepcopy(s)
        t["nonce"]="nonce-"+str(i+1)
        t["witness_root"]="root"+str(i+1)
        key="key"+str(i+1)
        receipts.append({"statement":t,"signature_b64":base64.b64encode(b"x"*64).decode(),"key_id":key})
        trust[key]={"witness_root":t["witness_root"],"public_key_pem":"mock-externally-pinned"}
    return receipts,trust,[]

def verified(pem,msg,sig):
    return True  # injected mock: never a real Ed25519 attestation

class ReceiptTests(unittest.TestCase):
    def test_three_mock_witnesses_cannot_certify(self):
        r=check(*fixture(),verified)
        self.assertEqual(r["verdict"],"REJECT_OR_UNVERIFIED")
        self.assertIn("INDEPENDENT_CONTROLLER_CUSTODY_AND_PRERUN_TIME_UNVERIFIED",r["reasons"])
        self.assertEqual(r["operational_authority"],"HOLD")
    def assert_reason(self,change,reason):
        d=list(fixture())
        change(d)
        r=check(*d,verified)
        self.assertIn(reason,r["reasons"],r)
    def test_replayed_nonce(self):
        self.assert_reason(lambda d:d[2].append("nonce-1"),"NONCE_REPLAY_OR_DUPLICATION")
    def test_duplicate_nonce_in_batch(self):
        self.assert_reason(lambda d:d[0][1]["statement"].update(nonce="nonce-1"),"NONCE_REPLAY_OR_DUPLICATION")
    def test_duplicate_witness_root(self):
        def change(d):
            d[0][1]["statement"]["witness_root"]="root1"
            d[1]["key2"]["witness_root"]="root1"
        self.assert_reason(change,"WITNESS_ROOT_DUPLICATE")
    def test_source_mismatch(self):
        self.assert_reason(lambda d:d[0][1]["statement"].update(source_sha256="d"*64),"CROSS_RECEIPT_BINDING_MISMATCH")
    def test_wrong_commit(self):
        self.assert_reason(lambda d:d[0][1]["statement"].update(pin_commit="bad"),"RECEIPT_DIGEST_OR_COMMIT_INVALID")
    def test_bad_signature(self):
        a,b,c=fixture()
        r=check(a,b,c,lambda *args:False)
        self.assertIn("SIGNATURE_INVALID",r["reasons"])
    def test_unknown_key(self):
        self.assert_reason(lambda d:d[1].pop("key1"),"UNTRUSTED_KEY_OR_ROOT")
    def test_missing_receipts(self):
        r=check([],{},[],verified)
        self.assertIn("RECEIPT_SET_INVALID",r["reasons"])
    def test_false_run_id(self):
        self.assert_reason(lambda d:d[0][0]["statement"].update(run_id=True),"RECEIPT_RUN_BINDING_INVALID")
    def test_schema_poison(self):
        self.assert_reason(lambda d:d[0][0]["statement"].update(schema="evil"),"RECEIPT_STATEMENT_SCHEMA_MISMATCH")
    def test_wrong_repo(self):
        self.assert_reason(lambda d:d[0][0]["statement"].update(repository="attacker/repo"),"RECEIPT_RUN_BINDING_INVALID")
    def test_missing_nonce_ledger(self):
        a,b,_=fixture()
        self.assertIn("NONCE_LEDGER_MISSING",check(a,b,None,verified)["reasons"])
    def test_invalid_envelope(self):
        self.assert_reason(lambda d:d[0][0].update(extra="x"),"RECEIPT_ENVELOPE_INVALID")

if __name__=="__main__":unittest.main()
