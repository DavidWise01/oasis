# Z325 — 24! capacity boundary

Classification: mathematical/symbolic, not physical element discovery. Frozen KET remains unchanged.

For 24 distinguishable freely permuted objects, 24! = 620448401733239439360000 configurations. This is not the count of RGB occupancy configurations: (3,1,2) has six distinct permutations. With three labeled RGB lanes of eight labeled addresses, independent within-lane permutations = (8!)^3 = 65548320768000. Placing unlabeled occupancy markers with fixed R/G/B counts 3/1/2 gives C(8,3)*C(8,1)*C(8,2)=12544 possible occupancy sets. If six markers are individually labeled and can use any 24 addresses, P(24,6)=96909120. If markers are labeled and channel constrained, P(8,3)*P(8,1)*P(8,2)=150528.

Local Python /mnt/data/z325/test_z325.py executed: 10/10 PASS, including 1005 rank/unrank samples (fixed seed plus boundaries). The test does not enumerate 24! states and establishes no quantum advantage. Factoradic indexing permits deterministic integer-to-permutation conversion and back, assuming all 24 objects are distinguishable. Cr24 layer remains optional and 5/3/1 independent.
