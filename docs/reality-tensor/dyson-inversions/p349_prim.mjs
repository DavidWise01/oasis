export const PRIM='{{1/8 x 1/8}}^{{n}}';
export const PRIMES=Object.freeze(['jane:pink','patricia:purple','toph:green','icarium:blue']);
export const AXES=Object.freeze(['N/S','E/W','N/E','N/W','S/E','S/W']);
export function scale(n){if(!Number.isSafeInteger(n)||n<0)throw new RangeError('n');return {numerator:1n,denominator:64n**BigInt(n),exponent:n};}
export function address(n,prime,axis){if(!Number.isInteger(prime)||prime<0||prime>=4||!Number.isInteger(axis)||axis<0||axis>=6)throw new RangeError('address');return {root:0,prim:PRIM,scale:scale(n),prime:PRIMES[prime],axis:AXES[axis]};}
