#!/usr/bin/env python3
"""ANNY abrupt Chromium-kill certification for committed IndexedDB transactions.

Uses Playwright CDP and a *dedicated* Chromium process group.
SIGKILL is deliberately sent only to the process group started by this script.
Not a power-loss or interrupt-inside-uncommitted-IDB-transaction test.

Run at repo root after installing Python playwright and Chromium:
    python apps/anny-neon/tests/abrupt_kill_gate.py

JSON report and after-reopen screenshots:
    ${ANNY_BROWSER_ARTIFACTS:-./anny-browser-evidence}/
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

ROOT = Path(__file__).resolve().parents[3]
PAGE = "/apps/anny-neon/crash-gate.html"
STAGES = ("PREPARED", "COMMITTED", "RELEASE_PENDING",
          "RECEIVER_RECORDED", "CONFIRMED")
EXPECT = {
    "PREPARED": ("PREPARED", 0, "HOLD_PRECOMMIT"),
    "COMMITTED": ("COMMITTED", 0, "HOLD_PRECOMMIT"),
    "RELEASE_PENDING": ("RELEASE_PENDING", 0, "PENDING_NO_EFFECT"),
    "RECEIVER_RECORDED": ("RELEASE_PENDING", 1, "PENDING_RECEIVER_ACCEPTED"),
    "CONFIRMED": ("CONFIRMED", 1, "CONFIRMED_VERIFIED"),
}
ARTIFACTS = Path(os.environ.get("ANNY_BROWSER_ARTIFACTS",
                               str(ROOT / "anny-browser-evidence")))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve_localhost():
    instance = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    return instance, thread


def check(ok, text, record, details=None):
    record["checks"].append({"name": text, "pass": bool(ok), "details": details})
    if not ok:
        raise AssertionError(text + " / " + str(details))


def start_chromium(playwright, profile):
    exe = os.environ.get("ANNY_CHROMIUM_EXECUTABLE") or playwright.chromium.executable_path
    if not Path(exe).exists():
        raise RuntimeError("Chromium executable missing: " + exe)
    cmd = [
        exe, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", "--disable-extensions",
        "--no-first-run", "--no-default-browser-check",
        "--disable-background-networking", "--remote-debugging-port=0",
        "--user-data-dir=" + str(profile), "about:blank",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    devtools = Path(profile) / "DevToolsActivePort"
    try:
        for _ in range(200):
            if devtools.exists():
                lines = devtools.read_text(encoding="utf-8").splitlines()
                if lines and lines[0].isdigit():
                    endpoint = "http://127.0.0.1:" + lines[0]
                    browser = playwright.chromium.connect_over_cdp(endpoint, timeout=15000)
                    return proc, browser
            if proc.poll() is not None:
                raise RuntimeError("Chromium exited before CDP became ready: " + str(proc.returncode))
            time.sleep(0.1)
        raise TimeoutError("Chromium DevToolsActivePort unavailable")
    except Exception:
        terminate_group(proc, signal.SIGKILL)
        raise


def terminate_group(proc, sig):
    if proc.poll() is None:
        os.killpg(proc.pid, sig)
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=15)


def open_lab(browser, base_url):
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    js_errors = []
    page.on("pageerror", lambda err: js_errors.append(str(err)))
    page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_function("() => !!window.annyCrashLab", timeout=15000)
    return page, js_errors


def invoke(page, method, stage, *args):
    # Browser method is specified by this test, not by an untrusted page.
    if method not in {"arm", "snapshot", "reconcile", "resume", "duplicate", "forged"}:
        raise ValueError("unknown browser method")
    return page.evaluate(
        """async ({method,stage,args}) => {
          if (!window.annyCrashLab) throw Error('CRASH_LAB_NOT_MOUNTED');
          return await window.annyCrashLab[method](stage,...args);
        }""",
        {"method": method, "stage": stage, "args": list(args)},
    )


def check_snapshot(data, stage, report, label):
    state, expected_count, decision = EXPECT[stage]
    row = data["record"]
    check(bool(row), label + ": journal record present", report)
    check(data["phase"] == state and row["state"] == state,
          label + ": expected journal phase", report, data["phase"])
    check(data["effectCount"] == expected_count,
          label + ": receiver ledger effect count", report, data["effectCount"])
    check(data["decision"] == decision,
          label + ": fail-closed reconciled classification", report, data["decision"])
    check(data["violet"] == ("VERIFIED" if stage == "CONFIRMED" else "HELD"),
          label + ": correct slot 18 status", report, data["violet"])
    has_receipt = data["receipt"] is not None
    check(has_receipt == (stage in ("RECEIVER_RECORDED", "CONFIRMED")),
          label + ": independently reconciled receiver receipt", report)
    journal_receipt = row.get("receipt")
    check(bool(journal_receipt) == (stage == "CONFIRMED"),
          label + ": journal receipt not fabricated", report)
    if journal_receipt:
        check(journal_receipt == data["receipt"],
              label + ": journal/receiver matching receipts", report)


def test_stage(playwright, url, stage):
    report = {"stage": stage, "checks": [], "status": "RUNNING"}
    with tempfile.TemporaryDirectory(prefix="anny-abrupt-" + stage.lower() + "-") as directory:
        profile = Path(directory)
        proc = None
        browser = None
        # One new profile per interrupted phase, preserving only across its kill/reopen.
        try:
            proc, browser = start_chromium(playwright, profile)
            page, errs = open_lab(browser, url)
            before = invoke(page, "arm", stage)
            check_snapshot(before, stage, report, "before SIGKILL")
            check(not errs, "No page JavaScript errors before SIGKILL", report, errs)
            report["transferId"] = before["transferId"]
            report["digest"] = before["record"]["digest"]
            report["before"] = {"decision": before["decision"], "phase": before["phase"],
                                "effectCount": before["effectCount"]}

            # Abrupt termination, no graceful browser/context/page close.
            terminate_group(proc, signal.SIGKILL)
            check(proc.returncode == -signal.SIGKILL,
                  "Dedicated Chromium process received SIGKILL", report, proc.returncode)
            proc = None
            browser = None
            # Chromium clears DevToolsActivePort during startup on new process.
            # Remove any stale rendezvous file only, never IndexedDB or profile data.
            active_file = profile / "DevToolsActivePort"
            if active_file.exists():
                active_file.unlink()
            proc, browser = start_chromium(playwright, profile)
            page, errs = open_lab(browser, url)
            after = invoke(page, "reconcile", stage)
            check_snapshot(after, stage, report, "after new Chromium process")
            check(after["transferId"] == before["transferId"]
                  and after["record"]["digest"] == before["record"]["digest"],
                  "Identity and digest survive process termination", report)
            check(not errs, "No page JavaScript errors after SIGKILL reopen", report, errs)
            report["after"] = {"decision": after["decision"], "phase": after["phase"],
                               "effectCount": after["effectCount"]}

            # The page only *reads* on reopen. Progress requires explicit resume.
            resumed = invoke(page, "resume", stage)
            expected_status = ("HOLD_PRECOMMIT" if stage in ("PREPARED", "COMMITTED")
                               else "ALREADY_CONFIRMED" if stage == "CONFIRMED"
                               else "RECONCILED")
            check(resumed["status"] == expected_status,
                  "Explicit continuation respects stage authorization", report,
                  resumed["status"])
            expect_replay = stage == "RELEASE_PENDING"
            check(resumed["replayed"] == expect_replay,
                  "Independent receipt-first replay rule", report, resumed["replayed"])
            final = invoke(page, "snapshot", stage)
            if stage in ("PREPARED", "COMMITTED"):
                check(final["decision"] == "HOLD_PRECOMMIT" and final["effectCount"] == 0,
                      "No unauthorized release before durable commit", report)
            else:
                check(final["decision"] == "CONFIRMED_VERIFIED"
                      and final["effectCount"] == 1 and final["violet"] == "VERIFIED",
                      "Reconciliation finishes with matching receipts", report)
                forged = invoke(page, "forged", stage)
                check(forged["violet"] == "AGREEMENT FAILED",
                      "Wrong independent receipt never verifies slot 18", report)
                duplicate = invoke(page, "duplicate", stage, 5)
                check(duplicate["allFulfilled"]
                      and duplicate["effectCount"] == 1
                      and duplicate["decision"] == "CONFIRMED_VERIFIED",
                      "Five concurrent duplicates retain one ledger-managed effect", report)
            page.screenshot(path=str(ARTIFACTS / ("abrupt-" + stage.lower() + ".png")),
                            full_page=True)
            report["final"] = {"decision": final["decision"],
                               "phase": final["phase"], "effectCount": final["effectCount"]}
            report["status"] = "PASS"
        except Exception as err:
            report["status"] = "FAIL"
            report["error"] = str(err)
            report["traceback"] = traceback.format_exc()
        finally:
            # Cleanup is allowed AFTER evidence is collected; it does not
            # participate in the forced-stop observation.
            if proc is not None:
                terminate_group(proc, signal.SIGKILL)
    report["passed"] = sum(1 for c in report["checks"] if c["pass"])
    report["total"] = len(report["checks"])
    (ARTIFACTS / ("abrupt-" + stage.lower() + ".json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    server, thread = serve_localhost()
    url = "http://127.0.0.1:" + str(server.server_port) + PAGE
    result = {
        "suite": "ANNY v16.1 abrupt Chromium process-kill boundary",
        "scope": "SIGKILL AFTER selected IndexedDB transaction resolves; NOT sudden power loss",
        "http_origin": url,
        "scenarios": [],
        "status": "RUNNING",
        "limits": [
            "No SIGKILL inside an unresolved IndexedDB transaction; checkpoints are after API completion.",
            "No forced power removal or disk-cache flush certification.",
            "At-most-once receiver ledger effect, not arbitrary distributed exactly-once external I/O.",
            "Fresh local Chromium profiles, one per stage, and local HTTP origin.",
        ],
    }
    try:
        with sync_playwright() as playwright:
            for stage in STAGES:
                report = test_stage(playwright, url, stage)
                result["scenarios"].append({
                    "stage": stage, "status": report["status"],
                    "passed": report["passed"], "total": report["total"],
                    "error": report.get("error"),
                })
                print(json.dumps(result["scenarios"][-1], ensure_ascii=False), flush=True)
        result["status"] = ("PASS" if all(x["status"] == "PASS" for x in result["scenarios"])
                            and len(result["scenarios"]) == len(STAGES) else "FAIL")
    except Exception as err:
        result["status"] = "FAIL"
        result["error"] = str(err)
        result["traceback"] = traceback.format_exc()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        result["ended_unix"] = int(time.time())
        (ARTIFACTS / "abrupt-kill-summary.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"status": result["status"],
                          "scenarios": len(result["scenarios"]),
                          "artifact": str(ARTIFACTS / "abrupt-kill-summary.json")},
                         ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
