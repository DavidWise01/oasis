/* OASIS Convergence — generative projection of frozen v1.0; no dependency or mutation of canonical laws. */
export const FREEZE = Object.freeze({
  version:"1.0", unity:"3/2/1", convergence:"3/3/3 → ∞ → 1",
  tracks:Object.freeze(["i","u","u.s"]),
  timelines:Object.freeze(["past","present","future"]),
  choices:Object.freeze([-1,0,1]),
  closure:"{{i.u.us}}"
});
const digits = n => {if(!Number.isInteger(n)||n<0||n>26)throw Error("address must be 0..26");return [Math.floor(n/9),Math.floor(n/3)%3,n%3];};
export function decode(address){
 const [t,l,c]=digits(address);
 return Object.freeze({address,track:FREEZE.tracks[t],timeline:FREEZE.timelines[l],choice:FREEZE.choices[c],coordinate:Object.freeze([t,l,c])});
}
export function encode(track,timeline,choice){
 const t=FREEZE.tracks.indexOf(track), l=FREEZE.timelines.indexOf(timeline), c=FREEZE.choices.indexOf(choice);
 if(t<0||l<0||c<0)throw Error("noncanonical state");return t*9+l*3+c;
}
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
export function* generate(seed=".",length=12){
 if(!Number.isSafeInteger(length)||length<0||length>10000)throw Error("length must be 0..10000");
 let state=hash(String(seed));
 for(let n=0;n<length;n++){
   state=(Math.imul(1664525,state)+1013904223)>>>0;
   const node=decode(state%27);
   yield Object.freeze({step:n+1,...node,token:`{{${node.track}|${node.timeline}|${node.choice}}}`});
 }
}
export function serialize(seed,length){return Object.freeze({freeze:FREEZE.version,seed:String(seed),states:[...generate(seed,length)],returnTo:FREEZE.closure});}
