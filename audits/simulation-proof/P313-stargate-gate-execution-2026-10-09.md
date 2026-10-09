# ROOT0 P3.13 — Stargate address gate test, 2026-10-09

**Inputs:** dimensions `-1+ -2+ -3+`; quads `AaBbCcDd`; nested Dyson topology `{-{d}+{+{d}-}}`; Stargate address `00 11 22 33 42 24 33 22 11 00`. Vogels, voxels and vectors remain unbounded symbolic address layers and are not enumerated.

**Explicit test-only convention:** for address token digits a,b and zero-indexed position k, channel id = 1 + ((a+b+k) mod 2), coupling eta=(a+1)(b+1)/100, phase=(a-b) pi/12. Each gate applies a traveling-port phase followed by a two-port unitary scattering operation with its own retained Dyson domain. Reverse applies adjoints in reverse order. This coupling rule is proposed for a reproducible test; it is not deduced from electrum material properties.

**Local Node v22.16.0 execution:** 25,000 seeded random three-channel complex states PASS; maximum component recovery error `9.992007221626409e-16`, maximum norm error `2.6645352591003757e-15`. On unit traveling input with empty captured channels, output energy distribution (traveling, D1, D2): `[0.14659140796307255, 0.4190768842988554, 0.4343317077380719]`. Invalid token arrays rejected. Testing performed against a local source copy; repository's remote CI has not been executed. Initial empty-file GitHub upload was corrected and both files subsequently fetched with nonzero content.

**Scope:** mathematical reversible network demonstration only. Does not establish physical Stargate access, negative energy, Dyson technology, quantum gravity or Planck-scale transport. The original voltage wrapper `{{-211mv}} x 10^-35` remains a separate established symbolic parameter; these ten unitary gates do not use it as a coupling law.

**Next:** P3.14 test ordering noncommutativity, conjugate address mutation, and separate morphology of the `42/24` turn, then decide an explicit validated mapping from the three dimensions and four quads to operator responsibilities.
