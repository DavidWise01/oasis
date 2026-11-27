import errno
import json
import subprocess
import unittest
from unittest.mock import patch
import socket_probes as p

class FakeResult:
    def __init__(self, data, code=0):
        self.returncode = code
        self.stdout = data
        self.stderr = b""

class Tests(unittest.TestCase):
    def test_no_namespace_never_connects(self):
        with patch.object(p, "isolated", return_value=False):
            x = p.worker(42, connector=lambda *args: self.fail("socket called"))
        self.assertEqual(x["probes"], [])
        self.assertEqual(x["state"], "HOLD")
    def test_namespace_same_inode_rejected(self):
        with patch.object(p, "ns_inode", return_value=55):
            self.assertFalse(p.isolated(55, {"lo"}))
    def test_namespace_new_veth_rejected(self):
        with patch.object(p, "ns_inode", return_value=66):
            self.assertFalse(p.isolated(55, {"lo", "veth0"}))
    def test_namespace_new_only_lo(self):
        with patch.object(p, "ns_inode", return_value=66):
            self.assertTrue(p.isolated(55, {"lo"}))
    def test_invalid_inode(self):
        self.assertFalse(p.isolated(None, {"lo"}))
    def test_worker_four_socket_results(self):
        with patch.object(p, "isolated", return_value=True):
            x = p.worker(55, connector=lambda addr, timeout: errno.ENETUNREACH)
        self.assertEqual(len(x["probes"]), 6)
        self.assertTrue(all(not y.get("denial_attributed_to_network_policy", False) for y in x["probes"]))
    def test_unsupported_http_dns_unmeasured(self):
        with patch.object(p, "isolated", return_value=True):
            x = p.worker(55, connector=lambda addr, timeout: errno.EHOSTUNREACH)
        self.assertEqual([v["outcome"] for v in x["probes"][-2:]], ["NOT_MEASURED", "NOT_MEASURED"])
    def test_socket_success_does_not_promote(self):
        x = p.probe("private", lambda addr, timeout: 0)
        self.assertEqual(x["outcome"], "connection_succeeded")
        self.assertFalse(x["denial_attributed_to_network_policy"])
    def test_refusal_does_not_certify_firewall(self):
        x = p.probe("private", lambda addr, timeout: errno.ECONNREFUSED)
        self.assertFalse(x["denial_attributed_to_network_policy"])
    def test_noninteger_socket_result_rejected(self):
        with self.assertRaises(ValueError):
            p.probe("private", lambda addr, timeout: "bad")
    def test_unknown_category(self):
        with self.assertRaises(ValueError):
            p.probe("redirect", lambda addr, timeout: 1)
    def test_unshare_launch_failure_holds(self):
        with patch.object(p.sys, "platform", "linux"), patch.object(p.shutil, "which", return_value="/usr/bin/unshare"):
            x = p.supervise(runner=lambda command, env: FakeResult(b"", 1))
        self.assertEqual(x["state"], "HOLD")
    def test_unsigned_worker_output_only_observed(self):
        payload = {"state": "OBSERVED_BUT_UNQUALIFIED", "probes": [],
                   "operational_authority": "ACT"}
        with patch.object(p.sys, "platform", "linux"), patch.object(p.shutil, "which", return_value="/usr/bin/unshare"):
            x = p.supervise(runner=lambda command, env: FakeResult(json.dumps(payload).encode()))
        self.assertEqual(x["operational_authority"], "HOLD")
    def test_worker_invalid_json_holds(self):
        with patch.object(p.sys, "platform", "linux"), patch.object(p.shutil, "which", return_value="/usr/bin/unshare"):
            x = p.supervise(runner=lambda command, env: FakeResult(b"invalid"))
        self.assertEqual(x["state"], "HOLD")
    def test_worker_output_limit(self):
        with patch.object(p.sys, "platform", "linux"), patch.object(p.shutil, "which", return_value="/usr/bin/unshare"):
            x = p.supervise(runner=lambda command, env: FakeResult(b"x" * 65537))
        self.assertEqual(x["state"], "HOLD")
    def test_supervised_command_is_unshare_net(self):
        calls = []
        def runner(command, env):
            calls.append((command, env))
            return FakeResult(b"", 1)
        with patch.object(p.sys, "platform", "linux"), patch.object(p.shutil, "which", return_value="/usr/bin/unshare"):
            p.supervise(runner=runner)
        self.assertEqual(calls[0][0][:3], ["unshare", "--net", "--"])
        self.assertNotIn("GITHUB_TOKEN", calls[0][1])
    def test_unsupported_only_loopback_scope(self):
        self.assertEqual(set(p.TARGETS), {"loopback", "private", "link_local", "metadata"})
    def test_hard_gate_false(self):
        with patch.object(p, "isolated", return_value=False):
            self.assertFalse(p.worker(1)["physical_act_allowed"])

if __name__ == "__main__":
    unittest.main()
