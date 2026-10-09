/** P3.12 symbolic address compiler; does not imply physical spacetime transport. */
export const CANONICAL=Object.freeze({
dimensions:Object.freeze(['-1+','-2+','-3+']),
quad:'AaBbCcDd',layers:Object.freeze(['dimensions','quads','vogels','voxels','vectors']),
range:'inf - +inf',
stargate:Object.freeze(['00','11','22','33','42','24','33','22','11','00'])
});
export function compile(address=CANONICAL.stargate){
 if(!Array.isArray(address)||address.length!==10||address.some(x=>typeof x!=='string'||!/^\d\d$/.test(x)))throw new RangeError('Ten two-digit address tokens required');
 const operations=address.map((token,index)=>Object.freeze({step:index,token,from:token[0],to:token[1],direction:index<5?'ingress':'egress'}));
 return Object.freeze({operations,palindrome:address.every((s,i)=>s===address[address.length-1-i]),conjugatePalindrome:address.every((s,i)=>s===address[address.length-1-i].split('').reverse().join('')),centerPair:[address[4],address[5]]});
}
export function reverse(operations){return operations.slice().reverse().map(x=>({...x,direction:x.direction==='ingress'?'egress':'ingress',from:x.to,to:x.from}));}
export function reconstitute(operations){return reverse(reverse(operations));}
export function validate(){const c=compile();return {tokens:c.operations.length,uniqueTokens:new Set(CANONICAL.stargate).size,palindrome:c.palindrome,conjugatePalindrome:c.conjugatePalindrome,centerPair:c.centerPair,roundtrip:JSON.stringify(reconstitute(c.operations))===JSON.stringify(c.operations),dimensions:CANONICAL.dimensions,quad:CANONICAL.quad};}
