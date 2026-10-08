"use strict";
(() => {
  const EPOCH = Date.UTC(2026, 9, 7);
  const oneDay=86400000;
  const dayNumber=()=>Math.max(1,Math.floor((Date.now()-EPOCH)/oneDay)+1);
  const render=()=>{
    const target=document.getElementById("ud0Day");
    if(target)target.textContent=String(dayNumber());
    const label=document.getElementById("ud0Clock");
    if(label)label.textContent="OaSIs integration day "+dayNumber()+" · epoch 2026-10-07 UTC · not UD0's historical creation date";
  };
  const link=(id,url)=>{
    const b=document.getElementById(id);
    if(b)b.addEventListener("click",()=>window.open(url,"_blank","noopener,noreferrer"));
  };
  link("ud0Open","https://davidwise01.github.io/ud0/");
  link("du1Open","https://davidwise01.github.io/du1/");
  render();
  setInterval(render,60000);
})();
