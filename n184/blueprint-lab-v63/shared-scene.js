'use strict';
/* N184 visual-only owned-snapshot scene cache. Frozen v6.1 unaffected. */
window.N184SharedScene=(()=>{
const G=window.N184Geometry;
const stats={builds:0,hits:0,clips:0,invalidations:0};
let sourceKey=null,source=null,cutKey=null,cut=null;
const snapshot=lines=>lines.map(l=>({a:l.a.slice(),b:l.b.slice(),color:l.color,width:l.width,name:l.name,four:l.four?l.four.map(v=>v.slice()):null}));
function sourceSignature(s){return JSON.stringify({angles:s.angles,projection:s.projection,distance:s.distance,explode:s.explode,layers:{outer:s.layers.outer,inner:s.layers.inner,box:s.layers.box,strong:s.layers.strong,medium:s.layers.medium,weak:s.layers.weak,core:s.layers.core,gate:s.layers.gate,wiring:s.layers.wiring}})}
function geometry(s){const key=sourceSignature(s);if(sourceKey!==key){source=snapshot(G.makeScene(s));sourceKey=key;cutKey=null;cut=null;stats.builds++;stats.invalidations++}else stats.hits++;return source}
function segments(s){const base=geometry(s),key=sourceKey+'|'+s.sliceAxis+'|'+s.slice+'|'+s.thick;if(key!==cutKey){cut=snapshot(G.clip(base,s.sliceAxis,s.slice,s.thick));cutKey=key;stats.clips++}return cut}
function reset(){sourceKey=null;source=null;cutKey=null;cut=null}
return{geometry,segments,reset,stats};
})();