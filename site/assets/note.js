/* Only local JSON is requested by the page. No third-party note widget scripts. */
(()=>{
 const grid=document.getElementById('note-articles');
 if(!grid)return;
 const articleUrl=value=>{
  try{const url=new URL(value);return url.protocol==='https:'&&url.hostname==='note.com'&&!url.username&&url.pathname.startsWith('/sustella_jp/n/')?url.href:null;}catch{return null;}
 };
 const imageUrl=value=>{
  try{const url=new URL(value);return url.protocol==='https:'&&url.hostname==='assets.st-note.com'&&!url.username?url.href:null;}catch{return null;}
 };
 const formatDate=new Intl.DateTimeFormat('ja-JP',{year:'numeric',month:'2-digit',day:'2-digit',timeZone:'Asia/Tokyo'});
 grid.querySelectorAll('img').forEach(img=>img.addEventListener('error',()=>img.remove(),{once:true}));
 const render=data=>{
  if(!data||!Array.isArray(data.items))return;
  const fragment=document.createDocumentFragment();
  let count=0;
  for(const item of data.items){
   if(!item||typeof item!=='object')continue;
   const href=articleUrl(item.url),date=new Date(item.publishedAt);
   if(!href||typeof item.title!=='string'||!item.title.trim()||!Number.isFinite(date.getTime()))continue;
   const article=document.createElement('article');article.className='note-card';
   const link=document.createElement('a');link.className='note-card-link';link.href=href;link.target='_blank';link.rel='noopener noreferrer';
   const media=document.createElement('div');media.className='note-card-media';media.setAttribute('aria-hidden','true');
   const fallback=document.createElement('span');fallback.className='note-card-placeholder';fallback.textContent='SUSTELLA';media.append(fallback);
   const thumbnail=imageUrl(item.thumbnail);
   if(thumbnail){const img=document.createElement('img');img.src=thumbnail;img.alt='';img.width=800;img.height=420;img.loading='lazy';img.decoding='async';img.referrerPolicy='no-referrer';img.addEventListener('error',()=>img.remove(),{once:true});media.append(img);}
   const body=document.createElement('div');body.className='note-card-copy';
   const time=document.createElement('time');time.dateTime=item.publishedAt;time.textContent=formatDate.format(date).replaceAll('/','.');
   const title=document.createElement('h3');title.textContent=item.title;
   const action=document.createElement('span');action.className='note-card-action';action.textContent='noteで読む ↗';
   body.append(time,title,action);link.append(media,body);article.append(link);fragment.append(article);
   if(++count===3)break;
  }
  if(count){grid.replaceChildren(fragment);grid.dataset.count=String(count);}
 };
 if(!['https:','http:'].includes(location.protocol))return; // Static cards remain visible for file previews.
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),8000);
 fetch('data/note.json',{cache:'no-cache',signal:controller.signal})
  .then(response=>{if(!response.ok)throw Error('Article data unavailable');return response.json();})
  .then(render).catch(()=>{}).finally(()=>clearTimeout(timeout)); // Keep last bundled cards on failure.
})();
