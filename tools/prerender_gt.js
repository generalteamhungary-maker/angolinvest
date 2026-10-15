// Keresőknek: a JS által kirajzolt lakás- és referencialistát statikus HTML-ként is beleírja az oldalba.
const {chromium}=require('playwright');const fs=require('fs');
const file=process.argv[2];
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+file);await p.waitForTimeout(800);
const parts=await p.evaluate(()=>{const o={};['projects','refCats','galTarsashaz','galCsaladi'].forEach(id=>o[id]=document.getElementById(id).innerHTML.trim());return o});
let s=fs.readFileSync(file,'utf8');
for(const [id,h] of Object.entries(parts)){const k='<!--PRE:'+id+'-->';if(!s.includes(k))throw new Error('nincs: '+k);s=s.replace(k,h)}
fs.writeFileSync(file,s);console.log('előrenderelve',Object.values(parts).map(x=>x.length));await b.close()})();
