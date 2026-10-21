import {ReceiverLedger} from './receiver.mjs';import {FileJournalStore} from './file-store.mjs';
const [file,op,key,id,digest,sourceHex]=process.argv.slice(2);
const r=new ReceiverLedger(new FileJournalStore(file));
try{console.log(JSON.stringify(op==='deliver'?await r.deliver({deliveryKey:key,transferId:id,digest,sourceHex}):await r.reconcile(key)))}catch(e){console.error(e.message);process.exitCode=2}
