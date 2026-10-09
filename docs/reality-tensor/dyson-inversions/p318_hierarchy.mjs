import {route,unroute} from './p317_route.mjs';
export const DIMENSIONS=Object.freeze(['-1+','-2+','-3+']);
export const QUADS=Object.freeze(['Aa','Bb','Cc','Dd']);
export const LEVELS=Object.freeze(['vogel','voxel','vector']);
const INT=/^(0|-?[1-9][0-9]*)$/;
export function encode(seed,dimension=0,quad=0,coords=[0n,0n,0n]){
 if(!Number.isInteger(dimension)||dimension<0||dimension>=3)throw new RangeError('dimension');
 if(!Number.isInteger(quad)||quad<0||quad>=4)throw new RangeError('quad');
 if(!Array.isArray(coords)||coords.length!==3||coords.some(v=>typeof v!=='bigint'))throw new TypeError('coordinates must be three bigint integers');
 return [route(seed),DIMENSIONS[dimension],QUADS[quad],...coords.map(String)].join('|');
}
export function decode(text){
 if(typeof text!=='string')throw new TypeError('address');
 const pieces=text.split('|');if(pieces.length!==6)throw new RangeError('hierarchy depth');
 const [prefix,d,q,...values]=pieces;
 const dimension=DIMENSIONS.indexOf(d),quad=QUADS.indexOf(q);
 if(dimension<0||quad<0||values.some(v=>!INT.test(v)||v==='-0'))throw new RangeError('noncanonical hierarchy');
 const seed=unroute(prefix),coords=values.map(BigInt);
 if(encode(seed,dimension,quad,coords)!==text)throw new RangeError('noncanonical encoding');
 return {seed,dimension,quad,coords};
}
export function inverse(text){const {seed,dimension,quad,coords}=decode(text);return encode(seed,dimension,quad,coords);}
export function specimen(seed){return encode(seed,2,3,[-2n,3n,0n]);}
