'use strict';
/* Visual-only perspective presets to avoid degenerate W-axis alignment on page open. */
(()=>{
const $=id=>document.getElementById(id);
const panel=document.createElement('section');panel.className='panel';
panel.innerHTML='<h2>00 · 4D visibility / uncollapse</h2><button id="pExpanded" type="button">EXPANDED 4D</button><button id="pOrthographic" type="button">ORTHOGRAPHIC 4D</button><button id="pAxial" type="button">AXIAL / ALIGNED</button><pre id="pReport" aria-live="polite"></pre><p class="muted">The 4D graph is unchanged. W-axis edge separation changes only through 4D view-plane rotation and projection.</p>';
document.querySelector('aside').prepend(panel);
const presets={
 expanded:{angles:[0,0,29,0,-21,14],projection:'perspective',distance:5.2},
 orthographic:{angles:[0,0,31,0,-24,17],projection:'orthographic',distance:5.2},
 axial:{angles:[0,0,0,0,0,0],projection:'perspective',distance:4}
};
function setPreset(name){
 const p=presets[name];
 for(let i=0;i<6;i++){const slider=$('rot'+i);slider.value=p.angles[i];slider.dispatchEvent(new Event('input',{bubbles:true}))}
 $('projection').value=p.projection;$('projection').dispatchEvent(new Event('change',{bubbles:true}));
 $('distance').value=p.distance;$('distance').dispatchEvent(new Event('input',{bubbles:true}));
 const projected=window.N184Geometry.vertices.map(v=>window.N184Geometry.projected4(v.map(x=>x*1.26),p.angles,p.projection,p.distance));
 const distances=window.N184Geometry.edges.filter(([a,b])=>window.N184Geometry.vertices[a][3]!==window.N184Geometry.vertices[b][3]).map(([a,b])=>Math.hypot(projected[a].x-projected[b].x,projected[a].y-projected[b].y,projected[a].z-projected[b].z));
 const min=Math.min(...distances);
 $('pReport').textContent='VIEW: '+name.toUpperCase()+'\nW-AXIS EDGES: '+distances.length+'\nMIN PROJECTED W EDGE: '+min.toFixed(5)+' LU\nTOPOLOGY: 16 vertices / 32 edges';
 document.querySelectorAll('#pExpanded,#pOrthographic,#pAxial').forEach(el=>el.setAttribute('aria-pressed',el.id==='p'+name[0].toUpperCase()+name.slice(1)));
}
$('pExpanded').onclick=()=>setPreset('expanded');
$('pOrthographic').onclick=()=>setPreset('orthographic');
$('pAxial').onclick=()=>setPreset('axial');
setPreset('expanded');
window.N184ProjectionPresets={setPreset,presets};
})();