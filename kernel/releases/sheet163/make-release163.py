from pathlib import Path
import json,hashlib,zipfile,datetime,os,stat,sys
ROOT=Path(__file__).resolve().parent
PARENT=ROOT/'baseline162'
ARCHIVE=ROOT.parent/'SHEET163-parallel-merkle-ordered-commit.zip'
SHA=ARCHIVE.with_name(ARCHIVE.name+'.sha256.txt')
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for part in iter(lambda:f.read(1<<20),b''):h.update(part)
 return h.hexdigest()
def relhashes(folder):return {p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}
prior_zip=ROOT.parent/'SHEET162-batched-mtls-recovery.zip'
with zipfile.ZipFile(prior_zip) as published:
 before={name[len('sheet162/'):]:hashlib.sha256(published.read(name)).hexdigest() for name in published.namelist() if name.startswith('sheet162/') and not name.endswith('/')}
after=relhashes(PARENT)
assert before==after,(len(before),len(after),next(iter((before.items() ^ after.items())),None))
bench=json.loads((ROOT/'benchmark163.json').read_text())
assert bench['newChecks']==45
newlog=(ROOT/'full-new-gate.log').read_text();assert 'SHEET163 GATE 45/45 PASS' in newlog
assert 'SHEET162 UNIT 19/19 PASS' in (ROOT/'inherited162-unit.log').read_text()
assert 'SHEET162 GATE 24/24 PASS' in (ROOT/'inherited162-network.log').read_text()
assert 'SHEET163 CHROMIUM 11/11 PASS' in (ROOT/'browser-test.log').read_text()
manifest={}
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f.name not in {'SHA256SUMS','release-receipt.json','release-build.log'}:manifest[f.relative_to(ROOT).as_posix()]=digest(f)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name,sha in manifest.items()))
receipt={'schema':'oasis.sheet163.release.v1','sheet':163,'parent':162,'status':'0e / new PASS','tests':{'new':45,'newExit':0,'sheet162Unit':19,'sheet162Network':24,'chromiumInteractions':11,'fullHistoricalRun':'NOT RUN'},'benchmarks':bench['conditions'],'batchComparison':bench['batchComparison'],'preservedParentFiles':len(before),'preservedParentSha256Verified':True,'archive':ARCHIVE.name,'verificationLimit':'One physical host, TLS socket counters are not verified handshakes, repeat-limited randomized A/B, no global consensus', 'releaseUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(ROOT/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted((x for x in ROOT.rglob('*') if x.is_file()),key=lambda p:p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for file in files:
  rel='sheet163/'+file.relative_to(ROOT).as_posix()
  z.write(file,rel)
with zipfile.ZipFile(ARCHIVE) as z:
 assert z.testzip() is None
 names=set(z.namelist())
 assert len(names)==len(files)
 for rel,originalHash in before.items():
  name='sheet163/baseline162/'+rel
  assert name in names,name
  assert hashlib.sha256(z.read(name)).hexdigest()==originalHash,rel
 for needed in ['sheet163/pipeline163.js','sheet163/node163.js','sheet163/gate163.js','sheet163/KERNEL-ASCII.txt','sheet163/BENCHMARK-REPORT.md','sheet163/SHA256SUMS','sheet163/release-receipt.json','sheet163/index.html']:
  assert needed in names,needed
value=digest(ARCHIVE);SHA.write_text(f'{value}  {ARCHIVE.name}\n')
print(json.dumps({'archive':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':value,'files':len(files),'inheritedFiles':len(before),'newChecks':45,'inheritedTests':43,'chromiumChecks':11},indent=2))
