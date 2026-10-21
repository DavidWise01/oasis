import test from 'node:test';
import assert from 'node:assert/strict';
import {SAPPHON_SPECTRUM,SAPPHON_BROADBAND,SAPPHON_SPECTRUM_GLYPH,validateSapphonSpectrum} from './sapphon-spectrum.mjs';

test('seven color intervals preserve all eighteen cubit positions',()=>{
 assert.equal(SAPPHON_SPECTRUM.length,7);
 assert.deepEqual(SAPPHON_SPECTRUM.flatMap(x=>x.slots),Array.from({length:18},(_,i)=>i+1));
 assert.equal(SAPPHON_SPECTRUM_GLYPH,'{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}');
 assert.equal(validateSapphonSpectrum(),true);
});
test('each Sapphon color has a short-wavelength minus and long-wavelength plus delimiter',()=>{
 for(const [i,band] of SAPPHON_SPECTRUM.entries()){
  assert(band.low<band.high);
  if(i)assert.equal(SAPPHON_SPECTRUM[i-1].low,band.high);
  assert(band.minus.word && band.plus.word);
 }
 assert.equal(SAPPHON_SPECTRUM[0].high,750);
 assert.equal(SAPPHON_SPECTRUM[6].low,380);
});
test('each polarity gets a distinct Greek epithet, including broadband white',()=>{
 const words=SAPPHON_SPECTRUM.flatMap(x=>[x.minus.word,x.plus.word]);
 words.push(SAPPHON_BROADBAND.minus.word,SAPPHON_BROADBAND.plus.word);
 assert.equal(words.length,16);
 assert.equal(new Set(words).size,16);
 assert.equal(SAPPHON_BROADBAND.rangeLabel,'Broadband · no single wavelength');
 assert.equal(Object.hasOwn(SAPPHON_BROADBAND,'low'),false);
});
test('invalid topology and wavelength gaps fail validation',()=>{
 assert.equal(validateSapphonSpectrum(SAPPHON_SPECTRUM.slice(0,6)),false);
 assert.equal(validateSapphonSpectrum(SAPPHON_SPECTRUM.map((b,i)=>i===2?{...b,high:591}:b)),false);
});
