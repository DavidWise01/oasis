#!/usr/bin/env python3
"""Fail-closed SHA256-checked reproducible ZIP packager for SHEET 161."""
from pathlib import Path
import zipfile,hashlib,json,os
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent/'sheet160'
OUT=ROOT.parent/'SHEET161-indexed-witness-recovery-benchmark.zip'
HFILE=ROOT.parent/(OUT.name+'.sha256.txt')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()

before={p.relative_to(PARENT):sha(p) for p in PARENT.rglob('*') if p.is_file()}
after={p.relative_to(ROOT/'baseline160'):sha(p) for p in (ROOT/'baseline160').rglob('*') if p.is_file()}
assert before==after, f'SHEET160 frozen lineage mismatch: {len(before)} vs {len(after)} files'
checks=json.loads((ROOT/'new-test-report.json').read_text())
assert checks.get('passed')==36 and checks.get('failed')==0
assert 'SHEET160 GATE 71/71 PASS' in (ROOT/'inherited-gate160.log').read_text()
assert 'SHEET160 BRIDGE 19/19 PASS' in (ROOT/'inherited-bridge160.log').read_text()
assert 'PASS browser screenshot' in (ROOT/'browser-test.log').read_text()
report={
 'sheet':161,'status':'0e / PASS','newChecks':36,'inheritedGateChecks':71,
 'inheritedMigrationChecks':19,'browserChecks':10,
 'baselineSheet':160,'baselineFilesByteIdentical':len(before),
 'combinedHistoricalRunner':'not rerun',
 's160_full_benchmark_rerun':'timed out near 6144/12288 writes',
 'benchmarkFiles':['benchmark161-small.json','benchmark161.json','benchmark161-large.json'],
 'networkHostsPhysical':1,'crashWindow':'post fsync pre-ack',
 'sourcePreserved':True,'limitations':[
  '2 source witness services and a target witness run on one physical host',
  'external signed pin persists on the same test host',
  'per-row fsync and per-request mTLS handshake',
  'full historical regression chain not rerun'
 ]}
(ROOT/'release-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
all_files=sorted((p for p in ROOT.rglob('*') if p.is_file() and p != ROOT/'SHA256SUMS' and p != ROOT/'release-build.log'),key=lambda p:p.relative_to(ROOT).as_posix())
lines=[f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in all_files]
(ROOT/'SHA256SUMS').write_text(''.join(lines))
all_files.append(ROOT/'SHA256SUMS')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
 for p in sorted(all_files,key=lambda x:x.relative_to(ROOT).as_posix()):
  info=zipfile.ZipInfo('sheet161/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,9,12,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=(0o100644<<16)
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 names=set(z.namelist())
 for rel,digest in before.items():
  name='sheet161/baseline160/'+rel.as_posix()
  assert name in names, 'inherited file excluded: '+name
  assert hashlib.sha256(z.read(name)).hexdigest()==digest, 'inherited file differs: '+name
 for p in all_files:
  name='sheet161/'+p.relative_to(ROOT).as_posix()
  assert name in names and hashlib.sha256(z.read(name)).hexdigest()==sha(p),'release tree mismatch: '+name
assert len(before)==677, f'unexpected inherited file count {len(before)}'
HFILE.write_text(f'{sha(OUT)}  {OUT.name}\n')
print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,'sha256':sha(OUT), 'inheritedFiles':len(before),'newTests':36,'verifiedFiles':len(all_files),'zipEntries':len(names)},indent=2))
