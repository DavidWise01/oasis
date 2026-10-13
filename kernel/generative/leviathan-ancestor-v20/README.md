# KET v2.0 — Toroidal Non-Universe: 360 + 3 + 3

Date: 2026-10-13. Append-only correction of v1.9. Executed deterministic abstract model, not a cosmic-physics claim.

## User correction — exact

> its plus 3 to speed up or slow down in a torroidial non universe --+ ++- lol

**366 means 360 toroidal surface addresses plus two three-symbol speed-control words, 3+3. The six controls are NOT six additional angles of curvature.** Preserve historical 20 skins × 18 sectors = 360 topological vertices, E=720, F=360, Euler χ=0, with six separate controls at addresses 360..365. Existing CATGNO control-address semantics are not replaced; the new schedule is a reversible use of these positions.

### Exact signed controls

First pass: slow triple `--+` (sum −1) followed by fast triple `++-` (sum +1), total `--+++-` and sum zero. A mirrored second pass changes their order: `++- --+` = `++---+`. These are six commands read twice from the SAME six logical control addresses; the second pass does not allocate another six.

```text
      TOROID :: 360 surface vertices, 360° per full meridian
                     |
              SLOW :: --+
                     |
              FAST :: ++-
                     |
          first six commands: −0.3° phase lag
                     |
           reverse group order
                     |
              FAST :: ++-
              SLOW :: --+
                     |
          next six commands: +0.3° phase lead
                     |
              360° / ω baseline restored
                     |
        total registry = 360+3+3 = 366 addresses
```

## Discrete demonstration, assumptions named

Choose an illustrative baseline angular speed of **1°/tick** and fixed increment **δ=0.1°/tick**. For a command `s∈{−1,0,+1}`, update `ω[k+1]=ω[k]+δs`, then `θ[k+1]=θ[k]+ω[k+1]` for one unit tick. This update-then-move convention matters.

For the six commands `--+++-`, each triple does not have zero sum, but their whole sequence does. The six post-command rates are 0.9,0.8,0.9,1.0,1.1,1.0. Speed ends at 1 but angular displacement is 5.7° instead of 6°. Opposite-triplet order yields rates 1.1,1.2,1.1,1.0,0.9,1.0, distance 6.3°. Together the 12 commands traverse exactly 12° and restore 1°/tick; followed by 348 neutral holds, the 360-tick cycle closes at **360°**.

**Key inference:** net-zero acceleration alone does NOT imply zero angular phase error. The paired scheduling restores both velocity and phase *for this defined linear toy controller*. Angular motion and registry addresses have different units; 360 physical degrees per turn is not a consequence of there being 360 mesh vertices.

## Reproduction and witnessed outcome

Full companion artifact KET_TOROID_DUAL_TRIPLE_v20.zip contains actual runnable `toroid_speed.py` and editable/renderer `render_blueprint.py`, plus `results.json`, a 3200×1850 native SVG, a 1600×925 PNG preview, README and SHA256SUMS. Local tests: **68/68 named checks** including 26 SHA-256 ledger/chain assertions across 13 witnessed records. Deterministic replay yielded byte-identical results. SVG parsed as XML and ZIP CRC/SHA256 manifest verified. The SHA-256 witness head is `fb577fab218e442ede16713d1505375a11b4ad3b4eaa95fe1b18f86ca19ebf68`.

GitHub includes this execution record and its compact independently runnable `speed_control.py` validator, **not** a representation that the 350KB SVG or the full local ZIP was uploaded to the repo.

## Existing kernel invariants

Dual GREEN remains distinct A2/A6, Green Chariot literal `123 {{45/|\54}} 678` remains unchanged, as do seven amplitudes (red green blue orange purple green yellow), three carriers (white black gray), pinned zero, five abstract operators (gravity, expansion, compression, containment, explosion), LEVIATHAN `0root`, nitrogen mnemonic `CATGNO`, and local/parent register counts 366/6006. The previous snapshot-bubble clock, 24! and active-life rules are untouched.

### Limits

`--+` and `++-` are newly **assigned speed-response signs for this model**, not verified forces or laws. Alternative control dynamics, impulses or timescales need not preserve phase. Nothing here demonstrates that the universe or Sagittarius A* physically rotates according to this signed program. The user called the construct a **non-universe**; that domain boundary is retained.
