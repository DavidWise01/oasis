#!/usr/bin/env python3
"""ANNY browser boundary gate: genuine Chromium UI + clean browser-process restart.

Run from a cloned checkout:
  python -m pip install playwright==1.57.0
  python -m playwright install chromium
  python apps/anny-neon/tests/browser_gate.py

The test serves GitHub Pages files from a local HTTP origin, never file://.
This is graceful Chromium restart/persistence evidence, NOT sudden power loss.
"""
from __future__ import annotations

import functools
import http.server
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import traceback

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PAGE_PATH = "/apps/anny-neon/"
ARTIFACTS = Path(os.environ.get("ANNY_BROWSER_ARTIFACTS", str(REPO_ROOT / "anny-browser-evidence")))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):  # Suppress routine static asset traffic.
        pass


def server():
    handler = functools.partial(QuietHandler, directory=str(REPO_ROOT))
    instance = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    return instance, thread


def gate(condition, label, report, detail=""):
    report["checks"].append({"name": label, "pass": bool(condition), "detail": str(detail)})
    if not condition:
        raise AssertionError(label + ": " + str(detail))


def js_text(page, selector):
    return page.locator(selector).inner_text().strip()


def launch(p, path):
    kwargs = {"user_data_dir": str(path), "headless": True,
              "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
    # Leave executable resolution to Playwright in CI.
    chrome = os.environ.get("ANNY_CHROMIUM_EXECUTABLE")
    if chrome:
        kwargs["executable_path"] = chrome
    return p.chromium.launch_persistent_context(**kwargs)


def bootstrap(page, base_url, report):
    errs = []
    page.on("pageerror", lambda err: errs.append(str(err)))
    page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
    page.locator("#spectrum-pairs .pair").first.wait_for(timeout=15000)
    page.wait_for_function(
        "() => document.querySelectorAll('#geometry-pairs .geometry-pair').length === 7"
        " && document.querySelectorAll('#radiation-toggles .radiation-toggle').length === 4",
        timeout=15000,
    )
    page.wait_for_function("() => document.getElementById('phase').textContent !== 'IDLE'", timeout=15000)
    gate(not errs, "No startup JavaScript errors", report, errs)
    return errs


def run():
    report = {
        "suite": "ANNY Chromium geometry/recovery boundary",
        "scope": "actual browser, local HTTP origin; graceful browser restart only",
        "notes": [
            "Radiation toggle state is intentionally presentation-only and resets on reload.",
            "IndexedDB journal and receiver state must survive a new Chromium process with the same profile.",
            "No sudden termination, process crash during transaction, or power-failure durability is certified.",
        ],
        "checks": [],
        "status": "RUNNING",
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    httpd, thread = server()
    url = "http://127.0.0.1:" + str(httpd.server_port) + PAGE_PATH
    report["url"] = url
    screenshot_page = None
    try:
        with tempfile.TemporaryDirectory(prefix="anny-chromium-profile-") as profile:
            with sync_playwright() as p:
                context = launch(p, profile)
                try:
                    page = context.pages[0] if context.pages else context.new_page()
                    screenshot_page = page
                    errors = bootstrap(page, url, report)
                    gate(page.locator("#radiation-tally").inner_text() == "4/4 overlays enabled",
                         "Four overlays active at startup", report)
                    gate(page.locator("#geometry-photons .geometry-radiation-token").count() == 2
                         and page.locator("#geometry-particles .geometry-radiation-token").count() == 2,
                         "Photon and particle axes have 2 markers each", report)
                    gate(page.locator("#geometry-pairs button").count() == 7,
                         "Seven signed color pairs present", report)
                    gate("Violet" in js_text(page, "#geometry-focus"),
                         "Anny Violet selected initially", report)
                    page.locator('#radiation-toggles button[data-radiation="alpha"]').click()
                    page.wait_for_function(
                        "() => document.querySelectorAll('#geometry-particles .geometry-radiation-token').length === 1"
                    )
                    gate(page.locator("#geometry-particles .geometry-radiation-token").count() == 1
                         and page.locator("#geometry-photons .geometry-radiation-token").count() == 2,
                         "Alpha toggle synchronizes only particle axis", report)
                    for species in ("gamma", "xray"):
                        page.locator('#radiation-toggles button[data-radiation="' + species + '"]').click()
                    page.wait_for_function(
                        "() => document.querySelector('#sapphon-radiation-geometry').dataset.photonActive === 'false'"
                    )
                    gate(page.locator("#geometry-photons .geometry-radiation-token").count() == 0
                         and page.locator("#geometry-particles .geometry-radiation-token").count() == 1,
                         "Photon suppression does not erase beta particle", report)
                    page.locator("#radiation-reset").click()
                    page.wait_for_function(
                        "() => document.querySelector('#sapphon-radiation-geometry').dataset.photonActive === 'true'"
                        " && document.querySelectorAll('#geometry-photons .geometry-radiation-token').length === 2"
                        " && document.querySelectorAll('#geometry-particles .geometry-radiation-token').length === 2"
                    )
                    gate(page.locator("#radiation-tally").inner_text() == "4/4 overlays enabled",
                         "Restore-all republishes four radiation overlays", report)
                    page.locator('#geometry-pairs button[data-color="green"]').click()
                    green = js_text(page, "#geometry-focus")
                    gate("Φύσις" in green and "Χλόη" in green and "495" in green and "570" in green,
                         "Green Greek −/+ names and endpoints render", report, green)
                    page.locator('#geometry-pairs button[data-color="violet"]').click()
                    violet = js_text(page, "#geometry-focus")
                    gate("Ἴρις" in violet and "Αἰθήρ" in violet and "18" in violet,
                         "Anny Violet Greek poles and slot 18 render", report, violet)
                    gate(page.locator("#sapphon-void-anchor .outer-anchor").count() == 1
                         and page.locator("#sapphon-gravity-anchor .outer-anchor").count() == 1
                         and page.locator("#white-sapphon-pair .pair").count() == 1,
                         "VOID, GRAVITY, and White remain distinct", report)
                    page.locator("#run").click()
                    page.wait_for_function(
                        "() => document.getElementById('phase').textContent === 'CONFIRMED'"
                        " && document.getElementById('violet').textContent === 'VERIFIED'",
                        timeout=20000,
                    )
                    before = json.loads(js_text(page, "#log"))
                    transfer_id = before["transferId"]
                    gate(before["effectCount"] == 1 and len(before["events"]) == 3
                         and before["events"][-1]["phase"] == "CONFIRMED",
                         "Harvester release confirmed with one ledger effect", report, transfer_id)
                    page.locator("#gate").click()
                    page.wait_for_function(
                        "() => { try { const r=JSON.parse(document.getElementById('log').textContent);"
                        "return r.gate===undefined && r.passed===3 && r.total===3; } catch(e) {return false;} }",
                        timeout=20000,
                    )
                    first_gate = json.loads(js_text(page, "#log"))
                    gate(first_gate["passed"] == 3 and first_gate["effectCount"] == 1,
                         "Same-session independent recovery gate passes", report)
                    gate(not errors, "No script failures before restart", report, errors)
                finally:
                    context.close()
                    screenshot_page = None

                # A genuinely new browser process, same on-disk profile.
                context2 = launch(p, profile)
                try:
                    page2 = context2.pages[0] if context2.pages else context2.new_page()
                    screenshot_page = page2
                    errs2 = bootstrap(page2, url, report)
                    gate(page2.evaluate("localStorage.getItem('anny-neon-id')") == transfer_id,
                         "Transfer ID survives browser-process restart", report)
                    gate(js_text(page2, "#phase") == "CONFIRMED" and js_text(page2, "#violet") == "VERIFIED",
                         "Two independent IndexedDB receipts survive restart", report)
                    page2.locator("#reload").click()
                    page2.wait_for_function(
                        "() => document.getElementById('phase').textContent === 'CONFIRMED'"
                    )
                    gate(json.loads(js_text(page2, "#log")).get("id") == transfer_id,
                         "Reload control restores exact original transfer", report)
                    page2.locator("#race").click()
                    page2.wait_for_function(
                        "() => {try{return JSON.parse(document.getElementById('log').textContent).effectCount===1}"
                        "catch(e){return false}}",
                        timeout=20000,
                    )
                    after_race = json.loads(js_text(page2, "#log"))
                    gate(after_race["effectCount"] == 1
                         and len(after_race["settled"]) == 5
                         and all(s == "fulfilled" for s in after_race["settled"]),
                         "Five duplicate deliveries retain one effect after restart", report)
                    gate(page2.locator("#radiation-tally").inner_text() == "4/4 overlays enabled"
                         and page2.locator('#geometry-pairs button[data-color="violet"]')
                           .get_attribute("aria-pressed") == "true",
                         "Visual toggles correctly reset after reload", report)
                    gate(not errs2, "No JavaScript errors after restart", report, errs2)
                    page2.screenshot(path=str(ARTIFACTS / "anny-restart-verified.png"), full_page=True)
                finally:
                    context2.close()
                    screenshot_page = None
        report["status"] = "PASS"
    except Exception as e:
        report["status"] = "FAIL"
        report["error"] = str(e)
        report["traceback"] = traceback.format_exc()
        try:
            if screenshot_page:
                screenshot_page.screenshot(path=str(ARTIFACTS / "anny-failure.png"), full_page=True)
        except Exception:
            pass
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        report["finished_unix"] = int(time.time())
        report["passed"] = sum(bool(x["pass"]) for x in report["checks"])
        report["total"] = len(report["checks"])
        (ARTIFACTS / "anny-browser-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"status": report["status"],"passed": report["passed"],"total": report["total"],
                          "artifact": str(ARTIFACTS / "anny-browser-report.json"),
                          "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
