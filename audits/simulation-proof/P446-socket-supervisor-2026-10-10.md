# ROOT0 P4.46 — socket recovery and cross-UID regression (2026-10-10)

Node 22.16.0 on Linux local final rerun:
- New `test_p446.mjs`: **8/8 assertions PASS**; 33.939 ms. Missing pathname, non-socket file, UID mismatch, active listener denial, SIGKILL-orphaned Unix socket recovery, and repeat absent check.
- Inherited `test_p445.mjs`: **13/13 assertions PASS**; 443.545 ms. Uses witness UID 65534 and controller UID 33, tests socket ACL, key/DB read denial, authenticated CAS, replay and restart.
- New `p446_socket.mjs` and `test_p446.mjs` committed and fetched back from GitHub successfully.

**Security caveat:** probing a refused socket, checking device/inode and unlinking still permits a privileged or hostile process to race the final unlink. This helper must only be used by a trusted supervisor in a protected directory, and the current P445 service does not automatically integrate it. The older P4.43 `p443_atomic.mjs` dependency is still not committed in GitHub; the downloadable ZIP contains the runnable chain, but the GitHub P445 checkout remains incomplete. Hosted GitHub CI and external host custody are not verified.

Reproducible ZIP SHA256: `003b174707c8ed7df2acc5f16da7c3530dcafb8dda05b2d51d32244b14b20af9`. Next P4.47: commit P443 dependency and P445 regression, test clean checkout; move trusted socket supervision to service manager rather than unlink logic.