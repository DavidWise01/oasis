#!/usr/bin/env python3
"""ANNY hardware-binding evidence gate. OFFLINE; does not control power.

Three pinned independent Ed25519 keys: witness, meter and target recovery.
Checks provenance from the physically instrumented power circuit, and ties
signed recovery claims to the sacrificial storage device and changed boot ID.
A passing result is a CANDIDATE for human review, never a power-loss certificate.
Private keys and hardware identity values MUST come from out-of-band sources.
"""
from __future__ import annotations
import argparse
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
from cryptography.exceptions import InvalidSignature
import witness_attestation as signed

SCHEMA = 'anny-hardware-evidence-v1'
RECOVERY_SCHEMA = 'anny-signed-target-recovery-v1'
HARDWARE_FIELDS = ('machine_id', 'disk_serial', 'disk_model', 'disk_firmware',
                   'filesystem_uuid', 'power_circuit_id', 'meter_channel_id',
                   'meter_serial', 'meter_calibration_sha256')
EXPECTED = {
    'PREPARE_UNCOMMITTED': ('ABSENT', False, 0, 'HELD'),
    'COMMIT_UNCOMMITTED': ('PREPARED', False, 0, 'HELD'),
    'RECEIVER_UNCOMMITTED': ('RELEASE_PENDING', False, 0, 'HELD'),
    'CONFIRM_UNCOMMITTED': ('RELEASE_PENDING', True, 1, 'HELD'),
    'CONFIRM_COMMITTED': ('CONFIRMED', True, 1, 'VERIFIED'),
}


def sha_file(path):
    raw = Path(path).read_bytes()
    if not raw or len(raw) > 1_000_000:
        raise ValueError('EVIDENCE_FILE_BOUNDS')
    return hashlib.sha256(raw).hexdigest()


def require_str(value, code):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(code)
    return value


def verify_target_recovery(path, config, manifest, hardware):
    raw = Path(path).read_bytes()
    if not raw or len(raw) > 100_000:
        raise ValueError('RECOVERY_SIZE_BOUNDS')
    env = json.loads(raw)
    if not isinstance(env, dict) or set(env) != {'payload', 'signature_b64'}:
        raise ValueError('RECOVERY_ENVELOPE_INVALID')
    payload = env['payload']
    if not isinstance(payload, dict):
        raise ValueError('RECOVERY_PAYLOAD_INVALID')
    signature = base64.b64decode(env['signature_b64'], validate=True)
    if len(signature) != 64:
        raise ValueError('RECOVERY_SIGNATURE_LENGTH')
    try:
        signed.decode_key(config['ed25519_public_key_b64']).verify(
            signature, signed.canonical(payload))
    except InvalidSignature as exc:
        raise ValueError('RECOVERY_SIGNATURE_INVALID') from exc
    if payload.get('schema') != RECOVERY_SCHEMA or payload.get('run_id') != manifest.get('run_id'):
        raise ValueError('RECOVERY_RUN_MISMATCH')
    if payload.get('manifest_sha256') != manifest.get('manifest_sha256'):
        raise ValueError('RECOVERY_MANIFEST_MISMATCH')
    if payload.get('device_id') != config['device_id']:
        raise ValueError('RECOVERY_TARGET_DEVICE_MISMATCH')
    if payload.get('hardware') != hardware:
        raise ValueError('RECOVERY_HARDWARE_MISMATCH')
    old_boot = require_str(manifest.get('target', {}).get('boot_id'), 'MANIFEST_BOOT_MISSING')
    new_boot = require_str(payload.get('postboot_boot_id'), 'POSTBOOT_ID_MISSING')
    if payload.get('preboot_boot_id') != old_boot or new_boot == old_boot:
        raise ValueError('NO_CONFIRMED_NEW_BOOT')
    if payload.get('machine_id') != hardware['machine_id']:
        raise ValueError('TARGET_MACHINE_MISMATCH')
    exp = EXPECTED.get(manifest.get('case'))
    if exp is None:
        raise ValueError('UNKNOWN_HARDWARE_TEST_CASE')
    state = payload.get('snapshot')
    if not isinstance(state, dict):
        raise ValueError('RECOVERY_SNAPSHOT_MISSING')
    actual = (state.get('state'), state.get('receipt'),
              state.get('effect_count'), state.get('violet'))
    if tuple(map(type, actual))[1:3] != (bool, int):
        raise ValueError('RECOVERY_SNAPSHOT_TYPES')
    if actual != exp or state.get('receiver_rows') != int(exp[1]):
        raise ValueError('RECOVERY_STATE_MISMATCH')
    if state.get('integrity') != ['ok', 'ok'] or state.get('source_consistent') is not True:
        raise ValueError('RECOVERY_INTEGRITY_INVALID')
    return payload, hashlib.sha256(raw).hexdigest()


