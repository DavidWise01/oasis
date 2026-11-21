# AETHER-086 — Distribution-Aware Evidence Transfer

Invariant 086: Historical evidence earns influence through demonstrated relevance to present conditions, not simply through its quantity or age.

Eight synthetic evaluation seeds (86000–86007), six environmental mechanisms, 20 batches per regime, 300 held-out cases per batch: 288,000 cases **per policy**. Three policies: global historical residual pooling, local 80-label audit only, and a median-error similarity gate selecting whether to combine 400 historical labels with the current 80.

| Policy | Wrong-sign authorizations | Authorized |
| --- | ---: | ---: |
| Global transfer | 427 | 254782 |
| Local only | 194 | 242334 |
| Similarity gate | 413 | 255660 |

The similarity-gated policy fails especially for asymmetric outliers (399 incorrect vs 183 local-only). Median absolute residual matching does not imply matching tails or conditional decision risk. No unconditional performance or 2% conditional-risk guarantee is claimed.

Public interactive report: https://davidwise01.github.io/oasis/aether/086/

Next: AETHER-087 tail-aware transfer, with targeted conditional-risk testing and evidence-lineage controls.

.dlw
