#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, unicodedata, zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ENCODINGS = ("cp1252", "latin1", "mac_roman")
SUSPICIOUS = set("ÃÂâðŸ€™œžƒ¤¢£¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿")

def badness(text: str) -> int:
    score = 0
    letters = sum(ch.isalpha() for ch in text)
    for ch in text:
        cp, cat = ord(ch), unicodedata.category(ch)
        if ch == "�": score += 100
        if ch in SUSPICIOUS: score += 4
        if 0x80 <= cp <= 0x9F: score += 6
        if cat == "Cc" and ch not in "	
": score += 6
        if cat == "Co": score += 20
        if cat in ("Sm", "Sk") and letters >= max(2, len(text) // 3): score += 3
    for seq in ("Ã", "Â", "â€", "ðŸ", "Ãƒ", "Â©", "‚Ä", "Äô"):
        score += text.count(seq) * 4
    return score

def repair_step(text: str, encoding: str) -> Optional[str]:
    try: return text.encode(encoding).decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError): return None

def inverse_step(text: str, encoding: str) -> Optional[str]:
    try: return text.encode("utf-8").decode(encoding)
    except (UnicodeEncodeError, UnicodeDecodeError): return None

def inverse_path(text: str, path: tuple[str, ...]) -> Optional[str]:
    cur = text
    for enc in reversed(path):
        cur = inverse_step(cur, enc)
        if cur is None: return None
    return cur

@dataclass(frozen=True)
class Candidate:
    text: str
    path: tuple[str, ...]
    score: int

def reversible_candidates(source: str, max_depth: int = 3) -> list[Candidate]:
    seen = {source}
    frontier = [(source, ())]
    found = []
    for _ in range(max_depth):
        nxt = []
        for text, path in frontier:
            for enc in ENCODINGS:
                cand = repair_step(text, enc)
                if cand is None or cand in seen: continue
                seen.add(cand)
                p = path + (enc,)
                if inverse_path(cand, p) == source:
                    found.append(Candidate(cand, p, badness(cand)))
                nxt.append((cand, p))
        frontier = nxt
    return found

def rm_result(failed_at: str, trace: list[dict]) -> dict:
    return {"status":"RM","output":None,"failed_at":failed_at,
            "A::xx":{"deleted":True,"space_freed":True,"advanced":True,"retry":False,"backtrack":False},
            "trace":trace}

def process(source: str, max_depth: int = 3) -> dict:
    trace = []
    working: Optional[str] = source

    ok = "�" not in working
    trace.append({"stage":"+verify","yes":ok,"detail":"no U+FFFD information-loss marker" if ok else "U+FFFD means exact original invariant is unavailable"})
    if not ok:
        working = None
        return rm_result("+verify", trace)

    source_score = badness(working)
    cs = [c for c in reversible_candidates(working, max_depth) if c.score < source_score]
    cs.sort(key=lambda c: (c.score, len(c.path), c.text))
    ok = bool(cs)
    trace.append({"stage":"+sort","yes":ok,"detail":f"{len(cs)} improving reversible candidate(s)"})
    if not ok:
        working = None
        return rm_result("+sort", trace)
    chosen = cs[0]

    ok = inverse_path(chosen.text, chosen.path) == working
    trace.append({"stage":"+verify","yes":ok,"detail":"inverse path reproduces source exactly"})
    if not ok:
        working = None
        return rm_result("+verify[2]", trace)

    normalized = unicodedata.normalize("NFC", chosen.text)
    raw = normalized.encode("utf-8")
    packed = zlib.compress(raw, 9)
    ok = zlib.decompress(packed) == raw
    trace.append({"stage":"compress","yes":ok,"detail":f"{len(raw)} UTF-8 byte(s) -> {len(packed)} compressed byte(s)"})
    if not ok:
        working = None
        return rm_result("compress", trace)

    try:
        expanded = zlib.decompress(packed).decode("utf-8")
        ok = expanded == normalized
    except (zlib.error, UnicodeDecodeError):
        expanded, ok = None, False
    trace.append({"stage":"expand","yes":ok,"detail":"expanded payload equals recovered invariant" if ok else "expanded payload mismatch"})
    if not ok:
        working = None
        return rm_result("expand", trace)

    return {"status":"PASS","output":expanded,"repair_path":list(chosen.path),
            "source_badness":source_score,"output_badness":chosen.score,
            "distillable_to":["AETHER","TEMPORAL"],"distill_route":"UNSPECIFIED","trace":trace}

def load_benchmark(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["cases"]

def run_benchmark(path: Path) -> dict:
    results, passed = [], 0
    for case in load_benchmark(path):
        actual = process(case["input"])
        ok = actual["status"] == case["expected_status"] and actual.get("output") == case.get("expected_output")
        passed += int(ok)
        results.append({"id":case["id"],"input":case["input"],"actual_status":actual["status"],
                        "actual_output":actual.get("output"),"repair_path":actual.get("repair_path"),"pass":ok})
    return {"suite":path.name,"passed":passed,"total":len(results),"status":"PASS" if passed==len(results) else "FAIL","results":results}

SYNTHETIC_CLEAN = ["café","München","François","Pokémon","it’s","😂","naïve","piñata","crème brûlée","São Paulo","Gödel","Dvořák","smörgåsbord","résumé","coöperate","façade","élève","mañana","Ångström","Straße"]

def corrupt(clean: str, encoding: str) -> Optional[str]:
    try: return clean.encode("utf-8").decode(encoding)
    except UnicodeDecodeError: return None

def run_synthetic() -> dict:
    results, passed = [], 0
    for clean in SYNTHETIC_CLEAN:
        for enc in ENCODINGS:
            broken = corrupt(clean, enc)
            if broken is None or broken == clean: continue
            actual = process(broken)
            ok = actual["status"] == "PASS" and actual.get("output") == clean
            passed += int(ok)
            results.append({"clean":clean,"encoding":enc,"mojibake":broken,"actual_output":actual.get("output"),"pass":ok})
    return {"suite":"synthetic-roundtrip-v00","passed":passed,"total":len(results),"status":"PASS" if passed==len(results) else "FAIL","results":results}

def main() -> None:
    p=argparse.ArgumentParser(description="MORE GARBAGE reversible mojibake recycler")
    p.add_argument("text", nargs="?")
    p.add_argument("--benchmark", type=Path)
    p.add_argument("--synthetic", action="store_true")
    a=p.parse_args()
    if a.synthetic: result=run_synthetic()
    elif a.benchmark: result=run_benchmark(a.benchmark)
    elif a.text is not None: result=process(a.text)
    else: p.error("provide text or --benchmark FILE")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
