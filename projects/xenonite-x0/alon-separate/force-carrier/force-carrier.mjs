/**
 * ALON distinct force-carrier observation overlay.
 * Symbolic modes are not actual weak/strong force particles.
 * Literal from user preserved, including unmatched terminal braces.
 */
import { ALON_TRACKS, evaluateAlon } from "../alon-track.mjs";
export const FORCE_LITERAL = "{{ 1 :: force carrier :: { weak , medium strong }} :: 1 :: - or + :: 1 :: color :: 2 out of 8 :: }}}";
export const FORCE_MODES = Object.freeze(["weak","medium","strong"]);
export const FORCE_COLORS = Object.freeze([
 Object.freeze({id:"bk",name:"black",css:"#242932"}),
 Object.freeze({id:"wt",name:"white",css:"#e7eff6"}),
 Object.freeze({id:"red",name:"red",css:"#e47570"}),
 Object.freeze({id:"blu",name:"blue",css:"#69abe1"}),
 Object.freeze({id:"gree",name:"green",css:"#80c6a0"}),
 Object.freeze({id:"yell",name:"yellow",css:"#e3ca7c"}),
 Object.freeze({id:"purpl",name:"purple",css:"#b59adf"}),
 Object.freeze({id:"orang",name:"orange",css:"#e2a16d"})
]);
export const FORCE_IDENTITY = Object.freeze({
 literal:FORCE_LITERAL,
 activeCarrierCount:1, modeOptions:FORCE_MODES, chosenModes:1,
 signOptions:Object.freeze(["-","+"]), chosenSigns:1,
 palette:FORCE_COLORS, chosenColors:2, totalColors:8,
 colorPairsUnordered:true,possibleColorPairs:28,possibleSymbolicCombinations:168,
 materialChemistryUnchanged:true, noPhysicalBosonEquation:true, noMeasuredWavelengths:true,
 unbalancedTerminalBracesPreserved:true,
 frozenKelvinAndMadreUnchanged:true
});
const MAX_RECORDS=128;
function normalize(v){
 if(!v || !ALON_TRACKS.some(t=>t.id===v.lane))throw new RangeError("Choose one ALON lane.");
 if(!FORCE_MODES.includes(v.mode))throw new RangeError("Choose one weak, medium or strong mode.");
 if(!["-","+"].includes(v.sign))throw new RangeError("Choose one polarity sign.");
 if(!Array.isArray(v.colors)||v.colors.length!==2||v.colors[0]===v.colors[1]||
   !v.colors.every(id=>FORCE_COLORS.some(c=>c.id===id)))
   throw new RangeError("Choose exactly TWO DISTINCT colors from eight.");
 const colors=[...v.colors].sort((a,b)=>
   FORCE_COLORS.findIndex(c=>c.id===a)-FORCE_COLORS.findIndex(c=>c.id===b));
 return Object.freeze({carrierCount:1,lane:v.lane,mode:v.mode,sign:v.sign,
   colors:Object.freeze(colors)});
}
export function createAlonForceCarrier(){
 let selection=normalize({lane:"A",mode:"medium",sign:"-",colors:["bk","orang"]});
 const entries=[];
 function select(next){
  const updated=normalize(next); // atomic validation prevents partial updates
  selection=updated;
  return selection;
 }
 function current(physical={}){
  return Object.freeze({
   selection,calculation:evaluateAlon(physical),
   records:entries.length,remaining:MAX_RECORDS-entries.length
  });
 }
 function append(physical={}){
  // Validate the physical parameters before updating any ledger.
  const measured=evaluateAlon(physical);
  if(entries.length>=MAX_RECORDS)throw new RangeError("128 manual snapshots reached; export JSON.");
  const item=Object.freeze({
    sequence:entries.length+1, kind:"explicit-human-snapshot",
    selected:Object.freeze({...selection,colors:Object.freeze([...selection.colors])}),
    physics:Object.freeze({
      deltaPressureMPa:measured.deltaPressureMPa,
      idealizedSphereStressMPa:measured.nominalSphereStressMPa,
      illustrativeStressIntensityMPaRootM:measured.modeIStressIntensityMPaRootM,
      specimenToughnessRatio:measured.indicativeFractureRatio,
      passiveSignalRetained:measured.illustrativeRetainedSignal
    }),
    inputs:measured.input,
    provenance:"user-supplied operator and illustrative equations; no physical interaction law"
  });
  entries.push(item);
  return item;
 }
 function ledger(){
  return {schema:"oasis.alon.separate.force-carrier.v1",
   identity:FORCE_IDENTITY,activeSelection:selection,
   records:entries.map(e=>({...e,selected:{...e.selected,colors:[...e.selected.colors]}})),
   note:"In-memory, explicit manual append only; no autonomous process."};
 }
 return Object.freeze({identity:FORCE_IDENTITY,select,current,append,ledger});
}
