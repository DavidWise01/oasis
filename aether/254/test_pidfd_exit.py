import copy
import hashlib
import os
import sys
import unittest
from unittest.mock import patch
from pidfd_exit import (CHILD_SCRIPT, HOLD, observe, parse_proc_stat,
                         review, sealed_record, transcript_digest)

def fixture():
    observation = {"pid": 401, "start_ticks": 12345,
        "boot_id": "11111111-2222-3333-4444-555555555555",
        "namespace_inode": 202, "stat_sha256": "a"*64,
        "pidfd_readable": True, "waitid_pid": 401,
        "waitid_code": getattr(os, "CLD_EXITED", 1),
        "waitid_status": 7, "wait_returncode": 7, "elapsed_ms": 50,
        "child_script_sha256": hashlib.sha256(CHILD_SCRIPT.encode()).hexdigest()}
    return sealed_record(observation)

class Tests(unittest.TestCase):
    def expect(self, change, code):
        record = fixture()
        change(record)
        answer = review(record)
        self.assertIn(code, answer["reasons"], answer)
        self.assertEqual(answer["operational_authority"], "HOLD")
    def test_healthy_snapshot_still_hold(self):
        self.expect(lambda x: None, "EXTERNAL_WITNESS_AND_KERNEL_CUSTODY_UNVERIFIED")
    def test_wrong_pidfd_readiness(self):
        self.expect(lambda x: x["observation"].update(pidfd_readable=False), "PIDFD_NOT_READABLE")
    def test_wait_pid_swapped(self):
        self.expect(lambda x: x["observation"].update(waitid_pid=999), "WAITID_PID_MISMATCH")
    def test_wait_status_changed(self):
        self.expect(lambda x: x["observation"].update(waitid_status=0), "WAIT_STATUS_MISMATCH")
    def test_wait_returncode_changed(self):
        self.expect(lambda x: x["observation"].update(wait_returncode=0), "WAIT_STATUS_MISMATCH")
    def test_signal_exit_not_accepted(self):
        self.expect(lambda x: x["observation"].update(waitid_code=999), "WAITID_NOT_NORMAL_EXIT")
    def test_script_substitution(self):
        self.expect(lambda x: x["observation"].update(child_script_sha256="b"*64), "CHILD_SCRIPT_MISMATCH")
    def test_pid_bool_rejected(self):
        self.expect(lambda x: x["observation"].update(pid=True), "PID_INVALID")
    def test_elapsed_limit(self):
        self.expect(lambda x: x["observation"].update(elapsed_ms=5000), "ELAPSED_INVALID")
    def test_hash_tamper(self):
        self.expect(lambda x: x["observation"].update(netns_inode=777), "TRANSCRIPT_DIGEST_MISMATCH")
    def test_authority_tamper(self):
        self.expect(lambda x: x.update(operational_authority="ACT"), "AUTHORITY_FIELD_TAMPER")
    def test_empty_document(self):
        self.assertIn("RECORD_SCHEMA_INVALID", review(None)["reasons"])
    def test_stat_parser_embedded_parenthesis(self):
        fields = ["S"] + ["0"]*18 + ["4567"] + ["0"]*3
        raw = "77 (comm ) with spaces) " + " ".join(fields)
        self.assertEqual(parse_proc_stat(raw), {"pid":77,"start_ticks":4567})
    def test_stat_parser_short_rejected(self):
        with self.assertRaises(ValueError):
            parse_proc_stat("5 (x) S 1")
    def test_fixed_child_script(self):
        self.assertNotIn("shell=True", CHILD_SCRIPT)
        self.assertIn("os._exit(7)", CHILD_SCRIPT)
    @unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pidfd_open") and
                         hasattr(os, "P_PIDFD"), "Linux pidfd required")
    def test_actual_local_pidfd_exit(self):
        try:
            record = observe()
        except (PermissionError, NotImplementedError) as error:
            self.skipTest("pidfd not permitted: " + type(error).__name__)
        r = review(record)
        self.assertEqual(record["observation"]["wait_returncode"], 7)
        self.assertNotIn("WAITID_PID_MISMATCH", r["reasons"])
        self.assertIn("CHILD_PROCESS_EXIT_IS_NOT_LOCK_RECLAMATION_AUTHORITY", r["reasons"])

if __name__ == "__main__":
    unittest.main()
