/**
 * ALON: independent four-track symbolic shell, not Madre Sapphon and not KELVIN.
 * User literal: {{ -AaaA....LllL....OooO....NnnN.... }}
 *
 * Material calculation: illustrative spherical pressure membrane and LEFM crack
 * sensitivity. There is NO constitutive law for fictional Xenonite here.
 */
export const ALON_LITERAL = "{{ -AaaA....LllL....OooO....NnnN.... }}";
export const ALON_TRACKS = Object.freeze([
  Object.freeze({id:"A",glyph:"AaaA",meaning:"Aluminum / Al",kind:"element",nominalCount:23,atomicNumber:13}),
  Object.freeze({id:"L",glyph:"LllL",meaning:"Lattice / defect sites",kind:"structure",nominalCount:null,atomicNumber:null}),
  Object.freeze({id:"O",glyph:"OooO",meaning:"Oxygen / O",kind:"element",nominalCount:27,atomicNumber:8}),
  Object.freeze({id:"N",glyph:"NnnN",meaning:"Nitrogen / N",kind:"element",nominalCount:5,atomicNumber:7})
]);
export const ALON_IDENTITY = Object.freeze({
  id:"ALON-FOUR-TRACK",
  version:"1.0.0",
  notation:ALON_LITERAL,
  prefix:"-",
  trackCount:4,
  glyphsPerTrack:4,
  dotGates:Object.freeze([4,4,4,4]),
  totalGlyphCharacters:16,
  totalDelimiterDots:16,
  family:"ALON material observation",
  separateFrom:"Aa.Nn.Nn / Madre Sapphon and frozen KELVIN v11.3",
  literalGlyphsAreAtoms:false,
  actualElements:Object.freeze(["Al","O","N"]),
  crystal:"polycrystalline cubic defect spinel",
  nominalApproximation:"Al23O27N5",
  nominalAtomCountPerWrittenRatio:55,
  compositionVaries:true,
  sitesAreNotSpatialCoordinates:true,
  reportedSampleModulusGPa:319,
  reportedSampleFractureToughnessMPaRootM:2.19,
  caveat:"NASA specimen values, not material allowables or bulkhead qualification",
  modelType:"illustrative thin-shell + stress-intensity hypothesis",
  physicallyBuilt:false,
  frozenRuntimeTouched:false,
  autonomous:false
});
const nominalModel=Object.freeze([
  ...Array(23).fill("Al"), ...Array(27).fill("O"), ...Array(5).fill("N")
]);
const LIMIT=128;
function num(v,name,positive){
 if(v===""||v===null||v===undefined||!Number.isFinite(Number(v))||
    Number(v)<0||(positive&&Number(v)===0)) throw new RangeError(name+" requires a finite "+(positive?"positive":"nonnegative")+" value");
 return Number(v);
}
export function evaluateAlon(inputs={}){
 const pIn=num(inputs.pIn??29,"inside atm",false);
 const pOut=num(inputs.pOut??1,"outside atm",false);
 const radius=num(inputs.radius??0.2,"radius m",true);
 const wallMm=num(inputs.wallMm??10,"wall thickness mm",true);
 const flawHalfLengthMm=num(inputs.flawHalfLengthMm??0.1,"flaw half-length mm",true);
 const factorY=num(inputs.factorY??1,"geometry factor Y",true);
 const attenuation=num(inputs.attenuation??0.8,"illustrative attenuation per meter",false);
 const pathMeters=num(inputs.pathMeters??0.5,"propagation path meters",false);
 const deltaPressurePa=(pIn-pOut)*101325;
 const validInternal=deltaPressurePa>0;
 const stressMPa=validInternal?deltaPressurePa*radius/(2*(wallMm/1000))/1e6:null;
 const K=validInternal?factorY*stressMPa*Math.sqrt(Math.PI*(flawHalfLengthMm/1000)):null;
 const Kic=ALON_IDENTITY.reportedSampleFractureToughnessMPaRootM;
 const ratio=K===null?null:K/Kic;
 const warnings=[
   "Experimental fracture toughness is from specific NASA-tested ALON samples; real flaw geometry, environment and reliability vary.",
   "This is an ideal sphere, not a real ALON/metal joint, flat pane or pressure-vessel qualification."
 ];
 if(!validInternal) warnings.unshift("No positive internal gauge pressure: external buckling is not evaluated.");
 if((wallMm/1000)/radius>0.1) warnings.unshift("Wall/radius above 0.1: thin-shell approximation may be inaccurate.");
 if(ratio!==null&&ratio>=1) warnings.unshift("Simplified mode-I stress intensity meets or exceeds the cited specimen toughness: likely critical in this approximation.");
 return Object.freeze({
   input:Object.freeze({pIn,pOut,radius,wallMm,flawHalfLengthMm,factorY,attenuation,pathMeters}),
   deltaPressureMPa:deltaPressurePa/1e6,
   nominalSphereStressMPa:stressMPa,
   modeIStressIntensityMPaRootM:K,
   specimenToughnessMPaRootM:Kic,
   indicativeFractureRatio:ratio,
   illustrativeRetainedSignal:Math.exp(-attenuation*pathMeters),
   physicallySafe:null,
   microstructurePrediction:false,
   warnings:Object.freeze(warnings)
 });
}
export function createAlonTrack(){
 let focus="A";
 const ledger=[];
 function setFocus(v){
   if(!ALON_TRACKS.some(t=>t.id===v))throw new RangeError("Unknown ALON lane");
   focus=v;
   return current();
 }
 function current(inputs={}){
   return Object.freeze({
     notation:ALON_LITERAL,
     focus,
     lane:ALON_TRACKS.find(t=>t.id===focus),
     nominalAtoms:nominalModel,
     calculation:evaluateAlon(inputs),
     saved:ledger.length,
     remaining:LIMIT-ledger.length
   });
 }
 function snapshot(inputs={}){
   const calc=evaluateAlon(inputs); // validate before append
   if(ledger.length>=LIMIT)throw new RangeError("128 manual snapshots reached. Export the ledger.");
   const item=Object.freeze({
     sequence:ledger.length+1,
     action:"explicit-operator-snapshot",
     track:focus,
     trackGlyph:ALON_TRACKS.find(t=>t.id===focus).glyph,
     input:calc.input,
     output:Object.freeze({
       pressureMPa:calc.deltaPressureMPa,
       sphericalStressMPa:calc.nominalSphereStressMPa,
       stressIntensity:calc.modeIStressIntensityMPaRootM,
       toughnessRatio:calc.indicativeFractureRatio,
       signalRetention:calc.illustrativeRetainedSignal
     }),
     evidence:"calculated, hypothetical pressure geometry; not a laboratory measurement"
   });
   ledger.push(item);
   return item;
 }
 function exportLedger(){
   return {
     schema:"oasis.alon-four-track.v1",
     identity:ALON_IDENTITY,
     note:"Only human clicks append; settings change only the current transient view.",
     entries:ledger.map(e=>({...e}))
   };
 }
 return Object.freeze({identity:ALON_IDENTITY,setFocus,current,snapshot,exportLedger});
}
