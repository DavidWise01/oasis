#!/usr/bin/env python3
"""ANNY five-run evidence ingestion: offline, read-only, no power controls.

An externally pinned batch SHA-256 binds five independently policy-pinned,
Ed25519-verified power-cut candidates. Requires stable sacrificial hardware,
signer identities, meter channel, fresh event nonces, distinct runs, ordered
capture times and consecutive target boot IDs. Never certifies power loss.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import hardware_boundary as hardware
import witness_attestation as signed

SCHEMA = 'anny-five-run-evidence-batch-v1'
ORDER = tuple(hardware.EXPECTED)
FIELDS = ('case', 'manifest', 'policy', 'trusted_policy_sha256',
          'witness', 'meter', 'recovery')


def file_at(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or len(name) > 280:
        raise ValueError('INVALID_RELATIVE_EVIDENCE_PATH')
    rel = Path(name)
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0] == '.':
        raise ValueError('UNSAFE_EVIDENCE_PATH')
    p = root / rel
    if any(part.is_symlink() for part in (root, *[root.joinpath(*rel.parts[:i])
               for i in range(1, len(rel.parts) + 1)])):
        raise ValueError('SYMLINK_EVIDENCE_FORBIDDEN')
    if not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('EVIDENCE_FILE_MISSING_OR_OUTSIDE_ROOT')
    return p


def load_json(path: Path, limit: int = 250_000):
    raw = path.read_bytes()
    if not raw or len(raw) > limit:
        raise ValueError('BUNDLE_OR_EVIDENCE_SIZE_INVALID')
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def verify_batch(root, bundle_path, trusted_bundle_sha256):
    report = {'schema': SCHEMA, 'status': 'NOT_AUTHENTICATED',
              'certified': False, 'physical_power_loss_certified': False,
              'checks': {}, 'runs': [], 'evidence_class': 'OFFLINE_SIGNED_CANDIDATE_BATCH'}
    checks = report['checks']
    try:
        if not isinstance(trusted_bundle_sha256, str) or len(trusted_bundle_sha256) != 64 or \
                any(c not in '0123456789abcdef' for c in trusted_bundle_sha256):
            raise ValueError('OUT_OF_BAND_BATCH_HASH_REQUIRED')
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError('BATCH_ROOT_NOT_DIRECTORY')
        bundle_raw = Path(bundle_path)
        if bundle_raw.is_symlink():
            raise ValueError('UNTRUSTED_BUNDLE_SYMLINK')
        bundle_path = bundle_raw.resolve(strict=True)
        if not bundle_path.is_relative_to(root):
            raise ValueError('UNTRUSTED_BUNDLE_LOCATION')
        bundle, bundle_sha = load_json(bundle_path, 25_000)
        checks['out_of_band_bundle_anchor'] = bundle_sha == trusted_bundle_sha256
        if not checks['out_of_band_bundle_anchor']:
            raise ValueError('BUNDLE_ANCHOR_MISMATCH')
        if not isinstance(bundle, dict) or set(bundle) != {'schema', 'runs'} or \
                bundle.get('schema') != SCHEMA or not isinstance(bundle.get('runs'), list) or \
                len(bundle['runs']) != 5:
            raise ValueError('FIVE_RUN_BUNDLE_SCHEMA')
        baseline_hw = baseline_signers = previous_boot = previous_recovery = None
        seen_nonces, seen_runs, seen_hashes = set(), set(), set()
        for i, item in enumerate(bundle['runs']):
            if not isinstance(item, dict) or set(item) != set(FIELDS) or \
                    item['case'] != ORDER[i]:
                raise ValueError('CASE_ORDER_OR_FIELDS_INVALID')
            pin = item['trusted_policy_sha256']
            if not isinstance(pin, str) or len(pin) != 64 or \
                    any(c not in '0123456789abcdef' for c in pin):
                raise ValueError('RUN_POLICY_HASH_REQUIRED')
            files = {k: file_at(root, item[k]) for k in FIELDS if k not in
                     ('case', 'trusted_policy_sha256')}
            if len(set(files.values())) != len(files):
                raise ValueError('DUPLICATED_EVIDENCE_FILE_PATH')
            result = hardware.evaluate(files['manifest'], files['policy'], pin,
                                       files['witness'], files['meter'], files['recovery'])
            summary = {'case': item['case'], 'status': result['status'],
                       'authenticated': result['status'] ==
                       'AUTHENTICATED_HARDWARE_EVIDENCE_CANDIDATE'}
            report['runs'].append(summary)
            if not summary['authenticated']:
                raise ValueError('RUN_NOT_AUTHENTICATED:' + item['case'] + ':' +
                                 str(result.get('error', result['status'])))
            manifest, manifest_sha = load_json(files['manifest'])
            policy, policy_sha = load_json(files['policy'])
            recovery, recovery_sha = load_json(files['recovery'])
            meter, meter_sha = signed.read_lines(files['meter'])
            witness, witness_sha = signed.read_lines(files['witness'])
            run_id = manifest['run_id']
            if run_id in seen_runs:
                raise ValueError('RUN_ID_REPLAY')
            seen_runs.add(run_id)
            if policy_sha != pin:
                raise ValueError('POLICY_FILE_DIGEST_MISMATCH')
            hw = policy['hardware']
            signers = tuple((policy[role]['device_id'],
                             policy[role]['ed25519_public_key_b64']) for role in
                            ('witness', 'meter', 'target'))
            if baseline_hw is None:
                baseline_hw, baseline_signers = hw, signers
            elif hw != baseline_hw:
                raise ValueError('HARDWARE_SWAPPED_BETWEEN_RUNS')
            elif signers != baseline_signers:
                raise ValueError('SIGNER_SWAPPED_BETWEEN_RUNS')
            current_preboot = recovery['payload']['preboot_boot_id']
            current_postboot = recovery['payload']['postboot_boot_id']
            if previous_boot is not None and current_preboot != previous_boot:
                raise ValueError('BOOT_CHAIN_DISCONTINUITY')
            times = [signed.timestamp(m['payload']['observed_utc']) for m in meter]
            recovered = signed.timestamp(recovery['payload']['observed_utc'])
            if previous_recovery is not None and times[0] <= previous_recovery:
                raise ValueError('OVERLAPPING_RUN_TIMELINES')
            for event in witness + meter:
                nonce = event['payload']['nonce']
                if nonce in seen_nonces:
                    raise ValueError('CROSS_RUN_NONCE_REPLAY')
                seen_nonces.add(nonce)
            for sha in (manifest_sha, policy_sha, recovery_sha, witness_sha, meter_sha):
                if sha in seen_hashes:
                    raise ValueError('REUSED_EVIDENCE_FILE')
                seen_hashes.add(sha)
            previous_boot, previous_recovery = current_postboot, recovered
            summary.update({'run_id': run_id, 'manifest_sha256': manifest_sha,
                            'policy_sha256': policy_sha,
                            'witness_sha256': witness_sha, 'meter_sha256': meter_sha,
                            'recovery_sha256': recovery_sha,
                            'preboot_id': current_preboot, 'postboot_id': current_postboot})
        checks.update({'five_distinct_ordered_runs': len(seen_runs) == 5,
                       'five_pinned_policies': len(report['runs']) == 5,
                       'same_hardware_and_signers': True,
                       'continuous_new_boot_chain': True,
                       'nonoverlapping_signed_timeline': True,
                       'unique_signed_event_nonces': len(seen_nonces) == 30,
                       'no_reused_file_hashes': len(seen_hashes) == 25})
        if not all(checks.values()):
            raise ValueError('FIVE_RUN_AGGREGATE_CHECK_FAILURE')
        report['status'] = 'AUTHENTICATED_FIVE_RUN_EVIDENCE_CANDIDATE'
        report['batch_sha256'] = bundle_sha
        report['hardware'] = baseline_hw
    except (OSError, ValueError, KeyError, TypeError, OverflowError,
            json.JSONDecodeError, UnicodeDecodeError) as exc:
        report['error'] = str(exc)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--bundle', required=True)
    p.add_argument('--trusted-bundle-sha256', required=True)
    p.add_argument('--report', required=True)
    args = p.parse_args()
    result = verify_batch(args.root, args.bundle, args.trusted_bundle_sha256)
    Path(args.report).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'certified': False,
                      'report': args.report}))
    return 0 if result['status'] == 'AUTHENTICATED_FIVE_RUN_EVIDENCE_CANDIDATE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
