#!/usr/bin/env python3
"""External rotation-curve residual check against Eilers et al. (2019).

This script does not re-fit the existing gravitational model. Its observational
input is Cautun et al.'s public redistribution of Eilers' tabulation (GPL-3.0):
https://github.com/MariusCautun/Milky_Way_mass_profile/blob/eb747da6b0383f23cfa4e1fc0dfb8f00a857bfac/MW_rotation_Eilers_2019.txt

Usage:
    python rotation_holdout_validate.py --self-test
    python rotation_holdout_validate.py --source MW_rotation_Eilers_2019.txt --out /tmp/rot-check
    python rotation_holdout_validate.py --fetch --out /tmp/rot-check

Require the adjacent milky_way_bound.py script. For a remote source download,
--fetch is explicit and uses a pinned source-commit URL.
"""
import argparse
import csv
import json
import math
from pathlib import Path
from urllib.request import urlopen
from milky_way_bound import field as galactic_field, R0, PC

PINNED_SOURCE = (
    "https://raw.githubusercontent.com/MariusCautun/Milky_Way_mass_profile/"
    "eb747da6b0383f23cfa4e1fc0dfb8f00a857bfac/"
    "MW_rotation_Eilers_2019.txt"
)
FIELDS = (
    "bin_index", "radius_kpc", "observed_km_s",
    "source_sigma_col3_km_s", "source_sigma_col4_km_s",
    "source_systematic_percent", "model_km_s",
    "model_minus_observed_km_s", "conservative_envelope_km_s",
    "outside_simple_envelope", "scope", "source_license"
)
HEADER = [
    "# Original numeric table: Eilers et al. 2019 via "
    "MariusCautun/Milky_Way_mass_profile (GPL-3.0).",
    "# https://github.com/MariusCautun/Milky_Way_mass_profile/blob/"
    "eb747da6b0383f23cfa4e1fc0dfb8f00a857bfac/"
    "MW_rotation_Eilers_2019.txt",
    "# Derived table: GPL-3.0-or-later with original source attribution.",
    "# The two sigma columns are retained separately, as labeled in the source.",
]

def model_speed(radius_kpc):
    if radius_kpc <= 0:
        raise ValueError("radius must be positive")
    f = galactic_field(1000.0*radius_kpc)
    return f["circular_km_s"]

def parse_observations(raw_text):
    observations = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        values = line.split()
        if len(values) != 5:
            raise ValueError("Expected five fields in source data: "+line)
        r, observed, sig1, sig2, systematic = map(float, values)
        if not all(map(math.isfinite, (r,observed,sig1,sig2,systematic))):
            raise ValueError("Non-finite source values")
        if r<=0 or observed<=0 or min(sig1,sig2,systematic)<0:
            raise ValueError("Invalid physical or uncertainty range")
        observations.append((r,observed,sig1,sig2,systematic))
    if len(observations)!=38:
        raise ValueError(f"Expected 38 source bins; found {len(observations)}")
    return observations

def evaluate(entries):
    records=[]
    for i,(r,obs,e1,e2,sys) in enumerate(entries, start=1):
        predicted=model_speed(r)
        delta=predicted-obs
        # Descriptive *envelope*, NOT a statistical confidence level.
        envelope=max(e1,e2)+sys*obs/100.0
        records.append({
          "bin_index": i, "radius_kpc": r, "observed_km_s": obs,
          "source_sigma_col3_km_s": e1, "source_sigma_col4_km_s": e2,
          "source_systematic_percent": sys, "model_km_s": predicted,
          "model_minus_observed_km_s": delta,
          "conservative_envelope_km_s": envelope,
          "outside_simple_envelope": "YES" if abs(delta)>envelope else "NO",
          "scope": ("WITHIN_ORIGINAL_CORRIDOR" if r<=R0/1000
                    else "OUTSIDE_ORIGINAL_CORRIDOR"),
          "source_license": "GPL-3.0-or-later"})
    return records

