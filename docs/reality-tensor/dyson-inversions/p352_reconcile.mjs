/** P3.52: Exact independent envelopes and reversible prime-channel traversal. */
export const SHAPES=Object.freeze({total:Object.freeze([60,24,12,2,1,1,0,0]),boxy:Object.freeze([10,6,8,4,2,1,1,0,0]),circle:Object.freeze([11,9,7,5,4,3,2,1,1,0,0])});
export const PRIMES=Object.freeze(['jane:pink','patricia:purple','toph:green','icarium:blue']);
export const AXES=Object.freeze(['N/S','E/W','N/E','N/W','S/E','S/W']);
export const STEPS=1440;
export function spec(name){const seq=SHAPES[name];if(!seq)throw new RangeError('shape');const radices=seq.slice(0,-2);const capacity=radices.reduce((a,v)=>a*v,1);return {name,sequence:[...seq],radices,capacity,sentinels:[0,0]};}
export function decode(name,index){const s=spec(name);if(!Number.isSafeInteger(index)||index<0||index>=s.capacity)throw new RangeError('index');const digits=Array(s.radices.length);for(let i=digits.length-1;i>=0;i--){digits[i]=index%s.radices[i];index=Math.floor(index/s.radices[i]);}return [...digits,0,0];}
export function encode(name,digits){const s=spec(name);if(!Array.isArray(digits)||digits.length!==s.sequence.length||digits.at(-1)!==0||digits.at(-2)!==0||digits.slice(0,-2).some((v,i)=>!Number.isInteger(v)||v<0||v>=s.radices[i]))throw new RangeError('digits');return digits.slice(0,-2).reduce((n,v,i)=>n*s.radices[i]+v,0);}
export function channel(prime,axis,sign){if(!Number.isInteger(prime)||prime<0||prime>=4||!Number.isInteger(axis)||axis<0||axis>=6||![-1,1].includes(sign))throw new RangeError('channel');return (prime*6+axis)*2+(sign===1?1:0);}
export function unchannel(i){if(!Number.isInteger(i)||i<0||i>=48)throw new RangeError('channel');return {prime:Math.floor(i/12),axis:Math.floor(i/2)%6,sign:i%2===1?1:-1};}
export function traversal(shape,address,channelIndex,index){const position=decode(shape,address);const c=unchannel(channelIndex);if(!Number.isInteger(index)||index<0||index>=STEPS)throw new RangeError('spinor');const hop=Math.floor(index/360),step=index%360;return {root:0,shape,address,position,channel:channelIndex,identity:PRIMES[c.prime],axis:AXES[c.axis],sign:c.sign,hop,step,sheet:hop%2===0?-1:1};}
export function recover(t){const c=unchannel(t.channel);return {shape:t.shape,address:encode(t.shape,t.position),channel:channel(c.prime,c.axis,c.sign),index:t.hop*360+t.step};}
