#!/usr/bin/env python3
"""No-hardware unit tests for ANNY powercut read/prepare/witness evidence.
No electrical power is controlled. No claim of physical power-loss PASS.
"""
import json, pathlib, tempfile, unittest
from unittest.mock import patch
import powercut_gate as g

class PowercutSafetyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix="anny-no-physical-cut-")
  self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name)
  self.root.joinpath(g.MARKER).write_text(g.MARKER+"\n")

 def fixture(self,case="RECEIVER_UNCOMMITTED"):
  m=g.setup_fixture(self.root,case)
  return m,self.root/m["run_id"]/"manifest.json"

 def test_all_five_scenarios_require_external_witness(self):
  for case in g.CASES:
   m,manifest=self.fixture(case)
   report=g.verify(manifest,None,self.root/(m["run_id"]+".json"))
   self.assertFalse(report["certified"])
   self.assertEqual(report["status"],"NOT_CERTIFIED")
   self.assertFalse(report["checks"]["external_witness_three_events"])
   self.assertFalse(report["checks"]["target_boot_changed"])
   self.assertEqual(report["snapshot"]["integrity"],["ok","ok"])

 def test_marker_required_fail_closed(self):
  marker=self.root/g.MARKER
  marker.unlink()
  with self.assertRaisesRegex(ValueError,"SACRIFICIAL_MARKER_REQUIRED"):
   g.setup_fixture(self.root,"COMMIT_UNCOMMITTED")

 def test_manifest_hash_tampering_fails(self):
  _,manifest=self.fixture()
  m=json.loads(manifest.read_text())
  m["case"]="CONFIRM_COMMITTED"
  manifest.write_text(json.dumps(m))
  with self.assertRaisesRegex(ValueError,"MANIFEST_HASH_MISMATCH"):
   g.read_manifest(manifest)

 def test_same_machine_cannot_be_witness(self):
  _,manifest=self.fixture()
  with self.assertRaisesRegex(ValueError,"WITNESS_MUST_BE_ON_SEPARATE_HOST"):
   g.witness(manifest,self.root/"evidence.jsonl","REGISTER","self test")

 def test_separate_witness_ledger_order_and_hash_chain(self):
  m,manifest=self.fixture()
  ledger=self.root/"external-ledger.jsonl"
  target=g.host_id()
  independent={"hostname":target["hostname"]+"-other-host",
               "machine_id":"simulated-independent-test-host","boot_id":"simulation"}
  with patch.object(g,"host_id",return_value=independent):
   with self.assertRaisesRegex(ValueError,"WITNESS_EVENT_ORDER"):
    g.witness(manifest,ledger,"OFF_OBSERVED","out of order")
   for event in ("REGISTER","OFF_OBSERVED","ON_OBSERVED"):
    g.witness(manifest,ledger,event,"synthetic, NOT electrical observation")
  events,tail=g.ledger_load(ledger)
  self.assertEqual(len(events),3)
  self.assertEqual(tail,events[-1]["entry_sha256"])
  report=g.verify(manifest,ledger,self.root/"report.json")
  self.assertFalse(report["certified"])
  self.assertEqual(report["status"],"NOT_CERTIFIED")
  self.assertTrue(report["checks"]["external_witness_three_events"])
  self.assertTrue(report["checks"]["witness_manifest_consistent"])
  self.assertTrue(report["checks"]["witness_on_separate_host"])
  self.assertFalse(report["checks"]["target_boot_changed"])

 def test_modified_witness_event_detected(self):
  m,manifest=self.fixture()
  ledger=self.root/"witness.jsonl"
  target=g.host_id()
  independent={"hostname":target["hostname"]+"-other-host",
               "machine_id":"simulated-test-witness","boot_id":"test"}
  with patch.object(g,"host_id",return_value=independent):
   g.witness(manifest,ledger,"REGISTER","synthetic only")
  data=ledger.read_text().replace('"REGISTER"','"ON_OBSERVED"')
  ledger.write_text(data)
  with self.assertRaisesRegex(ValueError,"WITNESS_CHAIN_INVALID"):
   g.ledger_load(ledger)

 def test_receipts_never_auto_certify(self):
  m,manifest=self.fixture("CONFIRM_COMMITTED")
  # Even a correctly formed committed receiver baseline isn't a power cut.
  snapshot=g.inspect(m)
  self.assertEqual(snapshot["state"],"RELEASE_PENDING")
  self.assertEqual(snapshot["effect_count"],1)
  self.assertEqual(snapshot["violet"],"HELD")
  report=g.verify(manifest,None,self.root/"report.json")
  self.assertEqual(report["status"],"NOT_CERTIFIED")
  self.assertFalse(report["certified"])

if __name__=="__main__":
 unittest.main(verbosity=2)
