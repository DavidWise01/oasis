#!/usr/bin/env python3
"""ANNY: interrupt TWO unresolved IndexedDB transactions in dedicated Chromium processes.

Each scenario initializes a valid Harvester RELEASE_PENDING transfer in an isolated
IndexedDB store. A second readwrite transaction writes either the receiver ledger
record or journal CONFIRMED record and keeps issuing audit writes in that SAME tx.
A controller observes its pending progress and sends SIGKILL to the dedicated
Chromium process group. After a new process opens the SAME browser profile,
independent ledger reads must show the original baseline, not a partial write.

This is browser PROCESS termination while transaction is pending. It is not an
electrical power-cut or external exactly-once delivery certification.
"""
from __future__ import annotations
import functools
import http.server
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time
import traceback
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
PAGE_PATH="/apps/anny-neon/midflight-gate.html"
MODES=("RECEIVER_WRITE","JOURNAL_CONFIRM")
EXPECTED={
  "RECEIVER_WRITE":("RELEASE_PENDING",0,"PENDING_NO_EFFECT",True),
  "JOURNAL_CONFIRM":("RELEASE_PENDING",1,"PENDING_RECEIVER_ACCEPTED",False),
}
ARTIFACTS=Path(os.environ.get("ANNY_BROWSER_ARTIFACTS",
   str(ROOT/"anny-midflight-evidence")))

class QuietHandler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*_args):
  pass

def serve():
 server=http.server.ThreadingHTTPServer(
  ("127.0.0.1",0),functools.partial(QuietHandler,directory=str(ROOT)))
 t=threading.Thread(target=server.serve_forever,daemon=True)
 t.start()
 return server,t

def record(ok,name,report,detail=None):
 report["checks"].append({"pass":bool(ok),"name":name,"detail":detail})
 if not ok:raise AssertionError(name+" : "+str(detail))

def kill_group(process):
 if process.poll() is None:
  os.killpg(process.pid,signal.SIGKILL)
 try:
  process.wait(timeout=15)
 except subprocess.TimeoutExpired:
  os.killpg(process.pid,signal.SIGKILL)
  process.wait(timeout=15)

