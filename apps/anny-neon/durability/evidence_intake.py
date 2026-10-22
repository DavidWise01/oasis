#!/usr/bin/env python3
"""ANNY offline five-run evidence intake and quarantine boundary.

Authenticates an OUT-OF-BAND anchored five-run directory using the existing
Ed25519 verifiers. Inventories exactly the 25 expected input files plus the
batch descriptor. Produces a redacted review receipt, not a power certificate.
Never copies raw evidence, generates keys, or controls electrical power.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import five_run_gate as five

SCHEMA = 'anny-evidence-intake-v1'
EXPECTED_PER_RUN = ('manifest', 'policy', 'witness', 'meter', 'recovery')
EXPECTED_COUNT = 26  # batch descriptor + five files for each of five runs
MAX_FILE_SIZE = 1_000_000
MAX_TOTAL_SIZE = 6_000_000


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def scan(root: Path, bundle_path: Path) -> dict:
    """Inventory only known evidence names. Unexpected files fail closed."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('EVIDENCE_ROOT_INVALID')
    bundle_path = Path(bundle_path)
    if bundle_path.is_symlink():
        raise ValueError('BUNDLE_SYMLINK_FORBIDDEN')
    descriptor = bundle_path.resolve(strict=True)
    if not descriptor.is_relative_to(root):
        raise ValueError('BUNDLE_OUTSIDE_ROOT')
    bundle, _ = five.load_json(descriptor, 25_000)
    if not isinstance(bundle, dict) or set(bundle) != {'schema', 'runs'} or bundle['schema'] != five.SCHEMA or not isinstance(bundle['runs'], list) or len(bundle['runs']) != 5:
        raise ValueError('INVALID_FIVE_RUN_DESCRIPTOR')
    expected = {descriptor}
    inventory = []
    for idx, entry in enumerate(bundle['runs']):
        if not isinstance(entry, dict) or set(entry) != set(five.FIELDS) or entry['case'] != five.ORDER[idx]:
            raise ValueError('INVALID_ORDER_OR_FIELDS')
        for label in EXPECTED_PER_RUN:
            p = five.file_at(root, entry[label])
            if p in expected:
                raise ValueError('EVIDENCE_FILE_REUSE')
            expected.add(p)
            meta = p.stat(follow_symlinks=False)
            if not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1:
                raise ValueError('EVIDENCE_FILE_NOT_STANDALONE')
            if meta.st_size == 0 or meta.st_size > MAX_FILE_SIZE:
                raise ValueError('EVIDENCE_FILE_SIZE_INVALID')
            raw = p.read_bytes()
            if len(raw) != meta.st_size:
                raise ValueError('EVIDENCE_FILE_SIZE_CHANGED')
            # No private keys should enter a source-data review bundle.
            if b'-----BEGIN' in raw and b'PRIVATE KEY-----' in raw:
                raise ValueError('PRIVATE_KEY_MATERIAL_FORBIDDEN')
            inventory.append({'case':entry['case'], 'role':label,
                 'sha256':digest(raw), 'bytes':len(raw)})
    if len(expected) != EXPECTED_COUNT:
        raise ValueError('EXPECTED_26_EVIDENCE_FILES')
    # Reject any surprise file, including hidden files and symlinks. We never
    # extract archives or follow symlinks while walking the staging root.
    actual = set()
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in dirs:
            if (parent / name).is_symlink():
                raise ValueError('UNEXPECTED_EVIDENCE_SYMLINK')
        for name in files:
            actual.add(parent / name)
    if expected != actual:
        raise ValueError('UNEXPECTED_OR_MISSING_EVIDENCE_FILES')
    inventory.sort(key=lambda x: (five.ORDER.index(x['case']), EXPECTED_PER_RUN.index(x['role'])))
    total = descriptor.stat().st_size + sum(f['bytes'] for f in inventory)
    if total > MAX_TOTAL_SIZE:
        raise ValueError('EVIDENCE_TOTAL_SIZE_INVALID')
    # Hash raw file identities but omit serials, device IDs and names from the public receipt.
    return {'count':len(expected),'bytes':total,'sha256_index':inventory}


def evaluate(root, bundle_path, trusted_bundle_sha256):
    result = {'schema':SCHEMA,'status':'QUARANTINED',
      'certified':False, 'physical_power_loss_certified':False,
      'real_hardware_observed_by_this_program':False,
      'public_metadata_only':True, 'checks':{}, 'evidence_class':'OFFLINE_UNTRUSTED_UNTIL_REVIEW'}
    try:
        if not isinstance(trusted_bundle_sha256,str) or len(trusted_bundle_sha256)!=64 or any(c not in '0123456789abcdef' for c in trusted_bundle_sha256):
            raise ValueError('EXTERNAL_BATCH_HASH_REQUIRED')
        root = Path(root).resolve(strict=True)
        bundle_path = Path(bundle_path)
        files = scan(root, bundle_path)
        result['checks']['inventory_exact_26_files'] = files['count'] == EXPECTED_COUNT
        batch = five.verify_batch(root, bundle_path, trusted_bundle_sha256)
        result['checks']['five_run_crypto_and_continuity'] = batch['status']=='AUTHENTICATED_FIVE_RUN_EVIDENCE_CANDIDATE'
        if not result['checks']['five_run_crypto_and_continuity']:
            raise ValueError('BATCH_NOT_AUTHENTICATED:'+str(batch.get('error','UNKNOWN')))
        result['status'] = 'AUTHENTICATED_REVIEW_REQUIRED'
        result['evidence_class'] = 'SIGNED_FIVE_RUN_CANDIDATE_NOT_PHYSICAL_CERTIFICATE'
        result['checks']['external_batch_hash_matches'] = True
        result['checks']['redacted_only'] = True
        result['bundle_sha256'] = trusted_bundle_sha256
        result['inventory'] = files
        # Do not emit batch['hardware'] or report signatures, serial numbers,
        # device public keys or full file paths into the report.
        result['authenticated_run_count'] = len(batch['runs'])
        result['review_requirements'] = [
           'independently inspect out-of-band device onboarding and key ownership',
           'independently verify meter hardware/voltage cut and timing',
           'reconcile target storage reboot and controller write-cache behavior',
           'review each individual post-boot recovery and external side effects'
        ]
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        result['error_code'] = str(exc).split(':',1)[0]
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--bundle', required=True)
    p.add_argument('--trusted-bundle-sha256',required=True)
    p.add_argument('--report',required=True)
    args=p.parse_args()
    report=evaluate(args.root,args.bundle,args.trusted_bundle_sha256)
    report_path=Path(args.report).resolve()
    if report_path.parent == Path(args.root).resolve() or report_path.is_relative_to(Path(args.root).resolve()):
        raise ValueError('REPORT_MUST_STAY_OUTSIDE_RAW_EVIDENCE_DIR')
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':report['status'],'certified':False,'report':str(report_path)}))
    return 0 if report['status']=='AUTHENTICATED_REVIEW_REQUIRED' else 2

if __name__=='__main__':
    raise SystemExit(main())
