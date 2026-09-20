# MORE GARBAGE benchmark strategy

There is no single authoritative suite specifically for post-hoc mojibake repair, so this project uses layers:

1. fixed reversible corpus;
2. generated roundtrip corruption;
3. Unicode conformance data for adjacent normalization/encoding behavior;
4. mature repair-library regression cases as external edge-case sources.

Current local record:

```text
fixed corpus       11 / 11 PASS
synthetic sweep    60 / 60 PASS
```

References:
- Unicode UCD test files: https://www.unicode.org/reports/tr44/#Test_Files
- Unicode conformance: https://www.unicode.org/versions/latest/core-spec/chapter-3/
- ftfy: https://github.com/rspeer/python-ftfy
