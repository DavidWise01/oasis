"""Synthetic-only Ed25519 hardware-binding tests. No actual power is controlled."""
import copy
import datetime as dt
import json
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import hardware_boundary as h
import witness_attestation as a
import test_witness_attestation as fixture_module

class HardwareEvidenceTests(unittest.TestCase):
    def setUp(self):
        f=fixture_module.SignedWitnessEvidenceTests('test_valid_dual_signature_is_candidate_not_certificate')
        f.setUp()
        self.addCleanup(f.temp.cleanup)
        self.f=f
        self.tkey=Ed25519PrivateKey.generate()
        self.hw={
            'machine_id':'SYNTHETIC-MACHINE-AAA',
            'disk_serial':'SYNTHETIC-DISK-123',
            'disk_model':'DISPOSABLE-TEST-DISK',
            'disk_firmware':'TEST-1.0',
            'filesystem_uuid':'SYNTHETIC-FS-1',
            'power_circuit_id':'TEST-BRANCH-A',
            'meter_channel_id':'CHANNEL-7',
            'meter_serial':'METER-SIMULATED-004',
            'meter_calibration_sha256':'a'*64
        }
        f.manifest['target']={'hostname':'sim-target','machine_id':self.hw['machine_id'],
                              'boot_id':'BOOT-BEFORE-TEST'}
        f.manifest['manifest_sha256']=a.digest(a.canonical({k:v for k,v in f.manifest.items() if k!='manifest_sha256'}))
        f.policy['manifest_sha256']=f.manifest['manifest_sha256']
        f.policy['hardware']=self.hw
        f.policy['target']={'device_id':'TARGET-RECOVERY-001', 'ed25519_public_key_b64':f.pub(self.tkey)}
        for role in a.SEQUENCE:
            for item in f.events[role]:
                p=item['payload']
                p['manifest_sha256']=f.manifest['manifest_sha256']
                if role=='meter':
                    for x in ('power_circuit_id','meter_channel_id','meter_serial','meter_calibration_sha256'):
                        p[x]=self.hw[x]
                    p['measurement_kind']='rms_voltage'
            f.resign(role)
        self.recovery={
            'schema':h.RECOVERY_SCHEMA,'run_id':f.manifest['run_id'],
            'manifest_sha256':f.manifest['manifest_sha256'],
            'device_id':f.policy['target']['device_id'],
            'machine_id':self.hw['machine_id'],'hardware':copy.deepcopy(self.hw),
            'preboot_boot_id':'BOOT-BEFORE-TEST','postboot_boot_id':'BOOT-AFTER-TEST',
            'snapshot':{'state':'CONFIRMED','receipt':True,'effect_count':1,'receiver_rows':1,
                        'violet':'VERIFIED','integrity':['ok','ok'],'source_consistent':True},
            'observed_utc': (dt.datetime(2026,10,21,22,27,tzinfo=dt.timezone.utc)+dt.timedelta(seconds=50)).isoformat()
        }
        self.write()

    def write(self):
        self.f.write()
        self.path=self.f.root/'recovery.json'
        self.path.write_text(json.dumps(self.f.sign(self.tkey,self.recovery)))

    def resign_meter(self):
        self.f.resign('meter')
        self.write()

    def resign_recovery(self):
        self.write()

    def evaluate(self, pin=None):
        f=self.f
        return h.evaluate(f.root/'manifest.json',f.root/'policy.json',
                          pin or a.digest((f.root/'policy.json').read_bytes()),
                          f.root/'witness.jsonl',f.root/'meter.jsonl',self.path)

    def rejected(self, error):
        r=self.evaluate()
        self.assertEqual(r['status'],'NOT_AUTHENTICATED',r)
        self.assertFalse(r['certified'])
        self.assertFalse(r['physical_power_loss_certified'])
        self.assertIn(error,r.get('error',''),r)

    def test_valid_three_signed_claims_remain_uncertified(self):
        r=self.evaluate()
        self.assertEqual(r['status'],'AUTHENTICATED_HARDWARE_EVIDENCE_CANDIDATE',r)
        self.assertFalse(r['certified'])
        self.assertFalse(r['physical_power_loss_certified'])
        self.assertEqual(r['evidence']['disk_serial'],self.hw['disk_serial'])

    def test_unpinned_policy_hash_rejected(self):
        self.assertIn('OUT_OF_BAND_POLICY_HASH_REQUIRED',self.evaluate(pin='invalid')['error'])

    def test_policy_swap_cannot_change_disk(self):
        trusted=a.digest((self.f.root/'policy.json').read_bytes())
        self.f.policy['hardware']['disk_serial']='CHANGED-DISK'
        self.write()
        self.assertIn('POLICY_ANCHOR_MISMATCH',self.evaluate(pin=trusted)['error'])

    def test_target_key_must_differ_from_witness(self):
        self.f.policy['target']['ed25519_public_key_b64']=self.f.policy['witness']['ed25519_public_key_b64']
        self.write()
        self.rejected('SIGNER_SEPARATION_REQUIRED')

    def test_target_device_id_must_differ_from_meter(self):
        self.f.policy['target']['device_id']=self.f.policy['meter']['device_id']
        self.write()
        self.rejected('SIGNER_SEPARATION_REQUIRED')

    def test_wrong_signed_meter_channel(self):
        self.f.events['meter'][1]['payload']['meter_channel_id']='WRONG-CHANNEL'
        self.resign_meter()
        self.rejected('METER_CIRCUIT_OR_CALIBRATION_MISMATCH')

    def test_wrong_signed_meter_circuit(self):
        self.f.events['meter'][1]['payload']['power_circuit_id']='OTHER-BRANCH'
        self.resign_meter()
        self.rejected('METER_CIRCUIT_OR_CALIBRATION_MISMATCH')

    def test_wrong_signed_meter_calibration(self):
        self.f.events['meter'][0]['payload']['meter_calibration_sha256']='b'*64
        self.resign_meter()
        self.rejected('METER_CIRCUIT_OR_CALIBRATION_MISMATCH')

    def test_non_meter_reading_rejected(self):
        self.f.events['meter'][1]['payload']['measurement_kind']='temperature'
        self.resign_meter()
        self.rejected('METER_CIRCUIT_OR_CALIBRATION_MISMATCH')

    def test_mismatched_target_disk_serial(self):
        self.recovery['hardware']['disk_serial']='DIFFERENT-STORAGE'
        self.resign_recovery()
        self.rejected('RECOVERY_HARDWARE_MISMATCH')

    def test_wrong_recovery_signer(self):
        self.path.write_text(json.dumps(self.f.sign(self.f.mkey,self.recovery)))
        self.rejected('RECOVERY_SIGNATURE_INVALID')

    def test_target_reboot_required(self):
        self.recovery['postboot_boot_id']=self.recovery['preboot_boot_id']
        self.resign_recovery()
        self.rejected('NO_CONFIRMED_NEW_BOOT')

    def test_target_same_machine_id_required(self):
        self.recovery['machine_id']='OTHER-MACHINE'
        self.resign_recovery()
        self.rejected('TARGET_MACHINE_MISMATCH')

    def test_recovery_wrong_effect_count(self):
        self.recovery['snapshot']['effect_count']=2
        self.resign_recovery()
        self.rejected('RECOVERY_STATE_MISMATCH')

    def test_recovery_wrong_receiver_rows(self):
        self.recovery['snapshot']['receiver_rows']=2
        self.resign_recovery()
        self.rejected('RECOVERY_STATE_MISMATCH')

    def test_recovery_bad_sqlite_integrity(self):
        self.recovery['snapshot']['integrity']=['corrupt','ok']
        self.resign_recovery()
        self.rejected('RECOVERY_INTEGRITY_INVALID')

    def test_recovery_before_restoration_rejected(self):
        self.recovery['observed_utc']='2026-10-21T22:27:10+00:00'
        self.resign_recovery()
        self.rejected('RECOVERY_TIME_OUTSIDE_WINDOW')

    def test_recovery_more_than_one_day_after_rejected(self):
        self.recovery['observed_utc']='2026-10-25T22:27:50+00:00'
        self.resign_recovery()
        self.rejected('RECOVERY_TIME_OUTSIDE_WINDOW')

    def test_meter_off_voltage_absent(self):
        self.f.events['meter'][1]['payload']['voltage_v']=120
        self.resign_meter()
        self.rejected('METER_TRACE_DOES_NOT_SHOW_CUT')

    def test_witness_event_run_id_replayed(self):
        self.f.events['witness'][1]['payload']['run_id']='run-other'
        self.f.resign('witness')
        self.write()
        self.rejected('MANIFEST_RUN_MISMATCH')

    def test_recovery_signature_tamper(self):
        env=json.loads(self.path.read_text())
        env['payload']['postboot_boot_id']='TAMPERED-AFTER-SIGN'
        self.path.write_text(json.dumps(env))
        self.rejected('RECOVERY_SIGNATURE_INVALID')

if __name__=='__main__': unittest.main(verbosity=2)
