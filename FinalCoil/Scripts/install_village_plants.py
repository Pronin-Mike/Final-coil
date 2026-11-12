import unreal,json,os,shutil,math,time
from editor_toolset.toolsets.actor import ActorTools
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/VillagePlants';Q=R+'/Review/VillagePlants';os.makedirs(Q,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert ed.get_editor_world().get_name()=='L_Berezovka_Terrain';assert levels.save_current_level()
backup=R+'/Saved/Backups/BeforeVillagePlants';os.makedirs(backup,exist_ok=True)
if not os.path.exists(backup+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',backup+'/L_Berezovka_Terrain.umap')
def snapshot():
 out={}
 for a in actors.get_all_level_actors():
  n=a.get_actor_label()
  if n.startswith('VEG_Village_'):continue
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
  cs=a.get_components_by_class(unreal.StaticMeshComponent)
  out[n]={'p':[p.x,p.y,p.z],'r':[r.pitch,r.yaw,r.roll],'s':[s.x,s.y,s.z],'materials':[[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())] for c in cs]}
 return out
before=snapshot();json.dump(before,open(Q+'/existing_before.json','w'),indent=1)
plan=json.load(open(R+'/SourceArt/VillagePlants/planting.json'));AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
def material(name,root,tip,wind,kind):
 m=unreal.load_asset(D+'/'+name)
 if not m:m=AT.create_asset(name,D,unreal.Material,unreal.MaterialFactoryNew())
 L.delete_all_material_expressions(m);m.set_editor_property('two_sided',True)
 if kind=='grass':m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('opacity_mask_clip_value',.35)
 if kind!='bark':m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
 def node(cls,x,y):return L.create_material_expression(m,cls,x,y)
 def cn(a,p,b,i):assert L.connect_material_expressions(a,p,b,i)
 uv=node(unreal.MaterialExpressionTextureCoordinate,-800,-300);rand=node(unreal.MaterialExpressionPerInstanceRandom,-800,-100);pos=node(unreal.MaterialExpressionWorldPosition,-800,100);tm=node(unreal.MaterialExpressionTime,-800,300)
 def inp(n):v=unreal.CustomInput();v.set_editor_property('input_name',n);return v
 color=node(unreal.MaterialExpressionCustom,-300,-250);color.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);color.set_editor_property('inputs',[inp('UV'),inp('R')])
 code='float3 a=float3(%f,%f,%f), b=float3(%f,%f,%f); float t=saturate(UV.y); float vein=1-.14*exp(-abs(UV.x-.5)*40); return lerp(a,b,smoothstep(.05,.95,t))*vein*(.82+.32*R);'%(*root,*tip)
 color.set_editor_property('code',code);cn(uv,'',color,'UV');cn(rand,'',color,'R');assert L.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 if kind=='grass':
  mask=node(unreal.MaterialExpressionCustom,-300,-450);mask.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT1);mask.set_editor_property('inputs',[inp('UV'),inp('R')])
  mask.set_editor_property('code','float x=UV.x*8;float c=floor(x);float r=frac(sin(c*127.1+R*317.7)*43758.5453);float h=.48+.52*r;float t=UV.y/h;float center=(r-.5)*.38+sin(t*(1.6+r)+r*6.28)*.22*t;float d=abs(frac(x)-.5-center);float w=.12*pow(saturate(1-t),.65);float aa=max(.006,fwidth(x)*.55);return (1-smoothstep(w-aa,w+aa,d))*(1-smoothstep(.98,1,t));')
  cn(uv,'',mask,'UV');cn(rand,'',mask,'R');L.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK)
 ss=node(unreal.MaterialExpressionConstant3Vector,-300,-50);ss.set_editor_property('constant',unreal.LinearColor(*(c*.65 for c in tip),1));L.connect_material_property(ss,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
 rough=node(unreal.MaterialExpressionConstant,-300,100);rough.set_editor_property('r',.82 if kind=='bark' else .72);L.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 spec=node(unreal.MaterialExpressionConstant,-300,200);spec.set_editor_property('r',.2);L.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
 w=node(unreal.MaterialExpressionCustom,-300,400);w.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);w.set_editor_property('inputs',[inp('P'),inp('T'),inp('UV')]);w.set_editor_property('code','float a=sin(T*1.45+P.x*.004+P.y*.002)+.3*sin(T*2.7+P.y*.011);return float3(a,a*.42,0)*pow(saturate(UV.y),2)*'+str(wind)+';')
 cn(pos,'',w,'P');cn(tm,'',w,'T');cn(uv,'',w,'UV');L.connect_material_property(w,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
 for expr in L.get_material_expressions(m):
  if isinstance(expr,unreal.MaterialExpressionCustom):expr.set_editor_property('code','UV.y=1-UV.y;\n'+expr.get_editor_property('code'))
 errors=L.recompile_material(m);assert not errors,str(errors);A.save_loaded_asset(m);return m
if not globals().get("REUSE_PLANT_ASSETS",False):
 mats=[material('M_Grass_Green',(.022,.040,.009),(.13,.19,.038),2.0,'grass'),material('M_Grass_Dry',(.035,.040,.012),(.22,.19,.070),2.6,'grass'),material('M_Shrub_Leaf',(.022,.055,.010),(.075,.16,.028),.9,'leaf'),material('M_Shrub_Bark',(.045,.032,.020),(.085,.065,.040),0,'bark')]
 meshes=[]
 for i,rec in enumerate(plan['meshes']):
  name=rec['name'];task=unreal.AssetImportTask();task.filename=R+'/SourceArt/VillagePlants/'+name+'.obj';task.destination_path=D;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
  AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/'+name);assert mesh
  ns=mesh.get_editor_property('nanite_settings');ns.enabled=False;mesh.set_editor_property('nanite_settings',ns)
  for j,slot in enumerate(mesh.get_editor_property('static_materials')):
   slotname=str(slot.get_editor_property('material_slot_name')).lower()
   mat=mats[3] if 'bark' in slotname else mats[2] if i>=4 else mats[1] if i in [1,3] else mats[0]
   mesh.set_material(j,mat)
  A.save_loaded_asset(mesh);meshes.append(mesh)
else:meshes=[unreal.load_asset(D+"/"+r["name"]) for r in plan["meshes"]]
created=[]
for i,(mesh,points) in enumerate(zip(meshes,plan['plants'])):
 name='VEG_Village_'+plan['meshes'][i]['name'].removeprefix('SM_Village')
 a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==name),None)
 if not a:
  a=actors.spawn_actor_from_class(unreal.Actor,unreal.Vector(0,0,0));a.set_actor_label(name);a.set_folder_path('90_Vegetation/VillageOnly')
  c=ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Plants')
 else:
  c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
  if c:c.clear_instances()
  else:c=ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Plants')
 c.set_static_mesh(mesh);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False)
 c.set_editor_property('cast_shadow',i>=4);c.set_cull_distances(5000 if i<4 else 22000,9000 if i<4 else 32000)
 transforms=[unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(s,s,s)) for x,y,z,yaw,s in points]
 c.add_instances(transforms,False,True,False)
 assert c.get_instance_count()==len(points),(name,c.get_instance_count(),len(points))
 if points:
  q=c.get_instance_transform(0,True).rotation
  assert abs(q.x)<.00001 and abs(q.y)<.00001,'Plant rotated off vertical: '+name
 created.append({'actor':name,'count':len(points),'mesh':mesh.get_path_name(),'collision':'NoCollision','cull_end_cm':9000 if i<4 else 32000})
after=snapshot();assert before==after,'Existing actor changed unexpectedly'
for path in A.list_assets(D,recursive=True,include_folder=False):A.save_asset(path,only_if_is_dirty=False)
assert levels.save_current_level()
json.dump({'instances':created,'existing_actors_unchanged':len(before),'plots_and_forest_unchanged':True,'compile_errors':[],'constraints':plan['constraints'],'timestamp':time.time()},open(Q+'/installed.json','w'),indent=2)
unreal.log('VILLAGE_PLANTS_INSTALLED_OK '+str(sum(p['count'] for p in created)))
