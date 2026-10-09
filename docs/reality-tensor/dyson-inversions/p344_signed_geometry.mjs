/** P3.44 signed dimensions; pinned root is not a dimension. */
export const FRAMES=Object.freeze({
  "3d":Object.freeze({literal:"{{0.x.w.y}}^3",axes:Object.freeze(["x","w","y"])}),
  "4d":Object.freeze({literal:"{{0.x.w.y.z}}^4",axes:Object.freeze(["x","w","y","z"])})
});
export const SIGNS=Object.freeze([-1,0,1]);
export const COMPASS_PAIRS=Object.freeze(["N/S","E/W","N/E","N/W","S/E","S/W"]);
export function encode(frame,coordinates){
 const spec=FRAMES[frame];
 if(!spec||!Array.isArray(coordinates)||coordinates.length!==spec.axes.length||!coordinates.every(v=>SIGNS.includes(v)))throw new RangeError("signed coordinates");
 return coordinates.reduce((n,v)=>n*3+(v+1),0);
}
export function decode(frame,index){
 const spec=FRAMES[frame],count=3**(spec?.axes.length??0);
 if(!spec||!Number.isInteger(index)||index<0||index>=count)throw new RangeError("address");
 const coords=Array(spec.axes.length);
 for(let i=coords.length-1;i>=0;i--){coords[i]=index%3-1;index=Math.floor(index/3);}
 return {root:0,literal:spec.literal,coordinates:Object.fromEntries(spec.axes.map((a,i)=>[a,coords[i]])),signs:coords};
}
export function invert(coords){if(!Array.isArray(coords)||!coords.every(v=>SIGNS.includes(v)))throw new RangeError("coords");return coords.map(v=>-v);}
export function embed3to4(coords,z=0){if(!Array.isArray(coords)||coords.length!==3||!coords.every(v=>SIGNS.includes(v))||!SIGNS.includes(z))throw new RangeError("embed");return [...coords,z];}
