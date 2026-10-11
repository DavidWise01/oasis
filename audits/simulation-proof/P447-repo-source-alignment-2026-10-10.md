# ROOT0 P4.47 — repository source synchronization (2026-10-10)

**Locally PASS 21/21** (P445 13/13, 465.345 ms; P446 8/8, 35.540 ms) in dependency-only clean staging directory, Node v22.16.0, Linux root and setpriv. Local syntax checks passed.

Committed missing `docs/reality-tensor/dyson-inversions/p443_atomic.mjs`, `test_p445.mjs`, and `p445_client.mjs`. The local fresh-directory run exposed test startup race: `stat(socket)` could return before chmod 0660. Committed fix waits for socket mode 0660. Repeated clean staging tests PASS.

Confirmed GitHub fetch of p443_atomic.mjs, p445_client.mjs, test_p445.mjs, p446_socket.mjs and test_p446.mjs. The P445 service was already in GitHub. Latest code fix commit `7a165f8834fd0d4153217a5705e42bfe11fe6a3d`. Combined GitHub status API returned no statuses: **hosted CI unverified**. No full remote checkout was performed (container network DNS to github.com unavailable); verified local dependency-only staging, not entire repository. Trusted socket recovery still requires a supervisor with a protected directory; helper may be raced by privileged processes. Same-host two UID isolation is not independent-host custody.

ZIP `p447_bundle.zip` sha256 `9d4c55fc4049bf83fb32689a6e1731009a75f824824fa074966764d351962ed8`.

Next gate: P4.48 add a repo workflow and supervise socket via socket activation, plus remote independent anchor design.