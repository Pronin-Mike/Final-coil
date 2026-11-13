"""Continuous shed roof, closed upper walls and cabin-matching garage cladding."""
import unreal,json,math,os,sys,shutil,traceback
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/G01GarageShed';Q=R+'/Review/G01GarageShed';D='/Game/FinalCoil/World/G01GarageShed';B=R+'/../.publishing/g01-garage-before-shed'
for p in [S,Q,B]:os.makedirs(p,exist_ok=True)
try:
 LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();assert LV.save_current_level()
 if not os.path.exists(B+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',B+'/L_Berezovka_Terrain.umap')
 by={a.get_actor_label():a for a in E.get_all_level_actors()}
 def v(p):return [p.x,p.y,p.z]
 def rec(a):
  r=a.get_actor_rotation();return dict(p=v(a.get_actor_location()),r=[r.pitch,r.yaw,r.roll],s=v(a.get_actor_scale3d()))
 if not os.path.exists(Q+'/baseline.json'):json.dump({n:rec(a) for n,a in by.items()},open(Q+'/baseline.json','w'),indent=2)
 baseline=json.load(open(Q+'/baseline.json'));house=json.load(open(R+'/SourceArt/G01HouseV2/house_spec.json'));yaw=house['yaw'];angle=math.radians(yaw);c,s=math.cos(angle),math.sin(angle);ground=house['ground_z'];gp=by['G01_Garage_Floor'].get_actor_location()
 # +X points to garage gate, +Y points away from the attached house.
 def pos(x,y,z):return unreal.Vector(gp.x+c*x-s*y,gp.y+s*x+c*y,ground+z)
 mats={k:unreal.load_asset('/Game/FinalCoil/World/G01HouseV2/MI_'+k) for k in ['Log','Roof','Trim']};assert all(mats.values());A.make_directory(D)
 def hide(a):
  a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
  for comp in a.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 retired=[]
 for name,a in by.items():
  if name in ['G01_Garage_RoofLeft','G01_Garage_RoofRight'] or name.startswith('G01_Garage_LogJoint_'):
   hide(a);a.set_folder_path('99_Archive/G01_Garage_PreShed');retired.append(name)
 structural=['BackWall','LeftWall','RightWallFront','RightWallBack','SideDoorHeader','FrontWallL','FrontWallR','GateHeader']
 for name in structural:by['G01_Garage_'+name].static_mesh_component.set_material(0,mats['Log'])
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder');created=[]
 def box(name,x,y,z,sx,sy,sz,mat='Log',roll=0,collision=True):
  label='G01_Garage_Shed_'+name;a=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());by[label]=a;a.set_actor_label(label);a.set_folder_path('61_G01/GarageShed');a.set_actor_location(pos(x,y,z),False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=roll),False);a.set_actor_scale3d(unreal.Vector(sx/100,sy/100,sz/100));a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,mats[mat]);a.static_mesh_component.set_collision_profile_name('BlockAll' if collision else 'NoCollision');created.append(label);return a
 # One watertight 16cm roof slab, with a 10% fall from house towards outer wall.
 def top(y):return 370-.10*y
 sys.path.insert(0,R+'/Scripts');import terrain_profile as T
 verts=[];faces=[]
 for dz in [-16,0]:
  verts.extend([(x,y,top(y)+dz) for x,y in [(-500,-410),(500,-410),(500,410),(-500,410)]])
 faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 T.write_obj(S+'/SM_GarageShedRoof.obj',verts,faces)
 # Front/back upper wall is a closed sloping prism, not an unfilled gable.
 caps=[(-10,-370,330),(10,-370,330),(10,370,330),(-10,370,330),(-10,-370,top(-370)+1),(10,-370,top(-370)+1),(10,370,top(370)+1),(-10,370,top(370)+1)]
 T.write_obj(S+'/SM_GarageShedCap.obj',caps,faces)
 def import_mesh(name,mat):
  task=unreal.AssetImportTask();task.filename=S+'/'+name+'.obj';task.destination_path=D;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/'+name);assert mesh
  mesh.set_material(0,mats[mat]);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert A.save_loaded_asset(mesh);return mesh
 roof=import_mesh('SM_GarageShedRoof','Roof');cap=import_mesh('SM_GarageShedCap','Log')
 for name,mesh,x in [('Roof',roof,0),('FrontCap',cap,460),('BackCap',cap,-460)]:
  label='G01_Garage_Shed_'+name;a=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());by[label]=a;a.set_actor_label(label);a.set_folder_path('61_G01/GarageShed');a.set_actor_location(pos(x,0,0),False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(1,-1,1));a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');created.append(label)
 for name,y in [('HouseSide',-360),('OuterSide',360)]:
  height=top(y)+1-330;box(name+'_UpperWall',0,y,330+height/2,900,20,height)
 # Roof edge boards close the slab ends and give the roof the same dark outline.
 slope=math.degrees(math.atan(.10))
 for name,x in [('Front',500),('Back',-500)]:box(name+'_Fascia',x,0,362,18,math.hypot(820,82),22,'Roof',roll=slope)
 for name,y in [('High',-410),('Low',410)]:box(name+'_Fascia',0,y,top(y)-8,1018,18,22,'Roof')
 box('WallFlashing',0,-370,409,1000,10,12,'Roof')
 # Same round-log rhythm and material as the house, with true gate/link openings.
 logs=[]
 def append_log(x,y,z,length,axis):
  if length<8:return
  rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=90) if axis=='Y' else unreal.Rotator(pitch=90,yaw=yaw,roll=0)
  logs.append(unreal.Transform(location=pos(x,y,z),rotation=rotation,scale=unreal.Vector(.24,.24,length/100)))
 for row in range(19):
  z=17+row*22
  ymax=min(370,(370-z-12)/.10)
  if ymax>-370:
   append_log(-460,(-370+ymax)/2,z,ymax+370,'Y')
   intervals=[(-370,min(-160,ymax)),(160,ymax)] if z<285 else [(-370,ymax)]
   for lo,hi in intervals:
    if hi>lo:append_log(460,(lo+hi)/2,z,hi-lo,'Y')
  for y in [-360,360]:
   if z+12>top(y):continue
   intervals=[(-450,-170),(-30,450)] if y<0 and z<290 else [(-450,450)]
   for lo,hi in intervals:append_log((lo+hi)/2,y,z,hi-lo,'X')
 from editor_toolset.toolsets.actor import ActorTools
 label='G01_Garage_Shed_LogCladding';a=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/GarageShed');comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Logs');comp.clear_instances();comp.set_static_mesh(cylinder);comp.set_material(0,mats['Log']);comp.set_collision_profile_name('NoCollision');comp.add_instances(logs,False,True,False)
 unchanged=[]
 for name,r in baseline.items():
  if name not in by:continue
  if rec(by[name])!=r:unchanged.append(name)
 assert not unchanged,unchanged
 E.set_selected_level_actors([]);assert LV.save_current_level()
 report=dict(status='saved',center=[gp.x,gp.y,ground],yaw=yaw,roof_size_cm=[1000,820],roof_thickness_cm=16,slope_percent=10,slope_degrees=slope,roof_high_cm=top(-410),roof_low_cm=top(410),slope_direction='from house to outside wall',roof_material=mats['Roof'].get_path_name(),wall_material=mats['Log'].get_path_name(),front_and_back_caps_closed=True,upper_lateral_walls_closed=True,existing_actor_transforms_unchanged=True,retired=retired,created=created,log_instances=len(logs))
 json.dump(report,open(Q+'/built.json','w'),indent=2);json.dump(report,open(S+'/roof_spec.json','w'),indent=2);house['garage_roof']=dict(type='single pitch',fall='away from house',slope_percent=10,roof_material=report['roof_material'],wall_material=report['wall_material']);house['porch_roof_gap_to_garage_cm']=31;json.dump(house,open(R+'/SourceArt/G01HouseV2/house_spec.json','w'),indent=2)
 unreal.log('G01_GARAGE_SHED_SAVED')
except BaseException:
 open(Q+'/error.txt','w').write(traceback.format_exc());raise
