/* TESSY intent-foundation v1.0 — symbolic grammar, not physical quantum model.
   Frozen rules: bottom sets intent; candidate locks/discards; ✓ closes box; X delimits completed words.
   Preserve case and original ordered letters. */
(function(root){
"use strict";
const alpha=/^[A-Za-z]$/;
function start(letter,intent){if(!alpha.test(letter))throw Error("foundation must be A-Z/a-z");return {base:letter,locked:letter,candidate:null,intent:intent??letter,closed:false,history:[]};}
function propose(s,c){if(s.closed||s.candidate!==null||!alpha.test(c))throw Error("invalid candidate or closed foundation");return {...s,candidate:c};}
function decide(s,action){if(s.closed||s.candidate===null||!["LOCK","DISCARD"].includes(action))throw Error("invalid resolution");const next=action==="LOCK"?s.locked+s.candidate:s.locked;return {...s,locked:next,candidate:null,history:[...s.history,{letter:s.candidate,action}]};}
function complete(s){if(s.closed||s.candidate!==null)throw Error("resolve candidate before completion");return {...s,closed:true,check:"✓"};}
function delimit(s){if(!s.closed)throw Error("X needs a checked foundation");return {word:s.locked,delimiter:"X",check:"✓",intent:s.intent,box:"||||"};}
const API=Object.freeze({start,propose,decide,complete,delimit});
if(typeof module!=="undefined"&&module.exports)module.exports=API;
else root.TessyIntent=API;
})(typeof globalThis!=="undefined"?globalThis:this);
