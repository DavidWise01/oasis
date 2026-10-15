# FOUNDATION 2 = 1 :: CORTEX

**Name:** Cortex. **Job:** Orchestrator. **Unit designation:** `1`, independently of Foundation 1's `1`. **Silo level:** even box/vessel 02. This is one governing controller **above** the existing Foundation 1 multi-agent worker transport, **not** a second independent controller or a new kernel.

```text
              0ROOT :: T128
                     |
                PATRICIA
                immutable law
                     |
                STOCHIEON
                   support
                     |
       FOUNDATION 2 :: 1 :: CORTEX
       validate / queue / route / observe
                     |
       FOUNDATION 1 :: 1 :: STRONG
       WASM-A -> signed OBF2 -> WASM-B
                     |
             TOPH DO / RECORD
                     |
             ONE SHARED STATE
                     |
                SCALAR 0
```

## Concrete implementation

A standalone interactive HTML `OASIS_FOUNDATION_2_CORTEX_LIVE.html` is packaged for offline use in the conversation. It embeds the existing Foundation 1 browser artifact with two separately instantiated 23,197-byte Rust OBF2 WebAssembly processors (SHA256 `65bdc720738cc2102eea025666aad10894b75439cea6d731b22c81bf2569e337`) and adds one deterministic JavaScript scheduler (`cortex-core.js`). No separate foundation or kernel fork.

Cortex validates decisions **YES / NO / MAYBE**, all five independent VAINL task labels (`V`, `A`, `I`, `N`, `L`), and the six interior workspaces `-1:A`, `-1:B`, `-3:C1`, `-3:C2`, `-3:C3`, `-1:D`. The shared geometry is unchanged: ten alternating odd toroids (1,3,5,7,9) and even boxes (2,4,6,8,10) with an adjustable **2.875%** visual flex, and `{{ -1{} -1{} -3{} -1{} }}` interior workspace group.

The controller allows one active operation, at most six queued+active operations, and at most 128 distinct retained request IDs in volatile memory. Duplicate IDs with the same content share the original result; conflicting changes are rejected. A successful Foundation 1 `APPLIED` response must increment the shared journal by exactly one, while other responses must make no new commit. Ordinary YES/NO/MAYBE interactions pass through Cortex; Foundation 1 diagnostics remain individually accessible for troubleshooting.

## Acceptance evidence (2026-10-14)

Node 22 loaded the actual embedded Rust WASM module twice, verified distinct memories, exercised Ed25519 signed message transfer, and performed one focused Foundation 2 test: two unique intents each committed exactly once; a repeat shared the existing result; a conflicting reuse was rejected; invalid intent was rejected; bounded queue returned `BACKPRESSURE` on saturation. One subsequent valid event yielded a total of **3 shared receipts and 3 journal entries**. Test result: **PASS**. Chromium's `set_content` rendered both panels, 10 layers and 5 VAINL selections without page errors. Browser-origin WebCrypto execution has not been independently accepted in Chromium; Node WebCrypto was used in the integration pass.

## Scope and boundaries

A real Cortex **scheduler**, not an autonomous language-model thinker. VAINL roles are scheduling labels, not five separate artificial agents. Events, idempotency keys and receipts remain browser-host memory—not a persisted durable event journal or a cross-restart exactly-once guarantee. The virtual network is not TLS or independent hardware. The `+2s` scalar-zero update is simulated time bookkeeping, not a physical law.

**No mutation of frozen KET, `{{i}}`, OBS or Rust codec source.**

These **two `1` labels** name a strong worker base and a single coordinating Cortex. Authority remains top-down, with one committed outcome per unique accepted request during one host session.
