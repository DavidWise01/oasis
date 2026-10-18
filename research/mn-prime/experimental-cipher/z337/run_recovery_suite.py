"""Z337: source-integrity and recovery regression gate. Run from repository checkout."""
import hashlib,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=ROOT/"research/mn-prime/experimental-cipher"
EXPECTED={
328:("3a7629b27bd2aca0baecf10f4c06bf044dae8fda",20),
329:("f8660f47fe59d7840a2aeb938542dfd330e045dd",20),
330:("f2f5b358811af574823a0c7c1cbba57ce0238f92",20),
331:("f8d1c07beb7fcac0faf4299b1743e8c018419b15",20),
332:("fbadfd2d27ced597b0b5d96fd661490cfd93c748",15),
333:("c794be8182a7e98360a63173f297d4ff98434afc",20),
}
def blob_sha(data):
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def main():
 total=0
 for z,(expected_sha,n) in EXPECTED.items():
  path=BASE/f"z{z}"/f"test_z{z}.py"
  if not path.is_file():
   print(f"FAIL Z{z}: missing {path}");return 2
  actual=blob_sha(path.read_bytes())
  if actual!=expected_sha:
   print(f"FAIL Z{z}: source mismatch {actual} != {expected_sha}");return 2
  run=subprocess.run([sys.executable,str(path)],cwd=path.parent,text=True,capture_output=True,timeout=60)
  found=re.findall(r"(?m)^(\d+)/(\d+) PASS\s*$",run.stdout)
  if run.returncode or not found or found[-1]!=(str(n),str(n)):
   print(f"FAIL Z{z}: exit {run.returncode}; report {found[-1] if found else None}")
   print(run.stdout[-1000:],run.stderr[-1000:]);return 1
  print(f"PASS Z{z} {n}/{n} source={actual}");total+=n
 print(f"PASS Z337 {total}/{total} verified checks")
 return 0
if __name__=="__main__":raise SystemExit(main())
