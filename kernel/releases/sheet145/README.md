# SHEET 145 — Resource-Side Recovery Fencing

**Test status:** 60/60 new regression checks passed. Inherited SHEET 144 lineage: 957 checks passed on rerun, but the initial inherited attempt failed the previously documented timing-sensitive SHEET 142 simultaneous-request assertion. Therefore the total **1017/1017** is a successful *rerun*, not a claim of consistently reproducible full-suite passing.

## Objective

SHEET 144 allowed a quorum-approved operator to reconcile an existing durable resource receipt after a hard crash. SHEET 145 closes a remaining *cooperative-resource* recovery gap: an old writer process holding a previously valid token must not be able to write after recovery advances the generation.

The new entry point `fence145.guardedWrite` serializes all cooperating resource mutations with `fence145.recover` using a common filesystem lock. A signed writer token binds generation, writer identity, operation ID, and an expiry window. A signed external checkpoint and an optionally independently retained checkpoint establish the minimum acceptable generation.

## Hard safety rules

1. **Durable fence first.** After a 2/3 signed recovery decision and immutable receipt check, persist a monotonic generation advance before releasing the orphaned transaction lock.
2. **Fail closed on incomplete cutover.** If the local generation is ahead of its signed external pin, all guarded writes are held until an authorized retry completes checkpoint installation.
3. **Fail closed on pending receipt.** A matching generation-two pin alone cannot enable writes. The SHEET 144 recovery ledger must show `RECOVERED` for the cutover plan.
4. **Old token is not grandfathered.** Even an idempotent request bearing an old-generation token is rejected before the inherited resource writer is invoked.
5. **Never fabricate the resource write.** SHEET 144's durable evidence controls reconciliation. If the receipt is missing, the original orphaned lock is not silently released.
6. **Independent rollback floor.** A separately retained signed checkpoint catches restoration of both mutable local files to an older generation, assuming the independent checkpoint has not itself been rolled back.
7. **No automatic orphan-lock revocation.** If the SHEET 145 lock is left behind by a true hard crash, manual verification is required. This release does not bypass or auto-clear it.

## Files

- `fence145.js` — standalone new guard and recovery adapter over the unmodified SHEET 144 baseline.
- `gate145.js` — deterministic and adversarial regression tests, including hard crash, pre-pin and post-pin failure injection, rollback, forged signatures, concurrent guard access, and stale-token resurrection.
- `writer145.js` — separate-process stale-writer replay test.
- `index.html` — interactive read-only SVG demonstration with six scenarios; it does *not* run the Node.js kernel in the browser.
- `KERNEL-ASCII.txt` — full SHEET 145 integration diagram.
- `baseline144/` — byte-preserved inherited kernel.
- `run-all.sh` — runs inherited checks in a temporary copy and the new gate.
- `SHA256SUMS` and `release-receipt.json` — release checksums and verification summary.

## Run

Node.js 22+ and Bash recommended:

```sh
cd sheet145
node gate145.js
bash run-all.sh
```

The full runner can intermittently fail an inherited SHEET 142 assertion in which simultaneous network requests are expected to overlap inside the lock; occasionally both requests run sequentially and pass. **The frozen inherited test remains unchanged**. The standalone SHEET 145 tests cover the new shared fence directly.

## Security boundaries

- This release demonstrates **cooperative local filesystem fencing**. Writers with direct, privileged access to the resource file can bypass the guard. Lock correctness is not equivalent to independently enforced fencing on remote storage or an external service.
- Keys are ephemeral local test keys, not production credentials. The optional externally retained floor was simulated with a distinct local file and does not provide third-party custody.
- The transition spans more than one filesystem object and is **recoverable/fail closed**, not physically atomic across disks or independent hosts.
- Full multi-host linearizability, hardware-protected signing, original SHEET 103 fixture compatibility, and production authorization remain outside verified scope.