def launch(playwright,profile):
 binary=os.environ.get("ANNY_CHROMIUM_EXECUTABLE") or playwright.chromium.executable_path
 if not Path(binary).exists():raise RuntimeError("Chromium executable missing: "+binary)
 proc=subprocess.Popen([
  binary,"--headless=new","--no-sandbox","--disable-gpu",
  "--disable-dev-shm-usage","--disable-extensions",
  "--no-first-run","--no-default-browser-check",
  "--disable-background-networking","--remote-debugging-port=0",
  "--user-data-dir="+str(profile),"about:blank"
 ],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
 try:
  portfile=profile/"DevToolsActivePort"
  for _ in range(200):
   if portfile.exists():
    lines=portfile.read_text().splitlines()
    if lines and lines[0].isdigit():
     browser=playwright.chromium.connect_over_cdp(
      "http://127.0.0.1:"+lines[0],timeout=15000)
     return proc,browser
   if proc.poll() is not None:raise RuntimeError("Chromium exited early")
   time.sleep(0.1)
  raise TimeoutError("DevToolsActivePort timeout")
 except Exception:
  kill_group(proc)
  raise

def open_page(browser,url):
 ctx=browser.contexts[0]
 page=ctx.pages[0] if ctx.pages else ctx.new_page()
 errors=[]
 page.on("pageerror",lambda e:errors.append(str(e)))
 page.goto(url,wait_until="domcontentloaded",timeout=30000)
 page.wait_for_function("() => !!window.annyMidflightLab",timeout=15000)
 return page,errors

def invoke(page,method,mode,token=None,*params):
 if method not in ("initialize","arm","progress","inspect",
                   "reconcile","continue","duplicate","forged","abort"):
  raise ValueError("Disallowed lab operation: "+method)
 args=[mode] if method=="initialize" else [mode,token,*params]
 return page.evaluate("""async ({method,args}) => {
    return await window.annyMidflightLab[method](...args);
 }""",{"method":method,"args":args})

def run_mode(playwright,url,mode):
 stage,base_effect,base_class,replay=EXPECTED[mode]
 result={"mode":mode,"status":"RUNNING","checks":[],"kill_stage":"TX_PENDING"}
 with tempfile.TemporaryDirectory(prefix="anny-unresolved-"+mode.lower()+"-") as d:
  profile=Path(d)
  proc=None
  try:
   proc,browser=launch(playwright,profile)
   page,errors=open_page(browser,url)
   baseline=invoke(page,"initialize",mode)
   token=baseline["token"]
   result["externalWitness"]=token
   result["digest"]=baseline["baseline"]["digest"]
   record(baseline["baseline"]["classification"]==base_class,
     "Valid independently committed baseline",result,baseline["baseline"])
   record(not errors,"No pre-kill JavaScript errors",result,errors)
   armed=invoke(page,"arm",mode,token)
   record(armed["active"] and armed["status"]=="QUEUED",
     "Dedicated IDB readwrite transaction opened",result,armed)
   page.wait_for_function("""({mode,token}) => {
    const s=window.annyMidflightLab.progress(mode,token);
    return s.status==="RUNNING" && s.progress>=5
      && !s.completed && !s.aborted;
   }""",arg={"mode":mode,"token":token},timeout=15000)
   progress=invoke(page,"progress",mode,token)
   record(progress["status"]=="RUNNING" and progress["progress"]>=5
     and not progress["completed"] and not progress["aborted"],
     "SIGKILL sampling captured unresolved transaction",result,progress)
   result["progressAtKill"]=progress["progress"]
   # Do not call context.close(), tx.abort(), or page.close().
   kill_group(proc)
   record(proc.returncode==-signal.SIGKILL,
     "Chromium killed by SIGKILL",result,proc.returncode)
   proc=None
   portfile=profile/"DevToolsActivePort"
   if portfile.exists():portfile.unlink() # rendezvous file, not durable data
   proc,browser=launch(playwright,profile)
   page,errors=open_page(browser,url)
   # An outside-browser Python witness supplies token. No localStorage dependency.
   after=invoke(page,"reconcile",mode,token)
   record(after["row"] is not None and after["row"]["state"]==stage,
     "Original journal phase survived unresolved transaction",result,
     after["row"]["state"] if after["row"] else None)
   record(after["classification"]==base_class and after["effectCount"]==base_effect,
     "No partial receiver/journal mutation became visible",result,
     {"classification":after["classification"],"effects":after["effectCount"]})
   record(after["row"]["digest"]==result["digest"] and after["token"]==token,
     "Witness identity and digest retained",result)
   record(after["view"]["slots"][17]["value"]=="HELD",
     "Unresolved transaction never authorized Violet VERIFIED",result)
   record(not errors,"No restart JavaScript errors",result,errors)
   completed=invoke(page,"continue",mode,token)
   record(completed["status"]=="RECONCILED" and completed["replayed"]==replay,
     "Explicit recovery uses independent receipt-first rule",result,
     {"status":completed["status"],"replayed":completed["replayed"]})
   final=invoke(page,"inspect",mode,token)
   record(final["classification"]=="CONFIRMED_VERIFIED" and
     final["effectCount"]==1 and final["view"]["slots"][17]["value"]=="VERIFIED",
     "After explicit continuation both receipts agree",result,
     {"classification":final["classification"],"effects":final["effectCount"]})
   duplicate=invoke(page,"duplicate",mode,token,5)
   record(duplicate["allFulfilled"] and duplicate["effectCount"]==1 and
     duplicate["classification"]=="CONFIRMED_VERIFIED",
     "Five concurrent repeats preserve one ledger effect",result,duplicate)
   forged=invoke(page,"forged",mode,token)
   record(forged["violet"]=="AGREEMENT FAILED",
     "Forged receiver receipt is never VERIFIED",result,forged)
   page.screenshot(path=str(ARTIFACTS/
     ("midflight-"+mode.lower()+"-verified.png")),full_page=True)
   result["status"]="PASS"
  except Exception as e:
   result["status"]="FAIL"
   result["error"]=str(e)
   result["traceback"]=traceback.format_exc()
  finally:
   if proc is not None:kill_group(proc)
 result["passed"]=sum(1 for c in result["checks"] if c["pass"])
 result["total"]=len(result["checks"])
 (ARTIFACTS/("midflight-"+mode.lower()+".json")).write_text(
   json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 return result

def main():
 ARTIFACTS.mkdir(parents=True,exist_ok=True)
 server,thread=serve()
 url="http://127.0.0.1:"+str(server.server_port)+PAGE_PATH
 summary={
  "suite":"ANNY unresolved IndexedDB SIGKILL gate",
  "browserScope":"Chromium SIGKILL with request-chain readwrite TX unresolved",
  "notProven":["OS power removal","mid-disk-write corruption",
   "distributed exactly-once external side effects","live deployed Pages origin"],
  "results":[],"status":"RUNNING"
 }
 try:
  with sync_playwright() as p:
   for mode in MODES:
    result=run_mode(p,url,mode)
    summary["results"].append({
      "mode":mode,"status":result["status"],
      "passed":result["passed"],"total":result["total"],
      "error":result.get("error")})
    print(json.dumps(summary["results"][-1]),flush=True)
  summary["status"]="PASS" if len(summary["results"])==2 and all(
   x["status"]=="PASS" for x in summary["results"]) else "FAIL"
 except Exception as e:
  summary["status"]="FAIL"
  summary["error"]=str(e)
  summary["traceback"]=traceback.format_exc()
 finally:
  server.shutdown()
  thread.join(timeout=5)
  summary["finishedUnix"]=int(time.time())
  (ARTIFACTS/"midflight-summary.json").write_text(
   json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
  print(json.dumps({"status":summary["status"],
     "scenarios":len(summary["results"]),"report":str(ARTIFACTS/"midflight-summary.json")}))
 return 0 if summary["status"]=="PASS" else 1

if __name__=="__main__":
 raise SystemExit(main())
