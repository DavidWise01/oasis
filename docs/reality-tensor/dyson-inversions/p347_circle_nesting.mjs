/** P3.47 corrected circle envelope; capacities and traversal are distinct. */
export const CIRCLE=Object.freeze([11,9,7,5,4,3,2,1,1,0,0]);
export const RADICES=Object.freeze(CIRCLE.slice(0,-2));
export const SENTINELS=Object.freeze([0,0]);
export const CAPACITY=RADICES.reduce((a,b)=>a*b,1);
export const TRAVERSAL=183; // user-proposed symbolic traversal, not derivable from radix sequence
export const PRIMES=Object.freeze(['jane:pink','patricia:purple','toph:green','icarium:blue']);
export function encode(digits){if(!Array.isArray(digits)||digits.length!==RADICES.length||digits.some((n,i)=>!Number.isInteger(n)||n<0||n>=RADICES[i]))throw new RangeError('digits');return digits.reduce((acc,n,i)=>acc*RADICES[i]+n,0);}
export function decode(index){if(!Number.isInteger(index)||index<0||index>=CAPACITY)throw new RangeError('index');const d=Array(RADICES.length);for(let i=d.length-1;i>=0;i--){d[i]=index%RADICES[i];index=Math.floor(index/RADICES[i]);}return Object.freeze([...d,...SENTINELS]);}
export function walk(tick){if(!Number.isSafeInteger(tick)||tick<0)throw new RangeError('tick');return {root:0,turn:Math.floor(tick/TRAVERSAL),position:tick%TRAVERSAL,sign:Math.floor(tick/TRAVERSAL)%2===0?-1:1};}
export function carrier(tick,prime){if(!Number.isInteger(prime)||prime<0||prime>=4)throw new RangeError('prime');return {...walk(tick),prime:PRIMES[prime],address:tick%CAPACITY};}
