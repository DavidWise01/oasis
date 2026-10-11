# ROOT0 P4.59 — live separate Unix UID TLS request execution (2026-10-10)

**PASS 37/37**, two runs of Node.js v22 local regression (1023.046 and 1058.637 ms) with OpenSSL and Linux setpriv. Witness service runs as UID 1000, actual signed TLS controller READ as UID 33, actual signed TLS rotation-role request as UID 65534. Rotation Ed25519 signing role denied READ. Cross-account signing-key file reads refused; witness UID1000 unable to read controller key. Inherited P458 signed policy rotation, replay, rollback/fork rejection, restart and SQLite persistence tested.

**Limits:** controller and rotation role each have separate Ed25519 request signing private keys but copied X.509 client credential for test. The rotation request from UID65534 established connectivity/authenticated request handling but did **not** execute a signed successful ROTATE from that UID because policy payload was not passed to worker. All UIDs share one kernel and root administrator; independently administered remote anchor remains untested. No hosted CI result verified.

**Roadmap 14/20 = 70%**, unchanged pending actual independent-host custody. GitHub worker committed; complete P459 executable test and dependency sources in download ZIP SHA256 e5cd4111c0f4bbbd815bf57997e1bdd3a88a4d18580496c29768e9aa27198c61.

Next P4.60: full role-specific certificates, execute signed ROTATE as separate unprivileged role; then remote-host custody with independent administrators.