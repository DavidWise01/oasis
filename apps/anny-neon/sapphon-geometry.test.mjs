import test from "node:test";
import assert from "node:assert/strict";
import {ANNY_GEOMETRY_REFERENCE,projectSapphonGeometry,validateSapphonGeometry} from "./sapphon-geometry.mjs";
import {SAPPHON_SPECTRUM,SAPPHON_BROADBAND,SAPPHON_OUTER_ANCHORS} from "./sapphon-spectrum.mjs";
import {RADIATION_OVERLAY} from "./radiation-overlay.mjs";

test("all selected overlays project into distinct photon and particle axes",()=>{
 const p=projectSapphonGeometry(["gamma","xray","alpha","beta"]);
 assert.equal(validateSapphonGeometry(p),true);
 assert.deepEqual(p.photon.map(x=>x.id),["gamma","xray"]);
 assert.deepEqual(p.particle.map(x=>x.id),["alpha","beta"]);
 assert(p.photon.every(x=>x.placement==="shortwave-adjacent"));
 assert(p.particle.every(x=>x.placement==="orthogonal-particle-axis"));
});
test("no radiation selection yields no phantom overlays and preserves seven signed pairs",()=>{
 const p=projectSapphonGeometry([]);
 assert.equal(p.photon.length,0);
 assert.equal(p.particle.length,0);
 assert.equal(p.photonAdjacencyActive,false);
 assert.deepEqual(p.pairs.map(x=>x.color),["Violet","Indigo","Blue","Green","Yellow","Orange","Red"]);
 assert.deepEqual(p.pairs.flatMap(x=>x.slots).sort((a,b)=>a-b),Array.from({length:18},(_,i)=>i+1));
 assert.equal(validateSapphonGeometry(p),true);
});
test("gamma and X-ray overlap allowed, never given numeric cutoffs",()=>{
 const gamma=projectSapphonGeometry(["gamma"]).photon[0];
 const xray=projectSapphonGeometry(["xray"]).photon[0];
 assert.equal(gamma.wavelengthNm,null);
 assert.equal(xray.wavelengthNm,null);
 assert.equal(gamma.placement,xray.placement);
 assert.equal(ANNY_GEOMETRY_REFERENCE.shortestVisibleNm,380);
 assert(!Object.hasOwn(gamma,"color"));
});
test("particle charge is not Sapphon symbolic polarity",()=>{
 const p=projectSapphonGeometry(["alpha","beta"],"Green");
 assert.deepEqual(p.particle.map(x=>x.charge),["+2e","−e / +e"]);
 assert.equal(p.focus.minus.polarity,"−");
 assert.equal(p.focus.plus.polarity,"+");
 assert.equal(p.photonAdjacencyActive,false);
 assert(p.particle.every(x=>x.wavelengthNm===null));
});
test("focus switches Greek endpoint labels without changing photon state",()=>{
 const p=projectSapphonGeometry(["xray"],"Red");
 const g=projectSapphonGeometry(["xray"],"Green");
 assert.deepEqual(p.photon,g.photon);
 assert.equal(p.focus.color,"Red");
 assert.equal(g.focus.color,"Green");
 assert.equal(p.focus.minus.name,SAPPHON_SPECTRUM[0].minus.word);
 assert.equal(g.focus.plus.name,SAPPHON_SPECTRUM[3].plus.word);
 assert.equal(p.focus.minus.nm,620);
 assert.equal(g.focus.plus.nm,570);
});
test("unknown focused pair fails closed",()=>{
 assert.throws(()=>projectSapphonGeometry([],"Teal"),/ANNY_GEOMETRY_UNKNOWN_BAND/);
});
test("VOID, GRAVITY, and broadband White remain without assigned wavelengths",()=>{
 const p=projectSapphonGeometry(["gamma","alpha"]);
 assert.deepEqual(p.anchors.map(x=>x.operator),["--","++"]);
 assert(p.anchors.every(x=>x.wavelengthNm===null));
 assert.equal(p.broadband.name,SAPPHON_BROADBAND.color);
 assert.equal(p.broadband.wavelengthNm,null);
 assert.equal(SAPPHON_OUTER_ANCHORS.length,2);
});
test("pure projection does not mutate registries, receipts, or routing",()=>{
 const originalBands=JSON.stringify(SAPPHON_SPECTRUM);
 const originalRadiation=JSON.stringify(RADIATION_OVERLAY);
 const originalOuter=JSON.stringify(SAPPHON_OUTER_ANCHORS);
 projectSapphonGeometry(["alpha"],"Blue");
 projectSapphonGeometry(["gamma","beta"],"Violet");
 assert.equal(JSON.stringify(SAPPHON_SPECTRUM),originalBands);
 assert.equal(JSON.stringify(RADIATION_OVERLAY),originalRadiation);
 assert.equal(JSON.stringify(SAPPHON_OUTER_ANCHORS),originalOuter);
});
test("tampered observer geometry is not accepted",()=>{
 const p=projectSapphonGeometry(["gamma","beta"]);
 assert.equal(validateSapphonGeometry({...p,pairs:p.pairs.slice(0,6)}),false);
 assert.equal(validateSapphonGeometry({...p,photonAdjacencyActive:false}),false);
 assert.equal(validateSapphonGeometry({...p,particle:[{...p.particle[0],kind:"photon"}]}),false);
 assert.equal(validateSapphonGeometry({...p,anchors:[{...p.anchors[0],wavelengthNm:0.1},p.anchors[1]]}),false);
});
