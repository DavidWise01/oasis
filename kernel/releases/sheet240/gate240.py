"""S240 dual-branch gate; execute from release ZIP with S239 and S238 dependencies."""
import pathlib,sys,subprocess,re
root=pathlib.Path(__file__).resolve().parent
checks=0
def require(ok,label):
 global checks
 if not ok:raise AssertionError(label)
 checks+=1
 print(f"PASS {checks:02d} {label}",flush=True)
def run(name,count,phrases):
 p=subprocess.run([sys.executable,str(root/name)],cwd=root,capture_output=True,text=True,timeout=100)
 (root/("run-"+name+".log")).write_text(p.stdout+"\nSTDERR:\n"+p.stderr)
 require(p.returncode==0,name+" subprocess success")
 require(len(re.findall(r"^PASS \d\d ",p.stdout,re.M))==count,name+" pass count")
 require("0e / PASS" in p.stdout,name+" completed")
 for phrase,label in phrases:require(phrase in p.stdout,name+" "+label)
 return count
a=run("gate239.py",17,[("no committed record was fabricated","no fabricated commit"),("broker rejects even correctly signed approval","denies uncommitted repair"),("all retries preserve exact original WAL","immutable quarantine")])
b=run("gate238.py",36,[("original S176 Node produced first WAL commit","real writer"),("lost floor ACK re-read identically","durable floor ACK"),("post-restart signed repair replay rejected","no duplicate recovery"),("original WAL committed prefix append-only","WAL prefix preserved")])
require(a+b==53,"53 inherited checks")
print(f"0e / PASS — {checks}/{checks} S240 orchestration; {a+b} inherited assertions")
