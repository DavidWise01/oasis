// OASIS {{i & dd}} v0.2: deterministic dual-rail carrier, not physical entanglement.
// Requires unchanged sibling file diatom.mjs in architecture/diatom-diamond.
import {createHash} from 'node:crypto';
import {encode, decode, project, serialize, glyphAt, FRAME} from './diatom.mjs';
export const PROCESSOR = '{{i & dd}}';
export const VERSION = '0.2.0';
export const GEOMETRY = FRAME + ' & ' + FRAME;
const h = value => createHash('sha256').update(value).digest('hex');
const canon = value => JSON.stringify(value);
function fail(msg){throw new Error('i&dd: '+msg);}
function countView(v){if (!Number.isInteger(v)||v<0||v>7) fail('view outside 0..7');return v;}
function lineageCheck(parent,generation){
  if(typeof parent!=='string'||!parent.length||parent.length>512) fail('invalid parent witness');
  if(!Number.isSafeInteger(generation)||generation<0) fail('invalid generation');
}
function identitySeal(addresses,sourceView,parent,generation) {
  return h(canon(['i&dd/v0.2',sourceView,parent,generation,addresses]));
}
function wireWitness(seal,plus,minus) {
  return h(canon(['i&dd/witness-v0.2',seal,serialize(plus),serialize(minus)]));
}
export function bindTwin(addresses,{sourceView=0,positiveView=0,negativeView=4,parent='ROOT',generation=0}={}) {
  countView(sourceView);countView(positiveView);countView(negativeView);
  lineageCheck(parent,generation);
  if(!Array.isArray(addresses)) fail('addresses must be an array');
  addresses.forEach(glyphAt);
  const positive=project(encode(addresses,sourceView),positiveView);
  const negative=project(encode(addresses.slice().reverse(),sourceView),negativeView);
  const seal=identitySeal(addresses,sourceView,parent,generation);
  return {
    language:PROCESSOR,version:VERSION,geometry:GEOMETRY,
    identity:{sourceView,length:addresses.length,seal},
    rails:{positive,negative},
    lineage:{parent,generation},
    witness:wireWitness(seal,positive,negative)
  };
}
export function recoverTwin(packet){
  if(!packet||packet.language!==PROCESSOR||packet.version!==VERSION||packet.geometry!==GEOMETRY) fail('bad processor envelope');
  const {identity,rails,lineage,witness}=packet;
  if(!identity||!rails||!lineage) fail('missing identity/rail/lineage');
  countView(identity.sourceView);lineageCheck(lineage.parent,lineage.generation);
  const front=decode(rails.positive);
  const mirror=decode(rails.negative).reverse();
  if(rails.positive.sourceView!==identity.sourceView || rails.negative.sourceView!==identity.sourceView) fail('source view mismatch');
  if(front.length!==identity.length||mirror.length!==identity.length) fail('length mismatch');
  if(front.some((token,index)=>token!==mirror[index])) fail('mirror correlation violation');
  const calculatedSeal=identitySeal(front,identity.sourceView,lineage.parent,lineage.generation);
  if(calculatedSeal!==identity.seal) fail('identity seal violation');
  if(wireWitness(calculatedSeal,rails.positive,rails.negative)!==witness) fail('witness seal violation');
  return front;
}
export function rotateTwin(packet,positiveView,negativeView){
  const addresses=recoverTwin(packet);
  return bindTwin(addresses,{
    sourceView:packet.identity.sourceView,positiveView,negativeView,
    parent:packet.lineage.parent,generation:packet.lineage.generation
  });
}
export function nextGeneration(packet,nextAddresses){
  recoverTwin(packet);
  return bindTwin(nextAddresses,{
    sourceView:packet.identity.sourceView,
    positiveView:packet.rails.positive.view,
    negativeView:packet.rails.negative.view,
    parent:packet.witness,
    generation:packet.lineage.generation+1
  });
}
export function mirrorReverse(packet){
  return nextGeneration(packet,recoverTwin(packet).slice().reverse());
}
export function serializeTwin(packet){
  recoverTwin(packet);
  return JSON.stringify(packet,null,2);
}
export function deserializeTwin(text){
  let packet;
  try{packet=JSON.parse(text);}catch{fail('invalid JSON');}
  recoverTwin(packet);
  return packet;
}
