# AETHER-254-RS — Linux pidfd Exit Transcript

The executable observer launches only a fixed, non-networking Python child that waits for a one-byte release and then exits with code 7. It reads the child's /proc stat while the child is alive, opens a pidfd, releases that child, polls for pidfd exit readiness, obtains waitid(P_PIDFD) data and reaps the direct child. The bounded observation includes boot ID, namespace inode, start ticks, kernel wait status, monotonic elapsed time and a deterministic SHA-256 digest.

The CLI intentionally exits nonzero on all paths. A valid child-exit observation never authorizes lock reclamation, process intervention, recovery or physical ACT. The fixed child is not an external production process; the signed/externally witnessed provenance of the kernel remains unverified. On unsupported kernels the observer fails closed. It never kills or signals an unexpected process.

Tests include a local integration case on Linux with pidfd support; on restricted systems permission errors can skip that test and must not be treated as a live pass.

Run:

    python3 -m unittest discover -s aether/254 -p 'test_*.py' -v
    python3 aether/254/pidfd_exit.py --out observation.json
    python3 aether/254/pidfd_exit.py --review observation.json

Review checks raw transcript digest and invariants and retains HOLD, 0% physical qualification. Previous Phase XVIII and XIX freezes remain unchanged.

Next AETHER-255-RS: externally attested pidfd transcript with fixed-child ancestry, cross-host replay protection, and independently pinned observer keys.
