import test from "node:test";
import assert from "node:assert/strict";
import { RADIATION_OVERLAY, RADIATION_GROUPS, validateRadiationOverlay, visibleRadiations } from "./radiation-overlay.mjs";
import { SAPPHON_SPECTRUM, SAPPHON_OUTER_ANCHORS } from "./sapphon-spectrum.mjs";

test("overlay covers exactly gamma, X-ray, alpha and beta", () => {
 assert.equal(validateRadiationOverlay(),true);
 assert.deepEqual(RADIATION_OVERLAY.map(x=>x.id),["gamma","xray","alpha","beta"]);
 assert.deepEqual(RADIATION_OVERLAY.map(x=>x.symbol),["γ","X","α","β"]);
 assert.deepEqual(RADIATION_GROUPS.map(x=>x.id),["photon","particle"]);
});
test("photons and particles are distinguished, with no invented fixed cutoffs", () => {
 assert.deepEqual(RADIATION_OVERLAY.map(x=>x.kind),["photon","photon","particle","particle"]);
 assert(RADIATION_OVERLAY.every(x=>x.wavelengthNm===null));
 assert(RADIATION_OVERLAY.find(x=>x.id==="alpha").description.includes("two protons and two neutrons"));
 assert(RADIATION_OVERLAY.find(x=>x.id==="beta").description.includes("positron"));
});
test("visibility toggle is a pure presentation filter", () => {
 assert.deepEqual(visibleRadiations(["gamma","alpha"]).map(x=>x.id),["gamma","alpha"]);
 assert.equal(visibleRadiations([]).length,0);
 assert.equal(visibleRadiations(RADIATION_OVERLAY.map(x=>x.id)).length,4);
 assert.equal(RADIATION_OVERLAY.length,4);
});
test("invalid kind and numeric wavelength assignments fail closed", () => {
 assert.equal(validateRadiationOverlay(RADIATION_OVERLAY.map((x,i)=>i===2?{...x,kind:"photon"}:x)),false);
 assert.equal(validateRadiationOverlay(RADIATION_OVERLAY.map((x,i)=>i===0?{...x,wavelengthNm:0.01}:x)),false);
 assert.equal(validateRadiationOverlay(RADIATION_OVERLAY.slice(0,3)),false);
});
test("existing cubit topology and symbolic void/gravity remain distinct", () => {
 assert.deepEqual(SAPPHON_SPECTRUM.flatMap(x=>x.slots),Array.from({length:18},(_,i)=>i+1));
 assert.deepEqual(SAPPHON_OUTER_ANCHORS.map(x=>x.operator),["--","++"]);
 assert.equal(new Set(RADIATION_OVERLAY.map(x=>x.id)).size,4);
});
