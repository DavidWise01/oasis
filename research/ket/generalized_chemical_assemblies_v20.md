# KET Experiment 20: Beyond neighboring shell closures (2026-10-23)

## Claim under test
`|` is a typed boundary/commit operator for any independently validated shell, bond, coordination assembly, or extended network—not only for noble gas closures or adjacent atomic numbers.

## Executed local test
15 curated cases; verified 15 unique case names, 3 coordination entities, 13 established chemistry examples, 2 special cases requiring careful evidence separation. Full CSV `assembly_cases.csv` available in conversation artifact. These are manually curated examples and classification checks, **not** exhaustive compound enumeration nor energy/stability computation.

| Case | Category | Interpretation |
|---|---|---|
| H2, H2O, NH3, CH4, CO2, HF | Molecules | Covalent/polar-covalent bonded species |
| BeH2, B2H6 | Special molecules/solids | Bridging or electron-deficient arrangements |
| NaCl, SiO2 | Extended materials | Ionic or covalent-network lattice |
| [Ag(NH3)2]+, [Zn(CN)4]2-, [PtCl6]2- | Coordination | Ligands attached to one central metal ion |
| Li→Be | Atomic-number sequence | Filled 2s² subshell at Be; **not** evidence of LiBe bond |
| BeLi PubChem record | Registry caveat | Formula entry exists but its given InChI lists separate elements; existence of entry alone is not bond verification |

## Proposed typed closures
- `|subshell`: independently verified electron subshell endpoint.
- `|bond`: molecular identity, bond evidence, and conditions documented.
- `|network`: repeated solid arrangement identified structurally.
- `|coordination`: metal/ligand geometry and donor count documented.

Pass criteria for a physical closure: source-backed existence and identity, structural relationship, and appropriate environment; stability has to be qualified by temperature/pressure/phase where relevant. Failure or uncertainty must be retained, not silently treated as a stable ring.

## References
- NIST Chemistry WebBook: https://www.nist.gov/programs-projects/nist-chemistry-webbook
- UMN ChemData enumerations: https://chemdata.r.umn.edu/api/tables.php/
- Purdue coordination examples: https://www.chem.purdue.edu/gchelp/cchem/whatis.html
- IUPAC coordination definition: https://goldbook.iupac.org/terms/view/C01326
- PubChem LiBe record: https://pubchem.ncbi.nlm.nih.gov/compound/Lithium-beryllide

## Next falsification
Evaluate nonadjacent 2-element pairs with documented compound evidence and counterexamples, then expand to structural graphs (triangles, tetrahedra, chains, rings, lattices), and test whether the typed KET closure predicts stability or only describes known outcomes.

KET frozen 184/257 baseline unchanged.