def evaluate(manifest_path, policy_path, trusted_policy_sha256,
             witness_path, meter_path, recovery_path):
    report = {'schema': SCHEMA, 'status': 'NOT_AUTHENTICATED', 'certified': False,
              'physical_power_loss_certified': False, 'checks': {},
              'evidence_class': 'THREE_SIGNED_CLAIMS_AND_PINNED_HARDWARE'}
    checks = report['checks']
    try:
        dual = signed.authenticate(manifest_path, policy_path, witness_path,
                                   meter_path, trusted_policy_sha256)
        checks['dual_signed_sources'] = dual['status'] == 'AUTHENTICATED_EVIDENCE_CANDIDATE'
        if not checks['dual_signed_sources']:
            raise ValueError('DUAL_SIGNATURE_GATE:' + str(dual.get('error', dual['status'])))
        raw_policy = Path(policy_path).read_bytes()
        if hashlib.sha256(raw_policy).hexdigest() != trusted_policy_sha256:
            raise ValueError('POLICY_PIN_CHANGED')
        policy = json.loads(raw_policy)
        manifest = json.loads(Path(manifest_path).read_bytes())
        hw = policy.get('hardware')
        if not isinstance(hw, dict) or set(hw) != set(HARDWARE_FIELDS):
            raise ValueError('HARDWARE_POLICY_FIELDS_INVALID')
        for key in HARDWARE_FIELDS:
            require_str(hw[key], 'HARDWARE_IDENTITY_MISSING:' + key)
        if len(hw['meter_calibration_sha256']) != 64 or any(
                x not in '0123456789abcdef' for x in hw['meter_calibration_sha256']):
            raise ValueError('CALIBRATION_HASH_INVALID')
        target = policy.get('target')
        if not isinstance(target, dict) or set(target) != {'device_id', 'ed25519_public_key_b64'}:
            raise ValueError('TARGET_SIGNER_POLICY_INVALID')
        require_str(target['device_id'], 'TARGET_SIGNER_ID_MISSING')
        keys = [signed.decode_key(policy[k]['ed25519_public_key_b64']) for k in ('witness', 'meter')]
        key3 = signed.decode_key(target['ed25519_public_key_b64'])
        from cryptography.hazmat.primitives import serialization
        raws = [k.public_bytes(encoding=serialization.Encoding.Raw,
                               format=serialization.PublicFormat.Raw) for k in keys + [key3]]
        checks['three_distinct_public_keys'] = len(set(raws)) == 3
        checks['three_distinct_device_ids'] = len({policy[k]['device_id'] for k in ('witness', 'meter', 'target')}) == 3
        if not checks['three_distinct_public_keys'] or not checks['three_distinct_device_ids']:
            raise ValueError('SIGNER_SEPARATION_REQUIRED')
        checks['machine_id_matches_manifest'] = hw['machine_id'] == manifest.get('target', {}).get('machine_id')
        if not checks['machine_id_matches_manifest']:
            raise ValueError('TARGET_MACHINE_POLICY_MISMATCH')
        meter_events, _ = signed.read_lines(meter_path)
        for entry in meter_events:
            p = entry['payload']
            if (p.get('power_circuit_id') != hw['power_circuit_id'] or
                p.get('meter_channel_id') != hw['meter_channel_id'] or
                p.get('meter_serial') != hw['meter_serial'] or
                p.get('meter_calibration_sha256') != hw['meter_calibration_sha256'] or
                p.get('measurement_kind') != 'rms_voltage'):
                raise ValueError('METER_CIRCUIT_OR_CALIBRATION_MISMATCH')
        checks['meter_instrument_and_circuit_pinned'] = True
        recovery, recovery_hash = verify_target_recovery(recovery_path, target, manifest, hw)
        checks['signed_target_recovery'] = True
        restore_time = signed.timestamp(meter_events[2]['payload']['observed_utc'])
        recovery_time = signed.timestamp(recovery.get('observed_utc'))
        checks['recovery_after_meter_restore'] = (
            restore_time <= recovery_time <= restore_time + dt.timedelta(days=1))
        if not checks['recovery_after_meter_restore']:
            raise ValueError('RECOVERY_TIME_OUTSIDE_WINDOW')
        checks['new_target_boot'] = True
        checks['expected_sqlite_recovery'] = True
        report['status'] = 'AUTHENTICATED_HARDWARE_EVIDENCE_CANDIDATE'
        report['evidence'] = {
            'recovery_sha256': recovery_hash, 'meter_sha256': sha_file(meter_path),
            'witness_sha256': sha_file(witness_path), 'policy_sha256': trusted_policy_sha256,
            'disk_serial': hw['disk_serial'], 'disk_firmware': hw['disk_firmware'],
            'power_circuit_id': hw['power_circuit_id'], 'meter_channel_id': hw['meter_channel_id'],
            'run_id': manifest['run_id'], 'case': manifest['case'],
        }
    except (OSError, TypeError, KeyError, ValueError, OverflowError, json.JSONDecodeError) as exc:
        report['error'] = str(exc)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--policy', required=True)
    parser.add_argument('--trusted-policy-sha256', required=True)
    parser.add_argument('--witness', required=True)
    parser.add_argument('--meter', required=True)
    parser.add_argument('--recovery', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    report = evaluate(args.manifest, args.policy, args.trusted_policy_sha256,
                      args.witness, args.meter, args.recovery)
    Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'certified': False, 'report': args.report}))
    return 0 if report['status'] == 'AUTHENTICATED_HARDWARE_EVIDENCE_CANDIDATE' else 2

if __name__ == '__main__':
    raise SystemExit(main())
