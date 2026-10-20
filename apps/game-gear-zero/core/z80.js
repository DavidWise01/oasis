/* GG-ZERO v0.1 ORIGINAL Z80 interpreter.
   Coverage: unprefixed and CB instructions, selected ED operations.
   DD/FD and block I/O incomplete: NOT commercial-ROM compatible yet. */
(function(root){'use strict';
const F={S:128,Z:64,Y:32,H:16,X:8,P:4,N:2,C:1};
const parity=v=>{v^=v>>4;v^=v>>2;v^=v>>1;return!(v&1)},signed=v=>v&128?v-256:v;
class Z80 {
 constructor(bus){this.bus=bus;this.reset()}
 reset(){this.r=new Uint8Array(8);this.a=0xff;this.f=0;this.pc=0;this.sp=0xdff0;this.ix=0;this.iy=0;this.i=0;this.ir=0;this.iff=false;this.ei=0;this.halted=false;this.irq=false;this.cycles=0;this.alt={a:0,f:0,b:0,c:0,d:0,e:0,h:0,l:0}}
 get A(){return this.r[7]}set A(v){this.r[7]=v&255}
 get H(){return this.r[4]}set H(v){this.r[4]=v&255}
 get L(){return this.r[5]}set L(v){this.r[5]=v&255}
 get HL(){return(this.H<<8)|this.L}set HL(v){this.H=v>>>8;this.L=v}
 read(a){return this.bus.read(a&65535)&255}write(a,v){this.bus.write(a&65535,v&255)}
 next(){let x=this.read(this.pc);this.pc=(this.pc+1)&65535;return x}
 next16(){const a=this.next();return a|this.next()<<8}
 pair(i){return i===3?this.sp:i===2?this.HL:(this.r[i*2]<<8)|this.r[i*2+1]}
 setPair(i,v){v&=65535;if(i===3)this.sp=v;else if(i===2)this.HL=v;else{this.r[2*i]=v>>8;this.r[2*i+1]=v}}
 pair2(i){return i===3?(this.A<<8)|this.f:this.pair(i)}
 setPair2(i,v){if(i===3){this.A=v>>8;this.f=v&255}else this.setPair(i,v)}
 getR(i){return i===6?this.read(this.HL):this.r[i]}
 setR(i,v){if(i===6)this.write(this.HL,v);else this.r[i]=v&255}
 push(v){this.sp=this.sp-1&65535;this.write(this.sp,v>>8);this.sp=this.sp-1&65535;this.write(this.sp,v)}
 pop(){const lo=this.read(this.sp);this.sp=this.sp+1&65535;const hi=this.read(this.sp);this.sp=this.sp+1&65535;return lo|hi<<8}
 sz(v){return(v&168)|(v===0?64:0)}
 szp(v){return this.sz(v)|(parity(v)?4:0)}
 inc(v){const r=(v+1)&255;this.f=(this.f&1)|this.sz(r)|((v&15)===15?16:0)|(v===127?4:0);return r}
 dec(v){const r=(v-1)&255;this.f=(this.f&1)|this.sz(r)|2|((v&15)===0?16:0)|(v===128?4:0);return r}
 add(v,carry=0){const a=this.A,t=a+v+carry,r=t&255;this.f=this.sz(r)|((a^v^r)&16?16:0)|((~(a^v)&(a^r)&128)?4:0)|(t>255?1:0);this.A=r}
 sub(v,carry=0,compare=false){const a=this.A,t=a-v-carry,r=t&255;this.f=this.sz(r)|2|((a^v^r)&16?16:0)|(((a^v)&(a^r)&128)?4:0)|(t<0?1:0);if(!compare)this.A=r}
 alu(y,v){if(y<2)this.add(v,y===1&&this.f&1?1:0);else if(y<4)this.sub(v,y===3&&this.f&1?1:0);else if(y===7)this.sub(v,0,true);else{this.A=y===4?(this.A&v):y===5?(this.A^v):(this.A|v);this.f=this.szp(this.A)|(y===4?16:0)}}
 cond(i){const fl=[64,64,1,1,4,4,128,128][i];return(i&1)?!!(this.f&fl):!(this.f&fl)}
 rotate(y,v){const oldc=this.f&1?1:0;let out=0,carry=0;switch(y){case 0:carry=v>>7;out=v<<1|carry;break;case 1:carry=v&1;out=v>>1|carry<<7;break;case 2:carry=v>>7;out=v<<1|oldc;break;case 3:carry=v&1;out=v>>1|oldc<<7;break;case 4:carry=v>>7;out=v<<1;break;case 5:carry=v&1;out=v>>1|v&128;break;case 6:carry=v>>7;out=v<<1|1;break;case 7:carry=v&1;out=v>>1;break}out&=255;this.f=this.szp(out)|(carry?1:0);return out}
 cb(op){const x=op>>6,y=op>>3&7,z=op&7,v=this.getR(z);if(x===1){this.f=(this.f&1)|16|(v&(1<<y)?0:68)|(y===7&&v&128?128:0)|(v&40);return z===6?12:8}this.setR(z,x===0?this.rotate(y,v):x===2?v&~(1<<y):v|(1<<y));return z===6?15:8}
 ed(op){const y=op>>3&7,z=op&7,p=y>>1,q=y&1;
 if(op===0x44||op===0x4c||op===0x54||op===0x5c||op===0x64||op===0x6c||op===0x74||op===0x7c){const v=this.A;this.A=0;this.sub(v);return 8}
 if(op===0x45||op===0x4d){this.pc=this.pop();this.iff=true;return 14}
 if(op===0x47){this.i=this.A;return 9}if(op===0x57){this.A=this.i;this.f=(this.f&1)|this.sz(this.A)|(this.iff?4:0);return 9}
 if((op&0xc7)===0x40){const v=this.bus.input(this.pair(0))&255;if(y!==6)this.setR(y,v);this.f=(this.f&1)|this.szp(v);return 12}
 if((op&0xc7)===0x41){this.bus.output(this.pair(0),y===6?0:this.getR(y));return 12}
 if((op&0xcf)===0x43){const a=this.next16(),v=this.pair(p);this.write(a,v);this.write(a+1,v>>8);return 20}
 if((op&0xcf)===0x4b){const a=this.next16();this.setPair(p,this.read(a)|this.read(a+1)<<8);return 20}
 if((op&0xc7)===0x42){const v=this.pair(p),a=this.HL,c=this.f&1,t=q?a+v+c:a-v-c,r=t&65535;this.HL=r;this.f=(r&32768?128:0)|(r===0?64:0)|(r>>8&40)|((a^v^r)&4096?16:0)|(t<0||t>65535?1:0)|(q?0:2);return 15}
 if(op===0xa0||op===0xb0){const v=this.read(this.HL);this.write(this.pair(1),v);this.HL=this.HL+1&65535;this.setPair(1,this.pair(1)+1);this.setPair(0,this.pair(0)-1);this.f=(this.f&193)|(this.pair(0)?4:0);if(op===0xb0&&this.pair(0)){this.pc=this.pc-2&65535;return 21}return 16}
 return 8;
 }
 step(){if(this.irq&&this.iff){this.irq=false;this.iff=false;this.halted=false;this.push(this.pc);this.pc=0x38;this.cycles+=13;return 13}
 if(this.halted){this.cycles+=4;return 4}
 const op=this.next(),x=op>>6,y=op>>3&7,z=op&7,p=y>>1,q=y&1;this.ir=this.ir+1&127;let t=4;
 if(op===0xcb)t=this.cb(this.next());
 else if(op===0xed)t=this.ed(this.next());
 else if(op===0xdd||op===0xfd){this.next();t=8;/* index instructions pending */}
 else if(x===0){
  if(z===0){if(y===0){}else if(y===1){[this.A,this.alt.a]=[this.alt.a,this.A];[this.f,this.alt.f]=[this.alt.f,this.f]}
   else if(y===2){this.r[0]=this.r[0]-1&255;const d=signed(this.next());if(this.r[0]){this.pc=this.pc+d&65535;t=13}else t=8}
   else if(y===3){const d=signed(this.next());this.pc=this.pc+d&65535;t=12}
   else{const d=signed(this.next());if(this.cond(y-4)){this.pc=this.pc+d&65535;t=12}else t=7}}
  else if(z===1){if(!q){this.setPair(p,this.next16());t=10}else{const a=this.HL,b=this.pair(p),r=(a+b)&65535;this.f=(this.f&196)|(r>>8&40)|((a^b^r)&4096?16:0)|(a+b>65535?1:0);this.HL=r;t=11}}
  else if(z===2){if(!q){if(p===0)this.write(this.pair(0),this.A);else if(p===1)this.write(this.pair(1),this.A);else{const a=this.next16();if(p===2){this.write(a,this.L);this.write(a+1,this.H);t=16}else{this.write(a,this.A);t=13}}if(p<2)t=7}
   else{if(p<2){this.A=this.read(this.pair(p));t=7}else{const a=this.next16();if(p===2){this.HL=this.read(a)|this.read(a+1)<<8;t=16}else{this.A=this.read(a);t=13}}}}
  else if(z===3){this.setPair(p,this.pair(p)+(q?-1:1));t=6}
  else if(z===4||z===5){const v=this.getR(y);this.setR(y,z===4?this.inc(v):this.dec(v));t=y===6?11:4}
  else if(z===6){this.setR(y,this.next());t=y===6?10:7}
  else{const a=this.A,c=this.f&1?1:0;let carry=0,res=a;
   if(y===0){carry=a>>7;res=a<<1|carry}
   if(y===1){carry=a&1;res=a>>1|carry<<7}
   if(y===2){carry=a>>7;res=a<<1|c}
   if(y===3){carry=a&1;res=a>>1|c<<7}
   if(y<4){this.A=res;this.f=(this.f&196)|(this.A&40)|(carry?1:0)}
   else if(y===5){this.A^=255;this.f=(this.f&197)|18|(this.A&40)}
   else if(y===6)this.f=(this.f&196)|(a&40)|1;
   else if(y===7)this.f=(this.f&196)|(a&40)|(this.f&1?16:1);
  }
 }else if(x===1){if(op===0x76)this.halted=true;else{this.setR(y,this.getR(z));t=(y===6||z===6)?7:4}}
 else if(x===2){this.alu(y,this.getR(z));t=z===6?7:4}
 else {
  if(z===0){if(this.cond(y)){this.pc=this.pop();t=11}else t=5}
  else if(z===1){if(!q){this.setPair2(p,this.pop());t=10}else if(p===0){this.pc=this.pop();t=10}else if(p===1){for(const [i,k]of [[0,'b'],[1,'c'],[2,'d'],[3,'e'],[4,'h'],[5,'l']]){const v=this.r[i];this.r[i]=this.alt[k];this.alt[k]=v}}else if(p===2)this.pc=this.HL;else{this.sp=this.HL;t=6}}
  else if(z===2){const a=this.next16();if(this.cond(y))this.pc=a;t=10}
  else if(z===3){if(y===0){this.pc=this.next16();t=10}else if(y===2){const port=this.next();this.bus.output((this.A<<8)|port,this.A);t=11}else if(y===3){const port=this.next();this.A=this.bus.input((this.A<<8)|port);t=11}else if(y===4){const v=this.HL;this.HL=this.read(this.sp)|this.read(this.sp+1)<<8;this.write(this.sp,v);this.write(this.sp+1,v>>8);t=19}else if(y===5){const v=this.pair(1);this.setPair(1,this.HL);this.HL=v}else if(y===6)this.iff=false;else if(y===7){this.iff=true;this.ei=2}}
  else if(z===4){const a=this.next16();if(this.cond(y)){this.push(this.pc);this.pc=a;t=17}else t=10}
  else if(z===5){if(!q){this.push(this.pair2(p));t=11}else if(p===0){const a=this.next16();this.push(this.pc);this.pc=a;t=17}}
  else if(z===6){this.alu(y,this.next());t=7}
  else if(z===7){this.push(this.pc);this.pc=y<<3;t=11}
 }
 if(this.ei)this.ei--;
 this.cycles+=t;return t;
 }
 interrupt(){this.irq=true}
}
root.GGZ80=Z80;
})(typeof window!=='undefined'?window:globalThis);