import copy
import tempfile
import unittest
from pathlib import Path
from receipt_export import export,review,digest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"258"))
from sqlite_cas import initialize,cas,snapshot

class Tests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"ledger.db"
        initialize(self.path)
        for i in range(3):
            head=snapshot(self.path)["head"]
            cas(self.path,"a"+str(i),"host"+str(i),"challenge"+str(i),
                "nonce"+str(i),head["sequence"],head["hash"])
        self.original=export(self.path)
    def check(self,mutate,reason):
        sample=copy.deepcopy(self.original)
        mutate(sample)
        result=review(sample)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_valid_snapshot_still_unqualified(self):
        self.check(lambda x:None,"EXTERNAL_CUSTODY_NOT_ATTESTED")
    def test_three_events(self):
        self.assertEqual(review(self.original)["checked_events"],3)
    def test_missing_event(self):
        self.check(lambda x:x["events"].pop(1),"MISSING_OR_REORDERED_EVENT")
    def test_reordered_events(self):
        self.check(lambda x:x["events"].reverse(),"MISSING_OR_REORDERED_EVENT")
    def test_duplicate_event(self):
        self.check(lambda x:x["events"].append(copy.deepcopy(x["events"][0])),"MISSING_OR_REORDERED_EVENT")
    def test_missing_receipt(self):
        self.check(lambda x:x["attempts"].pop(),"ACCEPTED_ATTEMPT_MISSING_OR_DUPLICATE")
    def test_duplicate_receipt(self):
        self.check(lambda x:x["attempts"].append(copy.deepcopy(x["attempts"][0])),"ATTEMPT_DUPLICATE_OR_INVALID")
    def test_event_data_tamper(self):
        self.check(lambda x:x["events"][0].update(host="other"),"ACCEPTED_ATTEMPT_MISSING_OR_DUPLICATE")
    def test_event_receipt_tamper(self):
        self.check(lambda x:x["events"][0].update(receipt_sha256="f"*64),"EVENT_RECEIPT_TAMPER")
    def test_attempt_receipt_tamper(self):
        self.check(lambda x:x["attempts"][0].update(receipt_sha256="f"*64),"ATTEMPT_RECEIPT_TAMPER")
    def test_final_head_tamper(self):
        self.check(lambda x:x["head"].update(sha256="f"*64),"FINAL_HEAD_MISMATCH")
    def test_export_digest_tamper(self):
        self.check(lambda x:x.update(export_sha256="f"*64),"EXPORT_DIGEST_MISMATCH")
    def test_nonce_replay(self):
        self.check(lambda x:x["events"][1].update(nonce=x["events"][0]["nonce"]),"NONCE_REPLAY")
    def test_challenge_replay(self):
        self.check(lambda x:x["events"][1].update(challenge=x["events"][0]["challenge"]),"CHALLENGE_REPLAY")
    def test_invalid_schema(self):
        self.check(lambda x:x.update(schema="wrong"),"EXPORT_VERSION_INVALID")
    def test_wrong_head_chain(self):
        self.check(lambda x:x["events"][1].update(previous_hash="f"*64),"EVENT_CHAIN_BROKEN")
    def test_invalid_document(self):
        self.assertIn("EXPORT_SCHEMA_INVALID",review(None)["reasons"])
    def test_unchanged_across_restart(self):
        again=export(self.path)
        self.assertEqual(self.original,again)
    def test_never_authorizes(self):
        self.assertFalse(review(self.original)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
