import unreal,json,os,re,hashlib,math,time
from editor_toolset.toolsets.actor import ActorTools
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/VillageRoadPass';Q=R+'/Review/VillageRoadPass';S=R+'/SourceArt/VillageRoadPass'
A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
LV.save_current_level();base=json.load(open(Q+'/baseline.json'));plan=json.load(open(S+'/plan.json'));B=plan['bounds'];by={a.get_actor_label():a for a in E.get_all_level_actors()}
# Fingerprints cover the original assets, including lake/forest surfaces and old shaders.
protected={}
for rec in base['actors']:
 for c in rec['components']:
  for path in [c['mesh']]+c['materials']:
   if not path or not path.startswith('/Game/'):continue
   file=R+'/Content/'+path.split('.')[0][6:]+'.uasset'
   if os.path.exists(file):protected[file]=hashlib.sha256(open(file,'rb').read()).hexdigest()
def duplicate(source,name):
 path=D+'/'+name
 obj=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(source,path)
 assert obj,(source,path);return obj
def custom_nodes(m):return [n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionCustom)]
source=unreal.load_asset('/Game/FinalCoil/World/GroundMaterial/M_Berezovka_Ground')
master=duplicate(source.get_path_name(),'M_Village_Surface')
sc=next(n for n in custom_nodes(source) if len(n.get_editor_property('inputs'))>5);tc=next(n for n in custom_nodes(master) if len(n.get_editor_property('inputs'))>5)
code=sc.get_editor_property('code')
roads=json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes'];lines=[]
for r in roads:
 if r['group']!='Road':continue
 a,b=r['p'],r['q'];lines.append('dd=segment(p,float2(%.5f,%.5f),float2(%.5f,%.5f));if(dd-%.5f<best){best=dd-%.5f;d=dd;w=%.5f;}'%(*a,*b,r['width']/2,r['width']/2,r['width']/2))
fn='float4 villageRoad(float2 p){float best=1e9,d=1e9,w=350,dd;'+''.join(lines)+'return float4(d,w,0,0);}\n'
assert '}; GroundFns g;' in code
code=code.replace('}; GroundFns g;',fn+'}; GroundFns g;')
bounds='float4(%.6f,%.6f,%.6f,%.6f)'%tuple(B)
snippet=open(S+'/SurfaceUpdate.hlsl').read().replace('BOUNDS',bounds)
condition='P.x>%.6f && P.x<%.6f && P.y>%.6f && P.y<%.6f'%(B[0],B[2],B[1],B[3])
replacement='if('+condition+'){\n'+snippet+'\n}\nreturn max(color*Tint,0.002);'
assert 'return max(color*Tint,0.002);' in code
tc.set_editor_property('code',code.replace('return max(color*Tint,0.002);',replacement))
err=L.recompile_material(master);assert not err,str(err);A.save_loaded_asset(master)
mi=duplicate('/Game/FinalCoil/World/GroundMaterial/MI_Berezovka_Terrain','MI_Village_Surface');L.set_material_instance_parent(mi,master);L.update_material_instance(mi);A.save_loaded_asset(mi)
by['TERRAIN_Terrain'].static_mesh_component.set_material(0,mi)
mesh_checks=[]
for kind in ['Road','Path']:
 name='SM_'+kind+'_OutsideVillage';task=unreal.AssetImportTask();task.filename=S+'/'+name+'.obj';task.destination_path=D;task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True
 AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/'+name);assert mesh
 ns=mesh.get_editor_property('nanite_settings');ns.enabled=False;mesh.set_editor_property('nanite_settings',ns)
 body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True)
 c=by['TERRAIN_'+kind].static_mesh_component;old=c.get_material(0);mesh.set_material(0,old);c.set_static_mesh(mesh);c.set_material(0,old);A.save_loaded_asset(mesh)
 mesh_checks.append({'actor':'TERRAIN_'+kind,'material_preserved':old.get_path_name(),'mesh':mesh.get_path_name()})
