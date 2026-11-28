# AETHER-302-RS — Signed Exact-Object Binding and Readback

AETHER-302 introduces a **new receipt schema**, rather than modifying the frozen AETHER-300 or AETHER-301 protocol. This Ed25519 statement cryptographically binds the handoff SHA-256, AETHER source head/sequence, exact HTTPS object URI (including query parameters), explicitly claimed immutable version ID, raw-object SHA-256, raw-object byte length and custodian receipt nonce. The pinned receipt bytes and a separately SHA-256-pinned public-key record must agree with an exact acquisition configuration.

Each opt-in capture uses the bounded AETHER-264 HTTPS collector, retaining raw signed-receipt and raw object observations from distinct allowlisted hosts in an atomic, SHA-256-linked SQLite window ledger. Exactly two windows are allowed, with a stable configuration, unique local window nonce and repeated signed-object version. Audit reconstructs the original body bytes, Ed25519 verification, signed URI/version/digest/length, retained manifest heads and optional historical prefix pin.

## Evidence boundaries

A verified signature establishes only that the holder of the pinned key signed the statement. It does NOT establish independently controlled custodian key ownership, provider-native immutable-version enforcement, independently witnessed elapsed time, or independent remote custody. Distinct DNS hosts do not necessarily indicate distinct operators. The object URL, version and digest are now part of the signed claim, which closes the AETHER-301 signed-receipt/object-reference gap **within this new protocol**, but a self-operated signer could still sign an entirely self-controlled object. Local SQLite history and locally held high-water pins are not immune to coordinated rollback. Do not promote operational authority from HOLD; physical qualification stays 0%.

Earlier phase files and historical freezes remain unchanged. Test cases use ephemeral Ed25519 keys and mocked HTTPS observations; no real custodian endpoints have been contacted.

## Offline regression

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/302 -p 'test_*.py' -v

## Explicit opt-in acquisition and recovery

    python3 aether/302/signed_object_binding.py capture --db /tmp/aether302.sqlite --config pinned-object-binding.json --pin <sha256> --nonce first-window-nonce-302

    python3 aether/302/signed_object_binding.py capture --db /tmp/aether302.sqlite --config pinned-object-binding.json --pin <sha256> --nonce second-window-nonce-302

    python3 aether/302/signed_object_binding.py audit --db /tmp/aether302.sqlite --config pinned-object-binding.json --pin <sha256> --prefix-seq 1 --prefix-sha256 <sha256>

Next natural bound — AETHER-303-RS: independently established custodian identity, signed key-rotation continuity, independently authenticated clock-source windows and provider-origin immutable-version proof. Do not conflate independently held keys with caller-pinned keys.
