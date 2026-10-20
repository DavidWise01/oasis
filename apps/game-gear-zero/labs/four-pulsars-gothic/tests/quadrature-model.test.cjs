#!/usr/bin/env node
/* Exact phaseModel regression from the self-contained HTML, Node >=18, no packages. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
const start=html.indexOf(' function phaseModel(t){');
const end=html.indexOf('\n let seed=',start);
assert.ok(start>0&&end>start,'Quarter-phase model source exists');
const phaseSource=html.slice(start,end);
const state={enabled:[true,true,true,true],phaseSlip:0};
const model=new Function('state','t','const duration=6400,QUARTERS=[0,.25,.5,.75],TAU=Math.PI*2;'+phaseSource+';return phaseModel(t);');
let checks=0;
for(let t=0;t<6400*4;t+=37){
 const q=model(state,t);
 assert.ok(q.locked&&q.residual<1e-9,'balance at '+t);
 assert.ok(Math.abs(q.total-2)<1e-9,'intensity at '+t);
 for(let i=0;i<4;i++)assert.ok(q.envelopes[i]>=-1e-12&&q.envelopes[i]<=1+1e-12);
 checks+=6;
}
for(const [degrees,expected] of [[45,2*Math.sin(Math.PI/8)],[90,Math.SQRT2]]){
 state.phaseSlip=degrees/360;
 const q=model(state,1600);
 assert.ok(!q.locked&&Math.abs(q.residual-expected)<1e-9);
 checks++;
}
state.phaseSlip=0;state.enabled[2]=false;
assert.ok(!model(state,700).locked&&Math.abs(model(state,700).residual-1)<1e-9);checks++;
state.enabled[2]=true;
assert.ok(model(state,700).locked);checks++;
console.log('PASS',checks,'quarter-phase assertions');
