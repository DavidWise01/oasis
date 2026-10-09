#!/usr/bin/env python3
"""Seal a complete, independently audited SHEET158 archive with its frozen parent."""
import hashlib,json,os,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
BASE=HERE/'baseline157'
PARENT=HERE.parent/'SHEET157-certified-witness-catchup.zip'
ARCHIVE=HERE.parent/'SHEET158-paginated-witness-consistency.zip'
CHECKSUM=ARCHIVE.with_name(ARCHIVE.name+'.sha256.txt')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def all_files(root):return sorted(p for p in root.rglob('*') if p.is_file())
assert PARENT.is_file(),f'Parent missing: {PARENT}'
assert (HERE/'combined-exit.txt').read_text().strip()=='0','Inherited-plus-new runner must exit 0'
results=json.loads((HERE/'new-test-report.json').read_text())
assert results['passed']==58 and results['failed']==0,'New gate must pass'
log=(HERE/'browser-test.log').read_text()
assert log.count('PASS chromium scenario')==8 and 'PASS chromium JSON export' in log and 'PASS chromium screenshot' in log
# Byte-compare every parent archive file with the frozen disk copy.
with zipfile.ZipFile(PARENT,'r') as p:
    entries={x.filename[len('sheet157/'):]:x for x in p.infolist() if x.filename.startswith('sheet157/') and not x.is_dir()}
    paths={str(x.relative_to(BASE)).replace('\\','/'):x for x in all_files(BASE)}
    assert paths.keys()==entries.keys(),f'Parent mismatch: missing {entries.keys()-paths.keys()}, extras {paths.keys()-entries.keys()}'
    for rel,entry in entries.items():
        assert hashlib.sha256(p.read(entry)).digest()==hashlib.sha256(paths[rel].read_bytes()).digest(),f'Parent file changed: {rel}'
release={
 'schema':'oasis.sheet158.release.v1',
 'sheet':158,'parentSheet':157,
 'title':'Paginated Witness Consistency and Crash-Safe Catch-Up',
 'status':'0e / PASS','verification':{
     'newChecks':58,'newChecksExit':0,'inheritedAndNewExit':0,
     'inheritedPreviousKnownChecks':1560,'combinedKnownChecks':1618,
     'chromiumScenarios':8,'chromiumExport':True,'chromiumScreenshot':True,
     'parentFilesPreserved':len(entries),'parentByteIdentical':True,
     'syntheticFixtureRecords':337,'realLiveCommitSlots':[338,339],
 },
 'protocol':{'certificate':'2 of 3 distinct Ed25519 signed heads','pageMaxRecords':24,'nonceHexChars':40,'recoveryCursor':'durable atomic state','crash':'page fsync before response, restart and resume'},
 'limitations':['One physical host with independently signed local mTLS processes','Page-linked linear proofs; not an O(log n) Merkle consistency proof','Total transfer O(missing records); full local JSON state O(history size)','Fully restored disk rollback requires external retained pin','Old SHEET142 intermittent test passed in this run but is not proven permanently resolved','Synthetic cryptographic fixture used for first 337 journal records']
}
(HERE/'release-receipt.json').write_text(json.dumps(release,indent=2)+'\n')
# Source inventory helps precise GitHub publication; build before SHA256SUMS.
source=['page-verify158.js','witness158.js','catchup158.js','gate158.js','run-all.sh','browser-check.py','make-release.py','KERNEL-ASCII.txt']
with (HERE/'SOURCE-ALL158.md').open('w') as out:
 out.write('# SHEET 158 — Full New Executable Sources\n\n')
 out.write('These are the exact new sources; the full frozen parent lineage is in the accompanying ZIP.\n\n')
 for name in source:
  lang='javascript' if name.endswith('.js') else 'python' if name.endswith('.py') else 'text' if name.endswith('.txt') else 'bash'
  out.write(f'## {name}\n\n```{lang}\n')
  out.write((HERE/name).read_text().rstrip()+ '\n```\n\n')
manifest=HERE/'SHA256SUMS'
files=[p for p in all_files(HERE) if p!=manifest]
manifest.write_text(''.join(f'{digest(p)}  {p.relative_to(HERE).as_posix()}\n' for p in files))
files=all_files(HERE)
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in files:z.write(p,arcname='sheet158/'+p.relative_to(HERE).as_posix())
with zipfile.ZipFile(ARCHIVE,'r') as z:
 assert z.testzip() is None
 names=set(z.namelist());assert len(names)==len(files)
 for p in files:
  arc='sheet158/'+p.relative_to(HERE).as_posix()
  assert arc in names and hashlib.sha256(z.read(arc)).hexdigest()==digest(p),arc
 for rel in entries:assert 'sheet158/baseline157/'+rel in names
CHECKSUM.write_text(f'{digest(ARCHIVE)}  {ARCHIVE.name}\n')
print(json.dumps({'zip':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':digest(ARCHIVE),'inheritedFiles':len(entries),'totalArchiveFiles':len(files),'newTests':58,'combinedExit':0},indent=2))
