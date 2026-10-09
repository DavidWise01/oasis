/** ROOT0 P3.46: discrete containment model; symbolic, not physical geometry. */
export const RADICES=Object.freeze([7,5,3,1,1]);
export const BOXY=Object.freeze([10,6,8,4,2,1,1,0,0]);
export const CIRCLE=Object.freeze([11,9,7,5,3,2,1,1,0,0]);
export const AXES=Object.freeze({3:['v','x','w'],4:['v','x','w','y'],5:['v','x','w','y','z']});
export const PRIMES=Object.freeze(['jane:pink','patricia:purple','toph:green','icarium:blue']);
export const DIRECTIONS=Object.freeze(['N/S','E/W','N/E','N/W','S/E','S/W']);
export const CAPACITY=RADICES.reduce((a,b)=>a*b,1);
export function nest(parts){if(!Array.isArray(parts)||parts.length!==RADICES.length||parts.some((v,i)=>!Number.isInteger(v)||v<0||v>=RADICES[i]))throw new RangeError('nest digits');return parts.reduce((n,v,i)=>n*RADICES[i]+v,0);}
export function unnest(index){if(!Number.isInteger(index)||index<0||index>=CAPACITY)throw new RangeError('nest index');const out=Array(RADICES.length);for(let i=RADICES.length-1;i>=0;i--){out[i]=index%RADICES[i];index=Math.floor(index/RADICES[i]);}return out;}
export function geometric(sequence){const template=sequence==='boxy'?BOXY:sequence==='circle'?CIRCLE:null;if(!template)throw new RangeError('shape');return {shape:sequence,layers:[...template],outer:template[0],center:template.slice(-2),scaleThreshold:11};}
export function normalizeScale(value){if(!Number.isFinite(value)||value<0)throw new RangeError('coordinate');return value>11?{structural:11,scale:value/11,scaled:true}:{structural:value,scale:1,scaled:false};}
export function signed(dim,values){const axes=AXES[dim];if(!axes||!Array.isArray(values)||values.length!==axes.length||values.some(v=>![-1,0,1].includes(v)))throw new RangeError('signed');return {root:0,axes:[...axes],coordinates:Object.fromEntries(axes.map((a,i)=>[a,values[i]]))};}
export function carrier(index,prime,direction,shape,coordinateDim,values){if(!Number.isInteger(index)||index<0||index>=1440||!Number.isInteger(prime)||prime<0||prime>=4||!Number.isInteger(direction)||direction<0||direction>=6)throw new RangeError('carrier index');return {slot:index,hop:Math.floor(index/360),step:index%360,sign:Math.floor(index/360)%2?-1:1,prime:PRIMES[prime],direction:DIRECTIONS[direction],enclosure:geometric(shape),state:signed(coordinateDim,values),nest:unnest(index%CAPACITY)};}
