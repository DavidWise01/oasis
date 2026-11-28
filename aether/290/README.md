# AETHER-290-RS — External High-Water Retention Claims and Ancestry Qualification

This opt-in collector fetches three byte-exact canonical JSON retention records using the AETHER-264 bounded HTTPS collector. A signer must produce an Ed25519 signature over a statement bound to: endpoint and controller IDs, fresh capture nonce, current AETHER-288 acknowledgment batch sequence and head, acknowledgment nonce count, source artifact SHA-256, and a declared retention-until value.

The verifier requires an explicit out-of-band SHA-256 pin of the supplied trust record and checks overlapping ancestry between claimed controllers and the journal. Within one SQLite transaction, it persists the original acquisition observation including raw body bytes, URL, source signature and claimed retention data (embedded in response), chain head, and three replay-protected record nonces. Recovery verifies the recorded observations, body and chain hashes, nonce assignments, and historical high-water pins; rollback or deletion of the acknowledgment journal is rejected.

**Strict evidence limits:** the retention-until field is a signed claim, not proof that external storage actually exists, remains immutable, or is retained until that time. Distinct HTTPS hostnames, independent-looking ancestry declarations, and three signatures may all be controlled by the same origin. Without externally authenticated trust-root ownership and witnessed long-term readback, independent custody is not established. This implementation has no physical ACT and cannot grant release authority.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/290 -p 'test_*.py' -v
    python3 aether/290/external_highwater.py capture --db /tmp/aether290.sqlite --ack-db /tmp/aether288.sqlite --trust trust.json --endpoints endpoints.json --pin <sha256> --challenge fresh-retention-challenge-290 --artifact-sha256 <sha256>
    python3 aether/290/external_highwater.py audit --db /tmp/aether290.sqlite --ack-db /tmp/aether288.sqlite --prefix-seq 1 --prefix-sha256 <sha256>

Tests use mocked HTTPS, actual temporary SQLite and freshly generated Ed25519 test keys; **no real endpoint is queried** by the tests. Historical phases XVIII/XIX remain frozen and all previous AETHER modules are unmodified.

Next AETHER-291-RS: independently witnessed retention readback after separate observation windows; verify actual immutable-object storage metadata and independently established operator identity, not merely signed claims.
