import sqlite3
import tempfile
import unittest
from pathlib import Path
from process_recovery import crash_recovery,multi_process_race,verify_database
from sqlite_cas import cas,initialize,snapshot

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/"ledger.sqlite3"
        initialize(self.path)
    def accept(self):
        h=snapshot(self.path)["head"]
        return cas(self.path,"attempt1","host1","challenge1","nonce1",h["sequence"],h["hash"])
    def test_genesis_verified(self):
        self.assertEqual(verify_database(self.path)["problems"],[])
    def test_accepted_receipts_verified(self):
        self.accept()
        result=verify_database(self.path)
        self.assertEqual(result["checked_events"],1)
        self.assertEqual(result["problems"],[])
    def test_rejected_receipt_verified(self):
        self.accept()
        cas(self.path,"attempt2","host2","challenge2","nonce2",0,"0"*64)
        self.assertEqual(verify_database(self.path)["checked_attempts"],2)
        self.assertEqual(verify_database(self.path)["problems"],[])
    def test_tampered_event_head(self):
        self.accept()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE events SET head_hash=? WHERE seq=1",("f"*64,))
        self.assertIn("EVENT_HEAD_HASH_INVALID",verify_database(self.path)["problems"])
    def test_tampered_receipt(self):
        self.accept()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE attempts SET receipt_hash=? WHERE id='attempt1'",("f"*64,))
        self.assertIn("ATTEMPT_RECEIPT_HASH_INVALID",verify_database(self.path)["problems"])
    def test_tampered_final_head(self):
        self.accept()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE head SET hash=? WHERE id=1",("f"*64,))
        self.assertIn("FINAL_HEAD_MISMATCH",verify_database(self.path)["problems"])
    def test_two_os_processes_one_winner(self):
        r=multi_process_race(self.path,2)
        self.assertEqual(r["accepted"],1)
        self.assertEqual(r["stale_rejected"],1)
        self.assertEqual(r["database_review"]["problems"],[])
    def test_eight_os_processes_one_winner(self):
        r=multi_process_race(self.path,8)
        self.assertTrue(r["one_local_winner"])
        self.assertEqual(r["stale_rejected"],7)
    def test_crash_before_commit_rolls_back(self):
        self.accept()
        r=crash_recovery(self.path)
        self.assertTrue(r["rollback_preserved_head"])
        self.assertEqual(r["post_restart_review"]["problems"],[])
    def test_crash_exit_code_17(self):
        self.assertEqual(crash_recovery(self.path)["interrupted_child_exit_code"],17)
    def test_race_workers_limit(self):
        with self.assertRaises(ValueError):
            multi_process_race(self.path,1)
    def test_no_authority(self):
        r=crash_recovery(self.path)
        self.assertEqual(r["operational_authority"],"HOLD")
        self.assertFalse(r["physical_act_allowed"])
    def test_local_not_external(self):
        self.assertFalse(verify_database(self.path)["external_atomicity_authenticated"])
        self.assertFalse(verify_database(self.path)["independent_custody_authenticated"])

if __name__=="__main__":
    unittest.main()
