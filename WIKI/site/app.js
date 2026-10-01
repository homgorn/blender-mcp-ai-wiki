/* Blender AI Wiki — 5-lang static/API frontend (no deps) */
const UI = {
 en:{title:"Blender AI Wiki",ph:"Search / type, tag, tool…",go:"Go",all:"All categories",found:n=>`${n} entries`,open:"Open",back:"← Back to list",tags:"Tags",file:"File",sections:"Sections"},
 ru:{title:"Blender AI Wiki",ph:"Поиск / тег / инструмент…",go:"Найти",all:"Все категории",found:n=>`Записей: ${n}`,open:"Открыть",back:"← Назад к списку",tags:"Теги",file:"Файл",sections:"Разделы"},
 es:{title:"Blender AI Wiki",ph:"Buscar / etiqueta / herramienta…",go:"Buscar",all:"Todas las categorías",found:n=>`${n} entradas`,open:"Abrir",back:"← Volver",tags:"Etiquetas",file:"Archivo",sections:"Secciones"},
 de:{title:"Blender AI Wiki",ph:"Suchen / Tag / Tool…",go:"Los",all:"Alle Kategorien",found:n=>`${n} Einträge`,open:"Öffnen",back:"← Zurück",tags:"Tags",file:"Datei",sections:"Abschnitte"},
 zh:{title:"Blender AI Wiki",ph:"搜索 / 标签 / 工具…",go:"搜索",all:"全部分类",found:n=>`共 ${n} 条`,open:"打开",back:"← 返回列表",tags:"标签",file:"文件",sections:"章节"},
};
let LANG = localStorage.getItem('wiki_lang') || 'en';
let MODE = 'static';
let DB = null, IDX = null;

