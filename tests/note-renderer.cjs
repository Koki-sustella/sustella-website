const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../site/assets/note.js'),'utf8');
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.events={};this.textContent='';}
 append(...children){this.children.push(...children);}
 setAttribute(name,value){this[name]=value;}
 addEventListener(name,callback){this.events[name]=callback;}
 replaceChildren(fragment){this.children=fragment.children;}
 querySelectorAll(){return [];}
 remove(){this.removed=true;}
}
async function run(data,{protocol='https:',fail=false}={}){
 const grid=new Element('grid');grid.children=['initial cards'];let requests=0;
 const document={getElementById:()=>grid,createElement:tag=>new Element(tag),createDocumentFragment:()=>new Element('fragment')};
 const fetch=async url=>{requests++;assert.equal(url,'data/note.json');if(fail)throw Error('offline');return {ok:true,json:async()=>data};};
 vm.runInNewContext(source,{document,location:{protocol},fetch,URL,Date,Intl,AbortController,setTimeout,clearTimeout});
 await new Promise(resolve=>setImmediate(resolve));
 return {grid,requests};
}
(async()=>{
 const item={title:'宿の価格',url:'https://note.com/sustella_jp/n/n123',publishedAt:'2026-10-19T22:00:00Z',thumbnail:'https://assets.st-note.com/cover.png'};
 let {grid}=await run({items:[item]});
 assert.equal(grid.dataset.count,'1');
 let link=grid.children[0].children[0],body=link.children[1];
 assert.equal(link.target,'_blank');assert.equal(link.rel,'noopener noreferrer');
 assert.equal(body.children[0].textContent,'2026.10.20');assert.equal(body.children[1].textContent,item.title);
 const img=link.children[0].children[1];img.events.error();assert.equal(img.removed,true);
 ({grid}=await run({items:[null,{...item,url:'javascript:alert(1)'},{...item,title:'<img onerror=alert(1)>',thumbnail:'https://evil.example/a.png'}]}));
 link=grid.children[0].children[0];assert.equal(link.children[0].children.length,1);
 assert.equal(link.children[1].children[1].textContent,'<img onerror=alert(1)>');
 assert.equal((await run({items:[]})).grid.children[0],'initial cards');
 assert.equal((await run({}, {fail:true})).grid.children[0],'initial cards');
 const local=await run({items:[item]},{protocol:'file:'});assert.equal(local.requests,0);assert.equal(local.grid.children[0],'initial cards');
 assert.equal((await run({items:[item,item,item,item]})).grid.children.length,3);
 console.log('Renderer verified: JST date, safe text/URLs, image fallback, empty/error fallback, local preview, three-card limit.');
})().catch(error=>{console.error(error);process.exitCode=1;});
