/** P3.45 corrected dimensional coordinates: vxw, vxwy, vxwyz. */
export const AXES=Object.freeze({3:Object.freeze(['v','x','w']),4:Object.freeze(['v','x','w','y']),5:Object.freeze(['v','x','w','y','z'])});
export const LITERALS=Object.freeze({3:'{{v.x.w}}^3',4:'{{v.x.w.y}}^4',5:'{{v.x.w.y.z}}^5'});
export function encode(dim,coords){const a=AXES[dim];if(!a||!Array.isArray(coords)||coords.length!==a.length||!coords.every(x=>Number.isInteger(x)&&x>=-1&&x<=1))throw new RangeError('coords');return coords.reduce((n,x)=>n*3+x+1,0);}
export function decode(dim,index){const a=AXES[dim];if(!a||!Number.isInteger(index)||index<0||index>=3**a.length)throw new RangeError('index');const out=Array(a.length);for(let i=a.length-1;i>=0;i--){out[i]=index%3-1;index=Math.floor(index/3);}return {root:0,axes:a,coords:out,values:Object.fromEntries(a.map((k,i)=>[k,out[i]])),literal:LITERALS[dim]};}
export function promote(dim,coords,newAxisValue=0){if(!AXES[dim+1])throw new RangeError('target');encode(dim,coords);if(![-1,0,1].includes(newAxisValue))throw new RangeError('sign');return [...coords,newAxisValue];}
export function inverse(coords){if(!Array.isArray(coords)||!coords.every(x=>[-1,0,1].includes(x)))throw new RangeError('coords');return coords.map(x=>-x);}
