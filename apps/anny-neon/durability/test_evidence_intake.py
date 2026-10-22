"""ANNY local-only intake and quarantine negative controls. No hardware use."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import evidence_intake as intake
import test_five_run_gate as fixtures

class IntakeTests(unittest.TestCase):
    def setUp(self):
        f=fixtures.FiveRunBatchTests('test_valid_five_synthetic_candidates_never_certify_power')
        f.setUp(); self.addCleanup(f.doCleanups)
        self.f=f

    def test_all_signed_synthetic_cases_yield_review_not_certificate(self):
        x=intake.evaluate(self.f.root,self.f.path,self.f.pin)
        self.assertEqual(x['status'],'AUTHENTICATED_REVIEW_REQUIRED',x)
        self.assertFalse(x['certified'])
        self.assertFalse(x['physical_power_loss_certified'])
        self.assertEqual(x['inventory']['count'],26)
        self.assertEqual(len(x['inventory']['sha256_index']),25)
        self.assertEqual(x['authenticated_run_count'],5)

    def test_wrong_external_anchor_quarantined(self):
        x=intake.evaluate(self.f.root,self.f.path,'0'*64)
        self.assertEqual(x['status'],'QUARANTINED')
        self.assertIn('BATCH_NOT_AUTHENTICATED',x['error_code'])

    def test_missing_anchor_quarantined(self):
        x=intake.evaluate(self.f.root,self.f.path,'untrusted')
        self.assertEqual(x['error_code'],'EXTERNAL_BATCH_HASH_REQUIRED')

    def test_unexpected_file_quarantined(self):
        (self.f.root/'README.md').write_text('unexpected')
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'UNEXPECTED_OR_MISSING_EVIDENCE_FILES')

    def test_hidden_file_quarantined(self):
        (self.f.root/'.hidden').write_text('unexpected')
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'UNEXPECTED_OR_MISSING_EVIDENCE_FILES')

    def test_symlinked_evidence_quarantined(self):
        p=self.f.root/'case-0'/'meter.jsonl';q=self.f.root/'real-meter.jsonl'
        q.write_bytes(p.read_bytes());p.unlink();p.symlink_to(q)
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'SYMLINK_EVIDENCE_FORBIDDEN')

    def test_hardlinked_evidence_quarantined(self):
        p=self.f.root/'case-0'/'meter.jsonl';q=self.f.root/'elsewhere'
        q.hardlink_to(p)
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'EVIDENCE_FILE_NOT_STANDALONE')

    def test_missing_evidence_quarantined(self):
        (self.f.root/'case-0'/'meter.jsonl').unlink()
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'EVIDENCE_FILE_MISSING_OR_OUTSIDE_ROOT')

    def test_report_redacts_hardware_identifiers_and_keys(self):
        x=intake.evaluate(self.f.root,self.f.path,self.f.pin)
        data=json.dumps(x)
        self.assertNotIn('SYNTHETIC-DISK-123',data)
        self.assertNotIn('ed25519_public_key_b64',data)
        self.assertNotIn('signature_b64',data)
        self.assertNotIn('PRIVATE KEY',data)

    def test_reused_path_quarantined(self):
        self.f.bundle['runs'][0]['meter']=self.f.bundle['runs'][0]['witness']
        self.f.write_bundle()
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'EVIDENCE_FILE_REUSE')

    def test_payload_tampering_even_with_reanchored_bundle_quarantined(self):
        p=self.f.root/'case-1'/'meter.jsonl'
        p.write_text(p.read_text().replace('120.0','110.0',1))
        x=intake.evaluate(self.f.root,self.f.path,self.f.pin)
        self.assertEqual(x['error_code'],'BATCH_NOT_AUTHENTICATED')

    def test_private_key_material_quarantined(self):
        p=self.f.root/'case-1'/'meter.jsonl'
        p.write_bytes(b'-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----')
        self.assertEqual(intake.evaluate(self.f.root,self.f.path,self.f.pin)['error_code'],'PRIVATE_KEY_MATERIAL_FORBIDDEN')

if __name__=='__main__':unittest.main()
