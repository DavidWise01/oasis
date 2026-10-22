# Phase 2.3 — real three-node local etcd experiment

**STATUS: NOT EXECUTED — Docker unavailable in the authoring runtime.**

`compose.yaml` starts three isolated etcd v3.5.18 containers on loopback TCP ports 12379, 22379 and 32379. `run_cluster_test.py` checks membership health; IT3 byte equality across nodes; a 2/3 write after stopping the third member; denial of an isolated 1/3 write; majority recovery; and follower catch-up.

## Run (Docker Compose v2 required)

```sh
cd docs/y2038/phase2_cluster
python3 run_cluster_test.py
python3 run_cluster_test.py --down
# to reset keys and volumes:
python3 run_cluster_test.py --clean
```

These are deliberately **INSECURE, test-only HTTP** endpoints bound to localhost. This fixture does NOT satisfy Phase 2.2's HTTPS/mTLS backend, nor Step 20 production evidence. No credentials are packaged.

This test uses Docker Compose, not three separate physical hosts, and cannot prove power-loss durability or a fault-free Raft implementation. Results must be independently executed and archived. Failing/timeout behaviors should be treated as failures, not skipped. Existing keys will conflict on second execution until volumes are reset.

Source reference: official etcd container-cluster setup, https://etcd.io/docs/v3.2/op-guide/container/.

Production release gate: BLOCKED.
