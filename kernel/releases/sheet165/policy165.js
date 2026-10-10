'use strict';
// SHEET 165: reproducible blocked bootstrap comparisons; fail-safe tuning decisions.
const crypto=require('node:crypto');
const MAX_WINDOW=4;
const BASELINE=Object.freeze({window:1,batch:8,reuseTls:true});
function key(p){validate(p);return `${p.window}/${p.batch}/${p.reuseTls?1:0}`;}
function validate(p){if(!p||![1,4].includes(p.window)||![4,8].includes(p.batch)||typeof p.reuseTls!=='boolean')throw Error('S165_POLICY_BOUNDS');return p;}
function rng(seed){let s=seed|0;if(!s)throw Error('S165_SEED');return()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)/4294967296;};}
function median(xs){if(!xs.length)throw Error('S165_EMPTY_SAMPLE');const a=xs.slice().sort((a,b)=>a-b),mid=Math.floor(a.length/2);return a.length%2?a[mid]:(a[mid-1]+a[mid])/2;}
function quantile(sorted,q){if(!sorted.length||q<0||q>1)throw Error('S165_QUANTILE');let k=(sorted.length-1)*q,lo=Math.floor(k),hi=Math.ceil(k);return sorted[lo]+(sorted[hi]-sorted[lo])*(k-lo);}
function ciLogRatios(xs,{seed=0x165cafe,draws=2400}={}){if(xs.length<2||!xs.every(x=>Number.isFinite(x)&&x>0))throw Error('S165_BAD_RATIOS');const random=rng(seed),log=xs.map(Math.log);let sum=0;const samples=[];for(let i=0;i<draws;i++){sum=0;for(let j=0;j<log.length;j++)sum+=log[Math.floor(random()*log.length)];samples.push(Math.exp(sum/log.length));}samples.sort((a,b)=>a-b);return {geometricMean:+Math.exp(log.reduce((a,b)=>a+b)/log.length).toFixed(4),lower95:+quantile(samples,.025).toFixed(4),upper95:+quantile(samples,.975).toFixed(4),n:xs.length,method:'paired-block bootstrap percentile on log throughput ratios',seed};}
function shuffle(xs,random){const a=xs.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function counterbalanced(configs,blocks=4,seed=0x16500){if(!Array.isArray(configs)||configs.length!==8||!Number.isInteger(blocks)||blocks<2||blocks>20)throw Error('S165_BLOCKS');const random=rng(seed),out=[];for(let b=0;b<blocks;b++){const order=shuffle(configs,random);if(b%2)order.reverse();out.push(order.map(c=>({...c,block:b})));}return out;}
function analyze(rows,{baseline=BASELINE,seed=0x1651c0}={}){
 const baseKey=key(baseline),blocks=[...new Set(rows.map(x=>x.block))].sort((a,b)=>a-b),keys=[...new Set(rows.map(x=>key(x)))];
 if(blocks.length<3||keys.length!==8)throw Error('S165_INSUFFICIENT_DESIGN');
 const by=new Map();for(const r of rows){if(!(r.recordsPerSecond>0))throw Error('S165_INVALID_THROUGHPUT');const k=key(r);if(!by.has(k))by.set(k,new Map());if(by.get(k).has(r.block))throw Error('S165_DUPLICATE_BLOCK');by.get(k).set(r.block,r.recordsPerSecond);}
 if(keys.some(k=>blocks.some(b=>!by.get(k).has(b))))throw Error('S165_MISSING_BLOCK');
 const scores=keys.map(k=>{const ratios=blocks.map(b=>by.get(k).get(b)/by.get(baseKey).get(b));const ci=ciLogRatios(ratios,{seed:seed^crypto.createHash('sha256').update(k).digest().readUInt32BE(0)});const medianRate=median(blocks.map(b=>by.get(k).get(b)));return{key:k,medianRate:+medianRate.toFixed(2),ci,eligible:k!==baseKey&&ci.lower95>=1.05};}).sort((a,b)=>b.ci.lower95-a.ci.lower95||a.key.localeCompare(b.key));
 const candidate=scores.find(x=>x.eligible)||null;const selected=candidate?decode(candidate.key):baseline;
 return{baseline,candidate:candidate?{...selected}:null,selected,decision:candidate?'ELIGIBLE_FOR_HOLDOUT':'FALLBACK_BASELINE_LOW_CONFIDENCE',scores,blocks:blocks.length,seed};
}
function decode(s){const [w,b,t]=s.split('/');return validate({window:+w,batch:+b,reuseTls:t==='1'});}
function holdoutDecision({baseline,optimized,baselineRates,optimizedRates,minGain=1.05,seed=0x165a}={}){
 validate(baseline);validate(optimized);if(baselineRates?.length!==optimizedRates?.length||baselineRates.length<2)throw Error('S165_HOLDOUT_SAMPLES');
 const ratios=optimizedRates.map((rate,i)=>rate/baselineRates[i]);const ci=ciLogRatios(ratios,{seed});const ok=ci.lower95>=minGain;
 return{active:ok?optimized:baseline,fallback:!ok,reason:ok?'HOLDOUT_CONFIDENCE_PASS':'HOLDOUT_CONFIDENCE_FALLBACK',ci,ratios:ratios.map(x=>+x.toFixed(4)),minGain};
}
module.exports={BASELINE,key,validate,rng,median,ciLogRatios,counterbalanced,analyze,decode,holdoutDecision};
