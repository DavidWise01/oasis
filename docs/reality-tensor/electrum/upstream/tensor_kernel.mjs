const T=(()=>{
/* ROOT0 P2.9 | 10K^2 Reality Tensor | pure ECMAScript module
 * This is a user-defined symbolic tensor, not a physical spacetime simulator.
 * Outer [||||] = four-axis, 10-position per axis square silo.
 * Inner [(((((())))))] = 10,000-position abstract cyclic address order.
 * Complex[0] = permanently anchored tensor address (0,0).
 * Transport policy is a NEW EXPLICIT implementation choice, not frozen v92.
 */
const SIDE=10, SILO_SIZE=10_000, TENSOR_SIZE=100_000_000;
const AXES=['x','y','z','~'];
const TERNARY=[-1,0,1];
const ZERO=Object.freeze({outer:0,inner:0});
const integer=(v,min,max)=>Number.isSafeInteger(v)&&v>=min&&v<=max;
function validate4(v){
  if(!Array.isArray(v)||v.length!==4||!v.every(n=>integer(n,0,9)))
    throw new RangeError('Expected [x,y,z,~] with each axis integer 0..9');
  return v;
}
function encode4(v){
  validate4(v); return v[0]*1000+v[1]*100+v[2]*10+v[3];
}
function decode4(n){
  if(!integer(n,0,SILO_SIZE-1))throw new RangeError('Silo address out of range');
  return [Math.floor(n/1000),Math.floor(n/100)%10,Math.floor(n/10)%10,n%10];
}
function validatePair(p){
  if(!p||!integer(p.outer,0,9999)||!integer(p.inner,0,9999))
    throw new RangeError('Expected {outer,inner} in 0..9999');
  return p;
}
function encodeTensor(pair){validatePair(pair);return pair.outer*SILO_SIZE+pair.inner;}
function decodeTensor(n){
  if(!integer(n,0,TENSOR_SIZE-1))throw new RangeError('Tensor address out of range');
  return {outer:Math.floor(n/SILO_SIZE),inner:n%SILO_SIZE};
}
function isZero(p){validatePair(p);return p.outer===0&&p.inner===0;}
function validateAction(a){
  if(!a||!integer(a.axis,0,3)||!integer(a.layer,0,1)||!TERNARY.includes(a.spin))
    throw new RangeError('Action requires axis 0..3, layer 0..1, spin -1/0/+1');
  return a;
}
/* Brickwork transposition on a bounded axis. Protect 0000 (outer referent):
 * on the all-zero slice, coordinate 0 is fixed and transpositions start at 1.
 * Every layer is an involution and hence invertible, even at boundaries. */
function outerSwap(id,axis=0,layer=0){
  if(!integer(id,0,9999)||!integer(axis,0,3)||!integer(layer,0,1))throw new RangeError('Invalid square route');
  const v=decode4(id),c=v[axis],reserved=v.every((u,j)=>j===axis||u===0);
  let nc=c;
  if(reserved){
    if(layer===0){if(c>=1&&c<=8)nc=(c%2===1?c+1:c-1);}
    else{if(c>=2&&c<=9)nc=(c%2===0?c+1:c-1);}
  }else if(layer===0){nc=(c%2===0?c+1:c-1);}
  else if(c>0&&c<9){nc=(c%2===1?c+1:c-1);}
  v[axis]=nc;
  return encode4(v);
}
/* The circular silo is a LOGICAL directed orbit, not Euclidean distance.
 * Its 0 address is reserved as a center anchor. Nonzero IDs form one
 * 9999-element circle. A reversible ±1 rotation changes only its index. */
function innerRotate(id,spin){
  if(!integer(id,0,9999)||!TERNARY.includes(spin))throw new RangeError('Invalid circular route');
  if(id===0||spin===0)return id;
  return 1+(((id-1+spin)%9999+9999)%9999);
}
function step(pair,action){
  validatePair(pair);validateAction(action);
  return {outer:outerSwap(pair.outer,action.axis,action.layer),inner:innerRotate(pair.inner,action.spin)};
}
function unstep(pair,action){
  validatePair(pair);validateAction(action);
  return {outer:outerSwap(pair.outer,action.axis,action.layer),inner:innerRotate(pair.inner,-action.spin)};
}
/* Reproducible, explicitly noncanonical policy. Full parity is supplied by tick. */
function actionAt(tick){
  if(!Number.isSafeInteger(tick)||tick<0)throw new RangeError('Tick must be >=0');
  return {axis:tick%4,layer:Math.floor(tick/4)%2,spin:TERNARY[tick%3]};
}
function next(pair,tick){return step(pair,actionAt(tick));}
function previous(pair,tick){return unstep(pair,actionAt(tick));}
/* Append-only event history, including compensating undo events. The caller
 * can start a NEW runtime/branch; no event in an existing branch is deleted.
 * An independent trusted digest anchor is still needed for authenticity. */
class TensorRuntime {
  #ledger=[];
  constructor(pair=ZERO){validatePair(pair);this.origin={...pair};this.pair={...pair};this.tick=0;}
  get eventCount(){return this.#ledger.length;}
  get events(){return [...this.#ledger];}
  forward(){
    const action=actionAt(this.tick),before={...this.pair},after=step(before,action);
    const event=Object.freeze({seq:this.eventCount,kind:'forward',tick:this.tick,before:Object.freeze(before),after:Object.freeze(after),action:Object.freeze(action)});
    this.#ledger.push(event);this.pair=after;this.tick++;return event;
  }
  reverse(){
    if(this.tick===0)return null;
    const action=actionAt(this.tick-1),before={...this.pair},after=unstep(before,action);
    if(encodeTensor(step(after,action))!==encodeTensor(before))throw new Error('Inverse mismatch');
    const event=Object.freeze({seq:this.eventCount,kind:'undo',tick:this.tick-1,before:Object.freeze(before),after:Object.freeze(after),action:Object.freeze(action)});
    this.#ledger.push(event);this.pair=after;this.tick--;return event;
  }
}

return {SIDE,AXES,TERNARY,ZERO,validate4,encode4,decode4,validatePair,encodeTensor,decodeTensor,isZero,validateAction,outerSwap,innerRotate,step,unstep,actionAt,next,previous,TensorRuntime};
})();
export const {SIDE,AXES,TERNARY,ZERO,validate4,encode4,decode4,validatePair,encodeTensor,decodeTensor,isZero,validateAction,outerSwap,innerRotate,step,unstep,actionAt,next,previous,TensorRuntime}=T;
