/** Additive A.I.O.N. adapter to the ALON module. No alteration of frozen K.E.T. or ALON source. */
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
// Prefer the genuine repository module when installed in oasis/alon-separate/ket-aion-runtime/.
// Keep a tested source-compatible standalone snapshot for portable execution.
const upstream=new URL('../../material-build/alon-crystal.mjs',import.meta.url);
const moduleURL=existsSync(fileURLToPath(upstream))?upstream:new URL('./alon-crystal.mjs',import.meta.url);
const {buildAlonCrystal,alonToCif,alonToXYZ}=await import(moduleURL.href);
import {writeFileSync, mkdirSync} from 'node:fs';
import {join} from 'node:path';
const dir=process.argv[2];
if(!dir)throw new Error('Usage: node bridge.mjs OUTPUT_DIRECTORY');
mkdirSync(dir,{recursive:true});
const cell=buildAlonCrystal({seed:42,vacancySite:0,latticeAngstrom:7.95});
const counts=cell.counts;
const wraps=cell.bonds.filter(b=>b.periodicWrap).length;
if(counts.occupied!==55 || cell.totalBonds!==122 || wraps!==42 || cell.formalIonicCharge!==0)
  throw new Error('ALON reference structure invariants failed');
writeFileSync(join(dir,'alon-cell.json'),JSON.stringify(cell,null,2)+'\n');
writeFileSync(join(dir,'alon-cell.cif'),alonToCif(cell));
writeFileSync(join(dir,'alon-cell.xyz'),alonToXYZ(cell));
console.log(JSON.stringify({schema:cell.schema,formula:cell.reference.formula,occupied:counts.occupied,
    bonds:cell.totalBonds,boundary_links:wraps,internal_links:cell.totalBonds-wraps,
    density_g_cm3:cell.densityGcm3, formal_ionic_charge:cell.formalIonicCharge,
    unrelaxed:cell.reference.topologyNotRelaxed}));
