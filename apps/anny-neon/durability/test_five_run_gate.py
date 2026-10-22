"""Synthetic five-run bundle tests: NO real meter, NO physical power cut."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import five_run_gate as gate
import hardware_boundary as hardware
import test_hardware_boundary as hwtests
import witness_attestation as signed


class FiveRunBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='anny-five-run-fake-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fixtures = []
        self.bundle = {'schema': gate.SCHEMA, 'runs': []}
        start = dt.datetime(2026, 10, 21, 19, 0, tzinfo=dt.timezone.utc)
        self.base_keys = None
        for i, case in enumerate(gate.ORDER):
            f = hwtests.HardwareEvidenceTests('test_valid_three_signed_claims_remain_uncertified')
            f.setUp()
            self.addCleanup(f.doCleanups)
            if self.base_keys is None:
                self.base_keys = (f.f.wkey, f.f.mkey, f.tkey)
            else:
                f.f.wkey, f.f.mkey, f.tkey = self.base_keys
            f.f.policy['witness']['ed25519_public_key_b64'] = f.f.pub(f.f.wkey)
            f.f.policy['meter']['ed25519_public_key_b64'] = f.f.pub(f.f.mkey)
            f.f.policy['target']['ed25519_public_key_b64'] = f.f.pub(f.tkey)
            f.f.manifest['run_id'] = 'synthetic-run-' + str(i)
            f.f.manifest['case'] = case
            f.f.manifest['expected'] = list(hardware.EXPECTED[case])
            f.f.manifest['target']['boot_id'] = 'SYNTHETIC-BOOT-' + str(i)
            f.recovery['preboot_boot_id'] = 'SYNTHETIC-BOOT-' + str(i)
            f.recovery['postboot_boot_id'] = 'SYNTHETIC-BOOT-' + str(i+1)
            exp = hardware.EXPECTED[case]
            f.recovery['snapshot'].update(state=exp[0], receipt=exp[1],
                effect_count=exp[2], receiver_rows=int(exp[1]), violet=exp[3])
            f.f.manifest['manifest_sha256'] = signed.digest(signed.canonical({
                k: v for k, v in f.f.manifest.items() if k != 'manifest_sha256'}))
            f.f.policy['manifest_sha256'] = f.f.manifest['manifest_sha256']
            f.recovery['run_id'] = f.f.manifest['run_id']
            f.recovery['manifest_sha256'] = f.f.manifest['manifest_sha256']
            for role in signed.SEQUENCE:
                for j, e in enumerate(f.f.events[role]):
                    p = e['payload']
                    p['run_id'] = f.f.manifest['run_id']
                    p['manifest_sha256'] = f.f.manifest['manifest_sha256']
                    p['observed_utc'] = (start + dt.timedelta(minutes=i*10,seconds=j*20)).isoformat()
                f.f.resign(role)
            f.recovery['observed_utc'] = (start + dt.timedelta(minutes=i*10,seconds=50)).isoformat()
            f.write()
            self.fixtures.append(f)
            self.save_run(i)
        self.write_bundle()

    def save_run(self, i):
        f = self.fixtures[i]
        folder = self.root / ('case-'+str(i))
        folder.mkdir(exist_ok=True)
        filepaths = {'manifest':f.f.root/'manifest.json',
                     'policy':f.f.root/'policy.json',
                     'witness':f.f.root/'witness.jsonl',
                     'meter':f.f.root/'meter.jsonl',
                     'recovery':f.path}
        for key,p in filepaths.items():
            shutil.copyfile(p, folder/p.name)
        entry = {'case':gate.ORDER[i], 'trusted_policy_sha256':hashlib.sha256(
            (folder/'policy.json').read_bytes()).hexdigest()}
        entry.update({k:str(Path(folder.name)/p.name) for k,p in filepaths.items()})
        if i>=len(self.bundle['runs']):
            self.bundle['runs'].append(entry)
        else:
            self.bundle['runs'][i] = entry

    def write_bundle(self):
        self.path = self.root/'batch.json'
        self.path.write_text(json.dumps(self.bundle,indent=2)+'\n')
        self.pin = hashlib.sha256(self.path.read_bytes()).hexdigest()

    def audit(self, pin=None):
        return gate.verify_batch(self.root,self.path,self.pin if pin is None else pin)

    def reject(self, code):
        r=self.audit()
        self.assertEqual(r['status'],'NOT_AUTHENTICATED',r)
        self.assertFalse(r['certified'])
        self.assertIn(code,r.get('error',''),r)

    def test_valid_five_synthetic_candidates_never_certify_power(self):
        r=self.audit()
        self.assertEqual(r['status'],'AUTHENTICATED_FIVE_RUN_EVIDENCE_CANDIDATE',r)
        self.assertFalse(r['certified'])
        self.assertFalse(r['physical_power_loss_certified'])
        self.assertEqual(len(r['runs']),5)
        self.assertTrue(all(r['checks'].values()),r)

    def test_unauthenticated_external_bundle_hash(self):
        r=self.audit('0'*64)
        self.assertEqual(r['status'],'NOT_AUTHENTICATED')
        self.assertIn('BUNDLE_ANCHOR_MISMATCH',r['error'])

    def test_bundle_hash_required(self):
        r=self.audit('wrong')
        self.assertIn('OUT_OF_BAND_BATCH_HASH_REQUIRED',r['error'])

    def test_missing_case_rejected(self):
        self.bundle['runs'].pop()
        self.write_bundle()
        self.reject('FIVE_RUN_BUNDLE_SCHEMA')

    def test_case_order_tamper_rejected(self):
        self.bundle['runs'][0],self.bundle['runs'][1]=self.bundle['runs'][1],self.bundle['runs'][0]
        self.write_bundle()
        self.reject('CASE_ORDER_OR_FIELDS_INVALID')

    def test_path_escape_rejected(self):
        self.bundle['runs'][0]['meter']='../../outside/meter.jsonl'
        self.write_bundle()
        self.reject('UNSAFE_EVIDENCE_PATH')

    def test_missing_meter_file_rejected(self):
        (self.root/'case-1'/'meter.jsonl').unlink()
        self.reject('EVIDENCE_FILE_MISSING_OR_OUTSIDE_ROOT')

    def test_cross_run_nonce_replay_even_when_resigned_rejected(self):
        reused=self.fixtures[0].f.events['meter'][0]['payload']['nonce']
        f=self.fixtures[1]
        f.f.events['meter'][1]['payload']['nonce']=reused
        f.f.resign('meter'); f.write();self.save_run(1);self.write_bundle()
        self.reject('CROSS_RUN_NONCE_REPLAY')

    def test_cross_run_target_signer_substitution(self):
        f=self.fixtures[2]
        f.tkey=Ed25519PrivateKey.generate()
        f.f.policy['target']['ed25519_public_key_b64']=f.f.pub(f.tkey)
        f.write();self.save_run(2);self.write_bundle()
        self.reject('SIGNER_SWAPPED_BETWEEN_RUNS')

    def test_swapped_disk_with_valid_resigned_recovery(self):
        f=self.fixtures[3]
        f.hw['disk_serial']='SYNTHETIC-OTHER-DISK'
        f.recovery['hardware']['disk_serial']='SYNTHETIC-OTHER-DISK'
        f.write();self.save_run(3);self.write_bundle()
        self.reject('HARDWARE_SWAPPED_BETWEEN_RUNS')

    def test_reused_run_id_after_valid_signature(self):
        f=self.fixtures[4]
        f.f.manifest['run_id']=self.fixtures[0].f.manifest['run_id']
        f.f.manifest['manifest_sha256']=signed.digest(signed.canonical({
            k:v for k,v in f.f.manifest.items() if k!='manifest_sha256'}))
        f.f.policy['manifest_sha256']=f.f.manifest['manifest_sha256']
        f.recovery['run_id']=f.f.manifest['run_id']
        f.recovery['manifest_sha256']=f.f.manifest['manifest_sha256']
        for role in signed.SEQUENCE:
            for entry in f.f.events[role]:
                entry['payload']['run_id']=f.f.manifest['run_id']
                entry['payload']['manifest_sha256']=f.f.manifest['manifest_sha256']
            f.f.resign(role)
        f.write();self.save_run(4);self.write_bundle()
        self.reject('RUN_ID_REPLAY')

    def test_reboot_continuity_broken_with_valid_signatures(self):
        f=self.fixtures[2]
        f.f.manifest['target']['boot_id']='UNRELATED-PREBOOT'
        f.f.manifest['manifest_sha256']=signed.digest(signed.canonical({
            k:v for k,v in f.f.manifest.items() if k!='manifest_sha256'}))
        f.f.policy['manifest_sha256']=f.f.manifest['manifest_sha256']
        f.recovery['manifest_sha256']=f.f.manifest['manifest_sha256']
        f.recovery['preboot_boot_id']='UNRELATED-PREBOOT'
        for role in signed.SEQUENCE:
            for entry in f.f.events[role]:
                entry['payload']['manifest_sha256']=f.f.manifest['manifest_sha256']
            f.f.resign(role)
        f.write();self.save_run(2);self.write_bundle()
        self.reject('BOOT_CHAIN_DISCONTINUITY')

    def test_overlapping_meter_capture_rejected(self):
        f=self.fixtures[2]
        base=dt.datetime(2026,10,21,19,0,tzinfo=dt.timezone.utc)+dt.timedelta(minutes=5)
        for role in signed.SEQUENCE:
            for j,entry in enumerate(f.f.events[role]):
                entry['payload']['observed_utc']=(base+dt.timedelta(seconds=j*20)).isoformat()
            f.f.resign(role)
        f.recovery['observed_utc']=(base+dt.timedelta(seconds=50)).isoformat()
        f.write();self.save_run(2);self.write_bundle()
        self.reject('OVERLAPPING_RUN_TIMELINES')

    def test_meter_signature_modified_after_anchor_rejected(self):
        p=self.root/'case-1'/'meter.jsonl'
        p.write_text(p.read_text().replace('120.0','110.0',1))
        self.reject('RUN_NOT_AUTHENTICATED')

    def test_evidence_symlink_rejected(self):
        p=self.root/'case-2'/'meter.jsonl'
        data=p.read_bytes();p.unlink()
        actual=self.root/'other-meter.jsonl';actual.write_bytes(data)
        p.symlink_to(actual)
        self.reject('SYMLINK_EVIDENCE_FORBIDDEN')

    def test_report_never_contains_private_key_material(self):
        r=self.audit()
        text=json.dumps(r)
        self.assertNotIn('PRIVATE KEY',text)
        self.assertNotIn('signature_b64',text)


if __name__=='__main__':
    unittest.main(verbosity=2)
