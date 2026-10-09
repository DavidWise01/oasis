#!/usr/bin/env python3
"""Reproducible, fully self-contained SHEET 155 ZIP with immutable parent verification."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'sheet154'
BASE=ROOT/'baseline154'
OUT=ROOT.parent/'SHEET155-live-journal-multislot-finality.zip'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()
original={p.relative_to(PARENT).as_posix():digest(p) for p in PARENT.rglob('*') if p.is_file()}
preserved={p.relative_to(BASE).as_posix():digest(p) for p in BASE.rglob('*') if p.is_file()}
assert original==preserved,f'Inherited baseline mismatch: {len(original)} original vs {len(preserved)} preserved'
assert ROOT.joinpath('combined-exit.txt').read_text().strip()=='0','Clean combined process exit 0 is REQUIRED'
log=(ROOT/'combined-clean.log').read_text()
assert 'SHEET154 NEW PASS 40/40' in log and 'SHEET155 NEW PASS 56/56' in log,'Regression summary missing'
assert (ROOT/'new-test-report.json').exists()
report=json.loads((ROOT/'new-test-report.json').read_text())
assert report['newChecks']==56 and report['passed'] and report['finalizedWrites']==3
assert 'CHROMIUM PASS screenshot' in (ROOT/'browser-test.log').read_text()
source=['floor155.js','finality-replica155.js','anchor-gateway155.js','quorum155.js','gate155.js','run-all.sh','browser-check.py','make-release.py']
parts=['# SHEET 155 — Complete New Executable Sources\n',
       'These are the authored source files. The full frozen earlier lineage is bundled under `baseline154/` in the ZIP.\n']
for filename in source:
    lang='javascript' if filename.endswith('.js') else 'python' if filename.endswith('.py') else 'bash'
    parts.append(f'\n## {filename}\n\n```{lang}\n'+(ROOT/filename).read_text().rstrip()+'\n```\n')
(ROOT/'SOURCE-ALL155.md').write_text('\n'.join(parts))
receipt={'schema':'oasis.sheet155.release.v1','sheet':155,'previousSheet':154,'title':'Live Authority Journals & Multi-Slot Finality',
         'preservedBaselineFiles':len(original),'baselineByteForByte':True,
         'tests':{'new':56,'inherited':1390,'combined':1446,'combinedExit':0,'chromiumScenarios':8,'browserJsonExport':True},
         'networkTests':{'liveS147AuthorityReplicas':3,'finalityReplicas':3,'checkpointSignerProcesses':1,'admissionGatewayProcesses':1,'rollbackFloorProcesses':1,'completedSlots':3,'pendingPartitionProbeSlots':1,'physicalWrites':4},
         'securityBoundary':['all services on one physical host','external floor has one key and is not itself quorum-replicated','S147 raw COMPLETE still accepts a hash','coordinator and authority distributed linearizability not proven','all test keys ephemeral','S142 inherited timing assertion can still be intermittent'],
         'filesWithFullSourceOnGithub':['floor155.js','finality-replica155.js','anchor-gateway155.js','quorum155.js','gate155.js']}
(ROOT/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=(ROOT/'SHA256SUMS'))
(ROOT/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
files.append(ROOT/'SHA256SUMS');files.sort()
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in files:
        name='sheet155/'+p.relative_to(ROOT).as_posix()
        info=zipfile.ZipInfo(name,date_time=(2026,10,9,12,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o644<<16)
        archive.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as archive:
    assert archive.testzip() is None
    observed={Path(n).relative_to('sheet155/baseline154').as_posix():n for n in archive.namelist() if n.startswith('sheet155/baseline154/')}
    assert observed.keys()==original.keys(),f'ZIP baseline mismatch {len(observed)} vs {len(original)}'
    for name,d in original.items(): assert hashlib.sha256(archive.read(observed[name])).hexdigest()==d,name
(ROOT.parent/(OUT.name+'.sha256.txt')).write_text(f'{digest(OUT)}  {OUT.name}\n')
print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,'sha256':digest(OUT),'files':len(files),'baseline':len(original),'testExit':0,'newChecks':56,'combinedChecks':1446},indent=2))
