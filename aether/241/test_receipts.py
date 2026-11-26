import base64
import copy
import unittest
from receipts import evaluate

def fixture():
    run={"repository":"DavidWise01/oasis","pin_commit":"a"*40,
         "manifest_sha256":"b"*64,"run_id":55,"run_head":"c"*40,
         "checkpoint_sha256":"d"*64,"challenge_id":"challenge",
         "started_at":"2026-11-26T14:00:00Z","completed_at":"2026-11-26T14:15:00Z"}
    receipts=[];trust={}
    for i in range(3):
        statement={k:run[k] for k in ("repository","pin_commit","manifest_sha256",
            "run_id","run_head","checkpoint_sha256","challenge_id")}
        statement.update(schema="AETHER-241/checkpoint-receipt-v1",
            nonce="n"+str(i),controller_id="controller"+str(i),
            issued_at="2026-11-26T13:59:00Z",checkpoint_at="2026-11-26T13:58:00Z")
        receipts.append({"key_id":"key"+str(i),"statement":statement,
                         "signature_b64":base64.b64encode(b"x"*64).decode()})
        trust["key"+str(i)]={"controller_id":"controller"+str(i),"pem":"mock-key"}
    return {"run":run,"receipts":receipts,"externally_pinned_keys":trust,
            "prior_consumed_nonces":[]}

def mock_verify(*args):return True
class ReceiptTests(unittest.TestCase):
    def expect(self,change,reason):
        d=fixture();change(d)
        result=evaluate(d,mock_verify)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_good_mock_still_hold(self):
        self.expect(lambda d:None,"EXTERNAL_CUSTODY_CONTROLLER_ANCESTRY_AND_CLOCK_UNAUTHENTICATED")
    def test_replay_nonce(self):
        self.expect(lambda d:d["prior_consumed_nonces"].append("n0"),"NONCE_REPLAY")
    def test_duplicate_nonce(self):
        self.expect(lambda d:d["receipts"][1]["statement"].update(nonce="n0"),"NONCE_REPLAY")
    def test_same_controller(self):
        self.expect(lambda d:d["receipts"][1]["statement"].update(controller_id="controller0"),"CONTROLLER_LABEL_DUPLICATE")
    def test_wrong_source(self):
        self.expect(lambda d:d["receipts"][0]["statement"].update(pin_commit="e"*40),"RECEIPT_RUN_MISMATCH")
    def test_postrun_receipt(self):
        self.expect(lambda d:d["receipts"][0]["statement"].update(issued_at="2026-11-26T14:16:00Z"),"RECEIPT_ISSUED_AFTER_RUN_START")
    def test_checkpoint_after_receipt(self):
        self.expect(lambda d:d["receipts"][0]["statement"].update(checkpoint_at="2026-11-26T14:02:00Z"),"CHECKPOINT_TIMESTAMP_AFTER_RECEIPT")
    def test_bad_signature(self):
        d=fixture();r=evaluate(d,lambda *args:False)
        self.assertIn("SIGNATURE_INVALID",r["reasons"])
    def test_key_mismatch(self):
        self.expect(lambda d:d["externally_pinned_keys"]["key0"].update(controller_id="other"),"KEY_NOT_EXTERNALLY_PINNED")
    def test_unknown_key(self):
        self.expect(lambda d:d["externally_pinned_keys"].pop("key0"),"KEY_NOT_EXTERNALLY_PINNED")
    def test_run_mismatch(self):
        self.expect(lambda d:d["receipts"][2]["statement"].update(run_id=999),"RECEIPT_RUN_MISMATCH")
    def test_inverted_run_time(self):
        self.expect(lambda d:d["run"].update(completed_at="2026-11-26T13:00:00Z"),"RUN_TIME_INVERTED")
    def test_bad_utc(self):
        self.expect(lambda d:d["receipts"][0]["statement"].update(issued_at="today"),"TIMESTAMP_INVALID")
    def test_missing_receipt(self):
        self.expect(lambda d:d["receipts"].pop(),"EXACT_THREE_RECEIPTS_REQUIRED")
    def test_schema_poison(self):
        self.expect(lambda d:d["receipts"][0]["statement"].update(schema="fake"),"STATEMENT_SCHEMA_INVALID")
    def test_duplicate_key(self):
        self.expect(lambda d:d["receipts"][1].update(key_id="key0"),"DUPLICATE_KEY")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",evaluate(None,mock_verify)["reasons"])
if __name__=="__main__":unittest.main()
