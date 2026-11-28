# AETHER-303-RS — Custodian Registry, Dual-Signed Key Rotation & Time Windows

AETHER-303 adds a **read-only cryptographic qualification** for one custodian identity across two key epochs. It requires a separately SHA-256-pinned trust-root document holding an Ed25519 registry key, a clock-witness key, and a declared source/custodian/registry/clock ancestry graph. The evaluator refuses shared **declared** ancestry and cycles but does not mistake that operator-supplied graph for independently verified control.

The first registry attestation signs custodian ID, epoch 1 key digest and exact historical source head. The transition from epoch 1 to epoch 2 must be signed by **both** old and new Ed25519 keyholders over the same canonical transition statement, binding the source head and predecessor transition. The epoch 2 registry attestation must refer to the exact hash of epoch 1 registration and the new key digest.

Two time-window claims must be signed by the pinned clock key, independently tied to the exact source and receipt heads, chained through prior-claim SHA-256, unique by nonce and monotonically increasing by **claimed** milliseconds. These checks prove *signature consistency* and *claim order* only. They do not prove independently controlled registry authority, clock identity, clock accuracy, elapsed time or actual storage retention. The algorithm always returns operational authority HOLD, physical qualification 0%, with every independent-custody flag false.

The new module does not alter historical frozen phases, invoke external network requests, or perform privileged writes. Its 22 offline test cases use ephemeral test keys, malicious key substitution, skipped epochs, signature tampering, crossed controller ancestry, replayed time nonces and broken historical hashes.

Run offline:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/303 -p 'test_*.py' -v

Evaluate a completely operator-pinned claim bundle:
    python3 aether/303/identity_rotation_time.py --bundle signed-identity-and-time-bundle.json --roots pinned-controller-roots.json --roots-sha256 <SHA256_OF_CANONICAL_ROOTS>

These are application-defined Ed25519 records, not a standards-certified identity registry. Never infer custodian independence from possession of a valid key; nor infer a real time interval from two signed numerals. GitHub and 0root.ai are mirrored owned ancestry, not separate independent witnesses.

## Next natural bound — AETHER-304-RS

Obtain service-operated key registry evidence and reproducible domain/controller ownership attestations from separately controlled roots; compare key-rotation and time-chain claims against authenticated, live readbacks; add rollback-resistant externally held checkpoint status. Physical authority remains HOLD.
