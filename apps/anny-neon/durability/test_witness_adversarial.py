#!/usr/bin/env python3
"""Adversarial witness integrity tests; NEVER creates a real power event.

Fresh synthetic fixtures, mocked independent host only inside this test.
No electrical power controls, no production data, no automatic certification.
"""
import concurrent.futures
import contextlib
import datetime as dt
import io
import json
import pathlib
import tempfile
import unittest
import uuid
from unittest.mock import patch
import powercut_gate as g

class AdversarialWitnessTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix="anny-witness-adversarial-")
  self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name)
  (self.root/g.MARKER).write_text(g.MARKER+"\n")
  self.manifest_data=g.setup_fixture(self.root,"RECEIVER_UNCOMMITTED")
  self.manifest=self.root/self.manifest_data["run_id"]/"manifest.json"
  self.ledger=self.root/"witness.jsonl"
  target=g.host_id()
  self.independent={"hostname":target["hostname"]+"-test-witness",
   "machine_id":"SYNTHETIC_SEPARATE_HOST_NOT_A_REAL_WITNESS",
   "boot_id":"SYNTHETIC_STABLE_BOOT"}

 def witness(self,event,note="synthetic operator note",host=None):
  with patch.object(g,"host_id",return_value=host or self.independent):
   with contextlib.redirect_stdout(io.StringIO()):
    return g.witness(self.manifest,self.ledger,event,note)

 def complete(self):
  for event in ("REGISTER","OFF_OBSERVED","ON_OBSERVED"):
   self.witness(event)

 def forge_rehash(self,mutator):
  events=[json.loads(line) for line in self.ledger.read_text().splitlines()]
  mutator(events)
  prev="GENESIS"
  for e in events:
   e["previous_sha256"]=prev
   e["entry_sha256"]=g.sha({k:v for k,v in e.items() if k!="entry_sha256"})
   prev=e["entry_sha256"]
  self.ledger.write_text("".join(json.dumps(e)+"\n" for e in events))

 def verify(self):
  with contextlib.redirect_stdout(io.StringIO()):
   return g.verify(self.manifest,self.ledger,self.root/"audit.json")

 def test_duplicate_register_cannot_be_appended(self):
  self.witness("REGISTER")
  with self.assertRaisesRegex(ValueError,"WITNESS_EVENT_ORDER"):
   self.witness("REGISTER")
  self.assertEqual(len(g.ledger_load(self.ledger)[0]),1)

 def test_replay_off_after_on_rejected(self):
  self.complete()
  with self.assertRaisesRegex(ValueError,"WITNESS_EVENT_ORDER"):
   self.witness("OFF_OBSERVED")

 def test_off_before_register_rejected(self):
  with self.assertRaisesRegex(ValueError,"WITNESS_EVENT_ORDER"):
   self.witness("OFF_OBSERVED")

 def test_on_before_off_rejected(self):
  self.witness("REGISTER")
  with self.assertRaisesRegex(ValueError,"WITNESS_EVENT_ORDER"):
   self.witness("ON_OBSERVED")

 def test_changed_witness_host_after_register_rejected(self):
  self.witness("REGISTER")
  changed={**self.independent,"machine_id":"OTHER_SYNTHETIC_HOST"}
  with self.assertRaisesRegex(ValueError,"WITNESS_IDENTITY_MISMATCH"):
   self.witness("OFF_OBSERVED",host=changed)

 def test_witness_reboot_after_register_rejected(self):
  self.witness("REGISTER")
  changed={**self.independent,"boot_id":"DIFFERENT_SYNTHETIC_BOOT"}
  with self.assertRaisesRegex(ValueError,"WITNESS_IDENTITY_MISMATCH"):
   self.witness("OFF_OBSERVED",host=changed)

 def test_missing_witness_boot_id_rejected(self):
  changed={**self.independent,"boot_id":None}
  with self.assertRaisesRegex(ValueError,"WITNESS_IDENTITY_INCOMPLETE"):
   self.witness("REGISTER",host=changed)

 def test_empty_operator_note_rejected(self):
  with self.assertRaisesRegex(ValueError,"WITNESS_NOTE_REQUIRED"):
   self.witness("REGISTER","   ")

 def test_unchanged_complete_manual_log_never_certifies(self):
  self.complete()
  report=self.verify()
  self.assertFalse(report["certified"])
  self.assertEqual(report["status"],"NOT_CERTIFIED")
  for key in ("external_witness_three_events","witness_host_stable",
              "witness_clock_monotonic","witness_event_binding",
              "witness_event_nonce_unique","witness_manifest_consistent"):
   self.assertTrue(report["checks"][key],key)
  self.assertFalse(report["checks"]["target_boot_changed"])

 def test_modified_boot_id_with_recomputed_hash_fails(self):
  self.complete()
  self.forge_rehash(lambda e:e[2]["witness_host"].update(boot_id="FORGED_BOOT"))
  report=self.verify()
  self.assertFalse(report["checks"]["witness_host_stable"])
  self.assertFalse(report["certified"])

 def test_timestamp_reverse_with_rehashed_chain_fails(self):
  self.complete()
  def reversed_time(events):
   events[2]["observed_utc"]=(g.parse_witness_clock(events[0]["observed_utc"])
    - dt.timedelta(seconds=100)).isoformat()
  self.forge_rehash(reversed_time)
  report=self.verify()
  self.assertFalse(report["checks"]["witness_clock_monotonic"])
  self.assertFalse(report["certified"])

 def test_monotonic_counter_replay_with_rehashed_chain_fails(self):
  self.complete()
  self.forge_rehash(lambda e:e[2].update(monotonic_ns=e[0]["monotonic_ns"]))
  report=self.verify()
  self.assertFalse(report["checks"]["witness_clock_monotonic"])

 def test_event_nonce_replay_rejected_even_with_new_hashes(self):
  self.complete()
  self.forge_rehash(lambda e:e[2].update(event_nonce=e[1]["event_nonce"]))
  with self.assertRaisesRegex(ValueError,"WITNESS_NONCE_REPLAY"):
   g.ledger_load(self.ledger)

 def test_manifest_binding_forgery_with_rehashed_chain_fails(self):
  self.complete()
  self.forge_rehash(lambda e:e[1].update(manifest_sha256="0"*64))
  report=self.verify()
  self.assertFalse(report["checks"]["witness_manifest_consistent"])
  self.assertFalse(report["checks"]["witness_event_binding"])

 def test_cross_run_log_does_not_substitute_for_target_run(self):
  self.complete()
  second=g.setup_fixture(self.root,"RECEIVER_UNCOMMITTED")
  other=self.root/second["run_id"]/"manifest.json"
  with contextlib.redirect_stdout(io.StringIO()):
   result=g.verify(other,self.ledger,self.root/"crossrun.json")
  self.assertFalse(result["checks"]["external_witness_three_events"])
  self.assertFalse(result["certified"])

 def test_appended_register_replay_in_valid_chain_rejected(self):
  self.complete()
  self.forge_rehash(lambda events:events.append({
   **events[0],"event_nonce":uuid.uuid4().hex}))
  report=self.verify()
  self.assertFalse(report["checks"]["external_witness_three_events"])
  self.assertFalse(report["certified"])

 def test_same_run_concurrent_register_single_writer(self):
  def worker(_):
   try:
    self.witness("REGISTER")
    return "APPENDED"
   except ValueError as e:
    return str(e)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
   results=list(ex.map(worker,(0,1)))
  self.assertEqual(results.count("APPENDED"),1,results)
  self.assertTrue(any("WITNESS_EVENT_ORDER" in x for x in results))
  self.assertEqual(len(g.ledger_load(self.ledger)[0]),1)

 def test_missing_witness_log_never_certifies(self):
  with contextlib.redirect_stdout(io.StringIO()):
   report=g.verify(self.manifest,None,self.root/"missing.json")
  self.assertFalse(report["certified"])
  self.assertFalse(report["checks"]["external_witness_three_events"])

 def test_invalid_utc_timestamp_string_cannot_be_ordered(self):
  self.complete()
  self.forge_rehash(lambda e:e[1].update(observed_utc="NOT_A_TIMESTAMP"))
  report=self.verify()
  self.assertFalse(report["checks"]["witness_clock_monotonic"])

 def test_symlinked_witness_ledger_is_rejected(self):
  target=self.root/"real.jsonl"
  target.write_text("")
  link=self.root/"symlink.jsonl"
  link.symlink_to(target)
  with self.assertRaisesRegex(ValueError,"WITNESS_SYMLINK_FORBIDDEN"):
   g.ledger_load(link)
  with self.assertRaisesRegex(ValueError,"WITNESS_SYMLINK_FORBIDDEN"):
   with patch.object(g,"host_id",return_value=self.independent):
    g.witness(self.manifest,link,"REGISTER","synthetic test")

if __name__=="__main__":
 unittest.main(verbosity=2)
