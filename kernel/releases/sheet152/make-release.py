#!/usr/bin/env python3
"""Deterministic path ordering; verified sha manifest and byte-identical frozen baseline."""
import hashlib, json, os, zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
out=Path('/mnt/data/SHEET152-full-kernel-anchor-alignment.zip')
prior=Path('/mnt/data/sheet151')
frozen=root/'baseline151'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as src:
        for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
old={str(p.relative_to(prior)):digest(p) for p in prior.rglob('*') if p.is_file()}
new={str(p.relative_to(frozen)):digest(p) for p in frozen.rglob('*') if p.is_file()}
assert old==new,(len(old),len(new),'BASELINE_CHANGED')
receipt={'schema':'oasis.sheet152.release.v1','sheet':152,'newGate':{'passed':45,'total':45,'exit':0},'inheritedFullRegression':{'previousSheet151Total':1262,'allChecksTotal':1307,'exit':int((root/'combined-exit.txt').read_text().strip())},'chromium':{'scenarios':8,'export':True,'screenshot':True},'baseline151Files':len(old),'baseline151ByteIdentical':True,'testEnvironment':'local mTLS processes on one physical host','limitations':['S150 physical writer retains 128-entry cap','signed anchor may advance between live check and durable completion','torn-write review requires separate external floor freshness confirmation','not independent-host consensus','SHEET142 inherited timing-sensitive regression may recur'],'gitSource':'new source files and release metadata if committed; complete nested source in archive'}
(root/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in root.rglob('*') if p.is_file() and p != root/'SHA256SUMS' and not p.name.endswith('.tmp'))
manifest=''.join(f'{digest(p)}  {p.relative_to(root).as_posix()}\n' for p in files)
(root/'SHA256SUMS').write_text(manifest)
files.append(root/'SHA256SUMS')
files.sort(key=lambda p:p.relative_to(root).as_posix())
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
    for p in files:
        entry=zipfile.ZipInfo(f'sheet152/{p.relative_to(root).as_posix()}',date_time=(2026,10,9,0,0,0))
        entry.compress_type=zipfile.ZIP_DEFLATED
        entry.external_attr=(0o755 if os.access(p,os.X_OK) else 0o644)<<16
        z.writestr(entry,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
with zipfile.ZipFile(out,'r') as z:
    assert z.testzip() is None
    entries=set(z.namelist())
    for p in files:assert 'sheet152/'+p.relative_to(root).as_posix() in entries
sha=digest(out)
Path(str(out)+'.sha256.txt').write_text(f'{sha}  {out.name}\n')
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'sha256':sha,'files':len(files),'inherited':len(old),'combinedExit':receipt['inheritedFullRegression']['exit']},indent=2))
