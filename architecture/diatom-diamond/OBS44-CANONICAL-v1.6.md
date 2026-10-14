# OBS44 — canonical 00..43 address registry, C# adapter v1.6

This additive address layer implements the user's exact registry with central `00 = n` and address `43 = .0x` (the complete string is one indivisible glyph).

## Registry

```
01 02 03 04 05 06 07 08 09 10 11 12 13
 a  b  c  d  e  f  g  h  i  j  k  l  m

14 15 16 17 18 19 20 21 22 23
 o  p  q  r  s  t  u  v  w  x

                    00
                     n

24 25 26 27 28 29 30 31 32 33
 y  z  1  2  3  4  5  6  7  8

34 35 36 37 38 39 40 41 42 43
 9  >  |  :  "  ^  (  -  + .0x
```

Total: 44 addressable glyphs = 26 letters + digits 1–9 (9) + 9 operator glyphs. `0` is **not** a standalone OBS44 glyph; `00` is the display code for **n**. Existing v0.7 language support for arbitrary nonnegative integers is unchanged beneath the adapter.

## How it integrates without altering the frozen floor

```
 OBS44 surface glyphs                    e.g. ["n", "a", ".0x"]
     | strict 44-entry registry
     v
 canonical decimal floor codes          ["0", "1", "43"]
     | existing frozen v0.7 lexical type: decimal tokens
     v
 frozen UUDDLRLRBASS × 5 per rail        (no code changes)
     | existing v1.1 / v1.2 OBS bus
     v
 OBS {o,b,s} coordinates                 o=26 for numeric-code carrier
     | dual stream, frame transport, inverse floor, dictionary
     v
 OBS44 surface glyphs                    ["n", "a", ".0x"]
```

**Important:** the surface glyph kind is defined by the OBS44 versioned dictionary, not the underlying OBS bus token `o` coordinate. Since all 44 addresses transit as canonical decimal codes, every coordinate's `o` equals 26 in the adapter. The type information is preserved in the **versioned registry**, not in `o` itself. No symbolic glyph string is silently fed into the old frozen lexer.

`OBS44/address-v1.6` identifies the adapter namespace. Do not mistake a raw v0.7 integer `0` for surface glyph `n` without the OBS44 namespace. For streaming transport, frame recovery requires an outer OBS44 protocol indicator.

`ObsAddress44.MakeFrame/RecoverFrame` uses the old 32-token v1.3 frame boundary. The reference project does not implement a C# TCP v1.5 wire adapter; that's a separate task.

## Checks

- `node oracle/obs44-test.mjs`: **4,520 assertions**, 1,070 packets, 16,359 source fragments, and 11 expected rejections passed with the *original* v0.7 + v1.1 + v1.2 JS modules extracted from previous release artifacts.
- Frozen source SHA-256: `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b` — verified unchanged.
- C# 14 / .NET 10 source is written, with parity/self-tests in `src/Program.cs`, **not compiled here** because this environment has no `dotnet` SDK. Do not report C# throughput until executing it.

## Run on Windows with .NET 10 SDK

```
dotnet run --project src/ObsKernel.csproj -c Release -- --map44
dotnet run --project src/ObsKernel.csproj -c Release -- --bench44 20000
```

Rates from `--bench44` are symbolic routing throughput, not neural inference. The frozen dual floor, OBS o/b/s specs, and v1.5 TCP baseline remain unmodified.