const $ = s => document.querySelector(s);
function t(k,...a){ const v = UI[LANG][k]; return typeof v==='function'? v(...a) : v; }
function setLang(l){ LANG=l; localStorage.setItem('wiki_lang',l);
  document.querySelectorAll('#lang-switch button').forEach(b=>b.classList.toggle('active',b.dataset.lang===l));
  document.documentElement.lang=l; applyI18n(); renderCats(); doSearch();
}
function applyI18n(){
  $('#app-title').textContent=t('title'); $('#q').placeholder=t('ph');
  $('#btn-search').textContent=t('go'); $('#foot').textContent='DB: data/meta.json + chunks · API: wiki_api.py :8099';
}
async function loadData(){
  if(MODE==='api'){
    const h=await (await fetch('http://127.0.0.1:8099/api/health')).json();
    return {api:true,total:h.entries};
  }
  if(!DB){
    try{
      const m=await (await fetch('data/meta.json')).json();
      DB={entries:m.items.map(x=>({meta:{id:x.id,title:x.title,category:x.category,type:x.type,difficulty:x.difficulty,tags:x.tags,language:x.language,description:x.desc},file_path:x.file,sections:[],full_content:'',_chunk:x.category||'misc'}))};
    }catch(e){
      DB=await (await fetch('data/wiki_database.json')).json();
    }
    try{IDX=await (await fetch('data/search_index.json')).json();}catch(e){IDX=null;}
  }
  return {api:false};
}
const CHUNKS={};
async function chunkFor(cat){
  const safe=String(cat||'misc').replace(/[^a-zA-Z0-9_-]/g,'_')||'misc';
  if(!CHUNKS[safe]){
    try{CHUNKS[safe]=await (await fetch(`data/chunks/entries_${safe}.json`)).json();}
    catch(e){CHUNKS[safe]={items:[]};}
  }
  return CHUNKS[safe];
}
function allEntries(){
  return DB.entries.map(e=>({id:e.meta.id,title:e.meta.title,category:e.meta.category||'misc',type:e.meta.type||'',difficulty:e.meta.difficulty||0,tags:e.meta.tags||[],language:e.meta.language||'en',file:e.file_path,desc:e.meta.description||''}));
}
function renderCats(){
  const cats=[...new Set(allEntries().map(e=>e.category))].sort();
  const box=$('#cats'); box.innerHTML='';
  const mk=(v,label)=>{const b=document.createElement('button');b.textContent=label;b.dataset.cat=v;
    b.onclick=()=>{document.querySelectorAll('#cats button').forEach(x=>x.classList.remove('active'));b.classList.add('active');doSearch();};box.appendChild(b);};
  mk('',t('all'));
  cats.forEach(c=>mk(c,c||'misc'));
  const sel=$('#f-cat'); sel.innerHTML=`<option value="">${t('all')}</option>`+cats.map(c=>`<option>${c}</option>`).join('');
}
async function apiSearch(q,cat,limit){
  const u=new URL('http://127.0.0.1:8099/api/search');
  u.searchParams.set('q',q);u.searchParams.set('limit',limit||20);
  if(LANG)u.searchParams.set('lang',LANG); if(cat)u.searchParams.set('category',cat);
  return (await (await fetch(u)).json()).items||[];
}
function staticSearch(q,cat){
  q=(q||'').toLowerCase().trim();
  let items=allEntries();
  if(LANG){const l=items.filter(e=>e.language===LANG); if(l.length) items=l;}
  if(cat) items=items.filter(e=>e.category===cat);
  if(!q) return items.slice(0,60);
  const words=q.split(/\s+/).filter(w=>w.length>1);
  return items.map(e=>{
    let s=0;const hay=(e.title+' '+e.desc+' '+e.tags.join(' ')+' '+e.id).toLowerCase();
    words.forEach(w=>{if(e.title.toLowerCase().includes(w))s+=10;else if(hay.includes(w))s+=3;});
    return {...e,score:s};
  }).filter(e=>e.score>0).sort((a,b)=>b.score-a.score).slice(0,60);
}
async function doSearch(){
  await loadData();
  const q=$('#q').value, cat=document.querySelector('#cats button.active')?.dataset.cat||$('#f-cat').value||'';
  let items = MODE==='api' ? await apiSearch(q,cat,60) : staticSearch(q,cat);
  $('#stats').textContent=t('found',items.length)+(MODE==='api'?' · API':' · static');
  const box=$('#results'); box.innerHTML='';
  items.forEach(e=>{
    const d=document.createElement('div');d.className='card';
    d.innerHTML=`<h3>${esc(e.title)}</h3><div class="meta">${esc(e.category)} · ${esc(e.type)} · ⭐${e.difficulty} · ${esc(e.language)} · score ${e.score??''}</div><div class="tags">${(e.tags||[]).slice(0,8).map(esc).join(' · ')}</div>`;
    d.onclick=()=>openEntry(e.id);box.appendChild(d);
  });
  $('#entry').hidden=true;
}
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
/* Minimal markdown renderer: headers, code fences, inline code, bold, tables, links, lists */
function md(src){
  src=String(src??'');
  const blocks=[];let n=0;
  src=src.replace(/```(\w*)\n([\s\S]*?)```/g,(m,lang,code)=>{blocks.push(`<pre><code>${esc(code)}</code></pre>`);return `\u0000${n++}\u0000`;});
  const lines=src.split('\n');let html='',inTable=false,inList=false;
  const inline=s=>esc(s)
    .replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>')
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>');
  const closeList=()=>{if(inList){html+='</ul>';inList=false;}};
  const closeTable=()=>{if(inTable){html+='</tbody></table>';inTable=false;}};
  for(const line of lines){
    if(/^\u0000\d+\u0000$/.test(line.trim())){closeList();closeTable();html+=blocks[+line.trim().replace(/\u0000/g,'')];continue;}
    let m;
    if(m=line.match(/^(#{1,4})\s+(.*)/)){closeList();closeTable();const l=m[1].length;html+=`<h${l+1}>${inline(m[2])}</h${l+1}>`;continue;}
    if(/^\s*---+\s*$/.test(line)){closeList();closeTable();html+='<hr>';continue;}
    if(/^\|.*\|\s*$/.test(line)){
      const cells=line.trim().replace(/^\||\|$/g,'').split('|').map(c=>inline(c.trim()));
      if(/^\|[\s:\-|]+\|\s*$/.test(line)) continue;
      if(!inTable){closeList();html+='<table><tbody>';inTable=true;}
      html+='<tr>'+cells.map(c=>`<td>${c}</td>`).join('')+'</tr>';continue;
    }
    if(m=line.match(/^\s*[-*]\s+(.*)/)){closeTable();if(!inList){html+='<ul>';inList=true;}html+=`<li>${inline(m[1])}</li>`;continue;}
    if(m=line.match(/^\s*\d+\.\s+(.*)/)){closeTable();if(!inList){html+='<ol>';inList=true;}html+=`<li>${inline(m[1])}</li>`;continue;}
    if(!line.trim()){closeList();closeTable();continue;}
    closeList();closeTable();html+=`<p>${inline(line)}</p>`;
  }
  closeList();closeTable();
  return html;
}
async function openEntry(id,push=true){
  let meta,sections=[],file='',full='';
  if(MODE==='api'){
    const r=await (await fetch('http://127.0.0.1:8099/api/entry?id='+encodeURIComponent(id))).json();
    if(r.error) return;
    meta=r.meta;sections=r.sections||[];file=r.file||'';full=r.full_content||'';
  }else{
    const m=DB.entries.find(x=>x.meta.id===id); if(!m) return;
    if(m.full_content){meta=m.meta;sections=m.sections||[];file=m.file_path;full=m.full_content;}
    else{
      const ch=await chunkFor(m.meta.category);
      const e=(ch.items||[]).find(x=>x.meta.id===id);
      if(!e) return;
      meta=e.meta;sections=e.sections||[];file=e.file_path;full=e.full_content||'';
    }
  }
  const el=$('#entry'); el.hidden=false;
  el.innerHTML=`<button id="bk">${esc(t('back'))}</button><h2>${esc(meta.title)}</h2>
  <div class="meta">ID ${esc(meta.id)} · ${esc(meta.category)} · ${esc(meta.type)} · ⭐${meta.difficulty} · ${esc(meta.language)}</div>
  <div class="tags">${t('tags')}: ${(meta.tags||[]).map(esc).join(' · ')}</div>
  <div>${t('file')}: <code>${esc(file)}</code> · <a href="#entry=${encodeURIComponent(meta.id)}">#entry=${esc(meta.id)}</a> · <a href="graph.html" target="_blank">graph</a></div>
  <div class="md-body">${md(full||sections.slice(0,12).map(s=>`## ${s.heading}\n\n${s.content||''}`).join('\n\n'))}</div>`;
  el.querySelector('#bk').onclick=()=>{history.replaceState(null,'',location.pathname);el.hidden=true;};
  if(push!==false){try{history.replaceState(null,'',`#entry=${encodeURIComponent(meta.id)}`);}catch(e){}}
  el.scrollIntoView({behavior:'smooth'});
}
function routeHash(){
  const m=(location.hash||'').match(/entry=([^&]+)/);
  if(m){openEntry(decodeURIComponent(m[1]),false);}
}
window.addEventListener('hashchange',routeHash);
document.querySelectorAll('#lang-switch button').forEach(b=>b.onclick=()=>setLang(b.dataset.lang));
$('#btn-search').onclick=doSearch;
$('#q').addEventListener('keydown',e=>{if(e.key==='Enter')doSearch();});
$('#api-mode').onchange=e=>{MODE=e.target.value;DB=null;doSearch();};
$('#f-cat').onchange=doSearch;
setLang(LANG);
routeHash();