def inp(n):i=unreal.CustomInput();i.set_editor_property('input_name',n);return i
def grass_material(source_name,name,inside,low):
 src=unreal.load_asset('/Game/FinalCoil/World/VillagePlants/'+source_name);m=duplicate(src.get_path_name(),name)
 s_nodes=custom_nodes(src);t_nodes=custom_nodes(m);assert len(s_nodes)==len(t_nodes)
 for s,t in zip(s_nodes,t_nodes):t.set_editor_property('code',s.get_editor_property('code'))
 mask=next(n for n in t_nodes if 'float x=UV.x*8' in n.get_editor_property('code'))
 names=[str(i.get_editor_property('input_name')) for i in mask.get_editor_property('inputs')]
 if 'P' not in names:mask.set_editor_property('inputs',list(mask.get_editor_property('inputs'))+[inp('P')])
 wp=next(n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionWorldPosition))
 assert L.connect_material_expressions(wp,'',mask,'P')
 code=mask.get_editor_property('code');gate='(('+condition+')?1.0:0.0)';gate=gate if inside else '(1.0-'+gate+')'
 code=code.replace('return (1-smoothstep','return '+gate+'*(1-smoothstep');mask.set_editor_property('code',code)
 if low:
  col=next(n for n in t_nodes if 'float3 a=float3' in n.get_editor_property('code'))
  dry='Dry' in source_name
  colors='float3 a=float3(.030,.045,.012), b=float3(.120,.125,.040);' if dry else 'float3 a=float3(.025,.050,.010), b=float3(.085,.140,.026);'
  col.set_editor_property('code',re.sub(r'float3 a=float3\([^)]*\), b=float3\([^)]*\);',colors,col.get_editor_property('code')))
  wind=next(n for n in t_nodes if 'sin(T*' in n.get_editor_property('code'));wind.set_editor_property('code',re.sub(r'\*[0-9.]+;$','*.32;',wind.get_editor_property('code')))
 err=L.recompile_material(m);assert not err,str(err);A.save_loaded_asset(m);return m
outside_mats=[grass_material('M_Grass_Green','M_Grass_Green_OutsideVillage',False,False),grass_material('M_Grass_Dry','M_Grass_Dry_OutsideVillage',False,False)]
old_checks=[]
for i in range(4):
 a=by['VEG_Village_Grass_%02d'%i];c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);count=c.get_instance_count();samples=[str(c.get_instance_transform(j,True)) for j in [0,count//2,count-1]]
 c.set_material(0,outside_mats[i%2]);assert c.get_instance_count()==count and samples==[str(c.get_instance_transform(j,True)) for j in [0,count//2,count-1]]
 old_checks.append({'actor':a.get_actor_label(),'instances_preserved':count})
local_mats=[grass_material('M_Grass_Green','M_Grass_Low_Green',True,True),grass_material('M_Grass_Dry','M_Grass_Low_Dry',True,True),grass_material('M_Grass_Green','M_Grass_Tall_Green',True,False),grass_material('M_Grass_Dry','M_Grass_Tall_Dry',True,False)]
created=[]
for i,points in enumerate(plan['plants']):
 name=['LowGreen','LowDry','TallGreen','TallDry'][i];label='VEG_VillageRoad_'+name
 a=by.get(label)
 if not a:a=E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('90_Vegetation/VillageRoadPass')
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
 if not c:c=ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Plants')
 c.clear_instances();mesh=unreal.load_asset('/Game/FinalCoil/World/VillagePlants/SM_VillageGrass_%02d'%i);c.set_static_mesh(mesh);c.set_material(0,local_mats[i]);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_editor_property('cast_shadow',False);c.set_editor_property('can_ever_affect_navigation',False);c.set_cull_distances(3500 if i<2 else 6000,6000 if i<2 else 10000)
 transforms=[unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(xy,xy,h)) for x,y,z,yaw,xy,h in points]
 c.add_instances(transforms,False,True,False);assert c.get_instance_count()==len(points);created.append({'name':label,'count':len(points)})
for path in A.list_assets(D,recursive=True,include_folder=False):A.save_asset(path,only_if_is_dirty=False)
assert LV.save_current_level()
for file,digest in protected.items():assert hashlib.sha256(open(file,'rb').read()).hexdigest()==digest,'Original asset changed: '+file
allowed={'TERRAIN_Terrain','TERRAIN_Road','TERRAIN_Path'}|{'VEG_Village_Grass_%02d'%i for i in range(4)}
for rec in base['actors']:
 a=by[rec['label']];p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
 assert [p.x,p.y,p.z]==rec['p'] and [r.pitch,r.yaw,r.roll]==rec['r'] and [s.x,s.y,s.z]==rec['s'],rec['label']
 if rec['label'] not in allowed:
  cs=a.get_components_by_class(unreal.StaticMeshComponent)
  for c,old in zip(cs,rec['components']):assert c.static_mesh.get_path_name()==old['mesh'] and [c.get_material(i).get_path_name() for i in range(c.get_num_materials())]==old['materials'],rec['label']
json.dump({'bounds_cm':B,'new_plants':created,'tall_groups':len(plan['tall_groups']),'old_grass_outside_unchanged':old_checks,'road_geometry':mesh_checks,'all_original_asset_hashes_unchanged':len(protected),'original_transforms_unchanged':len(base['actors']),'compile_errors':[],'time':time.time()},open(Q+'/installed.json','w'),indent=2)
unreal.log('VILLAGE_ROADPASS_INSTALLED_OK')
