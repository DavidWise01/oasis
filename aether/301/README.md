# AETHER-301-RS — Exact Remote Receipt and Retained Object Re-fetch

AETHER-301 uses the bounded, pinned-IP AETHER-264 HTTPS acquisition layer to fetch an exact canonical signed AETHER-300 receipt and an independently pinned object preimage from two **different allowed HTTPS hostnames**. Each capture is an explicit, nonce-separated operation; the implementation allows at most two local observation windows. A read-only audit recomputes both recorded raw-body digests, the signed receipt's Ed25519 verification, window ancestry, nonce uniqueness and high-water prefix comparison. Observations are stored in SQLite WAL with synchronous FULL and a canonical SHA-256-linked manifest.

Input configuration includes the receipt URL and exact receipt SHA-256; object URL and exact object SHA-256; source handoff SHA-256, high-water head/sequence; an Ed25519 key record with its separately supplied SHA-256 digest; and an exact configuration pin. A signed receipt must bind to the specified handoff/source high-water. A failed receipt or object readback rejects the entire acquisition, not a partial success.

## Evidence boundary

Two GETs from distinct hostnames do NOT prove independently operated origins, separately witnessed elapsed time, remote object version immutability or external custody. Pinned public-key content is NOT independent evidence of who controls the key. The AETHER-300 receipt's remote-object identifier is an **unverified claim**; the caller-selected object URL and digest are not cryptographically bound by that receipt. Stronger identity and object-reference proofs require a future separately witnessed protocol. A local prefix pin can be rolled back together with the local ledger. Source mirrors are one ancestry.

Every result preserves operational authority HOLD, physical qualification 0%, and false independent-custody/time/retention flags. Earlier phases and immutable freezes remain untouched.

## Offline tests

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/301 -p 'test_*.py' -v

Tests use ephemeral Ed25519 fixture keys and entirely mocked HTTPS responses. The test suite covers signature substitution, source mismatch, changed raw bytes, partial-failure transaction rollback, nonce replay, third-window exclusion, changed high-water pins and corruption recovery. No live remote endpoint or custodian has been contacted by authoring the code.

## Explicit opt-in live acquisition

    python3 aether/301/remote_custody_readback.py capture --db /tmp/aether301.sqlite --config pinned-custody-config.json --pin <sha256> --nonce first-window-nonce-301
    python3 aether/301/remote_custody_readback.py capture --db /tmp/aether301.sqlite --config pinned-custody-config.json --pin <sha256> --nonce second-window-nonce-301

Read-only recovery and historical pin comparison:

    python3 aether/301/remote_custody_readback.py audit --db /tmp/aether301.sqlite --config pinned-custody-config.json --pin <sha256> --prefix-seq 1 --prefix-head <sha256>

Next AETHER-302-RS: bind receipt statements to exact provider object URI/version/length/digest and independently attested service-operator identity, then test evidence across authenticated observation windows without upgrading physical authority.
