/** P3.48 six signed internal traversal axes inside the circle enclosure. */
export const RADICES=Object.freeze([11,9,7,5,4,3,2,1,1]);
export const SENTINELS=Object.freeze([0,0]);
export const AXES=Object.freeze(['N/S','E/W','N/E','N/W','S/E','S/W']);
export const CAPACITY=RADICES.reduce((a,b)=>a*b,1);
export const TOTAL=CAPACITY*AXES.length;
export const SHELL_STEPS=183, ROTATION_STEPS=360;
export function decodeSphere(index){
 if(!Number.isSafeInteger(index)||index<0||index>=CAPACITY)throw new RangeError('sphere index');
 const digits=Array(RADICES.length);for(let j=RADICES.length-1;j>=0;j--){digits[j]=index%RADICES[j];index=Math.floor(index/RADICES[j]);}
 return [...digits,...SENTINELS];
}
export function encodeSphere(digits){
 if(!Array.isArray(digits)||digits.length!==11||digits[9]!==0||digits[10]!==0||digits.slice(0,9).some((n,i)=>!Number.isInteger(n)||n<0||n>=RADICES[i]))throw new RangeError('sphere digits');
 return digits.slice(0,9).reduce((a,n,i)=>a*RADICES[i]+n,0);
}
export function encode(axis,sphere){if(!Number.isInteger(axis)||axis<0||axis>=6)throw new RangeError('axis');decodeSphere(sphere);return axis*CAPACITY+sphere;}
export function decode(index){if(!Number.isSafeInteger(index)||index<0||index>=TOTAL)throw new RangeError('index');const axis=Math.floor(index/CAPACITY),sphere=index%CAPACITY;return {axis,axisLabel:AXES[axis],sphere,digits:decodeSphere(sphere),root:0};}
export function motion(tick,axis){if(!Number.isSafeInteger(tick)||tick<0||!Number.isInteger(axis)||axis<0||axis>=6)throw new RangeError('motion');return {root:0,axis:AXES[axis],shell:tick%SHELL_STEPS,shellTurn:Math.floor(tick/SHELL_STEPS),torus:tick%ROTATION_STEPS,torusTurn:Math.floor(tick/ROTATION_STEPS),sheet:Math.floor(tick/ROTATION_STEPS)%2===0?-1:1};}
