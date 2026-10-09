# P3.32 — Patricia photon carrier

Canonical user-supplied symbol: `{{ -+- : +-+ }}`. Patricia's symbolic photon carrier is deliberately separate from Greg's 366×4 calendar counter. Root is pinned at zero. The two arm glyphs have symmetric opposite orientation. An *optional operational hypothesis* alternates the left and right labels at each logical tick; neither a rate nor a physical photon oscillation is inferred from the glyph alone.

Committed source `p332_patricia_photon.mjs` exposes literal, pinned root, state(tick), forward, backward and roundTrip; committed test `test_p332.mjs` checks 100,000 forward plus 100,000 backward steps, label anti-symmetry and invalid-state rejection. Tests are committed, but the exact committed JavaScript suite has **not yet been independently executed in this turn**; do not claim empirical or numerical proof beyond inspection of the code.

Next target: bind Patricia's paired symbolic state to the streamed Stargate on explicit user-supplied exchange timing, keeping her carrier independent of Greg's civil calendar. This remains mathematical notation, not a measured physical photon mechanism.