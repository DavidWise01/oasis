# P3.24 — Stargate is primitive, sides variable

User correction: `-+- /\\ +-+` is the structural primitive; either side can take an arbitrary **finite, valid** size provided the sides have opposite parity (one even, one odd). The pinned root remains 0. The legacy 255 non-root stages and 1 root correspond to only one instance, 128+127+1=256; the 256-state cipher remains a specific configuration, not a universal size constraint.

Implementation: `p324_primitive_stargate.mjs` and `test_p324.mjs` introduce `(even,odd,evenSide)` parametrization, alternating stages while both arms have capacity, then finishing the longer arm, and applying inverse gates in reverse order. The 100000 non-root stage guard is computational only. Gates remain illustrative mathematical 3-port unitaries and do not establish physical transport.

Executed independent JavaScript mathematical benchmark in tool runtime: 1,200 cases across (2,1), (4,3), (10,9), (128,127), (256,255), (1024,1023), both side orientations, 100 randomized complex three-channel initial states per orientation. PASS. Maximum norm discrepancy 1.3011813848606835e-13, max recovery component error 4.296563105299356e-14. Exact committed Node regression was not separately executed, and remote CI remains unverified.

Next P3.25: test arbitrary unbalanced opposite-parity arm pairs and formalize schedule independence versus noncommuting arm order. Do not misinterpret root-zero as a sink for conserved energy.
