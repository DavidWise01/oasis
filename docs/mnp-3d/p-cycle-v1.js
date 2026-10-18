/* Tessy cyclic p cipher: past reads, present lives, future writes; separate from d provenance. */
(function(root){'use strict';
const notation='{{ -p{{ast reads}+}present{+{lives{+{future{+{writes} }}}}}}}';
function begin(){return {tick:0,past:[],present:null,future:null,phase:'-p',notation};}
function read(s){if(s.phase!=='-p')throw Error('past read required');return {...s,phase:'-p+',present:{read:s.past.slice(),tick:s.tick}};}
function live(s,event){if(s.phase!=='-p+'||!s.present||typeof event!=='string'||!event.trim())throw Error('present event required');return {...s,phase:'+p',present:{...s.present,lived:event}};}
function write(s,output){if(s.phase!=='+p'||typeof output!=='string'||!output.trim())throw Error('future write required');return {...s,future:{written:output,fromTick:s.tick},phase:'COMMIT'};}
function turn(s){if(s.phase!=='COMMIT'||!s.future)throw Error('future must write before next cycle');const written={tick:s.tick+1,event:s.future.written,originTick:s.tick};return {tick:s.tick+1,past:[...s.past,written],present:null,future:null,phase:'-p',notation};}
const api=Object.freeze({notation,begin,read,live,write,turn});if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.TessyPCycle=api;
})(typeof globalThis!=='undefined'?globalThis:this);
