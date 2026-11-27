#!/usr/bin/env python3
"""AETHER-254-RS: bounded Linux pidfd child-exit observation, no authority grant."""
import argparse
import hashlib
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "AETHER-254/pidfd-exit-v1"
HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "external_custody_authenticated": False,
        "live_os_exit_authenticated_externally": False}
CHILD_SCRIPT = "import os,sys; sys.stdin.buffer.read(1); os._exit(7)"

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def parse_proc_stat(raw):
    """Parse Linux /proc/pid/stat despite embedded ')' and spaces in comm."""
    if not isinstance(raw, str) or len(raw) > 8192:
        raise ValueError("STAT_TEXT_INVALID")
    left = raw.find("(")
    right = raw.rfind(")")
    if left <= 0 or right <= left:
        raise ValueError("STAT_FORMAT_INVALID")
    pid = int(raw[:left].strip())
    fields = raw[right + 1:].strip().split()
    if len(fields) < 20:
        raise ValueError("STAT_FIELDS_MISSING")
    start_ticks = int(fields[19])  # field 22; fields begin at field 3
    if pid <= 0 or start_ticks < 0:
        raise ValueError("STAT_ID_INVALID")
    return {"pid": pid, "start_ticks": start_ticks}

def transcript_digest(record):
    return hashlib.sha256(canonical(record)).hexdigest()

def sealed_record(observation):
    record = {"schema": SCHEMA, "observation": observation, **HOLD}
    record["transcript_sha256"] = transcript_digest(record)
    return record

def review(record):
    reasons = []
    if not isinstance(record, dict) or set(record) != {
        "schema", "observation", "transcript_sha256",
        *HOLD.keys()}:
        return {"verdict": "REJECT_OR_UNVERIFIED",
                "reasons": ["RECORD_SCHEMA_INVALID"], **HOLD}
    if record["schema"] != SCHEMA:
        reasons.append("VERSION_INVALID")
    if any(record[k] != expected for k, expected in HOLD.items()):
        reasons.append("AUTHORITY_FIELD_TAMPER")
    obs = record["observation"]
    required = {"pid", "start_ticks", "boot_id", "namespace_inode",
                "stat_sha256", "pidfd_readable", "waitid_pid",
                "waitid_code", "waitid_status", "wait_returncode",
                "elapsed_ms", "child_script_sha256"}
    if not isinstance(obs, dict) or set(obs) != required:
        reasons.append("OBSERVATION_SCHEMA_INVALID")
    else:
        if type(obs["pid"]) is not int or obs["pid"] <= 0:
            reasons.append("PID_INVALID")
        if type(obs["start_ticks"]) is not int or obs["start_ticks"] < 0:
            reasons.append("START_TICKS_INVALID")
        if obs["pidfd_readable"] is not True:
            reasons.append("PIDFD_NOT_READABLE")
        if obs["waitid_pid"] != obs["pid"]:
            reasons.append("WAITID_PID_MISMATCH")
        if obs["waitid_code"] != getattr(os, "CLD_EXITED", 1):
            reasons.append("WAITID_NOT_NORMAL_EXIT")
        if obs["waitid_status"] != 7 or obs["wait_returncode"] != 7:
            reasons.append("WAIT_STATUS_MISMATCH")
        if obs["child_script_sha256"] != hashlib.sha256(CHILD_SCRIPT.encode()).hexdigest():
            reasons.append("CHILD_SCRIPT_MISMATCH")
        if type(obs["elapsed_ms"]) is not int or obs["elapsed_ms"] < 0 or obs["elapsed_ms"] > 3000:
            reasons.append("ELAPSED_INVALID")
    expected = transcript_digest({k:v for k,v in record.items() if k != "transcript_sha256"})
    if record["transcript_sha256"] != expected:
        reasons.append("TRANSCRIPT_DIGEST_MISMATCH")
    reasons += ["CHILD_PROCESS_EXIT_IS_NOT_LOCK_RECLAMATION_AUTHORITY",
                "EXTERNAL_WITNESS_AND_KERNEL_CUSTODY_UNVERIFIED"]
    return {"verdict": "REJECT_OR_UNVERIFIED",
            "reasons": sorted(set(reasons)), **HOLD}

def observe():
    """Launch only fixed benign child. No shell, arbitrary command, signals or locks."""
    if sys.platform != "linux" or not all(hasattr(os, name) for name in ("pidfd_open", "waitid", "P_PIDFD")):
        raise RuntimeError("LINUX_PIDFD_UNAVAILABLE")
    child = subprocess.Popen(
        [sys.executable, "-I", "-c", CHILD_SCRIPT], stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True,
        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
    pidfd = None
    released = False
    t0 = time.monotonic_ns()
    try:
        raw = Path("/proc/{}/stat".format(child.pid)).read_bytes()
        if len(raw) > 8192:
            raise ValueError("PROC_STAT_TOO_LARGE")
        identity = parse_proc_stat(raw.decode("utf-8"))
        if identity["pid"] != child.pid:
            raise ValueError("PROCESS_IDENTITY_MISMATCH")
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        netns = Path("/proc/{}/ns/net".format(child.pid)).stat().st_ino
        pidfd = os.pidfd_open(child.pid, 0)
        # Child cannot exit until stdin receives a byte or EOF.
        child.stdin.write(b"x")
        child.stdin.close()
        released = True
        poller = select.poll()
        poller.register(pidfd, select.POLLIN)
        events = poller.poll(3000)
        if not events or not (events[0][1] & select.POLLIN):
            raise TimeoutError("PIDFD_NOT_READY")
        result = os.waitid(os.P_PIDFD, pidfd, os.WEXITED | os.WNOWAIT)
        returncode = child.wait(timeout=1)
        elapsed = (time.monotonic_ns() - t0) // 1000000
        observation = {"pid": child.pid, "start_ticks": identity["start_ticks"],
                       "boot_id": boot, "namespace_inode": netns,
                       "stat_sha256": hashlib.sha256(raw).hexdigest(),
                       "pidfd_readable": True, "waitid_pid": result.si_pid,
                       "waitid_code": result.si_code, "waitid_status": result.si_status,
                       "wait_returncode": returncode, "elapsed_ms": elapsed,
                       "child_script_sha256": hashlib.sha256(CHILD_SCRIPT.encode()).hexdigest()}
        return sealed_record(observation)
    finally:
        if pidfd is not None:
            os.close(pidfd)
        if not released and child.stdin is not None:
            child.stdin.close()  # EOF releases only our fixed test child.
        try:
            child.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass  # Never kill or signal a process.

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    p.add_argument("--review", type=Path)
    args = p.parse_args()
    try:
        if args.review:
            raw = args.review.read_bytes()
            if len(raw) > 131072:
                raise ValueError("RECORD_TOO_LARGE")
            output = review(json.loads(raw))
        else:
            output = observe()
    except (OSError, ValueError, TypeError, RuntimeError, TimeoutError,
            subprocess.TimeoutExpired) as error:
        output = {"verdict": "REJECT_OR_UNVERIFIED",
                  "reasons": ["PIDFD_OBSERVATION_FAILED:" + type(error).__name__], **HOLD}
    rendered = json.dumps(output, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1  # Successful observation is never operational approval.

if __name__ == "__main__":
    raise SystemExit(main())
