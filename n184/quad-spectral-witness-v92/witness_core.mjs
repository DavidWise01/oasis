// OASIS v9.2 — 4 logical CERN-named software views of ONE immutable color record.
// Does NOT represent measurements by the actual CERN experiments.
import {STR,MAX_GENERATION,hueAt,hueCount,hsvRGB,rgbHex,swatch,
 nearestRegistryIndex,orbitFor,registryHue,collisionSummary} from '../generational-color-lattice-v91/color_core.mjs';

export const QUADS=Object.freeze([
 Object.freeze({id:'A',name:'ALICE',ip:2,view:'Hue / phase'}),
 Object.freeze({id:'B',name:'ATLAS',ip:1,view:'RGB / channels'}),
 Object.freeze({id:'C',name:'CMS',ip:5,view:'W / M / S'}),
 Object.freeze({id:'D',name:'LHCb',ip:8,view:'Registry / lineage'})
]);
export const QUORUM=3;
export function identityKey(gen,index,strength){
 hueAt(gen,index);
 if(!STR.some(x=>x.key===strength))throw RangeError('Unknown strength');
 return 'g'+gen+':i'+index+':s'+strength;
}
export function createColorRecord(gen,index,strength='S'){
 const value=swatch(gen,index,strength);
 return Object.freeze({schema:'oasis/n184/quad-color-record/v92',
  generation:gen,index,strength,identityKey:identityKey(gen,index,strength),
  value});
}
function parseHex(hex){
 if(!/^#[0-9A-Fa-f]{6}$/.test(hex))return null;
 return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
}
const near=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-9;
export function observeQuad(record,quad){
 if(!QUADS.some(x=>x.id===quad))throw RangeError('Invalid quad');
 if(!record||record.schema!=='oasis/n184/quad-color-record/v92')throw TypeError('Invalid color record');
 const {generation:g,index:i,strength:s,value}=record;
 const hue=hueAt(g,i);
 let attrs,pass=false;
 switch(quad){
  case 'A': {
   const sector=Math.floor((hue%360)/60),microtick=Math.floor((hue%360)/1.5)%240,
    phaseStep=Math.floor((hue%360)/4.5)%80;
   attrs={hueDegrees:value.hueDegrees,sector,microtick,phaseStep};
   pass=near(value.hueDegrees,hue) && sector>=0&&sector<6&&microtick>=0&&microtick<240;
   break;
  }
  case 'B': {
   const rgb=parseHex(value.displayHex),recalc=rgbHex(hsvRGB(hue,1,
    STR.find(x=>x.key===s).amplitude));
   attrs={rgb,hex:value.displayHex,maximumChannel:rgb?Math.max(...rgb):null,
    expectedHex:recalc};
   pass=!!rgb&&value.displayHex===recalc;
   break;
  }
  case 'C': {
   const tiers=Object.fromEntries(STR.map(x=>[x.key,swatch(g,i,x.key).displayHex]));
   const factor=STR.find(x=>x.key===s);
   attrs={selected:s,weakHex:tiers.W,mediumHex:tiers.M,strongHex:tiers.S,
    amplitude:value.amplitude,selectedHex:tiers[s]};
   pass=near(value.amplitude,factor.amplitude)&&tiers[s]===value.displayHex &&
    STR.every(x=>swatch(g,i,x.key).registryAddress===value.registryAddress);
   break;
  }
  case 'D': {
   const address=nearestRegistryIndex(hue),orbit=orbitFor(address),
   preview=rgbHex(hsvRGB(registryHue(address),.78,.98));
   attrs={address:value.registryAddress,orbit:value.registryOrbit,
    sourceMode:value.registryMode,sourcePreviewHex:value.registryPreviewHex,
    expectedAddress:address,expectedOrbit:orbit};
   pass=value.registryAddress===address&&value.registryOrbit===orbit&&
     value.registryMode==='hue'&&value.registryPreviewHex===preview;
   break;
  }
 }
 const meta=QUADS.find(x=>x.id===quad);
 return Object.freeze({quad,experiment:meta.name,ip:meta.ip,view:meta.view,
  identityKey:record.identityKey,valid:pass,features:Object.freeze(attrs)});
}
export function observeAll(record){
 return Object.freeze(QUADS.map(q=>observeQuad(record,q.id)));
}
export function injectReportFaults(reports,mode='none'){
 if(!Array.isArray(reports)||reports.length!==4)throw TypeError('Four reports required');
 if(!['none','one','two','all-coherent'].includes(mode))throw RangeError('Unknown report fault');
 const toAlter=mode==='one'?new Set(['A']):mode==='two'?new Set(['A','B']):
  mode==='all-coherent'?new Set(['A','B','C','D']):new Set();
 return Object.freeze(reports.map(r=>toAlter.has(r.quad)
  ?Object.freeze({...r,identityKey:r.identityKey+'!changed'})
  :r));
}
export function evaluateQuorum(reports){
 if(!Array.isArray(reports))throw TypeError('reports must be an array');
 const acceptedQuads=new Set(),votes=new Map(),duplicates=[],invalid=[];
 for(const r of reports){
  if(!r||!QUADS.some(q=>q.id===r.quad)||acceptedQuads.has(r.quad)){
   duplicates.push(r?.quad??null);continue;
  }
  acceptedQuads.add(r.quad);
  if(r.valid!==true||typeof r.identityKey!=='string'||!r.identityKey.length){
   invalid.push(r.quad);continue;
  }
  const arr=votes.get(r.identityKey)||[];arr.push(r.quad);votes.set(r.identityKey,arr);
 }
 const ranking=[...votes].sort((a,b)=>b[1].length-a[1].length||a[0].localeCompare(b[0]));
 const win=ranking[0]||[null,[]],consensus=win[1].length>=QUORUM;
 const dissent=reports.filter(r=>r&&r.identityKey!==win[0]).map(r=>r.quad);
 return Object.freeze({consensus,quorumRequired:QUORUM,totalPossible:4,
  majorityKey:consensus?win[0]:null,winnerVotes:win[1].length,
  agreeingQuads:Object.freeze(win[1].slice()),
  dissentingQuads:Object.freeze(dissent),invalidQuads:Object.freeze(invalid),
  duplicateQuads:Object.freeze(duplicates),
  diagnostic:"Derived software agreement only — NOT independent physical validation."});
}
export function surveyGeneration(gen){
 const total=hueCount(gen)*STR.length;
 let passed=0,failed=0;let sample=null;
 for(let i=0;i<hueCount(gen);i++)for(const tier of STR){
  const rec=createColorRecord(gen,i,tier.key),votes=observeAll(rec),v=evaluateQuorum(votes);
  if(v.consensus&&votes.every(x=>x.valid))passed++;else failed++;
  if(i===0&&tier.key==='S')sample={identity:rec.identityKey,hex:rec.value.displayHex,sourceAddress:rec.value.registryAddress};
 }
 return {generation:gen,colors:hueCount(gen),swatches:total,
  passed,failed,fullAgreementRate:total?passed/total:null,example:sample,
  registryProjection:collisionSummary(gen)};
}
export function surveyAll(){
 return Object.freeze(Array.from({length:MAX_GENERATION+1},(_,gen)=>surveyGeneration(gen)));
}
