import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const host=document.getElementById('canvasHost'), partsEl=document.getElementById('parts'),search=document.getElementById('search'),countEl=document.getElementById('count');
const titleEl=document.getElementById('detailTitle'),metaEl=document.getElementById('detailMeta'),statusEl=document.getElementById('detailStatus'),descEl=document.getElementById('detailDesc'),loading=document.getElementById('loading');
const xrayBtn=document.getElementById('xray'),isolateBtn=document.getElementById('isolate'),resetBtn=document.getElementById('reset');
const C={body:0x829c7d,body2:0x69836c,metal:0x8a9a91,chrome:0xc5d5c6,glass:0x81b2b8,rubber:0x252b27,engine:0x9c9e91,interior:0x4e5847,brake:0xb5a998,lights:0xe1c8a4,highlight:0xffc869};
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(38,1,.07,120);camera.position.set(6,4.6,7.5);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2)); renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.setSize(Math.max(host.clientWidth,320),Math.max(host.clientHeight,450));host.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.075;controls.minDistance=2;controls.maxDistance=17;controls.target.set(0,.83,0);controls.maxPolarAngle=Math.PI*.87;
scene.add(new THREE.HemisphereLight(0xe1f0db,0x314036,2.5));const light=new THREE.DirectionalLight(0xffe7b9,2.7);light.position.set(4,9,6);scene.add(light);const fill=new THREE.DirectionalLight(0x9ed0d3,1.4);fill.position.set(-5,4,-5);scene.add(fill);
const root=new THREE.Group();scene.add(root);
const systemGroups=new Map(), parts=new Map(), lookup=[], aliases=new Map();
const materialCache=new Map();
function mat(c,transparent=false,opacity=1){return new THREE.MeshStandardMaterial({color:c,roughness:.73,metalness:.2,transparent,opacity,side:THREE.DoubleSide,depthWrite:!transparent})}
function getMat(c){if(!materialCache.has(c))materialCache.set(c,mat(c));return materialCache.get(c)}
function system(name){if(!systemGroups.has(name)){const g=new THREE.Group();g.name=name;root.add(g);systemGroups.set(name,g)}return systemGroups.get(name)}
function register(id,name,group,obj){obj.userData.partId=id;obj.userData.partName=name;obj.traverse(v=>{if(v.isMesh){v.userData.partId=id;v.userData.partName=name;v.userData.category=group;}});parts.set(id,{id,name,category:group,obj});return obj}
function add(id,name,group,obj){register(id,name,group,obj);system(group).add(obj);return obj}
function cube(id,name,group,xyz,dim,color,rx=0,ry=0,rz=0){const mesh=new THREE.Mesh(new THREE.BoxGeometry(...dim),getMat(color));mesh.position.set(...xyz);mesh.rotation.set(rx,ry,rz);return add(id,name,group,mesh)}
function cyl(id,name,group,xyz,radius,height,color,axis='y',seg=24){const mesh=new THREE.Mesh(new THREE.CylinderGeometry(radius,radius,height,seg),getMat(color));mesh.position.set(...xyz);if(axis==='x')mesh.rotation.z=Math.PI/2;else if(axis==='z')mesh.rotation.x=Math.PI/2;return add(id,name,group,mesh)}
function tor(id,name,group,xyz,major,tube,color,axis='x'){const mesh=new THREE.Mesh(new THREE.TorusGeometry(major,tube,8,32),getMat(color));mesh.position.set(...xyz);if(axis==='x')mesh.rotation.y=Math.PI/2;else if(axis==='y')mesh.rotation.x=Math.PI/2;return add(id,name,group,mesh)}
function line(id,name,group,pts,color,radius=.025){const curve=new THREE.CatmullRomCurve3(pts.map(p=>new THREE.Vector3(...p)));const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,Math.max(12,pts.length*7),radius,7,false),getMat(color));return add(id,name,group,mesh)}
function shapePanel(id,name,group,pts,depth,color,offsetX=0){const shape=new THREE.Shape();shape.moveTo(-pts[0][0],pts[0][1]);pts.slice(1).forEach(p=>shape.lineTo(-p[0],p[1]));shape.closePath();const geo=new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:false,curveSegments:1});geo.rotateY(Math.PI/2);const mesh=new THREE.Mesh(geo,getMat(color));mesh.position.x=offsetX-depth/2;return add(id,name,group,mesh)}
function sphere(id,name,group,xyz,r,color){const mesh=new THREE.Mesh(new THREE.SphereGeometry(r,12,8),getMat(color));mesh.position.set(...xyz);return add(id,name,group,mesh)}
// Own schematic vehicle geometry: +Z points toward the rear of the car.
cube('body.shell','Несущий кузов','Кузов',[0,.83,0],[1.57,.6,3.85],C.body);
cube('body.floor','Днище кузова','Кузов',[0,.57,0],[1.55,.13,3.65],C.metal);
shapePanel('body.cabin','Каркас салона','Кузов',[[-1.05,1.08],[-.58,1.72],[.75,1.72],[1.22,1.08]],1.37,C.body2);
cube('body.roof','Крыша','Кузов',[0,1.74,.06],[1.44,.085,1.35],C.body);
cube('body.hood','Капот','Кузов',[0,1.12,-1.51],[1.53,.065,1.16],C.body2, .025);
cube('body.trunk','Крышка багажника','Кузов',[0,1.12,1.57],[1.48,.065,1.00],C.body2);
for(const side of [-1,1]){
const x=side*.798,s=side===-1?'left':'right',label=side===-1?'лев':'прав';
cube('body.frontwing.'+s,'Переднее '+label+'ое крыло','Кузов',[side*.765,1.01,-1.54],[.08,.40,.94],C.body);
cube('body.rearwing.'+s,'Заднее '+label+'ое крыло','Кузов',[side*.765,1.01,1.53],[.08,.42,.86],C.body);
cube('body.door.front.'+s,'Передняя '+label+'ая дверь','Кузов',[x,.97,-.53],[.045,.54,1.00],C.body2);
cube('body.door.rear.'+s,'Задняя '+label+'ая дверь','Кузов',[x,.97,.43],[.045,.54,.86],C.body2);
cube('body.sill.'+s,'Порог '+s,'Кузов',[x,.64,0],[.07,.13,2.52],C.metal);
cube('body.mirror.'+s,'Наружное зеркало','Кузов',[side*.95,1.31,-.94],[.26,.13,.12],C.chrome);
for(const [idx,z] of [['front',-.51],['rear',.45]]) {
 cube('glass.side.'+s+'.'+idx,'Боковое стекло','Кузов',[side*.703,1.4,z],[.012,.42,idx==='front'?.81:.77],C.glass);
}
cube('body.handle.'+s+'.front','Наружная ручка двери','Кузов',[side*.837,1.14,-.27],[.022,.04,.15],C.chrome);
cube('body.handle.'+s+'.rear','Наружная ручка двери','Кузов',[side*.837,1.14,.70],[.022,.04,.15],C.chrome);
cube('body.bumper.'+s,'Бампер','Кузов',[side*.59,.68,0],[.01,.04,.02],C.chrome);
for(const z of [-1.31,1.31]){
const f=z<0?'front':'rear';const nm=f==='front'?'Переднее':'Заднее';
cyl('wheel.tire.'+s+'.'+f,nm+' колесо','Колёса, ступицы и шины',[side*.89,.42,z],.335,.195,C.rubber,'x',40);
cyl('wheel.disc.'+s+'.'+f,'Диск колеса','Колёса, ступицы и шины',[side*.995,.42,z],.238,.025,C.chrome,'x',32);
cyl('wheel.hub.'+s+'.'+f,'Ступица колеса','Колёса, ступицы и шины',[side*1.016,.42,z],.075,.045,C.metal,'x');
tor('wheel.ring.'+s+'.'+f,'Колёсный колпак','Колёса, ступицы и шины',[side*1.02,.42,z],.155,.015,C.chrome);
cyl('brake.'+s+'.'+f,f==='front'?'Тормозной диск':'Тормозной барабан','Тормозная система',[side*.71,.42,z],.25,.11,C.brake,'x');
cyl('susp.spring.'+s+'.'+f,f==='front'?'Пружина передней подвески':'Рессорная опора','Подвеска',[side*.61,.60,z],.11,.32,C.metal);
line('susp.arm.'+s+'.'+f,'Рычаг подвески','Подвеска',[[side*.30,.47,z],[side*.72,.40,z]],C.chrome,.038);
cyl('susp.shock.'+s+'.'+f,'Амортизатор','Подвеска',[side*.53,.71,z],.057,.49,C.engine);
}
}
cube('glass.windshield','Лобовое стекло','Кузов',[0,1.42,-.88],[1.33,.51,.026],C.glass,-.55);
cube('glass.rear','Заднее стекло','Кузов',[0,1.42,.94],[1.31,.46,.028],C.glass,.52);
cube('body.frontbumper','Передний бампер','Кузов',[0,.7,-2.005],[1.84,.13,.13],C.chrome);
cube('body.rearbumper','Задний бампер','Кузов',[0,.7,2.005],[1.84,.13,.13],C.chrome);
cube('body.grille','Решётка радиатора в сборе','Кузов',[0,.91,-1.97],[1.04,.22,.035],C.rubber);
for(let i=0;i<9;i++) cube('body.grille.line.'+i,'Решётка радиатора в сборе','Кузов',[-.45+i*.112,.91,-1.998],[.025,.19,.023],C.chrome);
for(const x of [-.65,.65]){
cyl('light.head.'+x,'Передняя фара','Электрика',[x,.98,-1.975],.17,.052,C.lights,'z');
cyl('light.tail.'+x,'Задний фонарь','Электрика',[x,.98,1.973],.15,.055,0xc67a66,'z');
}
cube('body.license.front','Передний номерной знак','Кузов',[0,.71,-2.085],[.40,.10,.012],C.chrome);
cube('body.license.rear','Задний номерной знак','Кузов',[0,.88,2.063],[.42,.11,.014],C.chrome);
// Seats, dashboard and steering wheel inside cabin.
for(const x of [-.36,.36]){
cube('interior.seat.'+x,'Переднее сиденье','Интерьер салона',[x,.87,-.32],[.51,.19,.51],C.interior);
cube('interior.back.'+x,'Спинка сиденья','Интерьер салона',[x,1.14,-.06],[.52,.58,.13],C.interior,.13);
}
cube('interior.rearseat','Задний диван','Интерьер салона',[0,.85,.82],[1.25,.24,.5],C.interior);
cube('interior.dashboard','Панель приборов','Интерьер салона',[0,1.10,-.96],[1.35,.20,.21],C.rubber);
tor('interior.steering','Рулевое колесо','Рулевое управление',[-.37,1.17,-.69],.18,.022,C.chrome,'z');
line('interior.steering.column','Рулевая колонка','Рулевое управление',[[-.37,1.17,-.69],[-.37,1.00,-.94]],C.metal,.04);
line('interior.shifter','Рычаг КПП','Трансмиссия',[[0,.77,-.50],[.05,1.07,-.42]],C.chrome,.035);
// Engine and internals, represented as separate geometric assemblies.
cube('engine.block','Блок цилиндров','Двигатель',[0,.82,-1.23],[.80,.43,.74],C.engine);
cube('engine.head','Головка блока цилиндров','Двигатель',[0,1.09,-1.23],[.82,.13,.75],C.chrome);
cube('engine.cover','Клапанная крышка','Двигатель',[0,1.20,-1.23],[.72,.09,.63],C.body2);
cyl('engine.crankshaft','Коленчатый вал','Двигатель',[0,.67,-1.23],.063,.82,C.chrome,'z');
for(let i=0;i<4;i++){
const z=-1.50+i*.18;
cyl('engine.piston.'+i,'Поршень','Двигатель',[0,.93,z],.093,.16,C.chrome);
line('engine.rod.'+i,'Шатун','Двигатель',[[0,.91,z],[0,.69,z]],C.brake,.035);
cyl('engine.spark.'+i,'Свеча зажигания','Электрика',[.22,1.25,z],.028,.18,C.lights);
}
cyl('engine.fan','Вентилятор охлаждения','Подкапотное пространство',[0,1.0,-1.79],.19,.046,C.chrome,'z');
cube('engine.radiator','Радиатор','Подкапотное пространство',[0,.99,-1.85],[.83,.39,.11],C.metal);
cube('engine.airfilter','Воздушный фильтр','Подкапотное пространство',[0,1.34,-1.20],[.41,.14,.38],C.rubber);
cube('engine.battery','Аккумуляторная батарея','Электрика',[.55,.93,-1.40],[.31,.3,.42],C.rubber);
cyl('engine.generator','Генератор','Электрика',[-.52,.84,-1.40],.16,.34,C.chrome,'z');
cube('fuel.carb','Карбюратор','Топливная система',[.3,1.19,-1.20],[.22,.19,.25],C.metal);
line('cool.hose','Патрубок охлаждения','Подкапотное пространство',[[.25,1.22,-1.55],[.20,1.12,-1.78]],C.rubber,.042);
cube('fuel.tank','Топливный бак','Топливная система',[0,.42,1.55],[.8,.22,.55],C.metal);
line('fuel.line','Топливная магистраль','Топливная система',[[.34,.44,1.45],[.30,.46,.2],[.30,.70,-1.15]],C.metal,.015);
// Gearbox, drivetrain and rear axle
cube('transmission.clutch','Картер сцепления','Трансмиссия',[0,.65,-.78],[.46,.37,.32],C.metal);
cube('transmission.gearbox','Корпус коробки передач','Трансмиссия',[0,.58,-.30],[.44,.29,.7],C.engine);
for(let i=0;i<4;i++)cyl('transmission.gear.'+i,'Шестерня коробки передач','Трансмиссия',[i%2?-.10:.10,.58,-.51+i*.15],.12+i*.014,.055,C.chrome,'z',20);
cyl('transmission.shaft','Первичный и вторичный валы КПП','Трансмиссия',[0,.57,-.31],.037,.75,C.chrome,'z');
line('transmission.driveshaft','Карданный вал','Трансмиссия',[[0,.55,.17],[0,.46,1.31]],C.chrome,.07);
cube('transmission.diff','Редуктор заднего моста','Трансмиссия',[0,.43,1.31],[.45,.32,.35],C.engine);
cyl('transmission.axle','Задний мост','Трансмиссия',[0,.43,1.31],.082,1.64,C.chrome,'x');
line('exhaust.pipe','Приёмная и выпускная трубы','Выпускная система',[[-.25,.68,-1.1],[-.38,.42,-.6],[-.4,.32,.7],[-.3,.32,1.81]],C.metal,.04);
cube('exhaust.muffler','Основной глушитель','Выпускная система',[-.36,.33,1.09],[.25,.18,.49],C.engine);
line('steering.link','Рулевая тяга','Рулевое управление',[[-.61,.50,-1.30],[.6,.50,-1.30]],C.chrome,.035);
cube('heat.heater','Корпус отопителя','Отопление и вентиляция',[.4,1.09,-.84],[.35,.23,.22],C.metal);
line('electric.harness','Жгут проводки','Электрика',[[.57,1.15,-1.40],[.58,1.20,-1.05],[.67,1.10,-.6],[.6,1.0,.7]],0xd8ba82,.014);
const modelBox=new THREE.Box3().setFromObject(root); // used for approximate framing
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
let catalog=[],selected=null,xray=false,isolate=false,clickStart=null,highlighted=[],initialMaterials=new Map();
const categoryFallback={
'Кузов':['body.shell','body.cabin','body.hood','body.trunk'],
'Интерьер салона':['interior.seat.-0.36','interior.dashboard','interior.rearseat'],
'Трансмиссия':['transmission.gearbox','transmission.clutch','transmission.driveshaft','transmission.diff'],
'Двигатель':['engine.block','engine.head','engine.crankshaft','engine.cover'],
'Подкапотное пространство':['engine.radiator','engine.battery','engine.airfilter'],
'Электрика':['engine.battery','engine.generator','light.head.-0.65','electric.harness'],
'Рулевое управление':['interior.steering','steering.link'],
'Тормозная система':['brake.-1.front','brake.1.front','brake.-1.rear'],
'Подвеска':['susp.spring.-1.front','susp.arm.1.front','susp.shock.-1.rear'],
'Колёса, ступицы и шины':['wheel.tire.-1.front','wheel.tire.1.front','wheel.tire.-1.rear','wheel.tire.1.rear'],
'Топливная система':['fuel.tank','fuel.line','fuel.carb'],
'Выпускная система':['exhaust.pipe','exhaust.muffler'],
'Отопление и вентиляция':['heat.heater']
};
const locationRules=[
[/капот/i,['body.hood']],
[/крышк[аи] багажник/i,['body.trunk']],
[/лобов.*стекл/i,['glass.windshield']],
[/задн.*стекл/i,['glass.rear']],
[/передн.*лев.*крыл/i,['body.frontwing.left']],
[/передн.*прав.*крыл/i,['body.frontwing.right']],
[/задн.*лев.*крыл/i,['body.rearwing.left']],
[/задн.*прав.*крыл/i,['body.rearwing.right']],
[/передн.*бампер/i,['body.frontbumper']],
[/задн.*бампер/i,['body.rearbumper']],
[/реш[её]тк.*радиатор/i,['body.grille']],
[/несущ.*кузов|каркас кузова/i,['body.shell','body.cabin']],
[/крыш[аеи]$/i,['body.roof']],
[/коленчат.*вал/i,['engine.crankshaft']],
[/поршн/i,['engine.piston.0','engine.piston.1','engine.piston.2','engine.piston.3']],
[/шатун/i,['engine.rod.0','engine.rod.1','engine.rod.2','engine.rod.3']],
[/блок цилиндр/i,['engine.block']],
[/головк.*блок/i,['engine.head']],
[/клапанн.*крышк/i,['engine.cover']],
[/свеч[аи]/i,['engine.spark.0','engine.spark.1','engine.spark.2','engine.spark.3']],
[/карбюратор/i,['fuel.carb']],
[/бензобак|топливн.*бак/i,['fuel.tank']],
[/топливн.*магистрал/i,['fuel.line']],
[/радиатор/i,['engine.radiator']],
[/аккумулятор/i,['engine.battery']],
[/генератор/i,['engine.generator']],
[/воздушн.*фильтр/i,['engine.airfilter']],
[/корпус.*коробк|картер.*коробк/i,['transmission.gearbox']],
[/шестерн/i,['transmission.gear.0','transmission.gear.1','transmission.gear.2','transmission.gear.3']],
[/карданн.*вал/i,['transmission.driveshaft']],
[/дифференциал|редуктор.*мост/i,['transmission.diff']],
[/задн.*мост/i,['transmission.axle']],
[/сцеплени/i,['transmission.clutch']],
[/глушител/i,['exhaust.muffler']],
[/выхлоп|выпускн.*труб/i,['exhaust.pipe']],
[/рулев.*колесо|руль\b/i,['interior.steering']],
[/рулев.*колонк/i,['interior.steering.column']],
[/рулев.*тяг/i,['steering.link']],
[/щиток прибор|торпедо|панел.*прибор/i,['interior.dashboard']],
[/сидень|диван/i,['interior.seat.-0.36','interior.seat.0.36','interior.rearseat']],
[/рычаг переключени/i,['interior.shifter']],
[/передн.*тормозн.*диск/i,['brake.-1.front','brake.1.front']],
[/задн.*тормозн.*барабан/i,['brake.-1.rear','brake.1.rear']],
[/амортизатор/i,['susp.shock.-1.front','susp.shock.1.front','susp.shock.-1.rear','susp.shock.1.rear']],
[/пружин.*подвеск/i,['susp.spring.-1.front','susp.spring.1.front']],
[/лев.*фар/i,['light.head.-0.65']],
[/прав.*фар/i,['light.head.0.65']],
[/фар/i,['light.head.-0.65','light.head.0.65']],
[/шины|кол[её]с.*диск|кол[её]с[ао]|ступиц/i,['wheel.tire.-1.front','wheel.tire.1.front','wheel.tire.-1.rear','wheel.tire.1.rear']]
];
function resolve(item){for(const [re,ids] of locationRules){if(re.test(item.name)){const found=ids.filter(x=>parts.has(x));if(found.length)return {ids:found,exact:true};}}
if(item.section.toLowerCase().includes('двер')){const ids=['body.door.front.left','body.door.front.right','body.door.rear.left','body.door.rear.right'];return{ids,exact:false};}
return{ids:(categoryFallback[item.category]||['body.shell']).filter(id=>parts.has(id)),exact:false};}
function flatten(data){return data.flatMap((cat,c)=>cat.sections.flatMap((sec,s)=>sec.items.map((name,i)=>({id:c+'-'+s+'-'+i,category:cat.title,section:sec.name,name,removability:sec.removability?.[name]||sec.gameplay||'unspecified',gameplayDecision:sec.gameplayDecision||'',depth:sec.depth||'',index:c}))))}
const labels={fixed:'Несъёмная / основа',part:'Съёмная',use:'Используется, не снимается',unspecified:'Съёмность требует уточнения',assembly:'Единая сборка',unknown:'Не утверждено'};
function setButton(el,on){el.classList.toggle('on',on);el.setAttribute('aria-pressed',String(on))}
function updateScene(){
const chosen=new Set(selected?.resolved?.ids||[]),chosenSystem=selected?.category;
root.traverse(obj=>{
 if(!obj.isMesh)return;
 if(!initialMaterials.has(obj))initialMaterials.set(obj,obj.material);
 const base=initialMaterials.get(obj),isChosen=chosen.has(obj.userData.partId),isSystem=obj.userData.category===chosenSystem;
 obj.visible=!isolate||!selected||isChosen;
 if(isChosen){const bright=base.clone();bright.color.set(C.highlight);bright.emissive.set(0x674917);bright.emissiveIntensity=.55;bright.transparent=false;bright.opacity=1;bright.depthWrite=true;obj.material=bright;}
 else if(xray){const ghost=base.clone();ghost.transparent=true;ghost.opacity=(isSystem?.21:.095);ghost.depthWrite=false;ghost.metalness=0;obj.material=ghost;}
 else obj.material=base;
});
}
function choose(item){
 selected={...item,resolved:resolve(item)};updateScene();
 titleEl.textContent=item.name;metaEl.textContent=item.category+' / '+item.section;
 statusEl.classList.toggle('warn',!selected.resolved.exact);
 statusEl.textContent=selected.resolved.exact?'Выделен геометрический аналог':'Показан связанный агрегат (схема)';
 const state=labels[item.removability]||'Съёмность уточняется';
 const matched=selected.resolved.ids.map(id=>parts.get(id)?.name).filter(Boolean);
 descEl.textContent='Статус в игровом каталоге: '+state+'. '+(selected.resolved.exact?'В 3D отмечена схематичная геометрия этой детали или группы однотипных деталей.':'Точной отдельной 3D-геометрии этой позиции пока нет. Выделен ближайший связанный узел: '+[...new Set(matched)].join(', ')+'.')+(item.gameplayDecision?' '+item.gameplayDecision:'');
 document.querySelectorAll('.part.active').forEach(b=>b.classList.remove('active'));
 const b=document.querySelector('[data-part="'+item.id+'"]');if(b)b.classList.add('active');
}
function paintList(filter=''){
partsEl.replaceChildren();let shown=0;const term=filter.toLocaleLowerCase('ru');
for(const [c,cat] of catalog.entries()){
 const group=document.createElement('details');group.className='group';if(term||c===0)group.open=true;
 const visible=cat.sections.flatMap((section,s)=>section.items.map((name,i)=>({name,id:c+'-'+s+'-'+i,section,cat}))).filter(it=>(it.name+' '+it.section.name+' '+it.cat.title).toLocaleLowerCase('ru').includes(term));
 if(!visible.length)continue;
 shown+=visible.length;const sum=document.createElement('summary');sum.innerHTML='<span class="num">'+String(c+1).padStart(2,'0')+'</span><span></span><span class="chev">›</span>';sum.children[1].textContent=cat.title;group.appendChild(sum);
 for(const [s,section] of cat.sections.entries()){
  const items=section.items.map((name,i)=>({name,id:c+'-'+s+'-'+i})).filter(it=>(it.name+' '+section.name+' '+cat.title).toLocaleLowerCase('ru').includes(term));if(!items.length)continue;
  const h=document.createElement('div');h.className='subhead';h.textContent=section.name;group.appendChild(h);
  for(const item of items){const b=document.createElement('button');b.className='part'+(selected?.id===item.id?' active':'');b.type='button';b.dataset.part=item.id;b.textContent=item.name;b.addEventListener('click',()=>choose(lookup.find(x=>x.id===item.id)));group.appendChild(b)}
 }
 partsEl.appendChild(group);
}
if(!shown){const p=document.createElement('div');p.className='none';p.textContent='По этому запросу детали не найдены.';partsEl.appendChild(p)}
countEl.textContent='Показано '+shown+' из '+lookup.length+' позиций · '+catalog.length+' категорий';
}
search.addEventListener('input',()=>paintList(search.value));
xrayBtn.addEventListener('click',()=>{xray=!xray;setButton(xrayBtn,xray);updateScene()});
isolateBtn.addEventListener('click',()=>{isolate=!isolate;setButton(isolateBtn,isolate);updateScene()});
resetBtn.addEventListener('click',()=>{selected=null;xray=false;isolate=false;setButton(xrayBtn,false);setButton(isolateBtn,false);search.value='';paintList();updateScene();camera.position.set(6,4.6,7.5);controls.target.set(0,.83,0);controls.update();titleEl.textContent='Выберите деталь';metaEl.textContent='Все категории доступны в списке слева.';statusEl.textContent='Схематический просмотр';descEl.textContent='Поверните модель мышью или пальцем. Выберите деталь в списке, чтобы подсветить её или соответствующий агрегат.'});
renderer.domElement.addEventListener('pointerdown',e=>{clickStart=[e.clientX,e.clientY]});
renderer.domElement.addEventListener('pointerup',e=>{
 if(!clickStart||Math.hypot(clickStart[0]-e.clientX,clickStart[1]-e.clientY)>5)return;
 const box=renderer.domElement.getBoundingClientRect();pointer.x=((e.clientX-box.left)/box.width)*2-1;pointer.y=-((e.clientY-box.top)/box.height)*2+1;ray.setFromCamera(pointer,camera);
 const hits=ray.intersectObjects(root.children,true);const first=hits.find(h=>h.object.userData.partId);if(!first)return;
 const id=first.object.userData.partId,name=first.object.userData.partName,category=first.object.userData.category;
 const candidate=lookup.find(i=>i.category===category&&i.name.toLowerCase()===name.toLowerCase()) ||lookup.find(i=>i.category===category&&i.name.toLowerCase().includes(name.toLowerCase()))||lookup.find(i=>i.category===category&&resolve(i).ids.includes(id))||lookup.find(i=>i.category===category);
 if(candidate)choose(candidate);
});
const resize=new ResizeObserver(()=>{const w=Math.max(host.clientWidth,1),h=Math.max(host.clientHeight,1);camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);});resize.observe(host);
document.addEventListener('visibilitychange',()=>{if(document.hidden)controls.update()});
renderer.setAnimationLoop(()=>{if(document.hidden)return;controls.update();renderer.render(scene,camera)});
try{
 const response=await fetch('./assets/moskvich-3d/catalog.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);
 catalog=await response.json();lookup.push(...flatten(catalog));paintList();loading.remove();choose(lookup.find(p=>p.name==='Капот')||lookup[0]);
}catch(err){loading.textContent='Не удалось загрузить каталог: '+err.message+'; проверьте, что сайт открыт через HTTP(S).';console.error(err);}
