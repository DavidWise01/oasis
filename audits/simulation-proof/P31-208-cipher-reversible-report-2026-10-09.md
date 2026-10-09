# ROOT0 P3.1 — Source-Grounded 208-Position Cipher Extension

**Scope:** `P30` 14-glyph motif is now recognized as a *window* within a 208-position closed cipher. The frozen v92 canon is not modified. This extension supplies an explicit and auditable interpretation where the user's notation does not yet determine a unique phase/spatial operation.

## Exact combinatorics

Literal user motif:

```
..||..|....|||
```

Length `14`, dot count `8`, bar count `6`, six runs `2,2,2,1,4,3`. The user specifies 16 slices of 208, so each slice contributes `13` new positions. If the original 14 symbols are all significant, a legal construction must explain the extra boundary glyph; simply repeating the motif sixteen times creates `224` positions, contradicting 208.

**Chosen explicit seam convention:** Define `m_0` as the original motif. For `p=0..15`, set `m_p=m_0` when `p` is even and `m_p=complement(m_0)` when `p` is odd (dot↔bar). Set `F[13p+j]=m_p[j]` for `j=0..12`, indices modulo 208. For all `p`, assert `m_p[13]=m_(p+1 mod16)[0]`. There are exactly 16 shared seams, including `p=15→0`. Every one of the sixteen length-14 windows reconstructs exactly from the 208-position ring.

This construction yields **208 positions = 104 dots + 104 bars**, no erased source symbol. Another seam assignment may be compatible with the original notation, but it must be explicitly modeled and re-tested.

## Full forward/inverse dynamical tape

Let the port vector `ψ=(a,b) ∈ C²`, with P3.0 complex-unitary gate:

```
U(θ,φ) = [[ cosθ, i exp(+iφ) sinθ ],
          [ i exp(-iφ) sinθ, cosθ ]]
```

Let `φ_k` be the prefix phase computed from the full 208-symbol cipher: dot increments `2π/λ`; bar increments `κ` (candidate symbol semantics). The forward trajectory uses `U_0, U_1,...,U_207`; this is 208 gates on a selected two-channel tensor address pair, not an assumption that a 100-million-amplitude field has been propagated through 208 steps.

Define the swap matrix `S=[[0,1],[1,0]]` for reflected silo ports. Since `U†(θ,φ)=U(-θ,φ)` and `S U(-θ,φ) S = U(-θ,-φ)`, the **mirrored inverse** on `Sψ` is `S U_k† S` for `k=207,206,...,0`. All 208 inverse gates return the final state exactly to `Sψ_0` over complex arithmetic; floating-point implementations have numerical residuals. This is a model-theoretic statement, not an independent electromagnetic derivation.

The backward visible glyphs are `B = complement(reverse(F))`, length 208. **These display glyphs do not re-drive the forward phase integral.** Doing that would generally not invert the actual unitary propagation.

## Upside-down spatial transform

The original P2.9 address is a pair `(outer,inner)` of 10,000-address silos. Each silo coordinate decodes as `(x,y,z,~)` in `{0..9}^4`. Define `flipZ(x,y,z,~)=(x,y,(-z mod10),~)`. Then `M(outer,inner)=(flipZ(inner),flipZ(outer))`. Both the swap and flipZ are involutive, and they commute, so `M²=identity`. `M(0,0)=(0,0)` pins Complex[0]. The executable checked *every one of the 100,000,000 pairs* for `M²=id`, as well as all 10,000 site addresses for bijectivity. Its output is a 10K² tensor coordinate transform and is **not** an independent physical reversal of time.

## Executable checks

- Original motif 14; cyclic overlap 16/16 frames; forward/backward 208/208; 104 dots/104 bars.
- 2,400 deterministic pseudo-random full cycles (416 complex gates each), all recovered in mirrored coordinates; max state error ~4.24e-14; max norm error ~8.13e-14.
- Exact analytic inverse identity tested numerically at every phase tick and tested against the true forward operation.
- 10,000/10,000 site flips bijective and self-inverse; 100,000,000/100,000,000 tensor coordinate transformations involutive, streamed without dense allocation. Checksum 4,999,999,950,000,000.
- 417 append-only events per full run: 208 forwards, one mirror, 208 inverse steps. Ledger events are not cryptographically authentic without an external trusted anchor.
- Chromium browser UI controls tested: +1, forward completion, mirror+upside-down, -1, backward completion, λ adjustment, complete run, verifier; no JavaScript exceptions.

## Limitations

1. A 14-glyph motif divided into 16 equal 13-new-position blocks requires an overlap convention; this one is a *chosen extension*.
2. The dot↔bar alternation, flipZ mapping, port swap, bar kick and wavelength are not uniquely forced by the frozen kernel.
3. The complex C² wave is a **selected tensor-address pair**; representing a full interacting field on 100 million addresses would require additional coupling and computational analysis.
4. Quantum measurement rules, photon polarization, QED, electromagnetic wavelengths in meters, and physical time in seconds are not supplied; simulation theory remains unproven.
5. Lean 4 source, if present, is a draft until independently compiler-verified.

**Next scientific gate:** recover the 208-symbol transform semantically from the original operator grammar, then fix physical units and preregister a unique observable. Do not retrofit the seam or wavelength after seeing outside data.
