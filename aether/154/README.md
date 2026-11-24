# AETHER-154 — Reference identity and certificate intake

**Phase X 2/8: synthetic software-readiness 25%; physical qualification 0%.**

The exact local corrected execution passed **3,200/3,200** checks over 25 seeds × eight cases × 20 ticks × two policies. Signed-only comparator authorized **1,200 unsafe dry-run ACT** while the certificate-gated model authorized **zero unsafe dry-run ACT** and retained **2,800 safe actions**. All operational actions remain HOLD.

The six faults are absent issuer identity, unrecognized issuer ID, serial mismatch, expired certificate, broken declared traceability ancestry, and tampering with a signed uncertainty value. Mock reference issuer and bench keys do not establish actual independent metrological source provenance.

**Preserved failure:** The first run, AETHER-154A, incorrectly excluded the previous hash from its verifier reconstruction. Its 400 episode hash checks failed despite zero guarded unsafe decisions. The original source and all failed check rows remain untouched in the companion ZIP. AETHER-154 corrected **only** the verifier's reconstructed field set; the authorization gate remained unchanged. The corrected local source SHA-256 is `c40bf52d6a1b5ed5068d6e6967d2d25130b16cee9a62963dd354f675747e9fc7`.

**Physical evidence remains absent:** the [reference evidence register](physical_reference_register.json) intentionally retains null fields for device identity, serial, accreditation, certificate number, traceable calibration, original raw measurements and issuer verification. No real laboratory or physical standard has been authenticated; physical qualification 0%.

[Python reproducibility demonstration](experiment.py) · [Local results](results.csv) · [Acceptance manifest](manifest.json) · [Failed 154A record](../154a/failure.json) · [Interactive laboratory](index.html) · [Phase X tracker](../PHASE-X-STATUS.md).

The GitHub Python is independently authored from the executed local Python; GitHub checkout replay and live Pages deployment have not been verified. The complete executed and failed source, checks, traces, and manifests are in the downloadable evidence ZIP.
