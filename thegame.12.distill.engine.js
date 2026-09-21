/* DISTILL — TheGame six-box campaign. Append-only successor to puzzle 11. */
(function(root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Distill = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const VERSION = 'thegame-distill-12.1';
  const TARGET = [7, 9];
  function freeze(x) {
    if (x && typeof x === 'object' && !Object.isFrozen(x)) { Object.values(x).forEach(freeze); Object.freeze(x); }
    return x;
  }
  const LEVELS = freeze([
    {name:'First spark', tag:'LEARN THE PULSE', seed:['gh','aa','mm','bb','nn','cc'], budget:3, par:6,
      brief:'Keep g. Move h up once to i. Clear the five equal pairs.', lesson:'Tap a letter, then ±1. Tap two equal neighbors to ablate them.'},
    {name:'The drop', tag:'ORDER MATTERS', seed:['aa','bb','cg','ci','dd','ee'], budget:2, par:5,
      brief:'Save the middle vertical pair for last. The columns will fall into place.', lesson:'Horizontal matches leave holes. Vertical matches compress both columns upward.'},
    {name:'Crossed wires', tag:'CARDINAL ONLY', seed:['ab','ba','gi','mm','nn','oo'], budget:4, par:7,
      brief:'The matching diagonals are a decoy. Turn the top four letters into cardinal pairs.', lesson:'Across or down within an X group. A diagonal never cancels.'},
    {name:'Undertow', tag:'READ THE COLLAPSE', seed:['ag','ai','bm','bn','cc','dd'], budget:3, par:6,
      brief:'Clear the lower horizontal pairs. Use the vertical pairs to carry g and i upward.', lesson:'Compression keeps each column’s letter order. Plan what becomes adjacent next.'},
    {name:'Low power', tag:'SPEND WITH INTENT', seed:['gh','ab','cc','dd','ef','gg'], budget:5, par:8,
      brief:'Three useful pulses are enough. Keep one g for the final compound.', lesson:'A pulse costs one charge. Undo returns the charge and records the correction.'},
    {name:'David’s stack', tag:'THE ORIGINAL SIX', seed:['gh','ab','mn','ab','mn','ab'], budget:6, par:11,
      brief:'The original stack. Six pulses. Five ablations. Leave only gi.', lesson:'Every pulse counts here. Your register saves the entire route.'}
  ]);
  const EDGES = freeze([0,4,8].flatMap(base => [
    {a:base,b:base+1,direction:'N',vertical:false,group:base/4},
    {a:base+2,b:base+3,direction:'S',vertical:false,group:base/4},
    {a:base,b:base+2,direction:'W',vertical:true,group:base/4},
    {a:base+1,b:base+3,direction:'E',vertical:true,group:base/4}
  ]));
  const letter = n => n ? String.fromCharCode(96+n) : '_';
  const count = cells => cells.filter(Boolean).length;
  function order(cells) { return [0,2,4,6,8,10,1,3,5,7,9,11].filter(i => cells[i]); }
  function word(cells) { return order(cells).map(i => letter(cells[i])).join(''); }
  function won(cells) { return count(cells) === 2 && word(cells) === 'gi'; }
  function pairs(cells, equalOnly = true) {
    return EDGES.filter(e => cells[e.a] && cells[e.b] && (!equalOnly || cells[e.a] === cells[e.b]));
  }
  function clearPair(cells, edge) {
    const next = cells.slice(); next[edge.a] = 0; next[edge.b] = 0;
    if (edge.vertical) for (let col=0; col<2; col++) {
      const live = [0,1,2,3,4,5].map(row => next[row*2+col]).filter(Boolean);
      for (let row=0; row<6; row++) next[row*2+col] = live[row] || 0;
    }
    return next;
  }
  function setup(level) {
    if (!Number.isInteger(level) || level<0 || level>=LEVELS.length) throw new Error('Choose a campaign level from 1 to 6.');
    return {level, cells:LEVELS[level].seed.join('').split('').map(ch => ch.charCodeAt(0)-96),
      spent:0, moves:0, hints:0, chain:0, history:[]};
  }
  function initial() { return freeze({...setup(0), best:{}, register:[]}); }
  function remaining(s) { return LEVELS[s.level].budget - s.spent; }
  function phase(s) {
    if (won(s.cells)) return 'solved';
    if (count(s.cells)<2 || (remaining(s)===0 && pairs(s.cells).length===0)) return 'stuck';
    return 'playing';
  }
  function stars(s) {
    if (!won(s.cells)) return 0;
    if (s.moves<=LEVELS[s.level].par && s.hints===0) return 3;
    return s.moves<=LEVELS[s.level].par+2 && s.hints<=1 ? 2 : 1;
  }
  function snapshot(s) {
    return JSON.stringify({level:s.level,cells:s.cells,spent:s.spent,moves:s.moves,hints:s.hints,chain:s.chain,best:s.best,history:s.history});
  }
  function apply(s, input) {
    if (!input || typeof input.type!=='string') throw new Error('Choose a move.');
    const action = JSON.parse(JSON.stringify(input));
    const n = {...s, cells:s.cells.slice(), history:s.history.slice(), best:{...s.best}, register:s.register.slice()};
    let detail;
    if (action.type==='level' || action.type==='restart') {
      const level = action.type==='level' ? action.level : s.level;
      Object.assign(n, setup(level));
      detail = (action.type==='restart' ? 'Restart · ' : 'Enter · ') + LEVELS[level].name;
    } else if (action.type==='undo') {
      const prior = n.history.pop();
      if (!prior) throw new Error('No move to undo on this board.');
      Object.assign(n, {cells:prior.cells.slice(),spent:prior.spent,moves:prior.moves,chain:prior.chain});
      detail = 'Undo · board and pulse restored';
    } else if (action.type==='hint') {
      if (phase(s)!=='playing') throw new Error('Undo or retry this board first.');
      n.hints++; detail='Hint used · '+n.hints+' this attempt';
    } else {
      if (phase(s)!=='playing') throw new Error('This board has stopped. Undo, retry or choose another level.');
      n.history.push({cells:s.cells.slice(),spent:s.spent,moves:s.moves,chain:s.chain});
      if (action.type==='shift') {
        if (!Number.isInteger(action.index) || action.index<0 || action.index>11 || !s.cells[action.index]) throw new Error('Select a live letter.');
        if (action.delta!==1 && action.delta!==-1) throw new Error('A pulse moves exactly +1 or −1.');
        if (!remaining(s)) throw new Error('No pulses left. Match a pair or undo.');
        const value = s.cells[action.index] + action.delta;
        if (value<1 || value>26) throw new Error('Stay inside a=1 through z=26.');
        n.cells[action.index] = value; n.spent++; n.chain=0;
        detail=letter(s.cells[action.index])+' '+(action.delta>0?'+1':'−1')+' → '+letter(value);
      } else if (action.type==='ablate') {
        const edge=pairs(s.cells).find(e => (e.a===action.a&&e.b===action.b)||(e.a===action.b&&e.b===action.a));
        if (!edge) throw new Error('Match equal numbers across or down within one X.');
        n.cells=clearPair(s.cells,edge); n.chain++;
        detail='X'+(edge.group+1)+' '+edge.direction+' · '+letter(s.cells[edge.a])+' + '+letter(s.cells[edge.b])+' → _'+(edge.vertical?' · compress ↑':' · holes remain');
      } else throw new Error('Unknown move.');
      n.moves++;
      if (won(n.cells)) {
        const award={stars:stars(n),moves:n.moves,pulses:n.spent};
        const prior=n.best[n.level];
        if (!prior || award.stars>prior.stars || (award.stars===prior.stars&&award.moves<prior.moves)) n.best[n.level]=award;
        detail+=' · gi reached';
      }
    }
    n.register.push({seq:n.register.length+1,action,after:snapshot(n),detail});
    return freeze(n);
  }
  // A pair needs |a-b| unit pulses before removal. Those pulses can be postponed
  // until the pair is adjacent: they cannot affect the placement of other letters.
  // Search pair-removal orders, then the final two survivor values. This avoids
  // exploring redundant interleavings of individual pulses and remains exact.
  function solve(s, maxNodes=30000) {
    let nodes=0;
    const memo=new Map();
    const limit={};
    const pulses=(index,from,to) => Array.from({length:Math.abs(to-from)},()=>({type:'shift',index,delta:Math.sign(to-from)}));
    function search(cells, budget) {
      const key=cells.join(',')+'|'+budget;
      if (memo.has(key)) return memo.get(key);
      if (++nodes>maxNodes) throw limit;
      const live=order(cells);
      if (live.length<2) return null;
      if (live.length===2) {
        const cost=Math.abs(cells[live[0]]-7)+Math.abs(cells[live[1]]-9);
        return cost<=budget ? [...pulses(live[0],cells[live[0]],7),...pulses(live[1],cells[live[1]],9)] : null;
      }
      let best=null;
      for (const edge of pairs(cells,false)) {
        const cost=Math.abs(cells[edge.a]-cells[edge.b]);
        if (cost>budget) continue;
        const next=clearPair(cells,edge);
        const tail=search(next,budget-cost);
        if (tail!==null) {
          const plan=[...pulses(edge.a,cells[edge.a],cells[edge.b]),{type:'ablate',a:edge.a,b:edge.b},...tail];
          if (best===null || plan.length<best.length) best=plan;
          if (best.length===(live.length-2)/2) break;
        }
      }
      memo.set(key,best); return best;
    }
    try {
      const actions=search(s.cells,remaining(s));
      return {status:actions===null?'no-solution':'solved',actions:actions||[],nodes};
    } catch(e) { if (e===limit) return {status:'limit',actions:[],nodes}; throw e; }
  }
  function hintText(action,s) {
    if (action.type==='shift') return 'Box '+(Math.floor(action.index/2)+1)+', '+(action.index%2?'right':'left')+': '+letter(s.cells[action.index])+' '+(action.delta>0?'+1':'−1')+' → '+letter(s.cells[action.index]+action.delta)+'.';
    const edge=EDGES.find(e=>e.a===action.a&&e.b===action.b);
    return 'X'+(edge.group+1)+': ablate the '+edge.direction+' pair'+(edge.vertical?', then the columns compress.':'.');
  }
  function save(s) { return JSON.stringify({version:VERSION,register:s.register}); }
  function restore(text) {
    const data=JSON.parse(text);
    if (data.version!==VERSION || !Array.isArray(data.register) || data.register.length>15000) throw new Error('Unrecognized or oversized campaign register.');
    let s=initial();
    for (const e of data.register) {
      const next=apply(s,e.action), expected=next.register.at(-1);
      if (e.seq!==expected.seq || e.after!==expected.after || e.detail!==expected.detail) throw new Error('Register mismatch at move '+expected.seq+'.');
      s=next;
    }
    return s;
  }
  return freeze({VERSION,LEVELS,EDGES,initial,apply,phase,remaining,stars,letter,count,word,pairs,solve,hintText,save,restore,snapshot});
});
