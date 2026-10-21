import fs from 'node:fs';
import assert from 'node:assert/strict';
import {STR,MAX_GENERATION,SOURCE_COUNT,SOURCE_ORBITS,hueCount,cumulativeCount,hueAt,hsvRGB,rgbHex,colorName,
 nearestRegistryIndex,orbitFor,registryHue,wrappedAngularErrorDegrees,swatch,generation,collisionSummary} from './color_core.mjs';
const spec=JSON.parse(fs.readFileSync(new URL('./spec.json',import.meta.url),'utf8'));
const checks={};const check=(name,fn)=>{fn();checks[name]=true};
const near=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<t,String(a)+' != '+String(b));
check('new additive independent schema',()=>assert.equal(spec.schema,'oasis/n184/generational-color-lattice/v91'));
check('RGB primaries not paint RYB',()=>assert.equal(spec.palette.digitalPrimarySet,'R,G,B'));
check('weak medium strong ordered',()=>assert.deepEqual(STR.map(x=>x.name),['Weak','Medium','Strong']));
check('weak exactly one third',()=>near(STR[0].amplitude,1/3));
check('medium exactly two thirds',()=>near(STR[1].amplitude,2/3));
check('strong exactly unity',()=>assert.equal(STR[2].amplitude,1));
check('only three distinct strengths',()=>assert.equal(STR.length,3));
check('generation zero has three primaries',()=>assert.equal(hueCount(0),3));
check('generation one has three secondaries',()=>assert.equal(hueCount(1),3));
check('generation two has six tertiaries',()=>assert.equal(hueCount(2),6));
check('generation three has 12 hues',()=>assert.equal(hueCount(3),12));
check('generation four has 24 hues',()=>assert.equal(hueCount(4),24));
check('generation five has 48 hues',()=>assert.equal(hueCount(5),48));
check('generation six has 96 hues',()=>assert.equal(hueCount(6),96));
check('generation seven has 192 hues',()=>assert.equal(hueCount(7),192));
check('generation eight has 384 hues',()=>assert.equal(hueCount(8),384));
check('virtual generation bounded 0..8',()=>assert.equal(MAX_GENERATION,8));
check('gen0 total three',()=>assert.equal(cumulativeCount(0),3));
check('gen1 total six',()=>assert.equal(cumulativeCount(1),6));
check('gen2 total twelve',()=>assert.equal(cumulativeCount(2),12));
check('gen8 total 768',()=>assert.equal(cumulativeCount(8),768));
check('count recursion each generation is prior cumulative',()=>{for(let g=2;g<=8;g++)assert.equal(hueCount(g),cumulativeCount(g-1))});
check('exact red green blue angles',()=>assert.deepEqual([hueAt(0,0),hueAt(0,1),hueAt(0,2)],[0,120,240]));
check('exact yellow cyan magenta angles',()=>assert.deepEqual([hueAt(1,0),hueAt(1,1),hueAt(1,2)],[60,180,300]));
check('tertiary 30 90 150 210 270 330',()=>assert.deepEqual(generation(2).colors.map(x=>x.hue),[30,90,150,210,270,330]));
check('primary color names',()=>assert.deepEqual(generation(0).colors.map(c=>c.name),['Red','Green','Blue']));
check('secondary color names',()=>assert.deepEqual(generation(1).colors.map(c=>c.name),['Yellow','Cyan','Magenta']));
check('six named tertiaries',()=>assert.deepEqual(generation(2).colors.map(c=>c.name),['Orange','Chartreuse','Spring green','Azure','Violet','Rose']));
check('high gen gets deterministic address labels',()=>assert.equal(colorName(6,0),'G6 · 001'));
check('all generations have increasing nonduplicate hues',()=>{for(let g=0;g<=8;g++){const h=generation(g).colors.map(c=>c.hue);assert.equal(new Set(h).size,h.length);assert.ok(h.every((v,i)=>v>=0&&v<360&&(i===0||v>h[i-1])))}});
check('no generation reuses earlier hue',()=>{const prior=new Set();for(let g=0;g<=8;g++)for(const {hue}of generation(g).colors){assert.equal(prior.has(hue),false);prior.add(hue)}});
check('Gen g>=1 colors exactly bisect older wheel',()=>{
 let prior=generation(0).colors.map(x=>x.hue);
 for(let g=1;g<=8;g++){
  const curr=generation(g).colors.map(x=>x.hue);
  const old=prior.slice().sort((a,b)=>a-b);
  assert.equal(curr.length,old.length);
  for(let i=0;i<old.length;i++){
   const next=i===old.length-1?old[0]+360:old[i+1];
   near(curr[i],(old[i]+next)/2%360);
  }
  prior=[...prior,...curr];
 }
});
check('RGB pure red',()=>assert.equal(rgbHex(hsvRGB(0)),'#FF0000'));
check('RGB pure green',()=>assert.equal(rgbHex(hsvRGB(120)),'#00FF00'));
check('RGB pure blue',()=>assert.equal(rgbHex(hsvRGB(240)),'#0000FF'));
check('RGB secondary yellow',()=>assert.equal(rgbHex(hsvRGB(60)),'#FFFF00'));
check('RGB secondary cyan',()=>assert.equal(rgbHex(hsvRGB(180)),'#00FFFF'));
check('RGB secondary magenta',()=>assert.equal(rgbHex(hsvRGB(300)),'#FF00FF'));
check('orange tertiary',()=>assert.equal(rgbHex(hsvRGB(30)),'#FF8000'));
check('positive hue wraps 360',()=>assert.equal(rgbHex(hsvRGB(360)),'#FF0000'));
check('negative hue wraps',()=>assert.equal(rgbHex(hsvRGB(-120)),'#0000FF'));
check('weak red #550000',()=>assert.equal(swatch(0,0,'W').displayHex,'#550000'));
check('medium red #AA0000',()=>assert.equal(swatch(0,0,'M').displayHex,'#AA0000'));
check('strong red #FF0000',()=>assert.equal(swatch(0,0,'S').displayHex,'#FF0000'));
check('three strengths retain identical hue/address',()=>assert.equal(new Set(STR.map(s=>swatch(2,3,s.key).registryAddress)).size,1));
check('every generated hue has three strength swatches',()=>{for(let g=0;g<=8;g++)assert.equal(generation(g).swatches,hueCount(g)*3)});
check('valid source registry addresses total 370',()=>assert.equal(SOURCE_COUNT,370));
check('orbit lengths 122 122 126',()=>assert.deepEqual(SOURCE_ORBITS.map(o=>o.end-o.start+1),[122,122,126]));
check('orbit boundaries work',()=>assert.deepEqual([orbitFor(1),orbitFor(122),orbitFor(123),orbitFor(244),orbitFor(245),orbitFor(370)],[1,1,2,2,3,3]));
check('registry original index of red is 1',()=>assert.equal(nearestRegistryIndex(0),1));
check('registry original index of yellow near 63',()=>assert.equal(nearestRegistryIndex(60),63));
check('registry original green in second orbit',()=>assert.equal(orbitFor(nearestRegistryIndex(120)),2));
check('registry original blue in third orbit',()=>assert.equal(orbitFor(nearestRegistryIndex(240)),3));
check('registry source hue formula at index one',()=>assert.equal(registryHue(1),0));
check('registry source hue formula at final position',()=>near(registryHue(370),369*360/370));
check('registered hue mode .78 .98 preserved',()=>assert.deepEqual([spec.sourceAlignment.registryHueMode.saturation,spec.sourceAlignment.registryHueMode.value],[.78,.98]));
check('source preview differs from custom strong red',()=>assert.notEqual(swatch(0,0,'S').registryPreviewHex,swatch(0,0,'S').displayHex));
check('registry approx hue error at most half a source step',()=>{
 for(let g=0;g<=8;g++)for(let i=0;i<hueCount(g);i++)
  assert.ok(swatch(g,i,'S').registryHueErrorDegrees<=180/370+1e-8)
});
check('wrapped angular error handles 359 vs 1',()=>near(wrappedAngularErrorDegrees(359,1),2));
check('swatches return fixed index mode hue',()=>assert.equal(swatch(1,1,'S').registryMode,'hue'));
check('accumulated wheel gen7 exceeds 370 addresses',()=>assert.equal(collisionSummary(7).cumulativeHues,384));
check('gen7 has at least 14 address collisions',()=>assert.ok(collisionSummary(7).addressCollisions>=14));
check('gen8 has 768 virtual hues',()=>assert.equal(collisionSummary(8).cumulativeHues,768));
check('source 370 addresses never expanded',()=>assert.equal(spec.sourceAlignment.canonicalAddressCount,370));
check('prior second palette mode unchanged',()=>assert.ok(spec.sourceAlignment.registryOtherMode.includes('six')));
check('not asserting light intensity physics',()=>assert.ok(spec.generation.photometricCaveat.includes('not calibrated')));
check('weak med strong are not fundamental forces',()=>assert.ok(spec.limitations.some(x=>x.includes('weak/strong nuclear'))));
check('Ada year still frozen',()=>assert.equal(spec.preserved.gen0HistoryAdaYear,1832));
check('1970 history model unchanged',()=>assert.equal(spec.preserved.gen1HistoryModelYear,1970));
check('6/80/240 symbolic ring unchanged',()=>assert.deepEqual([spec.preserved.ringArcs,spec.preserved.phaseSteps,spec.preserved.microticks],[6,80,240]));
check('CERN quads preserved A0 B3 C0 D0',()=>assert.deepEqual(Object.values(spec.preserved.quadMagnetInventory),[0,3,0,0]));
check('time offset still zero',()=>assert.equal(spec.preserved.motherNatureOffsetYears,0));
check('generation out of bound rejected',()=>assert.throws(()=>hueCount(9)));
check('negative generation rejected',()=>assert.throws(()=>hueCount(-1)));
check('invalid hue index rejected',()=>assert.throws(()=>hueAt(0,3)));
check('invalid source address zero rejected',()=>assert.throws(()=>orbitFor(0)));
check('invalid HSV saturation rejected',()=>assert.throws(()=>hsvRGB(0,2,.9)));
check('invalid HSV value rejected',()=>assert.throws(()=>hsvRGB(0,1,-.1)));
check('invalid RGB channels rejected',()=>assert.throws(()=>rgbHex([0,256,255])));
check('unknown strength rejected',()=>assert.throws(()=>swatch(0,0,'X')));
check('viewer is locally self-contained',()=>{const x=fs.readFileSync(new URL('./index.html',import.meta.url),'utf8');for(const needle of ['color_core.mjs','canvas','370-hue address','Weak','Medium','Strong'])assert.ok(x.includes(needle),needle)});
console.log(JSON.stringify({result:'PASS',passed:Object.keys(checks).length,failed:0,
  verification:{genCounts:[0,1,2,3,4,5,6,7,8].map(g=>hueCount(g)),
   gen7AddressCollisions:collisionSummary(7).addressCollisions}},null,2));
