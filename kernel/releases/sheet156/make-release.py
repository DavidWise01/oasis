#!/usr/bin/env python3
"""SHEET 156 reproducible release: verify frozen ancestor, test exit, and all archive bytes."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'sheet155'
BASE=ROOT/'baseline155'
OUT=ROOT.parent/'SHEET156-quorum-witness-rollback-floor.zip'
SOURCES=['witness-verify156.js','witness156.js','floor-quorum156.js','finality-replica156.js','anchor-gateway156.js','gate156.js','run-all.sh','browser-check.py','make-release.py']
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as handle:
  for chunk in iter(lambda:handle.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
original={p.relative_to(PARENT).as_posix():digest(p) for p in PARENT.rglob('*') if p.is_file()}
preserved={p.relative_to(BASE).as_posix():digest(p) for p in BASE.rglob('*') if p.is_file()}
assert original==preserved,f'Preserved parent mismatch: {len(original)} vs {len(preserved)}'
assert (ROOT/'combined-exit.txt').read_text().strip()=='0','Combined exit must be 0'
log=(ROOT/'combined-run.log').read_text()
assert 'SHEET155 NEW PASS 56/56' in log and 'SHEET156 NEW PASS 73/73' in log,'Missing complete regression summary'
report=json.loads((ROOT/'new-test-report.json').read_text())
assert report['passed'] and report['newChecks']==73 and report['finalizedWrites']==3
browser=(ROOT/'browser-test.log').read_text()
assert browser.count('CHROMIUM PASS')==13 and 'CHROMIUM PASS screenshot' in browser
parts=['# SHEET 156 — Complete New Executable Source',
       'Exact source of the new release. Older modules remain preserved under `baseline155/` in the ZIP.']
for name in SOURCES:
 lang='javascript' if name.endswith('.js') else 'python' if name.endswith('.py') else 'bash'
 parts.append(f'\n## {name}\n\n```{lang}\n'+(ROOT/name).read_text().rstrip()+'\n```')
(ROOT/'SOURCE-ALL156.md').write_text('\n\n'.join(parts)+'\n')
receipt={
 'schema':'oasis.sheet156.release.v1','sheet':156,'previousSheet':155,
 'title':'Quorum Witness Rollback Floor with Fresh Signed Heads',
 'frozenParentFileCount':len(original),'baselineByteForByte':True,
 'tests':{'new':73,'inherited':1446,'combined':1519,'combinedExit':0,'chromiumScenarios':11,'chromiumExport':True},
 'processes':{'authority':3,'finality':3,'witnesses':3,'floorProxy':1,'checkpointSigner':1,'gateway':1},
 'witnessPolicy':{'requiredMajority':2,'total':3,'persistentConflictingPrepareHold':True,'freshHeadNonce':True},
 'securityLimitations':['all TLS processes run on one host','witnesses not independent administrators or machines','a majority witness rollback/compromise is outside threat model','lagging minority catchup not automated','S147 raw hash-only COMPLETE remains accessible to trusted leaders','S142 inherited timing-sensitive test remains open','global cross-host atomicity not proven'],
 'gitSourceFiles':SOURCES,
}
(ROOT/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'SHA256SUMS')
(ROOT/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
files.append(ROOT/'SHA256SUMS');files.sort()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  name='sheet156/'+p.relative_to(ROOT).as_posix()
  info=zipfile.ZipInfo(name,date_time=(2026,10,9,12,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 mapping={Path(n).relative_to('sheet156/baseline155').as_posix():n for n in z.namelist() if n.startswith('sheet156/baseline155/')}
 assert mapping.keys()==original.keys(),f'Archived baseline not exact: {len(mapping)} vs {len(original)}'
 for name,h in original.items(): assert hashlib.sha256(z.read(mapping[name])).hexdigest()==h,name
(ROOT.parent/(OUT.name+'.sha256.txt')).write_text(f'{digest(OUT)}  {OUT.name}\n')
print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,'sha256':digest(OUT),'files':len(files),'baseline':len(original),'exit':0,'combined':1519,'new':73},indent=2))
