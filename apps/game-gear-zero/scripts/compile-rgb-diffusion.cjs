#!/usr/bin/env node
/* Compile RGB DIFFUSION ARENA into a real .gg ROM. Node >=18, no packages.
 * This assembles the committed Z80 generator; it is not a full I13 compiler. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const source=path.join(root,'games/rgb-diffusion-game.js');
const target=path.resolve(root,process.argv[2]||'dist/rgb-diffusion-arena.gg');
const context=vm.createContext({window:{},Uint8Array,Uint8ClampedArray,Math});
vm.runInContext(fs.readFileSync(source,'utf8'),context,{filename:source,timeout:2000});
const rom=context.window.GGRGBDiffusion.create();
if(!(rom instanceof Uint8Array)||rom.length!==16384)throw Error('Expected exact 16 KiB Game Gear cartridge');
if(rom[0]!==0xc3||rom[1]!==0||rom[2]!==1)throw Error('Z80 reset vector invalid');
if(rom.rgbGame.board.join()!=='16,12'||rom.rgbGame.channels.blue!==4)throw Error('RGB game metadata inconsistent');
fs.mkdirSync(path.dirname(target),{recursive:true});
fs.writeFileSync(target,rom);
const verify=fs.readFileSync(target);if(!verify.equals(Buffer.from(rom)))throw Error('Writeback mismatch');
console.log(JSON.stringify({status:'COMPILED',rom:path.relative(root,target),bytes:verify.length,sha256:crypto.createHash('sha256').update(verify).digest('hex'),engine:'GG-ZERO original Z80 and Game Gear VDP',source:'games/rgb-diffusion-game.js',gameplay:'RGB four-neighbor 3-bit cellular propagation'},null,2));
