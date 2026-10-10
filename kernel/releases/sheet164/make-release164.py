from pathlib import Path
import hashlib,zipfile,json,sys
B=Path(__file__).resolve().parent
PRIOR=Path('/mnt/data/SHEET163-parallel-merkle-ordered-commit.zip')
ZIP=B.parent/'SHEET164-factorial-tuning.zip'
SHA=B.parent/'SHEET164-factorial-tuning.zip.sha256.txt'
def h(x):return hashlib.sha256(x).hexdigest()
# Confirm identical bytes with independently sealed predecessor, not mutable workspace state.
with zipfile.ZipFile(PRIOR) as prior:
    names=[n for n in prior.namelist() if not n.endswith('/')]
    for n in names:
        rel=n[len('sheet163/'):]
        f=B/'baseline163'/rel
        if not f.is_file():raise RuntimeError('Inherited file missing: '+n)
        if h(f.read_bytes())!=h(prior.read(n)):raise RuntimeError('Inherited byte mismatch: '+n)
if len(names)!=753:raise RuntimeError('Unexpected inherited file count')
needed=['pipeline164.js','transport164.js','gate164.js','benchmark164.json','gate164.log','index.html','README.md','BENCHMARK-REPORT.md','KERNEL-ASCII.txt','browser-check.log','audit/inherited163.log','audit/inherited163.exit','SOURCE-ALL164.md']
for n in needed:
    if not (B/n).is_file():raise RuntimeError('Missing release file: '+n)
if 'SHEET164 GATE 68/68 PASS' not in (B/'gate164.log').read_text():raise RuntimeError('New gate failed')
if (B/'audit/inherited163.exit').read_text().strip()!='0':raise RuntimeError('Inherited gate failed')
if 'SHEET163 GATE 45/45 PASS' not in (B/'audit/inherited163.log').read_text():raise RuntimeError('Inherited gate missing pass')
if 'SHEET164 CHROMIUM 12/12 PASS' not in (B/'browser-check.log').read_text():raise RuntimeError('Chromium check failed')
meta={'schema':'oasis.sheet164.release.v1','sheet':164,'parent':163,'status':'0e / PASS','newTests':68,'inherited163Tests':45,'chromiumChecks':12,'inheritedFileCount':len(names),'benchmarkFactorialRuns':16,'holdoutRuns':1,'crashRuns':1,'sourceRecords':384,'factorialRecoveredPerRun':128,'tlsReuseComparison':'certificate pinning active in both policies','fullHistoricalChain':'not run; only S163 gate isolated','benchmarkReport':'BENCHMARK-REPORT.md'}
(B/'release-receipt.json').write_text(json.dumps(meta,indent=2)+'\n')
files=sorted(p for p in B.rglob('*') if p.is_file() and not p.name.startswith('.'))
files=[p for p in files if p.name not in ('SHA256SUMS','release-receipt.json')]
manifest='\n'.join(f'{h(p.read_bytes())}  {p.relative_to(B)}' for p in files)+'\n'
(B/'SHA256SUMS').write_text(manifest)
files=sorted(p for p in B.rglob('*') if p.is_file() and not p.name.startswith('.'))
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as out:
    for p in files:out.write(p,'sheet164/'+str(p.relative_to(B)))
with zipfile.ZipFile(ZIP,'r') as z:
    if z.testzip() is not None:raise RuntimeError('Bad ZIP CRC')
    if len(z.namelist())!=len(files):raise RuntimeError('ZIP omissions')
    for n in names:
        new='sheet164/baseline163/'+n[len('sheet163/'):]
        if z.read(new)!=((B/'baseline163'/n[len('sheet163/'):]).read_bytes()):raise RuntimeError('Stored baseline mismatch')
    for p in files:
        if h(z.read('sheet164/'+str(p.relative_to(B))))!=h(p.read_bytes()):raise RuntimeError('New file mismatch '+str(p))
SHA.write_text(f'{h(ZIP.read_bytes())}  {ZIP.name}\n')
print(json.dumps({'archive':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':h(ZIP.read_bytes()),'inheritedFilesVerified':len(names),'newTests':68,'inheritedGate':45,'chromiumChecks':12,'packagedFiles':len(files)},indent=2))
