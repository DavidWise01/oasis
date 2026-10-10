'use strict';
// Pure, deterministic hysteresis; measurement inputs are performance observations, not security evidence.
const S165=require('./baseline165/policy165');
const RULES=Object.freeze({badBelow:.88,goodAbove:1.18,minDwellRows:48,cooldownRows:96,badWindows:3,goodWindows:4,driftBelow:.91,driftWindows:3});
const VALID_MODES=['candidate','baseline'];
function positive(n){return Number.isFinite(n)&&n>0;}
function initial(mode='candidate',atRows=0){if(!VALID_MODES.includes(mode)||!Number.isSafeInteger(atRows)||atRows<0)throw Error('S166_INITIAL');return{mode,rows:atRows,lastSwitchRows:atRows,cooldownUntilRows:0,bad:0,good:0,drift:0,fast:null,slow:null,driftDetected:false,windows:0};}
function validate(s){if(!s||!VALID_MODES.includes(s.mode)||!Number.isSafeInteger(s.rows)||s.rows<0||s.lastSwitchRows>s.rows)throw Error('S166_STATE');return s;}
function observe(state,{rows,rate,baselineRate,holdoutPassed=false}={},rules=RULES){
 validate(state);if(!Number.isSafeInteger(rows)||rows<=state.rows||!positive(rate)||!positive(baselineRate))throw Error('S166_SAMPLE');
 const ratio=rate/baselineRate;let s={...state,rows,windows:state.windows+1};
 s.fast=state.fast===null?ratio:0.45*ratio+0.55*state.fast;
 s.slow=state.slow===null?ratio:0.12*ratio+0.88*state.slow;
 s.drift= s.fast<s.slow*rules.driftBelow?state.drift+1:0;
 s.driftDetected=s.drift>=rules.driftWindows;
 s.bad=ratio<rules.badBelow?state.bad+1:0;
 s.good=ratio>rules.goodAbove?state.good+1:0;
 const dwell=rows-state.lastSwitchRows>=rules.minDwellRows;
 let transition=null;
 if(s.mode==='candidate'&&dwell&&s.bad>=rules.badWindows){
   transition={from:'candidate',to:'baseline',reason:'PERFORMANCE_DEGRADED',atRows:rows,observedRatio:+ratio.toFixed(5),windows:s.bad};
 }else if(s.mode==='baseline'&&dwell&&rows>=state.cooldownUntilRows&&s.good>=rules.goodWindows&&holdoutPassed===true){
   transition={from:'baseline',to:'candidate',reason:'VERIFIED_HOLDOUT_REPROMOTION',atRows:rows,observedRatio:+ratio.toFixed(5),windows:s.good};
 }
 return{state:s,transition,ratio};
}
function afterSigned(state,transition,rules=RULES){
 validate(state);if(!transition||state.mode!==transition.from||state.rows!==transition.atRows||!VALID_MODES.includes(transition.to)||transition.to===state.mode)throw Error('S166_TRANSITION_FORK');
 const s={...state,mode:transition.to,lastSwitchRows:state.rows,bad:0,good:0,drift:0,driftDetected:false,fast:null,slow:null};
 if(transition.to==='baseline')s.cooldownUntilRows=state.rows+rules.cooldownRows;
 return s;
}
function chooseVerifiedPolicy(state,optimized,baseline=S165.BASELINE){validate(state);S165.validate(optimized);S165.validate(baseline);return state.mode==='candidate'?optimized:baseline;}
module.exports={RULES,initial,observe,afterSigned,validate,chooseVerifiedPolicy};
