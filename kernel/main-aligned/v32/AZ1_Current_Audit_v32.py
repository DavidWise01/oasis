#!/usr/bin/env python3
"""AZ1 current-engine diagnostic audit v32.

Usage:
    python AZ1_Current_Audit_v32.py [AZ1_DIRECTORY]

The target directory must contain the current _tick.py and, optionally,
az1-chronicle.json. The audit is intentionally strict: the current terminal
frontier accumulator causes a nonzero verdict until that source policy is fixed.
"""
import datetime, importlib.util, json, pathlib, sys

HERE = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path.cwd()
tick_path = HERE / "_tick.py"
if not tick_path.exists():
    raise SystemExit("missing target: %s" % tick_path)

spec=importlib.util.spec_from_file_location("az1_tick_audit", tick_path)
_tick=importlib.util.module_from_spec(spec); spec.loader.exec_module(_tick)

def simulate(n, start=datetime.date(2026,6,29)):
    ch=_tick.fresh(); out=[]
    for i in range(n):
        out.append(_tick.run_research(ch,(start+datetime.timedelta(days=i)).isoformat()))
    return ch,out

checks=[]
a,ea=simulate(200); b,eb=simulate(200)
checks.append(("200-day run", len(ea)==200))
checks.append(("frontier monotone", all(ea[i]["level"] >= (ea[i-1]["level"] if i else 0) for i in range(len(ea)))))
checks.append(("deterministic", [(x["kind"],x["level"],x["knowledge"],x["text"]) for x in ea] ==
                                [(x["kind"],x["level"],x["knowledge"],x["text"]) for x in eb]))

chron_path=HERE/"az1-chronicle.json"
if chron_path.exists():
    stored=json.loads(chron_path.read_text(encoding="utf-8"))
    ch=_tick.fresh(); mismatch=False
    for exp in reversed(stored.get("log",[])):
        got=_tick.run_research(ch,exp["date"])
        keys=["date","day","kind","text","level","frontier","era","knowledge"]
        if any(got.get(k)!=exp.get(k) for k in keys):
            mismatch=True; break
    checks.append(("uploaded chronicle exact replay", not mismatch))

ch=_tick.fresh(); start=datetime.date(2026,6,29); violation=None
for i in range(30000):
    _tick.run_research(ch,(start+datetime.timedelta(days=i)).isoformat())
    th=1.0+ch["level"]*0.35
    if not (0 <= ch["research"] < th + 1e-9):
        violation=(i+1,ch["level"],ch["research"],th)
        break
checks.append(("terminal research remains bounded", violation is None))

for name,ok in checks:
    print(("[PASS] " if ok else "[FAIL] ")+name)
if violation:
    print("       first violation: day %d level %d research %.3f threshold %.3f" % violation)
bad=[x for x in checks if not x[1]]
print("VERDICT:", "%d/%d passed" % (len(checks)-len(bad),len(checks)))
raise SystemExit(1 if bad else 0)
