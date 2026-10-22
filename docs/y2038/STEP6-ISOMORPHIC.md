# Step 6 — {{i}} C/Python automated conformance

[Interactive Step 6](step6-isomorphic.html) · [Step 5](step5-isomorphic.html)

The GitHub Actions workflow `.github/workflows/y2038-it3.yml` compiles `it3.c` and invokes `check_it3.py` on pushes and PRs affecting the Y2038 workshop, plus manual workflow dispatch.

The checker requires:
- Exactly eight distinct C output records, each marked PASS
- C output packet bytes equal the pinned vectors
- Independent Python encoder bytes equal the same vectors
- Python decoder round-trip identical to the original signed integer
- Mutated reserved-bit packets rejected in Python
- C's own built-in round-trip and corruption checks complete with Result: PASS

To run from repository root:
```bash
cc -std=c11 -Wall -Wextra -Werror -fsanitize=undefined -fno-sanitize-recover=undefined docs/y2038/it3.c -o docs/y2038/it3
python3 docs/y2038/check_it3.py docs/y2038/it3
```

A successful run is a limited conformance gate, not proof of exhaustive protocol safety. This does not alter existing operating system timestamp structures.