def summarize(items):
    n=len(items)
    if not n:
        return {"n":0}
    return {
      "n":n,
      "outside_simple_envelope":sum(r["outside_simple_envelope"]=="YES" for r in items),
      "rms_residual_km_s":math.sqrt(sum(r["model_minus_observed_km_s"]**2 for r in items)/n),
      "mean_residual_km_s":sum(r["model_minus_observed_km_s"] for r in items)/n,
      "mean_absolute_residual_km_s":sum(abs(r["model_minus_observed_km_s"]) for r in items)/n,
    }

def check(entries):
    assert math.isclose(model_speed(R0/1000),233.0,rel_tol=1e-12)
    assert len(entries)==38
    assert math.isclose(entries[0]["model_km_s"],240.27751724506052,rel_tol=1e-10)
    assert math.isclose(entries[0]["model_minus_observed_km_s"],
                        13.44751724506052,rel_tol=1e-10)
    assert sum(x["outside_simple_envelope"]=="YES" for x in entries)==5
    assert sum(x["scope"]=="WITHIN_ORIGINAL_CORRIDOR" for x in entries)==7

def write_outputs(records, output_dir):
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    output_csv=output_dir/"EILERS2019_MODEL_RESIDUALS_20261027.csv"
    with output_csv.open("w",newline="",encoding="utf-8") as fp:
        for ln in HEADER:
            fp.write(ln+"\n")
        wr=csv.DictWriter(fp,fieldnames=FIELDS,lineterminator="\n")
        wr.writeheader()
        for r in records:
            wr.writerow({key: r[key] for key in FIELDS})
    summary={
      "calibration_solar_radius_kpc":R0/1000,
      "calibration_speed_km_s":233.0,
      "scope_all":summarize(records),
      "scope_within_original_corridor":summarize([
          r for r in records if r["scope"]=="WITHIN_ORIGINAL_CORRIDOR"]),
      "scope_outside_original_corridor":summarize([
          r for r in records if r["scope"]=="OUTSIDE_ORIGINAL_CORRIDOR"]),
      "flagged_bins": [
          {"radius_kpc":r["radius_kpc"],"residual_km_s":
           r["model_minus_observed_km_s"]}
          for r in records if r["outside_simple_envelope"]=="YES"],
      "disclaimer": ("External Eilers 2019 values are observational-inference "
          "estimates, not direct gravity measurements. "
          "Systematic errors are correlated; no independent-point chi-square "
          "significance or accepted/rejected hypothesis is asserted. "
          "Do not re-fit parameters using this held-out data while claiming "
          "it remains a holdout."),
    }
    with (output_dir/"EILERS2019_RESIDUAL_AUDIT.json").open(
        "w",encoding="utf-8") as fp:
        json.dump(summary,fp,indent=2)
        fp.write("\n")
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=False)
    source.add_argument("--source",help="Local Eilers/Cautun source txt")
    source.add_argument("--fetch",action="store_true",
        help="Explicitly download from pinned public GitHub source commit")
    p.add_argument("--self-test",action="store_true",
        help="Check core independent model predictions without source network")
    p.add_argument("--out",default="validation_output")
    args=p.parse_args()
    if args.self_test:
        assert math.isclose(model_speed(R0/1000),233.0,rel_tol=1e-12)
        assert math.isclose(model_speed(5.27),240.27751724506052,rel_tol=1e-10)
        print("PASS: original solar calibration and 5.27 kpc model prediction")
        return
    if args.source:
        raw=Path(args.source).read_text(encoding="utf-8")
    elif args.fetch:
        with urlopen(PINNED_SOURCE,timeout=25) as resp:
            raw=resp.read().decode("utf-8")
    else:
        p.error("Use --source, --fetch or --self-test")
    results=evaluate(parse_observations(raw))
    check(results)
    audit=write_outputs(results,args.out)
    print(json.dumps(audit,indent=2))
if __name__=="__main__":
    main()
