// ANNY read-only spectral / radiation geometry bridge.
// This file imports only presentation registries; it has no journal,
// receiver, ACK, IndexedDB, or network dependencies.
import {SAPPHON_SPECTRUM,SAPPHON_BROADBAND,SAPPHON_OUTER_ANCHORS,validateSapphonSpectrum,validateSapphonOuterAnchors} from "./sapphon-spectrum.mjs";
import {RADIATION_OVERLAY,validateRadiationOverlay,visibleRadiations} from "./radiation-overlay.mjs";

export const ANNY_GEOMETRY_REFERENCE=Object.freeze({
  shortestVisibleNm:380,
  longestVisibleNm:750,
  photonDirection:"shorter-than-visible context; X-ray and gamma spectral energies may overlap",
  particleDirection:"independent particle axis; no monochromatic wavelength",
  ontology:"illustrative observer projection, not interaction physics or delivery authority"
});

export function projectSapphonGeometry(activeIds,focusColor="Violet") {
  if (!validateSapphonSpectrum() || !validateSapphonOuterAnchors() || !validateRadiationOverlay()) {
    throw Error("ANNY_GEOMETRY_REGISTRY_INVALID");
  }
  const requested=new Set(activeIds);
  const active=visibleRadiations(requested);
  const photon=active.filter(x=>x.kind==="photon").map(x=>({
    id:x.id,symbol:x.symbol,name:x.label,kind:x.kind,accent:x.accent,
    placement:"shortwave-adjacent", // not assigned to Violet or to an nm cutoff
    wavelengthNm:null
  }));
  const particle=active.filter(x=>x.kind==="particle").map(x=>({
    id:x.id,symbol:x.symbol,name:x.label,kind:x.kind,accent:x.accent,
    placement:"orthogonal-particle-axis",
    charge:x.id==="alpha"?"+2e":"−e / +e",wavelengthNm:null
  }));
  const pairs=[...SAPPHON_SPECTRUM].reverse().map(b=>({
    color:b.color,low:b.low,high:b.high,accent:b.accent,
    slots:[...b.slots],
    minus:{name:b.minus.word,nm:b.low,polarity:"−"},
    plus:{name:b.plus.word,nm:b.high,polarity:"+"}
  }));
  const focus=pairs.find(p=>p.color===focusColor);
  if(!focus)throw Error("ANNY_GEOMETRY_UNKNOWN_BAND");
  return {
    photon,particle,pairs,focus,
    photonAdjacencyActive:photon.length>0,
    // These are symbolic operator frames, not physical terminal wavelengths.
    anchors:SAPPHON_OUTER_ANCHORS.map(x=>({operator:x.operator,label:x.label,kind:x.kind,wavelengthNm:x.wavelengthNm})),
    broadband:{name:SAPPHON_BROADBAND.color,wavelengthNm:null},
    reference:ANNY_GEOMETRY_REFERENCE
  };
}

export function validateSapphonGeometry(model){
  if(!model||!Array.isArray(model.pairs)||model.pairs.length!==7)return false;
  const slots=model.pairs.flatMap(p=>p.slots).sort((a,b)=>a-b);
  if(JSON.stringify(slots)!==JSON.stringify(Array.from({length:18},(_,i)=>i+1)))return false;
  if(model.pairs[0].low!==380||model.pairs[6].high!==750)return false;
  if(model.pairs.some(p=>p.minus.polarity!=="−"||p.plus.polarity!=="+"||p.minus.nm!==p.low||p.plus.nm!==p.high))return false;
  if(model.photon.some(x=>x.kind!=="photon"||x.placement!=="shortwave-adjacent"||x.wavelengthNm!==null))return false;
  if(model.particle.some(x=>x.kind!=="particle"||x.placement!=="orthogonal-particle-axis"||x.wavelengthNm!==null))return false;
  if(model.photonAdjacencyActive!==(model.photon.length>0))return false;
  if(!model.focus||!model.pairs.some(p=>p.color===model.focus.color))return false;
  if(model.broadband.name!=="White"||model.broadband.wavelengthNm!==null)return false;
  return model.anchors.length===2
    && model.anchors[0].operator==="--"&&model.anchors[1].operator==="++"
    && model.anchors.every(a=>a.kind==="symbolic-boundary"&&a.wavelengthNm===null);
}

