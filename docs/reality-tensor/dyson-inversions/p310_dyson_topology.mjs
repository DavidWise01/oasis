/** P3.10 exact structural grammar; no physical interpretation implied. */
export const CANONICAL='{-{d}+{+{d}-}}';
export function tokenize(source=CANONICAL){
 if(typeof source!=='string')throw new TypeError('source');
 const raw=[...source]; if(raw.some(c=>!('{}+-d'.includes(c))))throw new SyntaxError('unknown token');
 return raw;
}
export function parse(source=CANONICAL){
 const tokens=tokenize(source); let i=0,domain=0;
 function read(){if(tokens[i++]!=='{')throw new SyntaxError('expected {');const children=[];
 while(i<tokens.length&&tokens[i]!=='}'){
 const t=tokens[i];if(t==='{')children.push(read());else{children.push(t==='d'?{type:'domain',id:++domain}:{type:'sign',value:t});i++;}}
 if(tokens[i++]!=='}')throw new SyntaxError('missing }');return {type:'group',children};}
 const root=read();if(i!==tokens.length)throw new SyntaxError('trailing tokens');
 if(serialize(root)!==CANONICAL)throw new SyntaxError('not canonical nested form');
 return root;
}
export function serialize(n){if(n.type==='group')return '{'+n.children.map(serialize).join('')+'}';if(n.type==='sign')return n.value;if(n.type==='domain')return 'd';throw new TypeError('node');}
export function events(root=parse()){const out=[];function walk(n,path=[]){if(n.type==='group'){out.push({kind:'enter',path:path.join('.')});n.children.forEach((c,i)=>walk(c,[...path,i]));out.push({kind:'exit',path:path.join('.')});}else out.push({kind:n.type,value:n.type==='domain'?n.id:n.value,path:path.join('.')});}walk(root);return out;}
export function inverseEvents(ev){return ev.slice().reverse().map(e=>({...e,kind:e.kind==='enter'?'exit':e.kind==='exit'?'enter':e.kind==='sign'?'inverse-sign':e.kind==='domain'?'inverse-domain':e.kind}));}
export function verify(eventsF,eventsB){return JSON.stringify(inverseEvents(eventsF))===JSON.stringify(eventsB);}
