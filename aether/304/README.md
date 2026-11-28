# AETHER-304-RS — Pinned Registry and Clock Source Readback

AETHER-304 performs an **opt-in read-only HTTPS source readback** of the already-frozen AETHER-303 signed registry and clock claims. Its acquisition plan SHA-256-pins the complete qualification bundle and controller-root document, and names four exact HTTPS endpoints: registry epoch 1, registry epoch 2, clock window 1, and clock window 2. Registry endpoint hostnames must agree, clock endpoint hostnames must agree, and those two hostnames must differ.

The collector reuses the bounded AETHER-264 TLS hostname-checking, public-DNS-address-pinned HTTPS GET acquisition through AETHER-294's exact-byte observation parser. It accepts each remote response only when the **raw response bytes exactly match canonical JSON** of the corresponding signed AETHER-303 statement. AETHER-303's full dual-signed key-rotation and signed-time qualification must also pass. A signature is checked against supplied pinned keys, not independently established controller identity.

A successful 4-response readback is recorded atomically in a SQLite WAL journal with synchronous FULL and a SHA-256-linked canonical manifest. Each local capture requires a new nonce and only two observation windows are accepted. The read-only audit verifies all retained raw bytes and observation transport digests, source head and root pins, historical chain continuity, and an optional caller-supplied external prefix checkpoint.

**Assurance boundary:** HTTPS provides authenticated service-name transport under the platform's CA trust, but domain names, TLS certificates, registry signatures and distinct endpoints do not themselves prove separately operated controllers or external custody. Clock timestamps are independently **claimed** numbers, not an independently verified elapsed-time interval. A configuration pin or external high-water supplied by the operator can be rolled back together with the source history. This phase does not perform an authenticated controller-ownership challenge, provider-side object version readback, or remote immutable-storage proof. The output always stays `operational_authority: HOLD`, `physical_act_allowed: false`, `physical_qualification_percent: 0`. The GitHub and 0root.ai copies belong to one owned ancestry.

## Offline regression

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/304 -p 'test_*.py' -v

Twenty authored regression cases use ephemeral signing keys and mocked HTTPS observations; no live registry or clock service is contacted in CI.

## Explicit opt-in capture

    python3 aether/304/controller_readback.py capture --db /tmp/aether304.sqlite --plan approved-plan.json --bundle signed-303-bundle.json --roots pinned-303-roots.json --plan-sha256 PLAN_DIGEST --roots-sha256 ROOTS_DIGEST --nonce first-observation-nonce-304

Run a separate invocation with a **different nonce** for the second local observation. Source URLs, roots, bundle and pins must not change.

## Offline recovery

    python3 aether/304/controller_readback.py audit --db /tmp/aether304.sqlite --plan approved-plan.json --bundle signed-303-bundle.json --roots pinned-303-roots.json --plan-sha256 PLAN_DIGEST --roots-sha256 ROOTS_DIGEST --prefix-seq 1 --prefix-sha256 EXTERNALLY_RETAINED_HEAD

## Next natural bound — AETHER-305-RS

Establish externally observed controller-key ownership via a separate challenge/response witness, capture authenticated service ownership evidence without relying only on self-declared controller graphs, and qualify non-operator-controlled clock custody and high-water storage. Do not advance the physical authority gate.
