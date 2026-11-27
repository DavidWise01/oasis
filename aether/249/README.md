# AETHER-249-RS — Linux Restricted-Namespace Socket Outcomes

A new Linux subprocess harness invokes `unshare --net` and runs bounded socket attempts **only if** the child's network namespace differs from the parent's and the child exposes no network interface other than loopback. Any failure to create/verify that namespace stops before the socket probes. No fallback to the host namespace is permitted.

Four low-level socket probes record kernel errno and monotonic elapsed time: loopback, RFC1918, link-local and metadata IP. The redirect and DNS rebinding categories are explicitly NOT_MEASURED; neither can be established by a bare socket connect. The tool never interprets ECONNREFUSED or other error as proof that a firewall blocked egress.

Use: `python3 aether/249/socket_probes.py --out report.json`

Offline tests: `python3 -m unittest discover -s aether/249 -p 'test_*.py' -v`

The harness does not cryptographically authenticate the subprocess, namespace, kernel, time source, custody, or independent witnesses. Python worker JSON is untrusted diagnostic data, not a qualification verdict. No external network run is claimed. Exit status for the supervising CLI remains nonzero, operational authority HOLD and physical qualification 0%. Earlier Phase XVIII and XIX freezes remain unchanged.

Next AETHER-250-RS: separate trusted observer captures namespace inodes, routes and raw syscall transcripts, and independently signs the bounded evidence digest without enabling ACT.
