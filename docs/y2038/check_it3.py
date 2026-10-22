#!/usr/bin/env python3
"""Compare IT3/v1 C output to independent Python and pinned golden vectors."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import it3

CASES = json.loads((HERE / "it3-vectors.json").read_text(encoding="utf-8"))
RECORD = re.compile(r"^t=(-?\d+) : (PASS|FAIL)  ((?:[0-9A-F]{2} ?){16})$")
HEX = lambda b: b.hex(" ").upper()

def main():
    binary = sys.argv[1] if len(sys.argv) > 1 else "./it3"
    output = subprocess.run([binary], capture_output=True, text=True, check=True).stdout
    records = {}
    for line in output.splitlines():
        m = RECORD.fullmatch(line)
        if m:
            t, status, wire = m.groups()
            if t in records:
                raise AssertionError(f"duplicate timestamp: {t}")
            if status != "PASS":
                raise AssertionError(f"C reported FAIL for {t}")
            records[t] = wire.strip()
    expected = {v["seconds"]: v["hex"] for v in CASES}
    assert len(expected) == len(CASES) == 8
    assert records.keys() == expected.keys(), (records.keys(), expected.keys())
    assert output.strip().endswith("Result: PASS"), "C final status missing"
    for key, pinned in expected.items():
        t = int(key)
        wire = it3.encode(t)
        assert HEX(wire) == pinned, f"Python differs: {key}"
        assert records[key] == pinned, f"C differs: {key}"
        assert it3.decode(wire) == t, f"Python round trip: {key}"
        broken = bytearray(wire)
        broken[12] ^= 0x40
        try:
            it3.decode(broken)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Python accepted reserved-bit corruption: {key}")
    print(f"IT3 conformance PASS: {len(expected)} shared C/Python/golden packets")
    print(f"Corrupt packet rejection PASS: {len(expected)} Python cases")
if __name__ == "__main__":
    main()
