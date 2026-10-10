# SHEET 211 — OS-Enforced WAL Identity Isolation

**Executed in a Linux root test environment:** 14/14 local OS permission checks PASS. Protected writer directory owned by `daemon`, permission mode 0700; WAL owned by `daemon`, mode 0600. Unprivileged `nobody` is denied WAL read/append/unlink/chmod and directory traversal, whereas `daemon` can append. This closes the tested *different-UID* bypass of S210's filesystem.

**Important scope:** Only POSIX filesystem identity isolation was tested here. No live S210 service or original S176 Node writer was launched under `daemon` during this gate. Root, same-UID users, and privileged processes remain outside this protection. No independent signed authority, orphan repair, physical crash durability, SELinux/AppArmor policy, cross-host isolation, or full inherited regression run was tested.

Run the attached `gate211.py` with Linux root permission; it explicitly SKIPs without privilege. Next S212: end-to-end S210 service under its own UID, authenticated socket client boundaries and post-SIGKILL signed repair reconciliation.
