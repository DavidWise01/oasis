// OASIS v9.1 | additive RGB color wheel, ordered generation midpoints,
// and a read-only overlay on 370 symbolic color addresses.
// No changes to canonical 370 registry, 1832/1970 history, or CERN physics.
export const STR=(Object.freeze([
 Object.freeze({key:'W',name:'Weak',amplitude:1/3}),
 Object.freeze({key:'M',name:'Medium',amplitude:2/3}),
 Object.freeze({key:'S',name:'Strong',amplitude:1})
]));
export const MAX_GENERATION=8;
export const SOURCE_COUNT=370;
export const SOURCE_ORBITS=Object.freeze([
 Object.freeze({orbit:1,start:1,end:122}),
 Object.freeze({orbit:2,start:123,end:244}),
 Object.freeze({orbit:3,start:245,end:370})
]);
const NAMES={
 0:['Red','Green','Blue'],
 1:['Yellow','Cyan','Magenta'],
 2:['Orange','Chartreuse','Spring green','Azure','Violet','Rose']
};
const GEN_NAMES=['Primary','Secondary','Tertiary','Fourth-order blends',
 'Fifth-order blends','Sixth-order blends','Seventh-order blends',
 'Eighth-order blends','Ninth-order blends'];
export function hueCount(gen){
 if(!Number.isInteger(gen)||gen<0||gen>MAX_GENERATION)throw RangeError('generation must be 0..'+MAX_GENERATION);
 return gen===0?3:3*2**(gen-1);
}
export function cumulativeCount(gen){return gen===0?3:3*2**gen}
export function hueAt(gen,index){
 const count=hueCount(gen);
 if(!Number.isInteger(index)||index<0||index>=count)throw RangeError('hue index out of range');
 return gen===0?index*120:(2*index+1)*60/2**(gen-1);
}
export function hsvRGB(hue,saturation=1,value=1){
 if(![hue,saturation,value].every(Number.isFinite))throw TypeError('finite HSV values required');
 if(saturation<0||saturation>1||value<0||value>1)throw RangeError('S and V must be between 0 and 1');
 const h=((hue%360)+360)%360,chrom=value*saturation,
   x=chrom*(1-Math.abs((h/60)%2-1)),m=value-chrom;
 let channels;
 if(h<60)channels=[chrom,x,0];
 else if(h<120)channels=[x,chrom,0];
 else if(h<180)channels=[0,chrom,x];
 else if(h<240)channels=[0,x,chrom];
 else if(h<300)channels=[x,0,chrom];
 else channels=[chrom,0,x];
 return channels.map(v=>Math.round(255*(v+m)));
}
export function rgbHex(rgb){
 if(rgb.length!==3||!rgb.every(x=>Number.isInteger(x)&&x>=0&&x<=255))throw TypeError('Three 8-bit RGB channels expected');
 return '#'+rgb.map(n=>n.toString(16).padStart(2,'0')).join('').toUpperCase();
}
export function colorName(gen,index){
 hueAt(gen,index);
 return NAMES[gen]?.[index]||'G'+gen+' · '+String(index+1).padStart(3,'0');
}
export function nearestRegistryIndex(hue){
 if(!Number.isFinite(hue))throw TypeError('hue must be finite');
 const h=((hue%360)+360)%360;
 return (Math.round(h*SOURCE_COUNT/360)%SOURCE_COUNT)+1;
}
export function orbitFor(index){
 if(!Number.isInteger(index)||index<1||index>SOURCE_COUNT)throw RangeError('registry address must be 1..370');
 return SOURCE_ORBITS.find(x=>index>=x.start&&index<=x.end).orbit;
}
export function registryHue(index){orbitFor(index);return (index-1)*360/SOURCE_COUNT}
export function wrappedAngularErrorDegrees(a,b){
 const d=((a-b+540)%360+360)%360-180;
 return Math.abs(d);
}
export function swatch(gen,index,strength='S'){
 const h=hueAt(gen,index),entry=STR.find(s=>s.key===strength);
 if(!entry)throw Error('unknown strength '+strength);
 const registryIndex=nearestRegistryIndex(h);
 return Object.freeze({generation:gen,generationName:GEN_NAMES[gen],
  index,displayName:colorName(gen,index),hueDegrees:h,
  strength:entry.key,strengthName:entry.name,amplitude:entry.amplitude,
  displayHex:rgbHex(hsvRGB(h,1,entry.amplitude)),
  // A preview of the prior, source-defined registry 'hue' palette, not our swatch.
  registryAddress:registryIndex,registryMode:'hue',registryOrbit:orbitFor(registryIndex),
  registryHueDegrees:registryHue(registryIndex),
  registryHueErrorDegrees:wrappedAngularErrorDegrees(h,registryHue(registryIndex)),
  registryPreviewHex:rgbHex(hsvRGB(registryHue(registryIndex),.78,.98))
 });
}
export function generation(gen){
 const count=hueCount(gen);
 return Object.freeze({index:gen,name:GEN_NAMES[gen],hues:count,
  swatches:count*3,cumulativeHues:cumulativeCount(gen),
  colors:Array.from({length:count},(_,i)=>({
   name:colorName(gen,i),hue:hueAt(gen,i),
   strengths:Object.freeze(Object.fromEntries(STR.map(x=>[x.key,swatch(gen,i,x.key)])))
  }))
 });
}
export function collisionSummary(gen){
 const accumulated=[];
 for(let g=0;g<=gen;g++)for(let i=0;i<hueCount(g);i++){
  const hue=hueAt(g,i),index=nearestRegistryIndex(hue);
  accumulated.push({generation:g,hue,index});
 }
 const histogram=new Map();
 for(const item of accumulated)histogram.set(item.index,(histogram.get(item.index)||0)+1);
 return {throughGeneration:gen,cumulativeHues:accumulated.length,
  usedAddresses:histogram.size,addressCollisions:accumulated.length-histogram.size,
  maxAddressMultiplicity:Math.max(...histogram.values())};
}
// At each g>=1, the wheel of all older hues is uniformly spaced; new generation
// colors are exactly the midpoints. This produces a 3,3,6,12,24,... branching sequence.
