// OASIS v9.4 | periodic H/O/N mnemonic roots for 366 symbolic addresses.
// Existing 370 color source, seven-band cubit, and frozen five operator names remain intact.
import {STR,hsvRGB,rgbHex} from '../generational-color-lattice-v91/color_core.mjs';
import {slotAt,CUBIT} from '../analytical-cubit-color-bands-v93/cubit_core.mjs';

export const ROOTS=Object.freeze([
 Object.freeze({symbol:'H',name:'Hydrogen',atomicNumber:1,start:1,end:122,hueMin:0,hueMax:30,hex:'#FF0000'}),
 Object.freeze({symbol:'O',name:'Oxygen',atomicNumber:8,start:123,end:244,hueMin:120,hueMax:180,hex:'#00FF00'}),
 Object.freeze({symbol:'N',name:'Nitrogen',atomicNumber:7,start:245,end:366,hueMin:240,hueMax:290,hex:'#0000FF'})
]);
export const ROOT_CAPACITY=366;
export const SOURCE_370_CAPACITY=370;
export const SOURCE_TAIL=Object.freeze([367,368,369,370]);
export const OPERANTS=Object.freeze([
 Object.freeze({id:'gravity',name:'Gravity',meaning:'Inward attraction'}),
 Object.freeze({id:'expansion',name:'Expansion',meaning:'Outward growth'}),
 Object.freeze({id:'compression',name:'Compression',meaning:'Inward contraction'}),
 Object.freeze({id:'containment',name:'Containment',meaning:'Restorative boundary operation'}),
 Object.freeze({id:'explosion',name:'Explosion',meaning:'Impulsive outward disturbance'})
]);
export function rootAt(address){
 if(!Number.isInteger(address)||address<1||address>ROOT_CAPACITY)
  throw new RangeError('Elemental address must be an integer in 1..366');
 return ROOTS[Math.floor((address-1)/122)];
}
function assertColor(x){
 if(!x||!['H','O','N'].includes(x.rootSymbol)||![x.hue,x.saturation,x.value].every(Number.isFinite)
  ||x.saturation<0||x.saturation>1||x.value<0||x.value>1)
  throw new TypeError('Valid elemental color state required');
}
export function addressColor(address,strength='S'){
 const root=rootAt(address),tier=STR.find(x=>x.key===strength);
 if(!tier)throw new RangeError('Invalid W/M/S strength');
 const localIndex=address-root.start;
 const hue=root.hueMin+localIndex*(root.hueMax-root.hueMin)/121;
 return Object.freeze({schema:'oasis/n184/hon-color-state/v94',
  address,rootSymbol:root.symbol,rootName:root.name,atomicNumber:root.atomicNumber,
  localIndex,rootStart:root.start,rootEnd:root.end,rootAnchorHue:root.hueMin,
  rootMaxHue:root.hueMax,strength:tier.key,strengthName:tier.name,
  hue,saturation:1,value:tier.amplitude,
  hex:rgbHex(hsvRGB(hue,1,tier.amplitude)),
  lid:address===366,identityKey:'root'+root.symbol+':a'+address+':s'+strength});
}
function normalize(h){return ((h%360)+360)%360}
function shade(state,hue,saturation,value,ops){
 return Object.freeze({...state,hue:normalize(hue),
  saturation:Math.max(0,Math.min(1,saturation)),
  value:Math.max(0,Math.min(1,value)),
  hex:rgbHex(hsvRGB(hue,saturation,value)),
  appliedOperants:Object.freeze(ops.slice())});
}
export function operateColor(color,operatorIds=[]){
 assertColor(color);
 if(!Array.isArray(operatorIds)||operatorIds.length>5)throw new RangeError('At most five operants in a chain');
 let hue=color.hue,sat=color.saturation,val=color.value;
 const applied=[];
 for(const id of operatorIds){
  if(!OPERANTS.some(o=>o.id===id))throw new RangeError('Unknown operant: '+id);
  // Definitions below are newly declared symbolic display actions, not physics.
  if(id==='gravity')hue=color.rootAnchorHue+(hue-color.rootAnchorHue)*0.5;
  if(id==='expansion')hue=color.rootAnchorHue+(hue-color.rootAnchorHue)*1.25;
  if(id==='compression')sat*=0.5;
  if(id==='containment'){hue=Math.max(color.rootAnchorHue,Math.min(color.rootMaxHue,hue));sat=Math.min(sat,.8)}
  if(id==='explosion'){hue+=45;sat=1;val=Math.min(1,val+.2)}
  applied.push(id);
 }
 return shade(color,hue,sat,val,applied);
}
export function rootCatalog(){
 const rows=[];
 for(let i=1;i<=ROOT_CAPACITY;i++)rows.push(addressColor(i,'S'));
 return Object.freeze({total:rows.length,rootLengths:ROOTS.map(x=>x.end-x.start+1),
  rootNames:ROOTS.map(x=>x.name),
  last:rows.at(-1),source370Tail:[...SOURCE_TAIL],rows});
}
export function cubitToHON(position){
 const site=slotAt(position);
 const rootOrdinal=Math.floor((position-1)/6),root=ROOTS[rootOrdinal],local=(position-1)%6;
 const elementalAddress=root.start+Math.round(local*121/5);
 const elementalColor=addressColor(elementalAddress,site.strength);
 return Object.freeze({position,canonicalCubit:CUBIT,originalPacket:site.bandId,
  originalPacketColor:site.bandName,originalPacketHex:site.displayHex,
  originalSource370Address:site.sourceRegistryAddress,
  strength:site.strength,elementalRoot:root.symbol,atomicNumber:root.atomicNumber,
  elementalAddress,elementalColor,
  doublePipeSeam:site.dualSeamAfter,
  closedLid:position===18&&elementalAddress===366,
  scope:'symbolic mapping between two independent frozen display systems'});
}
export function cubitHONCatalog(){
 const slots=Object.freeze(Array.from({length:18},(_,i)=>cubitToHON(i+1)));
 const roots=Object.fromEntries(ROOTS.map(root=>[root.symbol,{
  slots:slots.filter(s=>s.elementalRoot===root.symbol).length,
  addresses:slots.filter(s=>s.elementalRoot===root.symbol).map(s=>s.elementalAddress),
  counts: Object.fromEntries(STR.map(level=>[
   level.key,slots.filter(s=>s.elementalRoot===root.symbol&&s.strength===level.key).length]))
 }]));
 return Object.freeze({schema:'oasis/n184/hon-analytical-cubit-audit/v94',
  sourceCubit:CUBIT,slots,rootSummaries:roots,siteCount:slots.length,
  physicalElementsClaimed:0,source370Untouched:true,opsStoredSeparately:true});
}
