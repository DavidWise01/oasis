# AMTSO-Aligned Juliet / Mandel Defensive Benchmark 00

Status: **0e / CLOSED**

This is an **AMTSO-aligned internal benchmark**, not an AMTSO certification or lab result.

## Scope

- harmless/synthetic artifacts only
- AMTSO Security Features Check categories mirrored at a high level
- sandbox evaluation dimensions modeled at a high level
- false-positive controls
- deterministic reporting
- containment / anti-evasion behavior
- fuzz regression
- transparent test-plan metadata

## Security-feature categories

```text
manual download detection
PUA detection
compressed threat detection
drive-by detection
phishing detection
cloud lookup connectivity
```

## Sandbox-oriented dimensions

```text
detection capability
anti-evasion behavior
speed/completion sanity
reporting accuracy
containment integrity
```

## Results

Planes: **9 / 9 PASS**

- `amtso_security_feature_categories` — 6/6 PASS
- `harmless_feature_artifacts` — 5/5 PASS
- `false_positive_controls` — 5/5 PASS
- `sandbox_containment_and_evasion` — 6/6 PASS
- `reporting_accuracy` — 3/3 PASS
- `determinism` — 2/2 PASS
- `throughput_sanity` — 4/4 PASS
- `fuzz_regression` — 2/2 PASS
- `test_plan_transparency` — 3/3 PASS

Pillar hash:
`ac5007366a1d9068054c7eebb8963b9f68c2b7bbb17017caddf71a2ba697f0d4`

Limitations:
- no live malware
- no external AMTSO lab involvement
- no claim of AMTSO compliance/certification
- no real-world endpoint efficacy claim

RESULT = **0e / CLOSED**
