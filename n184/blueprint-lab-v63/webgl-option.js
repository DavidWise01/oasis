'use strict';
/* Optional GPU main-viewport wireframe, while legacy Canvas2D is default and fallback. */
window.N184GPU=(()=>{
const $=id=>document.getElementById(id),base=$('scene'),host=base.parentElement;
host.style.position='relative';
const layer=document.createElement('canvas');layer.id='n184GpuLayer';layer.style.cssText='position:absolute;pointer-events:none;display:none;z-index:1';host.append(layer);
const panel=document.createElement('section');panel.className='panel';panel.innerHTML='<h2>18 · Experimental renderer backend</h2><label>Backend <select id="gpuMode"><option value="canvas">Canvas2D (default)</option><option value="webgl">WebGL2 (optional)</option></select></label><pre id="gpuStatus">CANVAS2D DEFAULT · GPU NOT INITIALIZED</pre><p class="muted">GPU draws main wireframe only. Drafting annotations, the three orthographic views and exports remain Canvas2D/SVG. Automatic fallback on unavailable/lost context. User visual parity test required.</p>';
document.querySelector('aside').append(panel);
let gl=null,prog=null,buffer=null,location=-1,mode='canvas',disposed=false;
function shader(type,text){const s=gl.createShader(type);gl.shaderSource(s,text);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const e=gl.getShaderInfoLog(s);gl.deleteShader(s);throw Error(e)}return s}
function init(){if(gl&&prog&&!disposed)return true;
gl=layer.getContext('webgl2',{alpha:false,antialias:false,preserveDrawingBuffer:false});if(!gl)return false;
const v=shader(gl.VERTEX_SHADER,'#version 300 es\nin vec2 pos;void main(){gl_Position=vec4(pos,0.0,1.0);}');
const f=shader(gl.FRAGMENT_SHADER,'#version 300 es\nprecision mediump float;uniform vec3 ink;out vec4 color;void main(){color=vec4(ink,1.0);}');
prog=gl.createProgram();gl.attachShader(prog,v);gl.attachShader(prog,f);gl.bindAttribLocation(prog,0,'pos');gl.linkProgram(prog);gl.deleteShader(v);gl.deleteShader(f);if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(prog));gl.useProgram(prog);location=gl.getUniformLocation(prog,'ink');buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,2,gl.FLOAT,false,0,0);disposed=false;return true}
function fallback(message){mode='canvas';$('gpuMode').value='canvas';layer.style.display='none';$('gpuStatus').textContent=message+' · CANVAS2D RESTORED';window.N184DirtyRender?.invalidate()}
layer.addEventListener('webglcontextlost',e=>{e.preventDefault();disposed=true;gl=null;prog=null;buffer=null;fallback('GPU CONTEXT LOST')});
layer.addEventListener('webglcontextrestored',()=>{disposed=true;fallback('GPU CONTEXT RESTORED; RE-ENABLE MANUALLY')});
$('gpuMode').onchange=()=>{if($('gpuMode').value==='canvas'){fallback('MANUAL SELECTION');return}try{if(!init()){fallback('WEBGL2 UNAVAILABLE');return}mode='webgl';layer.style.display='block';$('gpuStatus').textContent='WEBGL2 EXPERIMENTAL · MAIN VIEW ONLY';window.N184DirtyRender?.invalidate()}catch(e){fallback('WEBGL2 INITIALIZATION ERROR: '+e.message)}};
function draw(lines,yaw,pitch,zoom){if(mode!=='webgl')return false;try{const r=base.getBoundingClientRect(),p=host.getBoundingClientRect();layer.style.left=(r.left-p.left)+'px';layer.style.top=(r.top-p.top)+'px';layer.style.width=r.width+'px';layer.style.height=r.height+'px';const w=base.width,h=base.height;if(layer.width!==w||layer.height!==h){layer.width=w;layer.height=h}gl.viewport(0,0,w,h);gl.clearColor(.027,.09,.157,1);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(prog);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
const groups=new Map();for(const l of lines){let a=window.N184Geometry.toScreen(l.a,w,h,yaw,pitch,zoom),b=window.N184Geometry.toScreen(l.b,w,h,yaw,pitch,zoom);let arr=groups.get(l.color);if(!arr){arr=[];groups.set(l.color,arr)}arr.push(2*a[0]/w-1,1-2*a[1]/h,2*b[0]/w-1,1-2*b[1]/h)}
for(const [color,values] of groups){const rgba=color.replace('#',''),rgb=[0,2,4].map(i=>parseInt(rgba.slice(i,i+2),16)/255);gl.uniform3fv(location,rgb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values),gl.STREAM_DRAW);gl.drawArrays(gl.LINES,0,values.length/2)}return true}catch(e){fallback('GPU DRAW ERROR: '+e.message);return false}}
return{draw,getMode:()=>mode,layer};
})();