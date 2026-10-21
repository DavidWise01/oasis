// Anny read-only 18-position observation mapping. No writes or release controls.
export const ANNY_GLYPH='{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}';
export const ANNY_BANDS=[
 {name:'Red',color:'#ff6972',slots:[1,2]},
 {name:'Orange',color:'#ffaa63',slots:[3,4,5,6]},
 {name:'Yellow',color:'#f5dc73',slots:[7,8]},
 {name:'Green',color:'#86dbab',slots:[9,10]},
 {name:'Blue',color:'#80b9ff',slots:[11,12,13,14,15],doubleClosure:true},
 {name:'Indigo',color:'#b6a1ff',slots:[16,17]},
 {name:'Violet',color:'#d6a3ff',slots:[18]}
];
const absent=(name)=>({name,status:'absent',value:'—'});
export function observeAnny(transfer,receipt) {
 const slots=Array.from({length:18},(_,i)=>absent('Position '+(i+1)));
 if(!transfer)return {glyph:ANNY_GLYPH,bands:ANNY_BANDS,slots,phase:'NO_TRANSFER'};
 const set=(n,name,status,value)=>slots[n-1]={name,status,value:String(value??'—')};
 set(1,'Transfer identity','observed',transfer.transferId);
 set(2,'Attempt epoch','observed',transfer.epoch);
 const bytes=typeof transfer.sourceHex==='string' && /^[a-f\d]{10}$/i.test(transfer.sourceHex)
   ? transfer.sourceHex.match(/../g):[];
 for(let i=0;i<4;i++)set(i+3,'Source byte '+(i+1),bytes[i]?'observed':'missing',bytes[i]??'—');
 set(7,'Source byte 5',bytes[4]?'observed':'missing',bytes[4]??'—');
 set(8,'SHA-256 source digest',transfer.digest?'observed':'missing',transfer.digest??'—');
 const acks=Array.isArray(transfer.acks)?transfer.acks:[];
 for(const [index,path] of ['A','B'].entries()){
   const count=acks.filter(a=>a?.path===path && a.transferId===transfer.transferId && a.epoch===transfer.epoch && Number.isInteger(a.position) && a.position>=0 && a.position<5).length;
   set(9+index,'Path '+path+' ACK observations',count===5?'observed':'incomplete',count+'/5');
 }
 for(let i=0;i<5;i++){
   const a=acks.some(x=>x?.path==='A'&&x.epoch===transfer.epoch&&x.transferId===transfer.transferId&&x.position===i);
   const b=acks.some(x=>x?.path==='B'&&x.epoch===transfer.epoch&&x.transferId===transfer.transferId&&x.position===i);
   set(11+i,'Byte '+(i+1)+' dual ACKs',a&&b?'observed':'incomplete',(a?'A':'–')+'/'+(b?'B':'–'));
 }
 set(16,'Commit state',transfer.state==='COMMITTED'||transfer.state==='RELEASE_PENDING'||transfer.state==='CONFIRMED'?'observed':'pending',transfer.state);
 set(17,'Receiver receipt',receipt?.accepted && receipt.deliveryKey===transfer.deliveryKey && receipt.digest===transfer.digest?'observed':'pending',receipt?.accepted?'receipt present':'awaiting receipt');
 set(18,'Final confirmation',transfer.state==='CONFIRMED'?'observed':'pending',transfer.state==='CONFIRMED'?'CONFIRMED':'HELD');
 return {glyph:ANNY_GLYPH,bands:ANNY_BANDS,slots,phase:transfer.state};
}
export async function readAnny(journal,receiver,transferId){
 if(typeof transferId!=='string'||!transferId.trim())throw Error('TRANSFER_ID_REQUIRED');
 const transfer=await journal.read(transferId);
 const receipt=transfer?.deliveryKey?await receiver.reconcile(transfer.deliveryKey):null;
 return observeAnny(transfer,receipt);
}
