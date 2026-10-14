/**
 * OASIS KET / ASTROPHAGE FIELD v2.0.
 * Additive symbolic AST: parses specified chemistry/biology labels WITHOUT
 * claiming a physical salt-growth process, quantum entanglement or astrophyage life.
 * Preserves the frozen {{i}} and dual5 floor as external read-only dependencies.
 */
import {TextEncoder,TextDecoder} from 'node:util';
import {bindOBS,recoverOBS} from './obs-token-bus-v1.2.mjs';
import {I42,CANONICAL,parse,route,unroute} from './iso-graded-chain-v1.9c.mjs';

export const VERSION='ASTROPHAGE_FIELD/v2.0';
export const SOURCE=String.raw`ASTROPHAGE FIELD -+UUUU | | uuuu -+
{
  Na+ (589nm #FFD42A) { }
  Cl- (IR teal 850nm #2AE5D3) { }
  → NaCl {
    MYCELIUM {
      CYCAD {
        DIATOME 10000001 {
          3×BEAR
        }
      }
    }
  }
}`;
export const FIELD_SHELL='-+UUUU | | uuuu -+';
export const CODE='10000001';
export const ASCII_CANONICAL=SOURCE;
export const ISO_ARITHMETIC='{3x3}^{3}';

function tokenize(source){
 if(typeof source!=='string'||source.length>65536)throw new TypeError('field must be bounded text');
 const pieces=[]; let i=0;
 const lex=/^(?:-\+|3×BEAR|→|[{}()|]|#[A-Fa-f0-9]{6}|\d+nm|\d+|[A-Za-z][A-Za-z0-9+\-]*)/u;
 while(i<source.length){
  if(/\s/u.test(source[i])){i++;continue;}
  const m=lex.exec(source.slice(i));if(!m)throw new SyntaxError(`invalid lexical character at ${i}: ${source[i]}`);
  pieces.push(m[0]);i+=m[0].length;
 }
 return pieces;
}
const EXPECTED=tokenize(SOURCE);
export function parseField(input){
 const found=tokenize(input);
 if(found.length!==EXPECTED.length)throw new SyntaxError(`field length mismatch: expected ${EXPECTED.length}, got ${found.length}`);
 for(let i=0;i<found.length;i++)if(found[i]!==EXPECTED[i])throw new SyntaxError(`field token ${i}: expected ${EXPECTED[i]}, got ${found[i]}`);
 return structuredClone({
  version:VERSION,
  shell:{left:'-+',upper:'UUUU',channel:['|','|'],lower:'uuuu',right:'-+'},
  inputs:[
   {species:'Na+',tag:{wavelengthNm:589,visibleLabel:'#FFD42A',colorType:'user-annotation'},contents:[]},
   {species:'Cl-',tag:{wavelengthNm:850,visibleLabel:'#2AE5D3',colorType:'false-color near-infrared annotation'},contents:[]}
  ],
  arrow:'→',
  output:{species:'NaCl',children:[{species:'MYCELIUM',children:[{species:'CYCAD',children:[{species:'DIATOME',codeBinary:CODE,codeValue:129,children:[{count:3,symbol:'BEAR'}]}]}]}]},
  semanticMode:'user-authored symbolic associations; not a physically established reaction chain',
  canonical:SOURCE
 });
}
export function serializeField(ast){
 // Strong structural validation: require exact canonical tree, not merely a string field.
 if(!ast||typeof ast!=='object')throw new TypeError('field AST expected');
 const ref=parseField(SOURCE);
 if(JSON.stringify(ast)!==JSON.stringify(ref))throw new SyntaxError('AST modified or not canonical');
 return SOURCE;
}
export function routeIntoOBS(input){
 const ast=parseField(input); const canonical=serializeField(ast);
 // The OBS v1.2 lexer is deliberately narrow: numerical 0..255 tokens are its
 // lossless transport adapter for ANY UTF-8 source, including arrows and ×.
 const bytes=new TextEncoder().encode(canonical);
 const numericTokens=Array.from(bytes,b=>String(b));
 const packet=bindOBS(numericTokens);
 return {version:VERSION,encoding:'UTF-8 byte as canonical OBS numeric token',byteLength:bytes.length,packet};
}
export function recoverFromOBS(wire){
 if(!wire||wire.version!==VERSION||wire.encoding!=='UTF-8 byte as canonical OBS numeric token'||
 !Number.isSafeInteger(wire.byteLength)||wire.byteLength<1||wire.byteLength>65536)throw new Error('invalid ASTROPHAGE OBS envelope');
 const recovered=recoverOBS(wire.packet);
 if(recovered.length!==wire.byteLength)throw new Error('mismatched byte count');
 const bytes=Uint8Array.from(recovered.map(s=>{
  if(!/^(0|[1-9]\d*)$/.test(s)||Number(s)>255)throw new Error('nonbyte OBS token');
  return Number(s);
 }));
 const txt=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
 return serializeField(parseField(txt));
}
export function alignment(){
 const chain=parse(CANONICAL);
 return {version:VERSION,fieldShell:FIELD_SHELL,fieldNodes:['Na+','Cl-','NaCl','MYCELIUM','CYCAD','DIATOME','BEAR'],
 iso:{originalAddresses:I42.length,views:8,directedTransitions:I42.length*8*8,
  chain:CANONICAL,arithmetic:ISO_ARITHMETIC,arithmeticValue:(3*3)**3,
  distinctGlyphZeroAddresses:I42.filter(t=>t.glyph==='0').map(t=>t.id),
  identityPositions:chain.identityOccurrences},
 obs44:{center:'00',centerGlyph:'n',namespace:'OBS44',originalIAddressForN:'i4:2'},
 diatom:{frame:'|.|.|.|',nodesPerCell:4,explicitLinks:3,rails:2},
 obs:{o:'10^10',b:'10^200',s:'10^3000',product:'10^3210'},
 field:{binaryCode:CODE,decimalCode:129,bearMultiplier:3,nearInfraredNm:850,visibleYellowNm:589},
 physics:'metadata and symbolic AST only; no experimentally verified quantum entanglement, time elimination, or biological salt production'};
}
export function verifyISO(){
 let checks=0;
 for(const t of I42)for(let src=0;src<8;src++)for(let dst=0;dst<8;dst++){
  const packed=route(t.id,src,dst);
  if(unroute(packed)!==t.id||packed.glyph!==t.glyph)throw new Error('isomorphic lane identity lost');
  checks++;
 }
 if(checks!==2688)throw new Error('bad traversal count');
 return checks;
}
parseField(SOURCE);