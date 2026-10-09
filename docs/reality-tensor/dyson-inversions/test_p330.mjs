import assert from 'node:assert/strict';
import {CAPACITY,CYCLE,HALF,slot,inverse,realCalendar} from './p330_leap_counter.mjs';
assert.equal(CAPACITY,1464);assert.equal(HALF*2,CYCLE);
for(let i=0;i<CAPACITY;i++){const s=slot(i);assert.equal(inverse(s.year,s.daySlot),i);assert.equal(s.sign,s.daySlot<=183?-1:1);}
const normal=realCalendar(2024);assert.equal(normal.totalDays,1461);assert.equal(normal.vacantSlots.length,3);
const century=realCalendar(2097);assert.equal(century.totalDays,1460);assert.equal(century.vacantSlots.length,4);
for(const bad of [-1,1464,1.5])assert.throws(()=>slot(bad));
console.log(JSON.stringify({status:'PASS',slotRoundTrips:CAPACITY,normal,century,transition:[slot(182),slot(183)]},null,2));
