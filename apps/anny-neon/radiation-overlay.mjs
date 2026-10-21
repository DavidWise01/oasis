// ANNY radiation overlays: descriptive, read-only annotations.
// Do not treat particle radiation as monochromatic electromagnetic bands.
// X-ray/gamma energies may overlap; classification is often origin-based.
// No overlay affects the Harvester's transfer, ACK or journal state.
export const RADIATION_OVERLAY = Object.freeze([
 Object.freeze({
  id:"gamma", symbol:"γ", label:"Gamma", kind:"photon",
  tag:"HIGH-ENERGY PHOTON", accent:"#d184ff",
  description:"Electromagnetic photons from nuclear or other high-energy processes.",
  relation:"Short-wavelength side of visible light; gamma and X-ray energy ranges overlap.",
  wavelengthNm:null,
  order:0
 }),
 Object.freeze({
  id:"xray", symbol:"X", label:"X-ray", kind:"photon",
  tag:"HIGH-ENERGY PHOTON", accent:"#63d4ff",
  description:"Electromagnetic photons commonly generated through electron processes.",
  relation:"Beyond ultraviolet on the short-wavelength side; overlaps gamma photon energies.",
  wavelengthNm:null,
  order:1
 }),
 Object.freeze({
  id:"alpha", symbol:"α", label:"Alpha", kind:"particle",
  tag:"HELIUM NUCLEUS", accent:"#ff9a57",
  description:"A helium nucleus: two protons and two neutrons; charge +2e.",
  relation:"Particle radiation: not an electromagnetic color or fixed wavelength interval.",
  wavelengthNm:null,
  order:2
 }),
 Object.freeze({
  id:"beta", symbol:"β", label:"Beta", kind:"particle",
  tag:"ELECTRON / POSITRON", accent:"#78f5b9",
  description:"A beta-minus electron or beta-plus positron; charge −e or +e.",
  relation:"Particle radiation: not an electromagnetic color or fixed wavelength interval.",
  wavelengthNm:null,
  order:3
 })
]);
export const RADIATION_GROUPS = Object.freeze([
 Object.freeze({id:"photon",label:"PHOTON TRACK",description:"γ and X are electromagnetic radiation; boundaries overlap."}),
 Object.freeze({id:"particle",label:"PARTICLE TRACK",description:"α and β are emitted material particles, not photon-color bands."})
]);
export function validateRadiationOverlay(items=RADIATION_OVERLAY){
 if(!Array.isArray(items)||items.length!==4) return false;
 if(items.map(i=>i.id).join(",")!=="gamma,xray,alpha,beta")return false;
 if(items.map(i=>i.kind).join(",")!=="photon,photon,particle,particle")return false;
 return items.every((item,i)=>item.wavelengthNm===null&&item.order===i
   && typeof item.symbol==="string"&&item.symbol.length>0
   && typeof item.description==="string"&&item.description.length>0
   && typeof item.relation==="string"&&item.relation.length>0
   && typeof item.accent==="string");
}
export function visibleRadiations(activeIds,items=RADIATION_OVERLAY){
 const selected=new Set(activeIds);
 return items.filter(item=>selected.has(item.id));
}
function el(tag,className,text){
 const n=document.createElement(tag);if(className)n.className=className;
 if(text!==undefined)n.textContent=text;return n;
}
export function mountRadiationOverlay(root){
 if(!validateRadiationOverlay())throw Error("RADIATION_OVERLAY_REGISTRY_INVALID");
 if(!root)throw Error("RADIATION_OVERLAY_MOUNT_MISSING");
 const state=new Set(RADIATION_OVERLAY.map(i=>i.id));
 const controls=root.querySelector("#radiation-toggles");
 const tracks=root.querySelector("#radiation-tracks");
 const reset=root.querySelector("#radiation-reset");
 const tally=root.querySelector("#radiation-tally");
 if(!controls||!tracks||!reset||!tally)throw Error("RADIATION_OVERLAY_CONTROL_MISSING");
 function paint(){
  controls.replaceChildren();
  tracks.replaceChildren();
  for(const item of RADIATION_OVERLAY){
   const button=el("button","radiation-toggle",item.symbol+" "+item.label);
   button.type="button";button.dataset.radiation=item.id;
   button.style.setProperty("--radiation-tone",item.accent);
   button.setAttribute("aria-pressed",String(state.has(item.id)));
   button.addEventListener("click",()=>{
    if(state.has(item.id))state.delete(item.id);else state.add(item.id);
    paint();
   });
   controls.append(button);
  }
  for(const group of RADIATION_GROUPS){
   const section=el("section","radiation-track");
   section.dataset.kind=group.id;
   section.append(el("h4","radiation-track-title",group.label),
                  el("p","radiation-track-description",group.description));
   const cards=el("div","radiation-card-grid");
   for(const item of visibleRadiations(state).filter(x=>x.kind===group.id)){
    const card=el("article","radiation-card");
    card.dataset.radiation=item.id;card.dataset.kind=item.kind;
    card.style.setProperty("--radiation-tone",item.accent);
    const head=el("div","radiation-card-head");
    head.append(el("span","radiation-symbol",item.symbol),
                el("strong","radiation-card-name",item.label));
    card.append(head,el("span","radiation-tag",item.tag),
      el("p","radiation-description",item.description),
      el("p","radiation-relation",item.relation));
    cards.append(card);
   }
   if(!cards.childElementCount)cards.append(el("p","radiation-empty","This track is hidden."));
   section.append(cards);tracks.append(section);
  }
  tally.textContent=state.size+"/4 overlays enabled";
  root.dataset.active=Array.from(state).join(",");
 }
 reset.addEventListener("click",()=>{
  state.clear();for(const item of RADIATION_OVERLAY)state.add(item.id);
  paint();
 });
 paint();
}
