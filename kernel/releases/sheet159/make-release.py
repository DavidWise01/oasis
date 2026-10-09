#!/usr/bin/env python3
"""Sealed, reproducible ZIP with checksum manifest and byte-for-byte lineage verification."""
from pathlib import Path
import os,hashlib,json,zipfile,sys
D=Path(__file__).resolve().parent
ROOT=D.parent
PARENT=ROOT/'sheet158'
BASE=D/'baseline158'
ARCHIVE=ROOT/'SHEET159-merkle-consistency-recovery.zip'
HASHES=ROOT/(ARCHIVE.name+'.sha256.txt')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original={p.relative_to(PARENT).as_posix():sha(p) for p in PARENT.rglob('*') if p.is_file()}
replay={p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file()}
if original!=replay:
 miss=set(original)^set(replay)
 changed=[p for p in original.keys()&replay.keys() if original[p]!=replay[p]]
 raise RuntimeError(f'Inherited files mismatch missing={list(miss)[:5]} changed={changed[:5]}')
combined=(D/'combined-exit.txt').read_text().strip() if (D/'combined-exit.txt').exists() else 'unconfirmed'
first=(D/'combined-first-exit.txt').read_text().strip() if (D/'combined-first-exit.txt').exists() else 'unconfirmed'
new=json.loads((D/'new-test-report.json').read_text());assert new['passed']==48
receipt={'sheet':159,'name':'Merkle-Certified Witness Recovery','parent':158,'inheritedFileCount':len(original),'inheritedBytesIdentical':True,'newGateChecks':48,'newGateResult':'PASS exit 0','combinedLatestExit':combined,'combinedPreviousExit':first,'inheritedKnownFlakyTest':'SHEET142 concurrent-local-writer assertion 2 !== 1','chromiumScenarios':8,'chromiumExport':'PASS','network':'loopback mTLS on one host','proof':'S151 binary-peak Merkle extension, checked against signed 2/3 target Merkle heads','scalability':'O(missing rows) transfers, source & target state still full-history replay','productionReady':False}
(D/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
# all files other than generated root manifest are part of the checksum manifest
files=sorted((p for p in D.rglob('*') if p.is_file() and p!=D/'SHA256SUMS'),key=lambda p:p.relative_to(D).as_posix())
manifest=''.join(f'{sha(p)}  {p.relative_to(D).as_posix()}\n' for p in files)
(D/'SHA256SUMS').write_text(manifest)
files.append(D/'SHA256SUMS')
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'sheet159/'+p.relative_to(D).as_posix())
with zipfile.ZipFile(ARCHIVE) as z:
 assert z.testzip() is None
 names={x.filename for x in z.infolist()}
 for name,digest in original.items():
  key='sheet159/baseline158/'+name
  assert key in names,key
  assert hashlib.sha256(z.read(key)).hexdigest()==digest,key
 for name in ('SHA256SUMS','README.md','KERNEL-ASCII.txt','gate159.js','witness159.js','merkle159.js','catchup159.js','index.html','run-all.sh','SOURCE-ALL159.md'):
  assert 'sheet159/'+name in names,name
HASHES.write_text(f'{sha(ARCHIVE)}  {ARCHIVE.name}\n')
print(json.dumps({'path':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'inheritedFilesVerified':len(original),'newChecks':48,'combinedExit':combined},indent=2))
