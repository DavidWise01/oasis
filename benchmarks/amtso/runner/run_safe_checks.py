#!/usr/bin/env python3
import hashlib, json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
EVIDENCE = ROOT / "evidence"
EICAR = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'

def sha256(b): return hashlib.sha256(b).hexdigest()

def scan_bytes(data, depth=0):
    findings=[]
    if EICAR in data:
        findings.append("EICAR_CANONICAL")
    return findings

def scan_file(path, depth=0):
    findings=[]
    data=path.read_bytes()
    findings.extend(scan_bytes(data, depth))
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                b=z.read(name)
                findings.extend(scan_bytes(b, depth+1))
                if name.lower().endswith(".zip"):
                    import io
                    bio=io.BytesIO(b)
                    if zipfile.is_zipfile(bio):
                        with zipfile.ZipFile(bio) as z2:
                            for name2 in z2.namelist():
                                findings.extend(scan_bytes(z2.read(name2), depth+2))
    return sorted(set(findings))

results=[]
for p in sorted(SAMPLES.iterdir()):
    if not p.is_file(): continue
    findings=scan_file(p)
    verdict="1e" if findings else "0e"
    if "EICAR_CANONICAL" in findings:
        verdict="xe"
    results.append({
        "file":p.name,
        "sha256":sha256(p.read_bytes()),
        "findings":findings,
        "verdict":verdict,
        "executed":False,
        "network_used":False,
        "write_scope":"evidence-only"
    })

summary={
    "lab":"JULIET_MANDEL_AMTSO_VM_00",
    "results":results,
    "status":"PASS" if (
        all(r["verdict"]=="xe" for r in results if r["file"].startswith("eicar"))
        and all(r["verdict"]=="0e" for r in results if r["file"].startswith("benign"))
    ) else "FAIL"
}
EVIDENCE.mkdir(exist_ok=True)
(EVIDENCE/"results.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
