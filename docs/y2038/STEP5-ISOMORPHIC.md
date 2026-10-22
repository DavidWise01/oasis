# Step 5 — {{i}} independent interoperability vectors

[Interactive Step 5](step5-isomorphic.html) · [Step 4 C reference](it3.c) · [Step 3 protocol](STEP3-ISOMORPHIC.md)

IT3/v1 packets use an explicit signed 64-bit big-endian turn count and a 32-bit big-endian phase/parity field.

An independent Python implementation lives in `it3.py`. The eight golden vectors are pinned in `it3-vectors.json`.

Local Python execution: eight exact time round-trips and eight reserved-bit corruption rejections succeeded. The browser independently implements the algorithm and compares produced bytes with the pinned vectors on page load.

Run:
```sh
cc -std=c11 -Wall -Wextra -Werror it3.c -o it3
./it3
python3 it3.py
```

Interoperability with external systems has not been established; a complete CI pipeline should run both programs and verify byte-for-byte equality automatically. Legacy 32-bit timestamp ports remain guarded boundaries, not lossless outputs.