function el(tag,cls,content){
 const n=document.createElement(tag);
 if(cls)n.className=cls;
 if(content!==undefined)n.textContent=String(content);
 return n;
}
function renderMarker(item,dim=false){
 const chip=el("span","geometry-radiation-token"+(dim?" inactive":""));
 chip.dataset.radiation=item.id;
 chip.style.setProperty("--ray-tone",item.accent);
 chip.append(el("span","token-symbol",item.symbol),
   el("span","token-label",item.name));
 if(item.charge)chip.append(el("span","token-charge",item.charge));
 return chip;
}
export function mountSapphonGeometry(root,radiationRoot){
 if(!root||!radiationRoot)throw Error("ANNY_GEOMETRY_MOUNT_MISSING");
 const photonHost=root.querySelector("#geometry-photons");
 const particleHost=root.querySelector("#geometry-particles");
 const spectrumHost=root.querySelector("#geometry-pairs");
 const focusHost=root.querySelector("#geometry-focus");
 const stateHost=root.querySelector("#geometry-state");
 if(!photonHost||!particleHost||!spectrumHost||!focusHost||!stateHost)
   throw Error("ANNY_GEOMETRY_UI_MISSING");
 let focusColor="Violet";
 function readActive(){return String(radiationRoot.dataset.active||"").split(",").filter(Boolean)}
 function update(){
  const model=projectSapphonGeometry(readActive(),focusColor);
  if(!validateSapphonGeometry(model))throw Error("ANNY_GEOMETRY_MODEL_INVALID");
  photonHost.replaceChildren();
  particleHost.replaceChildren();
  spectrumHost.replaceChildren();
  for(const p of model.photon)photonHost.append(renderMarker(p));
  if(!model.photon.length)photonHost.append(el("span","geometry-muted","No photon overlays selected"));
  for(const p of model.particle)particleHost.append(renderMarker(p));
  if(!model.particle.length)particleHost.append(el("span","geometry-muted","No particle overlays selected"));
  for(const pair of model.pairs){
   const button=el("button","geometry-pair"+(pair.color===focusColor?" selected":""));
   button.type="button";
   button.dataset.color=pair.color.toLowerCase();
   button.style.setProperty("--pair-tone",pair.accent);
   button.setAttribute("aria-pressed",String(pair.color===focusColor));
   button.append(el("strong","pair-color",pair.color),
      el("span","pair-ports","−  ═  +"),
      el("small","pair-wave",pair.low+"–"+pair.high+" nm"));
   button.addEventListener("click",()=>{focusColor=pair.color;update()});
   spectrumHost.append(button);
  }
  const f=model.focus;
  focusHost.replaceChildren(el("strong","",f.color+" · "+f.low+"–"+f.high+" nm"),
   el("span","", "− "+f.minus.name+" · "+f.minus.nm+" nm"),
   el("span","", "+ "+f.plus.name+" · "+f.plus.nm+" nm"),
   el("small","","Cubit evidence slots "+f.slots.join(", ")+" · observation only"));
  stateHost.textContent=model.photon.length+" photon · "+model.particle.length+" particle overlays · "+f.color+" selected";
  root.dataset.photonActive=String(model.photonAdjacencyActive);
  root.dataset.focus=focusColor.toLowerCase();
  root.dataset.radiationActive=readActive().join(",");
 }
 const observer=new MutationObserver((records)=>{
  if(records.some(record=>record.attributeName==="data-active"))update();
 });
 observer.observe(radiationRoot,{attributes:true,attributeFilter:["data-active"]});
 update();
 return ()=>observer.disconnect();
}
