'use strict';
// S187 crash test child: hold a directory-based WAL lock until killed.
const fs=require('node:fs');
const lock=process.argv[2];
if(!lock)throw Error('LOCK_PATH_REQUIRED');
fs.mkdirSync(lock);
process.stdout.write('LOCK_HELD\n');
setInterval(()=>{},10000);
