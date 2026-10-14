/** OASIS {{i}} six-node graded chain v1.9c; additive, no physics interpretation. */
export const SYMBOLS=Object.freeze(['i','so','more','Pp','i','CcC']);
export const LEVELS=Object.freeze([1,2,3,4,5]);
export const CANONICAL='{{i}} < {{so}} << {{more}} <<< {{Pp}} <<<< {{i}} <<<<< {{CcC}}';
export const ARITHMETIC=Object.freeze({form:'{3x3}^{3}',value:729});
const LANG=Object.freeze([
 ['.',':','|',"'","z"],['a','b','c','d','e'],['f','g','h','i','j','k'],
 ['l','m','n','o','p'],['q','r','s','t','u','v'],['w','x','y','0','1'],
 ['2','4','6','8','0'],['1','3','5','7','9']
]);
export const I42=Object.freeze(LANG.flatMap((lane,r)=>lane.map((glyph,j)=>Object.freeze({
 id:'i'+(r+1)+':'+j,glyph,lane:r,slot:j
}))));
export function canonicalize(s) {
 if(typeof s!=='string')throw new TypeError('chain text expected');
 const segments=s.match(/\{\{[^{}]*\}\}|<+/g)||[];
 if(segments.join('')!==s.replace(/\s+/g,'')||segments.length!==11)throw new SyntaxError('invalid chain tokens');
 for(let i=0;i<6;i++)if(segments[2*i]!=='{{'+SYMBOLS[i]+'}}')throw new SyntaxError('node '+i);
 for(let i=0;i<5;i++)if(segments[2*i+1]!=='<'.repeat(LEVELS[i]))throw new SyntaxError('operator '+i);
 return CANONICAL;
}
export function parse(s) {
 canonicalize(s);
 return Object.freeze({version:'1.9c',nodes:SYMBOLS.map((glyph,position)=>({glyph,position})),
   edges:LEVELS.map((depth,i)=>({from:i,to:i+1,depth,lexeme:'<'.repeat(depth)})),
   identityOccurrences:[0,4],arithmetic:ARITHMETIC});
}
export function route(id,sourceView,targetView) {
 if(!Number.isInteger(sourceView)||sourceView<0||sourceView>7||
    !Number.isInteger(targetView)||targetView<0||targetView>7)throw new RangeError('view must be 0..7');
 const token=I42.find(x=>x.id===id);if(!token)throw new RangeError('unknown coordinate-distinct identity');
 return Object.freeze({version:'1.9c',id,sourceView,targetView,glyph:token.glyph,lane:token.lane,slot:token.slot,
   identityOccurrences:[0,4]});
}
export function unroute(packet) {
 if(!packet||packet.version!=='1.9c'||JSON.stringify(packet.identityOccurrences)!=='[0,4]')throw new Error('invalid ISO chain');
 const expected=route(packet.id,packet.sourceView,packet.targetView);
 if(Object.keys(expected).length!==Object.keys(packet).length||
    Object.entries(expected).some(([key,value])=>JSON.stringify(packet[key])!==JSON.stringify(value)))
    throw new Error('route mismatch');
 return expected.id;
}
canonicalize(CANONICAL);
