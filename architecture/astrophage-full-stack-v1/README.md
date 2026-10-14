# KET ASTROPHAGE — Full-Stack Release v1.0

**Status:** additive versioned freeze, 2026-10-13. Frozen KET source files unchanged. Not a scientific validation or production certification.

## Canonical topology

~~~text
-+UUUU | | uuuu -+
   Na+ (11, 589 nm annotated)       Cl- (17, 850 nm annotated)
           \                         /
                    NaCl
                     |
                  MYCELIUM
                     |
                   CYCAD
                     |
             DIATOME 10000001₂ = 129
                /     |     \
           BEAR-0  BEAR-1  BEAR-2
            0°      120°    240°
                     |
            typed FIELD + original text
                     |
              UTF-8 byte stream
                     |
           2 base-44 digits per byte
                     |
          OSIMODEL (8 lanes × 208 states)
                     |
         LIVE → WRITE → REMEMBER → FORGET → READ → LIVE
                     |
              SHA-256 event ledger
~~~

## Executable modules

- **adapter.mjs** — canonical field, reversible UTF-8/44 adapter, OSIMODEL address routing, cycle verification and deterministic summary.
- **test_adapter.mjs** — finite 303-check acceptance suite.
- **reference_visual.html** — corrected offline React/Canvas2D scene with 177-byte compiled arithmetic WASM.
- **../character-register-44/** — pre-existing 44-address encoder; center address 0 maps to n and terminal token .0x is indivisible.
- **../regenerative-loop/ket-cycle-v01/** — pre-existing six-phase cycle and hash-chained event receipts.
- **FREEZE.md** — versioned contract, limitations, and preservation rules.

From the Git repository root, with Node.js 18+:

~~~sh
node architecture/character-register-44/test_register.mjs
node architecture/regenerative-loop/ket-cycle-v01/test_cycle.mjs
node architecture/astrophage-full-stack-v1/test_adapter.mjs
~~~

The byte encoding is not an attempt to reinterpret unsupported punctuation. Each UTF-8 byte becomes two base-44 addresses: high=floor(byte/44), low=byte mod 44. Every packet retains its ordinal; bus address=lane*208+state with lane=ordinal mod 8. A repeated lane/state pair does not imply a distinct physical address.

Sodium's visible ~589 nm doublet belongs to excited neutral sodium, not a Na+ emission from NaCl. 850 nm is near infrared; teal is only a display proxy. The biological nesting is a symbolic hierarchy. The WASM is arithmetic-only, not a quantum field solver. The existing X/Y/Z six-signed-direction 3D WASM engine and its 366-address toroid contract are referenced, not live-coupled to this Canvas2D field.

The Node adapter and browser visualization are separate executable parts. This freeze is a content-addressed software snapshot, not protected branch immutability, authorization security, physical perpetual motion, or 6/6 production-gate acceptance.
