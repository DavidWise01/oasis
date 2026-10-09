# Lagado Test017 — X/Y/Z² nested symbolic atom test (2026-10-09)
Status: EXECUTED / EXPLORATORY MODEL / NO HISTORICAL DECIPHERMENT
Lineage: audits/lagado-translation-208-v16-2026-10-09.md
Frozen source CSV SHA256: f09fdf32794385e7118291a9780ab84a9abbdcb5ea5fa366760ff630c0c48caf
User capacity: 255+P16=256; 208 active; 48 reserve. Nested checkpoints 17,52,104,208. Preserve 1+1+2+(dotminus+dotplus)+8=16.

3D address construction: Original column x and row y each 0..15. Each frozen glyph contains two 2x2 layers z=0 stroke occupancy and z=1 endpoint occupancy. Signed dot charge q=(-2,-1,0,1,2) is retained separately from squared depth q²=(0,1,4), which loses the +/- sign. This is a computational model, not an inferred historical 3D location.
Counts: 208*8=1664 voxel addresses, 1595 occupied, 69 empty, 166 fully occupied. 32x32x2 tensor, two 6-connected components of sizes 1587 and 8; second is P16 witness. 382 neighboring source pairs (191 horizontal, 191 vertical); 1414 occupied face contacts.
Signed q distribution: -2:3; -1:40; 0:123; +1:39; +2:3.
q² distribution: 0:123; 1:79; 4:6.
Original neighbor counts: same q² 236/382, same signed q 217/382, same q² plus topology similarity >=2/3: 150/382.

Controls: 2500 seeded permutations per group; packets containing full frozen atom features are permuted jointly, with 208-position active mask held fixed.
Null unrestricted: mean same q²=188.184 p>=236=.0004; signed mean 160.290 p>=217=.0004; additional topology mean 120.933 p>=150=.0008.
Null within rows: mean same q²=200.955 p=.0004; signed 183.776 p=.0004; additional topology 135.164 p=.03159.
Null within columns: mean same q²=200.405 p=.0004; signed 171.671 p=.0004; additional topology 124.841 p=.0004.
Null within original 4x4 blocks: mean same q²=217.626 p=.00960; signed 196.579 p=.00120; additional topology 137.426 p=.05518.

CRUCIAL: Earlier frozen v14 active-dot inference explicitly optimized neighbor agreement of *unordered* dot families, which mathematically map to q². Thus significant q² clustering is a trained-in modeling goal, NOT independent evidence of an alchemical or historical 3D cipher. The added H/C/V topology metric does not pass the block-aware 0.05 control. The voxel cube is nearly entirely filled and therefore nearly entirely connected by construction.

Reproducibility: local lagado_xyz_v17_bundle.zip sha256 a337717217d038cb1d5d0a1f8ebc38e7335aac7dc88168cf6ce3b85f38a30da8. Contains executable Python, original v16 CSV, derived atom and contact CSVs, statistics JSON, interactive standalone HTML, technical report and Chromium screenshot. ZIP CRC PASS, Node JS parse PASS; Playwright Chromium set_content PASS, 208 dropdown options and 6/6 in-page checks, signed/squared/voxel view switching, P16 selection and eight-plane inspector, no page errors.
Next test: hold out independent shape topology and use an independent source scan, preserving full optimizer-aware block and column controls.