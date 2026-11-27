import sqlite3
import tempfile
import unittest
from pathlib import Path
from sqlite_cas import GENESIS,cas,initialize,race,snapshot,verify_snapshot

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.path=Path(t.name)/"ledger.db"
        initialize(self.path)
    def head(self):
        return snapshot(self.path)["head"]
    def one(self,attempt="a",host="h",challenge="c",nonce="n"):
        head=self.head()
        return cas(self.path,attempt,host,challenge,nonce,head["sequence"],head["hash"])
    def test_genesis(self):
        self.assertEqual(self.head(),{"sequence":0,"hash":GENESIS})
    def test_first_accept(self):
        r=self.one();self.assertEqual(r["decision"],"ACCEPTED")
        self.assertEqual(self.head()["sequence"],1)
    def test_stale_head_rejected(self):
        self.one()
        r=cas(self.path,"b","h2","c2","n2",0,GENESIS)
        self.assertEqual(r["decision"],"STALE_REJECTED")
        self.assertEqual(self.head()["sequence"],1)
    def test_nonce_replay_on_current_head(self):
        self.one()
        self.assertEqual(self.one("b","h2","c2","n")["decision"],"NONCE_REPLAY_REJECTED")
    def test_challenge_replay_on_current_head(self):
        self.one()
        self.assertEqual(self.one("b","h2","c","n2")["decision"],"CHALLENGE_REPLAY_REJECTED")
    def test_attempt_replay_hard_reject(self):
        self.one()
        with self.assertRaises(ValueError):
            self.one("a","h2","c2","n2")
    def test_transaction_rolls_back_on_replay(self):
        self.one()
        before=self.head()
        with self.assertRaises(ValueError):
            self.one("a","h2","c2","n2")
        self.assertEqual(self.head(),before)
    def test_two_competitors_exactly_one_wins(self):
        result=race(self.path,2)
        self.assertTrue(result["single_winner_observed"])
        self.assertEqual(result["stale_rejected"],1)
    def test_eight_competitors_exactly_one_wins(self):
        result=race(self.path,8)
        self.assertEqual(result["accepted"],1)
        self.assertEqual(result["stale_rejected"],7)
    def test_sixteen_competitors_exactly_one_wins(self):
        result=race(self.path,16)
        self.assertEqual(result["accepted"],1)
        self.assertEqual(result["stale_rejected"],15)
    def test_append_only_events(self):
        self.one()
        self.one("b","h2","c2","n2")
        s=snapshot(self.path)
        self.assertEqual(len(s["events"]),2)
        self.assertEqual(verify_snapshot(s),[])
    def test_failed_attempt_retained(self):
        self.one()
        cas(self.path,"b","h2","c2","n2",0,GENESIS)
        s=snapshot(self.path)
        self.assertEqual(len(s["attempts"]),2)
        self.assertEqual(len(s["events"]),1)
    def test_actual_db_file_exists(self):
        self.one()
        self.assertTrue(self.path.exists())
        self.assertGreater(self.path.stat().st_size,0)
    def test_authority_never_granted(self):
        self.assertEqual(self.one()["operational_authority"],"HOLD")
        self.assertFalse(snapshot(self.path)["physical_act_allowed"])
    def test_snapshot_head_mismatch(self):
        s=snapshot(self.path);s["head"]["hash"]="f"*64
        self.assertIn("FINAL_HEAD_MISMATCH",verify_snapshot(s))
    def test_snapshot_chain_mismatch(self):
        self.one()
        s=snapshot(self.path);s["events"][0]["previous_hash"]="f"*64
        self.assertIn("HEAD_CHAIN_BROKEN",verify_snapshot(s))
    def test_boolean_sequence_rejected(self):
        with self.assertRaises(ValueError):
            cas(self.path,"a","h","c","n",True,GENESIS)
    def test_bad_hash_rejected(self):
        with self.assertRaises(ValueError):
            cas(self.path,"a","h","c","n",0,"bad")
    def test_bad_worker_count(self):
        with self.assertRaises(ValueError):race(self.path,1)
    def test_no_network_or_external_custody(self):
        s=snapshot(self.path)
        self.assertFalse(s["external_atomicity_authenticated"])
        self.assertFalse(s["independent_custody_authenticated"])
if __name__=="__main__":
    unittest.main()
