'use strict';
/* N184 blueprint visual-only browser validation; does not write IndexedDB. */
(()=>{
const G=window.N184Geometry,$=id=>document.getElementById(id);
const section=document.createElement('section');section.className='panel';
section.innerHTML='<h2>15 · Browser validation console</h2><button id="runVisualChecks">RUN VISUAL CHECKS</button><button id="copyVisualChecks">COPY REPORT</button><pre id="visualResults" aria-live="polite">Not run. Visual browser acceptance remains pending.</pre><p class="muted">This console tests geometry functions, canvas availability, drawing wiring, SVG export hooks, and projected viewport coordinates. It does not simulate hardware power loss or independently certify visual appearance.</p>';
document.querySelector('aside').append(section);
const tests=[];
function check(label,fn){try{const v=fn();tests.push({label,status:v?'PASS':'FAIL'});}catch(e){tests.push({label,status:'ERROR: '+e.message})}}
function execute(){
tests.length=0;
check('4D tesseract: 16 vertices / 32 edges',()=>G.vertices.length===16&&G.edges.length===32);
check('Every vertex has degree 4',()=>G.vertices.every((_,i)=>G.edges.filter(e=>e.includes(i)).length===4));
check('Each edge differs in exactly one axis',()=>G.edges.every(([a,b])=>G.vertices[a].filter((x,k)=>x!==G.vertices[b][k]).length===1));
check('Reversible mapping all 38,400 pairs',()=>G.validate().uniquePairs===38400);
check('X-core vector zero sum',()=>[[-2,3],[-3,2],[2,-3],[3,-2]].reduce((p,v)=>[p[0]+v[0],p[1]+v[1]],[0,0]).every(x=>x===0));
check('4D planar rotation preserves norm',()=>{const p=[1,-1,1,-1],r=G.projected4(p,[35,20,-40,61,9,77],'orthographic',4).q4;return Math.abs(r.reduce((a,b)=>a+b*b,0)-4)<1e-10});
check('Projection points remain finite',()=>G.vertices.every(v=>{let p=G.projected4(v,[0,0,0,0,0,0],'perspective',4);return [p.x,p.y,p.z].every(Number.isFinite)}));
check('Canvas context and four viewports',()=>['scene','frontView','topView','sideView'].every(id=>$(id)?.getContext('2d')));
check('Inspection canvas and UI connected',()=>!!$('inspectionGrid')&&!!window.N184Inspection&&!!$('measurementValue'));
check('Drafting overlay and picker connected',()=>!!$('draftOverlay')&&!!$('draftVertex')&&!!$('draftSheet'));
check('SVG/PNG/print/scene export controls',()=>['saveSvg','savePng','printPdf','saveJson','loadJson'].every(id=>$(id)&&typeof $(id).onclick==='function'));
check('Slice intersection on X=0',()=>{let l=[{a:[-1,0,0],b:[1,0,0],four:null,name:'test'}];let p=window.N184Inspection.intersections(l,'X',0);return p.length===1&&Math.abs(p[0].point[0])<1e-12});
const pass=tests.filter(x=>x.status==='PASS').length;
const report='N184 BLUEPRINT LAB · VISUAL CHECKS\n'+new Date().toISOString()+'\n'+tests.map(t=>t.label+': '+t.status).join('\n')+'\nTOTAL '+pass+'/'+tests.length+' PASS\nNOTE: Browser-run output; source checks are not a visual pixel inspection.\nKERNEL v6.1 FROZEN';
$('visualResults').textContent=report;return report}
$('runVisualChecks').onclick=execute;
$('copyVisualChecks').onclick=()=>{const text=$('visualResults').textContent;if(navigator.clipboard?.writeText)navigator.clipboard.writeText(text).catch(()=>window.prompt('Copy the report',text));else window.prompt('Copy the report',text)};
window.N184VisualChecks={run:execute};
})();