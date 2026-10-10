# P4.12 deployment-wide genesis stress audit (2026-10-10)

Local Node 22.16.0 run: 11 assertions passed. 24 independent processes with different signed grants for one deployment: 1 accepted, 23 rejected. A different grant aimed at a second authority database for the same deployment is blocked by a deployment-scoped exclusive-create reservation. Missing registry fails closed; interrupted initialization retains the reservation.

Critical remaining vulnerability: erasing and reprovisioning the local registry permits an old signed grant to initialize another authority. This is local filesystem coordination, not independent trusted non-rollbackable history, distributed consensus, hardware timing, or real power-failure resilience. An earlier test attempt experienced a child-output failure under contention; final rerun passed in 402.42ms. The complete executable local package is included in the conversation ZIP.

Next P4.13: externally attested single-deployment witness and process-termination fault matrix.