#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile,os,datetime
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PARENT=ROOT/'sheet156'
ARCHIVE=ROOT/'SHEET157-certified-witness-catchup.zip'
SHA=ROOT/(ARCHIVE.name+'.sha256.txt')

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while True:
   b=f.read(1<<20)
   if not b: break
   h.update(b)
 return h.hexdigest()

before={str(p.relative_to(PARENT)):digest(p) for p in PARENT.rglob('*') if p.is_file()}
after={str(p.relative_to(HERE/'baseline156')):digest(p) for p in (HERE/'baseline156').rglob('*') if p.is_file()}
assert before==after, 'FROZEN S156 PARENT WAS NOT PRESERVED EXACTLY'
assert (HERE/'new-test-report.json').exists()
new=json.loads((HERE/'new-test-report.json').read_text())
assert new['passed'] is True and new['checks']==41, 'S157 new fault gate incomplete'
assert (HERE/'browser-test.log').read_text().count('PASS')==10
combined_exit=int((HERE/'combined-exit.txt').read_text().strip()) if (HERE/'combined-exit.txt').exists() else None
source_files=['witness157.js','catchup-verify157.js','catchup157.js','gate157.js','run-all.sh','browser-check.py','make-release.py']
listing=['# SHEET 157 — Complete New Authored Sources','','The frozen SHEET156 lineage remains in the full ZIP; this listing contains the new SHEET157 implementation and tests.','']
for name in source_files:
 code=(HERE/name).read_text()
 lang='javascript' if name.endswith('.js') else ('python' if name.endswith('.py') else 'bash')
 listing.extend([f'## {name}','',f'```{lang}',code.rstrip(),'```',''])
(HERE/'SOURCE-ALL157.md').write_text('\n'.join(listing))
receipt={
 'schema':'oasis.sheet157.release.v1','sheet':157,'previous':156,
 'title':'Quorum-Certified Minority Witness Catch-Up',
 'previousFilesPreserved':len(before),'previousBytesIdentical':True,
 'newGate':{'passed':True,'checks':41,'exit':0},
 'inheritedBaseline':{'lastPriorReleaseCombinedChecks':1519,'latestFullRerunExit':combined_exit,'latestFullRerunStatus':'TIMEOUT: incomplete inherited chain' if combined_exit is None else 'EXIT '+str(combined_exit)},
 'chromium':{'scenarios':8,'jsonExport':True,'screenshot':True},
 'faults':['signed quorum catch-up','prefix protection','conflicting pending quarantine','head replay','tampered export','witness restart','crash after durable install','idempotent retry','loss of two healthy peer attestors'],
 'scope':['one physical host','three TLS witness processes','synthetic Ed25519 finality votes in new gate','full export bounded 256 records'],
 'notes':'Witness catch-up endpoint is explicitly invoked; no unsafe automatic release of conflicting pending votes.'
}
(HERE/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
entries=sorted([p for p in HERE.rglob('*') if p.is_file() and p!=HERE/'SHA256SUMS'])
manifest=''.join(f'{digest(p)}  {p.relative_to(HERE).as_posix()}\n' for p in entries)
(HERE/'SHA256SUMS').write_text(manifest)
entries.append(HERE/'SHA256SUMS')
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as zipf:
 for p in entries:zipf.write(p,arcname='sheet157/'+p.relative_to(HERE).as_posix())
with zipfile.ZipFile(ARCHIVE) as z:
 bad=z.testzip();assert bad is None, f'bad zip member {bad}'
 archived={n[len('sheet157/baseline156/'):]:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('sheet157/baseline156/') and not n.endswith('/')}
 assert archived==before, 'ARCHIVED INHERITED BASELINE MISMATCH'
 for name in ['witness157.js','catchup157.js','catchup-verify157.js','gate157.js','SHA256SUMS']:
  assert 'sheet157/'+name in z.namelist()
SHA.write_text(f'{digest(ARCHIVE)}  {ARCHIVE.name}\n')
print(json.dumps({'zip':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':digest(ARCHIVE),'verifiedParentFiles':len(before),'newChecks':41,'combinedExit':combined_exit},indent=2))
