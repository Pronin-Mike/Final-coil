"""Apply the prepared G01 move. May run in editor or UE Python commandlet."""
import unreal,json,math,sys,os,shutil,traceback
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/HeroForestMove';Q=R+'/Review/HeroForestMove';D='/Game/FinalCoil/World/HeroForestMove';B=R+'/../.publishing/hero-forest-before'
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 assert LV.save_current_level();os.makedirs(B,exist_ok=True)
 if not os.path.exists(B+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',B+'/L_Berezovka_Terrain.umap')
 P=json.load(open(S+'/plan.json'));meta=json.load(open(S+'/prepared.json'));h=meta['new_plot'];delta=meta['delta_cm'];dz=h['z']-meta['old_plot']['z'];by={a.get_actor_label():a for a in E.get_all_level_actors()};baseline={a['label']:a for a in json.load(open(Q+'/baseline.json'))};A.make_directory(D)
 def dup(src,name):return unreal.load_asset(D+'/'+name) or A.duplicate_asset(src,D+'/'+name)
 master=dup('/Game/FinalCoil/World/CompactVillage/M_CompactSurface','M_HeroForestSurface');n=next(n for n in L.get_material_expressions(master) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5)
 code=n.get_editor_property('code');oldfn=open(S+'/Functions_before.hlsl').read();newfn=open(S+'/Functions.hlsl').read()
 assert oldfn in code or newfn in code,'Ground source functions do not match'
 if oldfn in code:code=code.replace(oldfn,newfn)
 n.set_editor_property('code',code);errors=L.recompile_material(master);assert not errors,str(errors);assert A.save_loaded_asset(master)
 mi=dup('/Game/FinalCoil/World/CompactVillage/MI_CompactSurface','MI_HeroForestSurface');L.set_material_instance_parent(mi,master);L.update_material_instance(mi);assert A.save_loaded_asset(mi)
 def import_mesh(name):
  task=unreal.AssetImportTask();task.filename=S+'/'+name+'.obj';task.destination_path=D;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/'+name);assert mesh,name
  ns=mesh.get_editor_property('nanite_settings');ns.enabled=False;mesh.set_editor_property('nanite_settings',ns);body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert A.save_loaded_asset(mesh);return mesh
 mesh=import_mesh('SM_HeroForestTerrain');terrain=by['TERRAIN_Terrain'];terrain.static_mesh_component.set_static_mesh(mesh);terrain.static_mesh_component.set_material(0,mi);mesh.set_material(0,mi);assert A.save_loaded_asset(mesh)
 moved=[]
 for name,a in by.items():
  if name.startswith(('G01_','POI_G01_','MARK_G01_')):
   r=baseline[name];p=r['p'];a.set_actor_location(unreal.Vector(p[0]+delta[0],p[1]+delta[1],p[2]+dz),False,False);moved.append(name)
 for name,a in by.items():
  if name.startswith('DIM_StopToHero_'):
   a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
   for comp in a.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 sys.path.insert(0,R+'/Scripts');import terrain_profile as T;T.GRID=json.load(open(S+'/heightfield.json'))
 outline=by['PLOT10_G01_1000m2'];comp=outline.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);outline.set_actor_location(unreal.Vector(),False,False);comp.clear_instances();ts=[]
 for p,q in zip(h['corners'],h['corners'][1:]+h['corners'][:1]):
  count=math.ceil(math.dist(p,q)/40)
  for i in range(count):
   x,y=p[0]+(q[0]-p[0])*i/count,p[1]+(q[1]-p[1])*i/count;xx,yy=p[0]+(q[0]-p[0])*(i+1)/count,p[1]+(q[1]-p[1])*(i+1)/count;z,zz=T.height(x,y)+15,T.height(xx,yy)+15;length=math.sqrt((xx-x)**2+(yy-y)**2+(zz-z)**2)
   ts.append(unreal.Transform(location=unreal.Vector((x+xx)/2,(y+yy)/2,(z+zz)/2),rotation=unreal.Rotator(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=unreal.Vector((length+.15)/100,.75,.02)))
 comp.add_instances(ts,False,True,False)
 # Remove only foliage roots now occupied by this plot or its new access.
 def distance(x,y,r):
  p,q=r['p'],r['q'];dx,dy=q[0]-p[0],q[1]-p[1];t=max(0,min(1,((x-p[0])*dx+(y-p[1])*dy)/(dx*dx+dy*dy)));return math.hypot(x-p[0]-t*dx,y-p[1]-t*dy)
 def on_site(x,y):
  dx,dy=x-h['center'][0],y-h['center'][1];c,s=h['c'],h['s']
  return (abs(c*dx+s*dy)<h['hx']+70 and abs(-s*dx+c*dy)<h['hy']+70) or any(distance(x,y,r)<r['width']/2+25 for r in P['walks'] if r['name'].startswith('G01_'))
 trimmed={}
 for name,a in by.items():
  if not name.startswith('VEG_'):continue
  comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
  if not comp:continue
  keep=[];removed=0
  for i in range(comp.get_instance_count()):
   t=comp.get_instance_transform(i,True);p=t.translation
   if on_site(p.x,p.y):removed+=1
   else:keep.append(t)
  if removed:comp.clear_instances();comp.add_instances(keep,False,True,False);trimmed[name]=removed
 parent=unreal.load_asset('/Game/FinalCoil/Vehicles/Moskvich412/M_VehicleBlockout');assert parent
 mats={}
 for name,color in [('Bark',[.16,.105,.065]),('Pine',[.075,.19,.105]),('Leaf',[.18,.29,.105])]:
  m=unreal.load_asset(D+'/MI_'+name) or AT.create_asset('MI_'+name,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());L.set_material_instance_parent(m,parent);L.set_material_instance_vector_parameter_value(m,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(m,'Metallic',0);L.set_material_instance_scalar_parameter_value(m,'Roughness',.95);L.update_material_instance(m);assert A.save_loaded_asset(m);mats[name]=m
 from editor_toolset.toolsets.actor import ActorTools
 trees=json.load(open(S+'/trees.json'))
 for kind,name in enumerate(['Pine','Leaf']):
  mesh=import_mesh('SM_Forest'+name+'_Blockout')
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   slotname=str(slot.get_editor_property('imported_material_slot_name'));mesh.set_material(i,mats['Bark' if 'Bark' in slotname else name])
  assert A.save_loaded_asset(mesh)
  label='BLOCKOUT_G01_Forest_'+name;actor=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());actor.set_actor_label(label);actor.set_folder_path('90_Vegetation/HeroForestBlockout');comp=actor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(actor,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Trees');comp.clear_instances();comp.set_static_mesh(mesh);comp.set_collision_profile_name('BlockAll');comp.set_cull_distances(0,150000)
  transforms=[unreal.Transform(location=unreal.Vector(t[0],t[1],t[2]),rotation=unreal.Rotator(pitch=0,yaw=t[3],roll=0),scale=unreal.Vector(t[4],t[4],t[5])) for t in trees if t[6]==kind];comp.add_instances(transforms,False,True,False)
 # Every original non-G01 actor transform stays exact.
 changed=[]
 for name,r in baseline.items():
  if name in moved:continue
  actor=by[name];p=actor.get_actor_location()
  if max(abs(p.x-r['p'][0]),abs(p.y-r['p'][1]),abs(p.z-r['p'][2]))>.001:changed.append(name)
 assert not changed,changed
 assert LV.save_current_level()
 for name in ['plan.json','heightfield.json','Functions.hlsl']:shutil.copy2(S+'/'+name,R+'/SourceArt/CompactVillage/'+name)
 shutil.copy2(S+'/heightfield.json',R+'/SourceArt/Terrain/heightfield.json')
 shutil.copy2(S+'/SM_HeroForestTerrain.obj',R+'/SourceArt/CompactVillage/SM_CompactTerrain.obj')
 # Keep vehicle and fitout helper coordinates consistent for subsequent tasks.
 vp=R+'/Review/Moskvich412/ue_placement.json';v=json.load(open(vp));v.setdefault('previous_position_before_forest_move',v['position_cm']);car=by['G01_Moskvich412'];p=car.get_actor_location();v['position_cm']=[p.x,p.y,p.z];v['floor_top_cm']=p.z;json.dump(v,open(vp,'w'),indent=2)
 fp=R+'/Review/GarageFitout/layout.json';f=json.load(open(fp));f['floor_z']=p.z;json.dump(f,open(fp,'w'),indent=2)
 report=dict(status='saved',translation_cm=[*delta,dz],moved_actors=moved,tree_count=len(trees),plot_area_m2=1000,new_house=h['house'],new_plot_center=h['center'],stop_to_house_m=P['hero_distance_m'],drive=meta['drive'],max_drive_grade_percent=meta['max_drive_grade_percent'],trimmed_foliage=trimmed,other_actor_positions_unchanged=True,terrain_mesh=mesh.get_path_name())
 report['terrain_mesh']=D+'/SM_HeroForestTerrain';json.dump(report,open(Q+'/installed.json','w'),indent=2)
 if os.path.exists(Q+'/install_error.txt'):os.remove(Q+'/install_error.txt')
 unreal.log('HERO_FOREST_MOVE_OK')
except BaseException:
 open(Q+'/install_error.txt','w').write(traceback.format_exc());raise
