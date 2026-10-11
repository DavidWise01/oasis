# LEELUU Source Lineage / Holdout Laboratory — Test 062

**Status: COMPLETED (two-scan A–E glyph robustness); full independently captured plate pending.**

## Experiment and exact provenance

After archival catalog Test061 found Bridgeman asset **AFF3514779**, Test062 undertook an actual computation on **the two locally available image files** from Tests052–053: the original 16×16 illustration crop (788 × 784 pixels) and the separately uploaded registered A–E photograph (246 × 784 pixels). The publicly accessible watermarked Bridgeman preview is at [AFF3514779](https://images-cdn.bridgemanimages.com/api/1.0/image/600wm.XXX.85971530.7055475/3514779.jpg); its bytes and the higher-resolution licensed file were **not** downloaded and **no quantitative pixel/image alignment against that preview occurred**. A public reseller credited Bridgeman for its own preview, so its image is not established as an independent second capture.

Frozen source-role counts **200 atomic-role glyphs + 54 operants + 2 witnesses = 256 addresses**; 109 prior image-similarity **model bonds** and 11 separate engineer-selected candidate grid adjacencies remain unchanged. The prior v53 20 processing conditions (4 margins × 5 thresholds) were applied only to the first source scan. Prior v52 frozen second-photo features were then used as the holdout outcome without adapting image-processing parameters.

## Independent-copy transfer test: the newly measured numbers

| Target and predictor | N | Spearman rho | Within-row permutation p (one-sided, 20,000) | Five-row bootstrap 95% interval |
|---|---:|---:|---:|---:|
| Glyph-specific original code variation versus 16-bit second-photo error | 56 | **0.3026** | **0.006850** | [+0.132, +0.549] |
| Original pairwise code-distance sensitivity versus second-photo pair-distance change | 93 | **0.0946** | **0.192540** | [-0.073, +0.258] |

**First conclusion:** Print glyphs whose 4×4 binary code changes more across the frozen 20 first-scan processing settings also tend to change more between the original and second photograph. That is modest but measurably positive rank association, when tested via within-source-row permutation. This is evidence for *predictability of reduced ink morphology*, not for element identities or atomic chemistry.

**Second conclusion:** The same trick does **not** convincingly predict the stability of pairwise glyph geometry. The pair ρ≈0.095, p≈0.193 is weak; the full 93-pair second-photo mean absolute edge-distance change is 2.075 code units. Sharing of endpoints/rows means even the permutation p-values are exploratory, not an independently sampled trial.

**Source-geometry feature definition:** each printed glyph was skeletonized, aligned to a 41×41 binary stamp and reduced to sixteen 4×4 occupancy bits. The two-scan Hamming mismatch averages 5.3393/16 bits. The 20 local margin/threshold variants include one guaranteed exact baseline; they are NOT twenty independent observed images.

## Only two out of eleven proposals are in second photograph

| Frozen complexity rank | Pair | First photo Hamming distance | Second photo distance | Holdout difference |
|---|---|---:|---:|---:|
| 4 | C8-C9 | 6 | 7 | 1 |
| 11 | A8-B8 | 7 | 7 | 0 |

The nine other proposed pairs (including the symbolic female K8–L8 and M8–N8 complexity anchor) lie partly or wholly below E and thus have **NO observed second-photo measurement**. The previously best stable pair K8–L8 remains best *within the first-image perturbation test only*; this test neither confirms nor refutes its held-out stability.

## Row-/endpoint-dependence and selection caveats

- All 56 visible glyphs come from just five printed rows A–E; 93 neighboring pairs share endpoints. The bootstrap of five row clusters is coarse and sensitive to dependent measurements.
- Our exact tests preserve the source-row occupancy; p-values are conditional on fixed selected images and features. The selected 11 source-pairs have undergone previous exploratory selection; do not interpret small p-values as a discovery of historical encoded information.
- We measured no spectrum, tissue sample, DNA sequence, nitrogen isotope or chemical bond. The speculative ATLANTEAN branch and the 1000-atom/24! symbolic LEELUU models remain computational/narrative constructs without physical verification.
- The Bridgeman catalog lists the full source image as 4961×4932 pixels and a medium as 1024×1018. Catalog existence and same printed subject do not establish independently captured photographic provenance; hosted resized watermarked previews may share a source.

## Next Test063 entry criteria

Obtain an authenticated **independent second complete engraving capture**, including F–P, with capture chain and rights. Pre-register segmentation; inspect source crop K8–L8 and M8–N8, and all background pairs on equal footing. Compare first-scan predictive code jitter against actual second-photo code/pair error; distinguish a repeated archive photo from a new capture by independent image provenance. Until then this test is **concluded, and the lower-grid independent experiment is blocked by missing evidence.**

## Reproducibility

- `analyze_v62.py` ingests unmodified v22 node/edge data, v41 atlas, v45 colors, v46 motifs, v52 full visible codes and v53 single-scan stability, plus the original cropped PNG and the user-supplied second photo. It runs **20,000 seeded within-row permutation controls** and **10,000 five-row bootstrap draws**. Fails closed if key legacy counts or source hash change.
- `build_lab_v62.py` generates a full **offline** data-image HTML (includes these two user-provided project image crops in JPEG, not the unlicensed archival file), 256-cell inspection, second-photo bitmask comparisons, glyph and pair scatter views, eleven candidate pair detail cards, archive provenance and Test063 export.
- `test_browser_v62.py` checks interactions with Chromium, including A8 and K8 observed-vs-missing logic. Packaging includes source files, frozen inputs, reproducible scripts and SHA256 manifest.

### External catalog links

1. Bridgeman catalog: <https://www.bridgemanimages.com/en-US/english-school-18th-century/the-writing-machine-from-the-academy-of-lagado-balnibarbi-in-travels-into-several-remote-nations-of/nomedium/asset/3514779>
2. Public watermarked preview, **not downloaded or analyzed as pixels**: <https://images-cdn.bridgemanimages.com/api/1.0/image/600wm.XXX.85971530.7055475/3514779.jpg>
3. MeisterDrucke reseller with explicit Bridgeman credit: <https://www.meisterdrucke.us/kunstdrucke/English-School/674370/Die-Schreibmaschine-aus-der-Akademie-von-Lagado%2C-Balnibarbi-in-Gullivers-Reisen-von-Jonathan-Swift.html>
## Executed release checks and committed HTML
- Exact offline HTML: `experiments/leeluu-source-lineage-holdout-lab-v62.html`; 737,404 UTF-8 bytes SHA256 `7dd0029df643abfe52e222c474097f472e8db148d386271b555d2e521ecd9287`; separately committed GitHub commit `d502c34e79c7f0fae0fb3ccdef73b578ce3ab467`.
- 29/29 real Chromium browser tests passed, zero page JS exceptions.
- Full 27-member deterministic ZIP `LEELUU_v62_Source_Holdout_Bundle.zip`: SHA256 `3a6bd8a0c4c75bab8900719f3e8cdc58ae3a203406275c556d03b7b119118fed`, CRC and per-file SHA256 verified; contents include original user-supplied source images, original CSV data, measured CSVs, source analysis, 20k row-stratified shuffled controls, 10k 5-row bootstrap, offline HTML, user-viewable preview, browser script and SHA256SUMS manifest.
- CLEANROOM fully extracted the ZIP into a new directory, reran Python computational analysis, regenerated the HTML, regenerated the report, reran all 29 browser checks and repacked deterministic ZIP. Six key output files including ZIP matched their original bytes by SHA256.
- The Bridgeman watermarked thumbnail was VIEWABLE on official catalog and direct public image link; attempts to acquire file bytes into computation failed in this runtime, and therefore there is no archived-preview pixel test. Do NOT claim image-pixel analysis of AFF3514779. External archival link and photo credit retained in HTML.
- GitHub audit establishes execution provenance without modifying old Test022–061 model graphs or classifying any symbolic chemistry as physical fact.
