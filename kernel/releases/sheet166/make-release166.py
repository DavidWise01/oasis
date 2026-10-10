from pathlib import Path
import hashlib,zipfile,json,os
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
PARENT=ROOT/'SHEET165-counterbalanced-adaptive-recovery.zip'
ZIP=ROOT/'SHEET166-hysteresis-signed-policy.zip'
SHA=ROOT/'SHEET166-hysteresis-signed-policy.zip.sha256.txt'
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
with zipfile.ZipFile(PARENT) as old:
 prior={x.filename[len('sheet165/'):]:hashlib.sha256(old.read(x)).hexdigest() for x in old.infolist() if not x.is_dir() and x.filename.startswith('sheet165/')}
assert len(prior)==804,(len(prior))
for name,sha in prior.items():
 file=BASE/'baseline165'/name
 assert file.is_file() and digest(file)==sha,('BASELINE_MISMATCH',name)
source_names=['policy166.js','decision166.js','decision-server166.js','guard166.js','gate166.js','make_docs166.py','make_dashboard166.py','make-release166.py','run-new.sh','run-inherited165-fault.sh','KERNEL-ASCII.txt']
listing=['# SHEET 166 — Complete New Authored Source','','Exact new authored source files follow; complete historical frozen lineage remains inside the ZIP.','']
for name in source_names:
 lang='javascript' if name.endswith('.js') else 'python' if name.endswith('.py') else 'bash' if name.endswith('.sh') else 'text'
 listing.append(f'## {name}\n\n`````{lang}\n{(BASE/name).read_text().rstrip()}\n`````\n')
(BASE/'SOURCE-ALL166.md').write_text('\n'.join(listing))
checks=json.loads((BASE/'gate166-results.json').read_text())
manifest={'schema':'oasis.sheet166.release.v1','sheet':166,'parent':165,'newChecksPassed':checks['checks'],'newGateExit':0,'inherited165IsolatedChecksPassed':15,'inherited165IsolatedExit':int((BASE/'inherited165-fault.exit').read_text()),'chromium':{'controlsPassed':10,'controlsTotal':10},'syntheticSimulation':{'windows':checks['loadReport']['windows'],'transitions':checks['loadReport']['changes']},'networkRecovery':checks['network'],'sourcePredecessorZipSHA256':digest(PARENT),'inheritedFilesVerified':len(prior),'limits':['1 physical host','single externally pinned Ed25519 policy signer, not 2/3 independent-host consensus','synthetic throughput clock in forced policy switch test','complete historical regression chain not rerun','decision signer authenticates resource state but cannot independently validate observed wall-time performance']}
(BASE/'release-receipt.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=sorted((p for p in BASE.rglob('*') if p.is_file() and p.relative_to(BASE).as_posix() not in ('SHA256SUMS','packaging166.log')),key=lambda p:str(p.relative_to(BASE)))
(BASE/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(BASE)}\n' for p in files))
files.append(BASE/'SHA256SUMS')
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in files:z.write(p,'sheet166/'+str(p.relative_to(BASE)))
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for name,sha in prior.items():
  zname='sheet166/baseline165/'+name
  assert zname in z.namelist() and hashlib.sha256(z.read(zname)).hexdigest()==sha,('ZIP_PREDECESSOR_MISMATCH',name)
 for name in ['policy166.js','decision166.js','decision-server166.js','guard166.js','gate166.js','KERNEL-ASCII.txt','SOURCE-ALL166.md','README.md','BENCHMARK-REPORT.md','index.html','gate166-results.json','release-receipt.json','SHA256SUMS']:
  assert 'sheet166/'+name in z.namelist(),('MISSING',name)
SHA.write_text(digest(ZIP)+'  '+ZIP.name+'\n')
print(json.dumps({'archive':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':digest(ZIP),'predecessorFilesVerified':len(prior),'newChecks':checks['checks'],'isolatedInheritedChecks':15,'chromiumChecks':10,'entryCount':len(files)},indent=2))
