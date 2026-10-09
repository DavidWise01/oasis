/** P3.50: exact hierarchical prim address, no expanded lattice allocation. */
export const PRIM='{{1/8 x 1/8}}^{{n}}';
export const PRIMES=Object.freeze(['jane:pink','patricia:purple','toph:green','icarium:blue']);
export const AXES=Object.freeze(['N/S','E/W','N/E','N/W','S/E','S/W']);
export const ROOT=0;
export function scale(n){if(!Number.isSafeInteger(n)||n<0||n>10000)throw new RangeError('depth');return {numerator:1n,denominator:64n**BigInt(n)};}
export function encode(prime,axis,sign=1){if(!Number.isInteger(prime)||prime<0||prime>=4||!Number.isInteger(axis)||axis<0||axis>=6||![-1,1].includes(sign))throw new RangeError('address');return (prime*6+axis)*2+(sign===1?1:0);}
export function decode(address){if(!Number.isInteger(address)||address<0||address>=48)throw new RangeError('address');return {prime:Math.floor(address/12),axis:Math.floor(address/2)%6,sign:address%2?1:-1};}
export function cell(n,address,hop=0,step=0){const d=decode(address);if(!Number.isInteger(hop)||hop<0||hop>=4||!Number.isInteger(step)||step<0||step>=360)throw new RangeError('motion');return {root:ROOT,depth:n,scale:scale(n),address,carrier:PRIMES[d.prime],axis:AXES[d.axis],sign:d.sign,hop,step,mobiusSheet:hop%2?-1:1};}
export function inverseMotion(hop,step){if(!Number.isInteger(hop)||hop<0||hop>=4||!Number.isInteger(step)||step<0||step>=360)throw new RangeError('motion');return hop*360+step;}