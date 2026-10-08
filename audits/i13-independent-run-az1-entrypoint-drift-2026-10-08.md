# Independent geometry benchmark — 2026-10-08

## Historical I13 witness: executed
Exact source: DavidWise01/I13-H1.1@19bf953ec293c7c371ca53a305638a53e30693cc file bench/toroidal_witness/run_frozen_test.mjs (blob 24869968e3d71dba517169880f02a17cefd72ded).
Run with Node v22.16.0 in isolated sandbox. Output:
- expected=55296, observed=55296
- verified=27648, unverified=27648
- mutationFailures=0, status=PASS
- receipt SHA-256 f0dbbdba8fa760562e4df783f34b7e25e64cd595ec2e4dbcfce913b1baea9b76
- This is direct reproduction of the script's finite enumeration. Note the script defines before/after as the same interpolated payload; zero mutations test a deliberately read-only witness rather than arbitrary adversarial mutators. Do not claim physical PDE proof.

## AZ1 documentation vs actual entrypoint
Source: DavidWise01/az1 README.md blob 54c881ae36851378c8575d04732a36e15dc7c3d2 describes repository-token citizens, hybrid breeding, generation counts 600 etc.
Current index.html retrieved via GitHub connector, 241,717 characters, title 'AZ1 · Universe One — 9 planets, real gravity, in 3D'. Search in retrieved HTML: no literal fitness, hybrid, localStorage, citizens; the page visibly implements a planetary 3D scene.
Status: DOCUMENTATION/ENTRYPOINT VERSION MISMATCH, not evidence that an agent simulation was never written or no longer exists. Search other historical files/commits before executable benchmark.

## Next tests
Retrieve historical AZ1 commit actually containing simulation, pin original entrypoint, and run deterministic seeded evolution tests including bounded population, ability to reproduce, clear distinction of repository-derived vs generated concepts. Test UD0 links and world routing separately.
