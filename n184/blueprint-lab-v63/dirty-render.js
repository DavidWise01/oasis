'use strict';
/* Renderer-only dirty-state signatures. Frozen mapping/recovery untouched. */
window.N184DirtyRender=(()=>{
let last=null,draws=0,skips=0;
function signature(state,canvasSizes){
return JSON.stringify({
 angles:state.angles,projection:state.projection,distance:state.distance,
 sliceAxis:state.sliceAxis,slice:state.slice,thick:state.thick,explode:state.explode,
 layers:state.layers,yaw:state.yaw,pitch:state.pitch,zoom:state.zoom,
 step:state.step,address:state.address,nibble:state.nibble,canvasSizes
});
}
function shouldDraw(state,sizes){const key=signature(state,sizes);if(key===last){skips++;return false}last=key;draws++;return true}
function invalidate(){last=null}
function metrics(){return {draws,skips}}
return{shouldDraw,invalidate,signature,metrics};
})();