
/* FINAL COIL — Stage 2: illustrated Moskvich-412 assembly documentation. All data shipped locally. */
(function(){
"use strict";
var data=window.FCAssyData;
if(!data||!Array.isArray(data.parts)){window.FCAssembly={error:"Данные схемы недоступны"};return}
var parts=data.parts,byId={},byIdentity={},categories=[],groupMap={},reverse={};
for(var i=0;i<parts.length;i++){byId[parts[i].id]=parts[i];byIdentity[parts[i].category+"|"+parts[i].section+"|"+parts[i].name]=parts[i].id;if(!groupMap[parts[i].category]){groupMap[parts[i].category]=true;categories.push(parts[i].category)}reverse[parts[i].id]=[]}
for(i=0;i<parts.length;i++)for(var j=0;j<parts[i].requires.length;j++){var req=parts[i].requires[j];if(reverse[req.id])reverse[req.id].push({id:parts[i].id,grade:req.grade})}
function e(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function a(url,title){if(!/^https:\/\//.test(url))return e(title);return '<a target="_blank" rel="noopener noreferrer" href="'+e(url)+'">'+e(title)+' ↗</a>'}
function normalized(s){return String(s==null?"":s).toLocaleLowerCase("ru").replace(/ё/g,"е").replace(/порш(?:ень|ня|ни|нев(?:ые|ых)?)/g,"поршн")}
function tag(status){return '<span class="fa-status fa-status-'+e(status)+'">'+e(({remove:"Снимается",part:"Часть сборки",fixed:"Несъёмная",use:"Работает, не снимается",open:"На уточнении"})[status]||status)+'</span>'}
function linkP(id,text){return '<a class="fa-linkpill" href="#/moskvich-parts" data-go-part="'+e(id)+'">'+e(text||byId[id]&&byId[id].name||id)+'</a>'}
function graphP(id,text){return '<a class="fa-linkpill" href="#/moskvich-assembly" data-focus-part="'+e(id)+'">'+e(text||byId[id]&&byId[id].name||id)+'</a>'}
function basicLinks(){return '<div class="fa-links"><a href="#/moskvich-412">Каталог 13 систем</a><a href="#/moskvich-parts">Карточки креплений</a><a href="#/moskvich-assembly">Схема последовательности установки</a></div>'}
var counters={remove:0,part:0,fixed:0,use:0,open:0},verified=0;
for(i=0;i<parts.length;i++){counters[parts[i].status]++;if(parts[i].fastener.source)verified++}
var cardState={q:"",category:"all",status:"all",page:0,expanded:""},cardPageSize=18;
function measures(){return '<div class="fa-measures"><div class="fa-measure"><strong>'+parts.length+'</strong><span>карточки по всему Москвичу</span></div><div class="fa-measure"><strong>'+counters.remove+'</strong><span>записей со снятием (включая повторы)</span></div><div class="fa-measure"><strong>'+data.edges+'</strong><span>условий порядка установки</span></div><div class="fa-measure"><strong>'+verified+'</strong><span>карточки с подтверждённой резьбой</span></div></div>'}
function cardsHtml(){return '<a class="crumb-link" href="#/moskvich-412">← К каталогу деталей</a><div class="eyebrow">ИЖ-412ИЭ-028 · 1985 / ЭТАП 2</div><h1>Карточки креплений</h1><p class="intro">Для каждой позиции — назначение, к чему крепится, тип соединения, размер и количество крепежа, известные блокеры установки и ограничения доступа при снятии.</p>'+basicLinks()+measures()+
'<div class="note">Точный крепёж нельзя безопасно выдумать. Если диаметр, шаг или длина не подтверждены для выбранного исполнения АЗЛК/ИЖ, в карточке стоит «не подтверждено». Для установки отличаем <strong>место крепления</strong> от <strong>обязательного предшественника</strong> и от <strong>демонтажа ради доступа</strong>.</div>'+
'<div class="fa-toolbar"><label class="fa-field">Название / ID<input id="fa-q" class="fa-control" type="search" autocomplete="off" placeholder="Например: двигатель, тормозной диск, M412-03..."></label><label class="fa-field">Система<select id="fa-cat" class="fa-control"><option value="all">Все 13 систем</option>'+categories.map(function(c){return '<option value="'+e(c)+'">'+e(c)+'</option>'}).join("")+'</select></label><label class="fa-field">Съёмность<select id="fa-status" class="fa-control"><option value="all">Любой статус</option><option value="remove">Снимается</option><option value="part">Часть сборки</option><option value="fixed">Не снимается</option><option value="use">Работает без снятия</option><option value="open">На уточнении</option></select></label></div><div id="fa-cards-summary" class="fa-quiet"></div><div id="fa-cards-list" class="fa-cards"></div><div id="fa-cards-pager"></div><p class="fa-source-note">Первоисточники и уровень достоверности доступны в каждой карточке. Общие логические зависимости — проектные правила, а не заводские универсальные запреты. Модификация ИЖ-412ИЭ-028 и год 1985 утверждены; точный крепёж ещё проверяем.</p>'}
function filteredCards(){var q=normalized(cardState.q).trim();return parts.filter(function(p){return (cardState.category==="all"||p.category===cardState.category)&&(cardState.status==="all"||p.status===cardState.status)&&(!q||normalized(p.name+" "+p.id+" "+p.category+" "+p.section).includes(q))})}
function cardField(title,val){return '<div class="fa-fieldvalue"><strong>'+e(title)+'</strong><div>'+val+'</div></div>'}
function cardHtml(p){
 var before=p.requires.length?p.requires.map(function(x){return linkP(x.id,x.label)+' <small class="fa-card-mono">'+(x.grade==="supported"?"есть источник":"правило проекта")+'</small>'}).join("<div></div>"):'<span class="fa-quiet">Обязательный предшественник пока не установлен. Это не доказательство свободной сборки.</span>';
 var access=p.access.length?p.access.map(function(x){return linkP(x.id,x.label)}).join(" "):'<span class="fa-quiet">Отдельные требования доступа не описаны.</span>';
 var outgoing=reverse[p.id].length?reverse[p.id].map(function(x){return linkP(x.id,byId[x.id].name)}).join(" "):'<span class="fa-quiet">Ни одна следующая установка явно не заблокирована этой деталью.</span>';
 var source=p.fastener.source?a(p.fastener.source,"Каталог крепежа"):'Размеры ещё не проверены по выбранной модификации';
 var row='<details class="fa-card" id="fa-card-'+e(p.id)+'"'+(cardState.expanded===p.id?' open':'')+'><summary><span class="fa-card-id">'+e(p.id)+'</span><span class="fa-card-title">'+e(p.name)+'</span>'+tag(p.status)+'</summary><div class="fa-cardbody">'+
 '<div class="fa-expandrow"><span class="fa-card-mono">'+e(p.category)+" / "+e(p.section)+'</span>'+graphP(p.id,"Показать связи на схеме")+'</div>'+
 cardField("Что это за деталь",e(p.description))+
 '<div class="fa-cardfields">'+cardField("К чему крепится",e(p.mount)+(p.parent?'<div>'+linkP(p.parent)+'</div>':""))+cardField("Способ крепления",e(p.fastener.type))+
 cardField("Болты / размер резьбы",e(p.fastener.size)+'<div class="fa-quiet">'+e(p.fastener.quantity)+'</div><div class="fa-quiet">'+source+'</div>')+
 cardField("Условия установки",before)+cardField("Что она блокирует",outgoing)+cardField("Что снять для доступа",access)+cardField("Игровая логика",e(p.rule))+'</div>'+
 '<div class="fa-source-note">'+e(p.sourceLevel)+(p.notes.length?'<p>'+p.notes.map(e).join(" ")+'</p>':"")+'</div>'+(p.fixationMode?'<div class="fa-mount-reference"><strong>Три опоры силового агрегата:</strong> помимо передней балки есть задняя поперечина и подушка. <a href="#/moskvich-assembly#engine-mount-check">Проверить полную фиксацию на схеме</a>. Подушки и кронштейны можно подготовить на двигателе заранее.</div>':'')+'</div></details>';
 return row;
}
function drawCardList(){
 var items=filteredCards(),count=items.length,maxPage=Math.max(0,Math.ceil(count/cardPageSize)-1);if(cardState.page>maxPage)cardState.page=maxPage;
 var start=cardState.page*cardPageSize,shown=items.slice(start,start+cardPageSize);
 var summary=document.getElementById("fa-cards-summary"),list=document.getElementById("fa-cards-list"),pager=document.getElementById("fa-cards-pager");
 if(!summary||!list||!pager)return;
 summary.textContent="Найдено: "+items.length+". Карточки "+(items.length?start+1:0)+"–"+Math.min(start+cardPageSize,items.length)+".";
 list.innerHTML=shown.map(cardHtml).join("")||'<div class="fa-empty">По запросу нет карточек.</div>';
 pager.innerHTML='<div class="fa-pagebar"><button type="button" id="fa-prev"'+(cardState.page===0?" disabled":"")+'>← Предыдущие</button><span>Страница '+(cardState.page+1)+' из '+(maxPage+1)+'</span><button type="button" id="fa-next"'+(cardState.page>=maxPage?" disabled":"")+'>Следующие →</button></div>';
 pager.querySelector("#fa-prev").addEventListener("click",function(){cardState.page=Math.max(0,cardState.page-1);cardState.expanded="";drawCardList()});
 pager.querySelector("#fa-next").addEventListener("click",function(){cardState.page++;cardState.expanded="";drawCardList()});
 list.querySelectorAll(".fa-card").forEach(function(el){el.addEventListener("toggle",function(){if(el.open)cardState.expanded=el.id.replace("fa-card-","")})});
}
function initCards(){
 var q=document.getElementById("fa-q"),cat=document.getElementById("fa-cat"),st=document.getElementById("fa-status");
 if(!q)return;
 q.value=cardState.q;cat.value=cardState.category;st.value=cardState.status;
 q.addEventListener("input",function(){cardState.q=q.value;cardState.page=0;cardState.expanded="";drawCardList()});
 cat.addEventListener("change",function(){cardState.category=cat.value;cardState.page=0;drawCardList()});
 st.addEventListener("change",function(){cardState.status=st.value;cardState.page=0;drawCardList()});
 document.getElementById("fa-cards-list").addEventListener("click",function(ev){var a=ev.target.closest("[data-go-part],[data-focus-part]");if(!a)return;if(a.dataset.focusPart){graphState.focus=a.dataset.focusPart;graphState.mode="focus"}else if(a.dataset.goPart){openCard(a.dataset.goPart)}});
 drawCardList();if(cardState.expanded)requestAnimationFrame(function(){var el=document.getElementById("fa-card-"+cardState.expanded);if(el){el.open=true;el.scrollIntoView({block:"nearest"})}});
}
function openCard(id){var p=byId[id];if(!p)return;cardState.q="";cardState.category=p.category;cardState.status="all";cardState.page=0;cardState.expanded=id;var arr=filteredCards();cardState.page=Math.floor(Math.max(0,arr.findIndex(function(n){return n.id===id}))/cardPageSize);if(location.hash!=="#/moskvich-parts")location.hash="#/moskvich-parts";else{var q=document.getElementById("fa-q"),cat=document.getElementById("fa-cat"),status=document.getElementById("fa-status");if(q)q.value="";if(cat)cat.value=cardState.category;if(status)status.value="all";drawCardList();var el=document.getElementById("fa-card-"+id);if(el){el.open=true;el.scrollIntoView({block:"nearest"})}}}
var graphState={mode:"overview",focus:null,q:"",scale:1};

/* Три опоры силового агрегата: предметная рабочая схема, не полная заводская норма. */
var mountState={frontBeam:false,left:false,right:false,rearBeam:false,rear:false,fixed:false};
function mountModel(){return data.engineMounts}
function mountReference(){var m=mountModel();if(!m)return "";return '<div class="fa-mount-reference"><strong>Источник конфигурации:</strong> '+a(m.source,"каталог ИЖ-412, чертёж №50 (1995)")+'<div class="fa-quiet">'+e(m.validity)+'</div></div>'}
function mountHtml(){
 var m=mountModel();if(!m)return "";
 var defs='<defs><marker id="fa-mount-arrow" viewBox="0 0 9 9" refX="8" refY="4.5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L9 4.5 L0 9 Z" fill="#95bf8e"/></marker></defs>';
 var svg='<svg viewBox="0 0 850 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Схема трёх опор силового агрегата: две передние и задняя">'+defs+
 '<rect x="268" y="88" width="310" height="58" rx="11" fill="#35523a" stroke="#89b786" stroke-width="2"/><text x="423" y="113" fill="#eaf3e7" text-anchor="middle" font-size="15" font-weight="700">Силовой агрегат</text><text x="423" y="133" fill="#c4d6bb" text-anchor="middle" font-size="12">двигатель + сцепление + КПП</text>'+
 '<path d="M 268 110 L 211 60" stroke="#8ab68b" stroke-width="3"/><path d="M 578 110 L 637 60" stroke="#8ab68b" stroke-width="3"/><path d="M 423 146 L 423 184" stroke="#8ab68b" stroke-width="3"/>'+
 '<rect x="42" y="23" width="220" height="52" rx="9" fill="#273b2c" stroke="#617b63"/><text x="152" y="44" text-anchor="middle" fill="#e5eedf" font-size="13">Левая передняя опора</text><text x="152" y="61" text-anchor="middle" fill="#b4cbac" font-size="11">412-1001200-Б</text>'+
 '<rect x="592" y="23" width="220" height="52" rx="9" fill="#273b2c" stroke="#617b63"/><text x="702" y="44" text-anchor="middle" fill="#e5eedf" font-size="13">Правая передняя опора</text><text x="702" y="61" text-anchor="middle" fill="#b4cbac" font-size="11">412-1001020</text>'+
 '<rect x="290" y="184" width="266" height="42" rx="9" fill="#273b2c" stroke="#617b63"/><text x="423" y="201" text-anchor="middle" fill="#e5eedf" font-size="13">Задняя опора</text><text x="423" y="217" text-anchor="middle" fill="#b4cbac" font-size="11">408Ю-1001050-Б</text></svg>';
 var checks=m.steps.map(function(item){return '<label class="fa-mount-step"><input type="checkbox" data-mount-check="'+e(item.id)+'"'+(mountState[item.id]?' checked':'')+'><span><strong>'+e(item.label)+'</strong><small>'+e(item.detail)+'</small></span></label>'}).join("");
 var rows=m.hardware.map(function(f){return '<tr><td><strong>'+e(f.code)+'</strong></td><td>'+e(f.position)+'</td><td>'+e(f.thread)+'</td><td>'+e(f.quantity)+'</td><td><small>'+e(f.status)+'</small><div>'+a(f.catalogSource,"Каталог")+(f.dimensionSource?' · '+a(f.dimensionSource,"Размер"):'')+'</div></td></tr>'}).join("");
 var groups=m.mounts.map(function(s){return '<div class="fa-mount-subcard"><h4>'+e(s.label)+'</h4><p>'+e(s.anchor)+'</p><ul>'+s.elements.map(function(x){return '<li>'+e(x[1])+' <code>'+e(x[0])+'</code> · '+e(x[2])+' шт.</li>'}).join("")+'</ul></div>'}).join("");
 return '<section class="fa-mount-section" id="engine-mount-check"><h2>Проверка установки силового агрегата: три опоры</h2>'+
 '<p class="fa-quiet">Развиваем реальную конструкцию. На схеме две передние опоры и одна задняя; поперечину задней опоры не включаем автоматически в основной каталог из 473 позиций.</p>'+
 '<div class="fa-mount-svg">'+svg+'</div><div class="fa-mount-cards">'+groups+'</div>'+
 '<h3>Проверь, что готово для окончательной фиксации</h3><div class="fa-mount-checks">'+checks+'</div><div class="fa-mount-result" id="fa-mount-result" role="status" aria-live="polite"></div>'+
 '<div class="fa-quiet">Это <strong>демонстрация проектного правила</strong>, а не внедрённая механика UE5. Силовой агрегат можно позиционировать талью до закрепления на всех трёх опорах.</div>'+
 '<h3>Реестр крепежа этого узла</h3><div class="fa-mount-tablewrap"><table class="fa-mount-table"><thead><tr><th>Номер</th><th>Применение</th><th>Резьба / размер</th><th>Количество</th><th>Уровень проверки</th></tr></thead><tbody>'+rows+'</tbody></table></div>'+
 mountReference()+'<p class="fa-quiet">Принадлежность крепежа к каталогу 1995 года и совпадение номенклатурного номера с болтом определённого размера ещё не доказывают взаимозаменяемость с каждой машиной 1985 года.</p></section>';
}
function drawMountResult(){
 var m=mountModel(),el=document.getElementById("fa-mount-result");if(!m||!el)return;
 var missing=m.steps.filter(function(s){return !mountState[s.id]});
 var supportsReady=m.steps.filter(function(s){return s.id!=="fixed"}).every(function(s){return mountState[s.id]});
 var done=missing.length===0;
 el.className="fa-mount-result"+(done?" completed":"");
 el.innerHTML=done?'<strong>Агрегат окончательно закреплён (по проектной проверке).</strong><div>Все три опоры и завершающая затяжка отмечены.</div>':
 supportsReady?'<strong>Три опоры подготовлены. Осталось проверить затяжку крепежа.</strong>':
 '<strong>Закрепление не завершено.</strong><div>Не выполнено: '+missing.map(function(s){return e(s.label)}).join("; ")+'.</div>';
}
function initMountChecks(){
 var section=document.getElementById("engine-mount-check");if(!section)return;
 section.addEventListener("change",function(ev){var t=ev.target;if(!t||!t.dataset||!t.dataset.mountCheck)return;mountState[t.dataset.mountCheck]=!!t.checked;drawMountResult()});
 drawMountResult();
}

function graphHtml(){return '<a class="crumb-link" href="#/moskvich-412">← К каталогу деталей</a><div class="eyebrow">ИЖ-412ИЭ-028 · 1985 / ЭТАП 2</div><h1>Схема порядка установки</h1><p class="intro">Посмотри весь автомобиль по 13 системам, переключись на полную схему из '+parts.length+' узлов или выбери конкретную деталь, чтобы увидеть, что её блокирует и что зависит от неё.</p>'+basicLinks()+measures()+
'<div class="note"><strong>Три разных типа связи:</strong> сплошная стрелка — подтверждённая последовательность, пунктир — проектное условие для реализации, синяя линия — место крепления (не является запретом сборки). Логика доступа при разборке показана отдельно. У всех систем может быть несколько допустимых последовательностей монтажа.</div>'+
'<div class="fa-mount-wrapper">'+mountHtml()+'</div>'+'<div class="fa-tabs" id="fa-tabs"><button type="button" data-mode="overview">Обзор систем</button><button type="button" data-mode="full">Все '+parts.length+' узла</button><button type="button" data-mode="focus">Связи детали</button></div>'+
'<div class="fa-graph-grid"><aside class="fa-explorer"><h3>Найти деталь</h3><input id="fa-gq" class="fa-control" type="search" placeholder="Поиск по имени или ID"><div class="fa-quiet">Любая из '+parts.length+' карточек доступна для просмотра зависимостей.</div><div id="fa-gresults" class="fa-results"></div></aside>'+
'<div class="fa-graph-panel"><div class="fa-graph-topbar"><strong id="fa-graph-title">Схема</strong><span><button id="fa-zoom-out" type="button">−</button> <button id="fa-zoom-in" type="button">+</button> <button id="fa-zoom-reset" type="button">100%</button></span></div>'+
'<div id="fa-graph-scroll" class="fa-graph-scroll"></div><div class="fa-graph-legend"><span><i class="fa-dot"></i>По источнику</span><span><i class="fa-dot design"></i>Проектная зависимость</span><span><i class="fa-dot mount"></i>Место крепления</span><span><i class="fa-dot access"></i>Доступ при снятии</span></div><div id="fa-graph-info" class="fa-focused-info"></div></div></div>'+
'<h2>Как понимать стрелки</h2><div class="split"><div class="panel"><h3>Установка ≠ диагностика</h3><p class="muted">На этом этапе фиксируем только крепление и геометрические условия. Неисправности, регулировки, питание и взаимодействия систем — этап 3.</p></div><div class="panel"><h3>Неполная заводская спецификация</h3><p class="muted">В граф внесены только обоснованные или явно помеченные проектные зависимости. Отсутствие стрелки не означает, что деталь можно поставить в любой момент. Размеры крепежа, год и завод требуют проверки.</p></div></div>'+
'<div class="fa-section"><h2>Отдельно проверить</h2><p class="muted">У Москвича-412 две передние опоры силового агрегата на балке передней подвески и задняя опора на отдельной поперечине кузова. Задняя поперечина сейчас не выделена самостоятельной позицией утверждённого каталога. На схеме не выдаём её за уже согласованную деталь: это зафиксированный пробел, который потребуется уточнить.</p></div>'}
function defs(){return '<defs><marker id="fa-arrow" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#9ac48b"/></marker><marker id="fa-arrow-plan" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#bba272"/></marker></defs>'}
function nodeSvg(id,x,y,w,h,small,cl){var p=byId[id];if(!p)return "";var title=p.name.length>40?p.name.slice(0,37)+"…":p.name,short=small?title.slice(0,31):title;
 return '<g class="fa-graph-node '+(cl||"")+'" data-node="'+e(p.id)+'"><rect rx="9" x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'"/><text x="'+(x+10)+'" y="'+(y+19)+'">'+e(short)+'</text><text class="fa-node-small" x="'+(x+10)+'" y="'+(y+38)+'">'+e(p.id)+'</text><title>'+e(p.name)+'</title></g>'}
function pathSvg(x1,y1,x2,y2,cls){var mid=(x1+x2)/2;return '<path class="fa-edge '+cls+'" d="M '+x1+' '+y1+' C '+mid+' '+y1+', '+mid+' '+y2+', '+x2+' '+y2+'"/>'}
function wrapSvg(w,h,contents){return '<svg viewBox="0 0 '+w+' '+h+'" width="'+Math.round(w*graphState.scale)+'" height="'+Math.round(h*graphState.scale)+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Схема связей установки деталей Москвича-412">'+defs()+contents+'</svg>'}
function overview(){
 var w=1200,h=690,nodes="",lines="",layout={},counts={};
 categories.forEach(function(c,ci){counts[c]=parts.filter(function(p){return p.category===c}).length;layout[c]={x:32+(ci%3)*392,y:44+Math.floor(ci/3)*132}});
 for(var i=0;i<parts.length;i++){var p=parts[i];for(var j=0;j<p.requires.length;j++){var q=byId[p.requires[j].id];if(!q||q.category===p.category)continue;var key=q.category+"|"+p.category;var s=layout[q.category],t=layout[p.category];if(!s||!t)continue;if(!overview.seen)overview.seen={};if(overview.seen[key])continue;overview.seen[key]=true;lines+=pathSvg(s.x+166,s.y+38,t.x+166,t.y+38,p.requires[j].grade==="supported"?"":"design")}}
 overview.seen=null;
 categories.forEach(function(c,i){var p=layout[c];nodes+='<g data-cat="'+e(c)+'" class="fa-graph-node"><rect x="'+p.x+'" y="'+p.y+'" width="338" height="76" rx="11"/><text x="'+(p.x+12)+'" y="'+(p.y+27)+'">'+e((i+1)+". "+c)+'</text><text class="fa-node-small" x="'+(p.x+12)+'" y="'+(p.y+54)+'">'+counts[c]+' конструктивных позиций · открыть систему</text></g>'});
 return wrapSvg(w,h,lines+nodes);
}
function full(){
 var w=1710,y=24,loc={},boxes="",edges="",byCat={};categories.forEach(function(c){byCat[c]=parts.filter(function(p){return p.category===c})});
 categories.forEach(function(c,ci){var arr=byCat[c],rows=Math.ceil(arr.length/5);boxes+='<rect fill="#223527" opacity=".7" x="15" y="'+(y-7)+'" width="1680" height="'+(rows*57+62)+'" rx="11"/><text fill="#d7e8d0" font-size="15" font-weight="700" x="30" y="'+(y+16)+'">'+e((ci+1)+". "+c)+'</text>';arr.forEach(function(p,i){var x=25+(i%5)*336,cy=y+32+Math.floor(i/5)*57;loc[p.id]={x,y:cy};boxes+=nodeSvg(p.id,x,cy,320,49,true,"")});y+=rows*57+73});
 for(var k=0;k<parts.length;k++){var p=parts[k];for(var a=0;a<p.requires.length;a++){var dep=p.requires[a],o=loc[dep.id],n=loc[p.id];if(o&&n){edges+=pathSvg(o.x+160,o.y+25,n.x+160,n.y+25,dep.grade==="supported"?"":"design")}}}
 return wrapSvg(w,y+18,edges+boxes);
}
function focusGraph(id){
 var p=byId[id]||parts[0],pre=p.requires.slice(0,14),post=reverse[p.id].slice(0,14),parents=p.parent&&p.parent!==p.id?[{id:p.parent,grade:"mount"}]:[],acc=p.access.slice(0,8);
 var rows=Math.max(2,pre.length,post.length);var h=Math.max(395,rows*74+110),y=h/2-23;
 var lines="",nodes="",leftX=20,midX=410,rightX=808,nodeW=320,nodeH=49;
 pre.forEach(function(d,i){var yy=30+i*74;nodes+=nodeSvg(d.id,leftX,yy,nodeW,nodeH,false,"");lines+=pathSvg(leftX+nodeW,yy+24,midX,y+24,d.grade==="supported"?"":"design")});
 post.forEach(function(d,i){var yy=30+i*74;nodes+=nodeSvg(d.id,rightX,yy,nodeW,nodeH,false,"");lines+=pathSvg(midX+nodeW,y+24,rightX,yy+24,d.grade==="supported"?"":"design")});
 parents.forEach(function(d){if(!pre.some(function(x){return x.id===d.id})){nodes+=nodeSvg(d.id,midX,15,nodeW,nodeH,false,"");lines+='<path class="fa-edge mount" d="M '+(midX+nodeW/2)+' 64 L '+(midX+nodeW/2)+' '+y+'"/>'}});
 var accessY=h-62;acc.forEach(function(d,i){if(i===0)nodes+='<text fill="#ad9c95" font-size="11" x="20" y="'+(accessY-14)+'">Для доступа при снятии (не блокеры установки)</text>';nodes+=nodeSvg(d.id,20+i*136,accessY,130,43,true,"");lines+='<path class="fa-edge access" d="M '+(20+i*136+65)+' '+accessY+' L '+(midX+nodeW/2)+' '+(y+48)+'"/>'});
 nodes+=nodeSvg(p.id,midX,y,nodeW,nodeH,false,"focus");
 nodes+='<text fill="#b0c9ac" font-size="12" x="20" y="19">Сначала установить</text><text fill="#cfe1c8" font-size="12" x="424" y="'+(y-12)+'">Выбранная деталь</text><text fill="#b0c9ac" font-size="12" x="808" y="19">Что она блокирует</text>';
 return wrapSvg(1170,h+5,lines+nodes);
}
function drawGraph(){
 var mode=graphState.mode,scroll=document.getElementById("fa-graph-scroll"),title=document.getElementById("fa-graph-title"),info=document.getElementById("fa-graph-info");if(!scroll||!title)return;
 document.querySelectorAll("[data-mode]").forEach(function(b){b.setAttribute("aria-pressed",String(b.dataset.mode===mode))});
 if(mode==="focus"&&!graphState.focus)graphState.focus=parts.find(function(p){return p.name==="Двигатель в сборе"})?.id||parts[0].id;
 var p=byId[graphState.focus];
 title.textContent=mode==="overview"?"13 систем — связи между системами":mode==="full"?"Полная схема: "+parts.length+" узла":"Зависимости: "+(p?p.name:"");
 scroll.innerHTML=mode==="overview"?overview():mode==="full"?full():focusGraph(graphState.focus);
 if(mode==="focus"&&p){
 var pre=p.requires.length?p.requires.map(function(x){return e(x.label)+(x.grade==="supported"?" (источник)":" (проект)")}).join("; "):"Не указаны";
 var post=reverse[p.id].length?reverse[p.id].map(function(x){return e(byId[x.id].name)}).join("; "):"Нет отмеченных зависимых узлов";
 info.innerHTML='<h3>'+e(p.name)+'</h3><p><strong>Монтаж:</strong> '+e(p.mount)+'</p><p><strong>Обязательные условия установки:</strong> '+pre+'</p><p><strong>Блокирует установку:</strong> '+post+'</p><p><strong>Для снятия нужен доступ:</strong> '+(p.access.length?p.access.map(function(x){return e(x.label)}).join("; "):"отдельно не описан")+'</p><button id="fa-open-card" type="button">Открыть полную карточку →</button>';
 info.querySelector("button").addEventListener("click",function(){openCard(p.id)});
 }else info.innerHTML=mode==="full"?'<p><strong>Все '+parts.length+' узла показаны.</strong> Прокручивайте схему; нажмите на любую деталь, чтобы увидеть входящие и исходящие зависимости. Стрелки отображают только внесённые условия установки.</p>':'<p>Нажмите на категорию для выбора деталей этой системы или найдите конкретную деталь слева. Категории — навигация по всем 13 системам, а не единственная строгая последовательность сборки.</p>';
}
function drawResults(){
 var q=normalized(graphState.q).trim(),arr=parts.filter(function(p){return !q||normalized(p.name+" "+p.id+" "+p.category).includes(q)}),list=document.getElementById("fa-gresults");
 if(!list)return;
 if(!q&&graphState.mode==="focus"&&graphState.focus){var a=byId[graphState.focus];arr=[a].concat(arr.filter(function(p){return p.category===a.category&&p.id!==a.id}).slice(0,23))}
 else if(!q)arr=parts.filter(function(p){return p.status==="remove"}).slice(0,28);
 list.innerHTML=arr.slice(0,42).map(function(p){return '<button type="button" class="fa-result'+(p.id===graphState.focus?" active":"")+'" data-choose="'+e(p.id)+'">'+e(p.name)+'<small>'+e(p.category)+' · '+e(p.id)+'</small></button>'}).join("")||'<p class="fa-quiet">Ничего не найдено</p>';
}
function initGraph(){
 var container=document.getElementById("fa-graph-scroll");if(!container)return;
 var search=document.getElementById("fa-gq");search.value=graphState.q;
 search.addEventListener("input",function(){graphState.q=search.value;drawResults()});
 document.getElementById("fa-gresults").addEventListener("click",function(ev){var el=ev.target.closest("[data-choose]");if(el){graphState.focus=el.dataset.choose;graphState.mode="focus";drawGraph();drawResults()}});
 document.getElementById("fa-tabs").addEventListener("click",function(ev){var el=ev.target.closest("[data-mode]");if(el){graphState.mode=el.dataset.mode;graphState.scale=1;drawGraph();drawResults()}});
 container.addEventListener("click",function(ev){var n=ev.target.closest("[data-node]"),cat=ev.target.closest("[data-cat]");if(n){graphState.focus=n.dataset.node;graphState.mode="focus";graphState.scale=1;drawGraph();drawResults()}else if(cat){graphState.q=cat.dataset.cat;search.value=graphState.q;drawResults();search.focus()}});
 document.getElementById("fa-zoom-in").addEventListener("click",function(){graphState.scale=Math.min(2.2,graphState.scale+.2);drawGraph()});
 document.getElementById("fa-zoom-out").addEventListener("click",function(){graphState.scale=Math.max(.55,graphState.scale-.2);drawGraph()});
 document.getElementById("fa-zoom-reset").addEventListener("click",function(){graphState.scale=1;drawGraph()});
 initMountChecks();drawGraph();drawResults();
}
window.FCAssembly={cardsHtml:cardsHtml,initCards:initCards,graphHtml:graphHtml,initGraph:initGraph,openCard:openCard,getId:function(category,section,name){return byIdentity[category+"|"+section+"|"+name]||""},parts:parts,byId:byId};
})();
