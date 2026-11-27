#!/usr/bin/env python3
"""AETHER-249-RS: fail-closed Linux network-namespace socket probe harness.

No namespace => no socket attempts. Does not prove independent external custody.
"""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import time

HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "network_isolation_independently_verified": False}
TARGETS = {
    "loopback": ("127.0.0.1", 9),
    "private": ("10.255.255.1", 9),
    "link_local": ("169.254.1.1", 9),
    "metadata": ("169.254.169.254", 80),
}
UNSUPPORTED = ("redirect", "dns_rebind")

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def ns_inode():
    return os.stat("/proc/self/ns/net").st_ino

def isolated(parent_inode, interfaces=None):
    if type(parent_inode) is not int or parent_inode <= 0:
        return False
    if ns_inode() == parent_inode:
        return False
    if interfaces is None:
        interfaces = {p.name for p in pathlib.Path("/sys/class/net").iterdir()}
    # Require an unconfigured namespace: not even a veth is accepted.
    return set(interfaces).issubset({"lo"})

def probe(category, connector=None):
    if category not in TARGETS:
        raise ValueError("UNSUPPORTED_CATEGORY")
    address, port = TARGETS[category]
    start = time.monotonic_ns()
    if connector is None:
        def connector(addr, timeout):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(timeout)
                sock.connect(addr)
                return 0
            except OSError as error:
                return int(error.errno or -1)
            finally:
                sock.close()
    number = connector((address, port), 0.3)
    duration_ms = (time.monotonic_ns() - start) // 1000000
    if type(number) is not int:
        raise ValueError("INVALID_ERRNO")
    # ECONNREFUSED is not proof of an egress block; it may be a live host.
    return {"category": category, "address": address, "port": port,
            "errno": number, "elapsed_ms": duration_ms,
            "outcome": "connection_succeeded" if number == 0 else "socket_failed",
            "denial_attributed_to_network_policy": False}

def worker(parent_inode, connector=None, interfaces=None):
    if not isolated(parent_inode, interfaces):
        return {"state": "HOLD", "reason": "NAMESPACE_ISOLATION_NOT_ESTABLISHED",
                "probes": [], **HOLD}
    results = [probe(name, connector) for name in TARGETS]
    results += [{"category": name, "outcome": "NOT_MEASURED",
                 "reason": "REQUIRES_CONTROLLED_HTTP_OR_DNS_RESOLVER_HARNESS"}
                for name in UNSUPPORTED]
    return {"state": "OBSERVED_BUT_UNQUALIFIED", "probes": results,
            "namespace_differs_from_parent": True,
            "interfaces_limited_to_loopback": True, **HOLD}

def supervise(runner=None, inherited_environment=None):
    if sys.platform != "linux" or not pathlib.Path("/proc/self/ns/net").exists():
        return {"state": "HOLD", "reason": "LINUX_NETNS_REQUIRED", **HOLD}
    if shutil.which("unshare") is None:
        return {"state": "HOLD", "reason": "UNSHARE_UNAVAILABLE", **HOLD}
    command = ["unshare", "--net", "--", sys.executable,
               str(pathlib.Path(__file__).resolve()), "--worker",
               "--parent-inode", str(ns_inode())]
    # Never inherit arbitrary secrets or credential-bearing environment.
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "LANG": "C", "PYTHONUNBUFFERED": "1"}
    if inherited_environment is not None:
        env = inherited_environment
    if runner is None:
        runner = lambda cmd, env: subprocess.run(cmd, env=env, capture_output=True,
                                                 timeout=10, check=False)
    try:
        completed = runner(command, env)
        if completed.returncode != 0:
            return {"state": "HOLD", "reason": "NAMESPACE_LAUNCH_FAILED",
                    "exit_code": completed.returncode, **HOLD}
        if len(completed.stdout) > 65536:
            raise ValueError("WORKER_OUTPUT_TOO_LARGE")
        payload = json.loads(completed.stdout)
        # A child JSON value is evidence, not trusted authority.
        if not isinstance(payload, dict) or payload.get("state") != "OBSERVED_BUT_UNQUALIFIED":
            raise ValueError("WORKER_REJECTED")
        raw_sha = hashlib.sha256(completed.stdout).hexdigest()
        return {"state": "OBSERVED_BUT_UNQUALIFIED", "worker_stdout_sha256": raw_sha,
                "worker_stdout_bytes": len(completed.stdout), "worker": payload, **HOLD}
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        return {"state": "HOLD", "reason": "WORKER_OUTPUT_UNAVAILABLE_OR_INVALID", **HOLD}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--parent-inode", type=int)
    parser.add_argument("--out", type=pathlib.Path)
    args = parser.parse_args()
    try:
        if args.worker:
            result = worker(args.parent_inode)
        else:
            result = supervise()
    except (OSError, ValueError, TypeError):
        result = {"state": "HOLD", "reason": "PROBE_ERROR", **HOLD}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    # No path to runtime or physical ACT approval.
    return 1 if not args.worker else (0 if result.get("state") == "OBSERVED_BUT_UNQUALIFIED" else 1)

if __name__ == "__main__":
    raise SystemExit(main())
