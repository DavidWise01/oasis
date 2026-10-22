# Step 4: {{i}} reference codec

[Interactive GitHub Pages demo](step4-isomorphic.html) · [Step 3 specification](STEP3-ISOMORPHIC.md)

Portable ISO C11 encode/decode implementation of the fixed 16-octet IT3/v1 application-level packet. No platform `time_t` dependency.

Build:
```sh
cc -std=c11 -Wall -Wextra -Werror -fsanitize=undefined -fno-sanitize-recover=undefined it3.c -o it3
./it3
```

C reference locally compiled with GCC and exercised under UBSan for eight samples: int64 min/max, 2038 limit and overflow, 2100, negative and zero timestamps. Also rejects a reserved-bit mutation of each sample. These are illustrative boundary checks, not comprehensive fuzzing.

Format: IT3 magic + version byte, int64 big-endian turns, 32-bit big-endian field with bit31 parity, bits 17–30 reserved zero and bits 0–16 phase seconds. Phase is in [0,86399]. `seconds=q*86400+p` with Euclidean division. Spinor parity is metadata, not authentication.

The encoder carries signed int64 timestamps; legacy int32 consumers must reject out-of-range seconds. For deployed applications, explicitly version-negotiate and migrate old storage/API contracts.
