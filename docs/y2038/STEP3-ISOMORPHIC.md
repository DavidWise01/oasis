# Y2038 Step 3 — {{i..}} binary envelope IT3/v1

[Interactive packet inspector](step3-isomorphic.html) · [Step 2](step2-isomorphic.html)

This is a **proposed application-level encoding**, not a standard Unix timestamp layout.

## Wire layout (16 bytes total)

- Octets 0–2: ASCII `IT3` (hex 49 54 33)
- Octet 3: version 0x01
- Octets 4–11: signed 64-bit integer `q` (two's-complement big-endian), number of completed UTC 86400-second periods relative to Unix epoch
- Octets 12–15: unsigned 32-bit big-endian bit field: bit 31 = spinor parity, bits 17–30 reserved **zero**, bits 0–16 = phase seconds (0..86399)

For Unix seconds `t` in signed int64 range, `q=floor(t/86400)`, `p=t-86400q`, `parity=q mod 2` normalized to 0 or 1. Encode `(parity<<31)|p`.

Decoder rejects invalid header, length, reserved bits, phase >= 86400, parity mismatch, or decoded `t=q*86400+p` beyond int64. A legacy signed int32 receiver must additionally reject `t` outside [-2147483648,2147483647].

## Semantics

```
{{i::time::mobius::spinor::transport::v1}}
  epoch   = 1970-01-01T00:00:00Z
  unit    = SI-style Unix second (POSIX timescale; leap seconds not encoded)
  carrier = IT3 v1
  turns   = int64 big-endian
  phase   = 17-bit unsigned second-of-day
  parity  = derived spinor sign
  decode  = turns*86400 + phase
```

Arcsecond phase is exactly `phase*15`, so no fractional rounding occurs. Retaining `q` preserves chronology; the spinor is redundant integrity metadata (not cryptographic authentication or a checksum).

## Deployment

Negotiate versioned format support before exchanging packets. Audit storage, database migrations, language bindings, and old binary clients. This format cannot be dropped into unmodified `time_t`/POSIX APIs.

The browser inspector validates edited packets but is not a substitute for a reference codec, cross-platform interoperability test, or production review.
