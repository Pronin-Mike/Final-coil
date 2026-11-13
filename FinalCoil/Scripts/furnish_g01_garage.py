"""Simple dimensioned garage furniture. UE cm; u=right, v=depth from gate."""
import unreal,math,json,os,shutil,traceback
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/GarageFitout';D='/Game/FinalCoil/World/GarageFitout'
os.makedirs(Q,exist_ok=True)
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary
 assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
 assert not unreal.EditorLevelLibrary.get_game_world()
 assert LV.save_current_level()
 backup=Q+'/before_actors.json';by={a.get_actor_label():a for a in E.get_all_level_actors()}
 def xyz(p):return [p.x,p.y,p.z]
 def record(a):
  r=a.get_actor_rotation();return dict(p=xyz(a.get_actor_location()),r=[r.pitch,r.yaw,r.roll],s=xyz(a.get_actor_scale3d()))
 if not os.path.exists(backup):
  json.dump({n:record(a) for n,a in by.items()},open(backup,'w'),indent=2)
  shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',R+'/../.publishing/L_Berezovka_before_garage_fitout.umap')
 floor=by['G01_Garage_Floor'];origin=floor.get_actor_location();yaw=floor.get_actor_rotation().yaw;a=math.radians(yaw);c,s=math.cos(a),math.sin(a);z=origin.z+floor.get_actor_scale3d().z*50
 def pos(u,v,h):return unreal.Vector(origin.x+c*v-s*u,origin.y+s*v+c*u,z+h)
 A.make_directory(D);parent=unreal.load_asset('/Game/FinalCoil/Vehicles/Moskvich412/M_VehicleBlockout');assert parent
 mats={}
 for name,color,metal,rough in [('Frame',[.13,.20,.17],.55,.65),('Shelf',[.30,.24,.15],0,.8),('Panel',[.22,.28,.29],.45,.75),('Tools',[.34,.37,.39],.7,.55),('Box',[.35,.23,.12],0,.95)]:
  mi=unreal.load_asset(D+'/MI_'+name) or AT.create_asset('MI_'+name,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
  L.set_material_instance_parent(mi,parent);L.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(mi,'Metallic',metal);L.set_material_instance_scalar_parameter_value(mi,'Roughness',rough);L.update_material_instance(mi);assert A.save_loaded_asset(mi);mats[name]=mi
 mats['Rubber']=unreal.load_asset('/Game/FinalCoil/Vehicles/Moskvich412/MI_Rubber');mats['Handle']=mats['Tools']
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder');created=[]
 def shape(name,u,v,h,su,sv,sh,mat,mesh=None,rot=None,collide=True,group=None):
  label='G01_Fitout_'+name;actor=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());by[label]=actor;actor.set_actor_label(label);actor.set_folder_path('61_G01/GarageFitout/'+(group or name.split('_')[0]));actor.set_actor_location(pos(u,v,h),False,False);actor.set_actor_rotation(rot or unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);actor.set_actor_scale3d(unreal.Vector(sv/100,su/100,sh/100));comp=actor.static_mesh_component;comp.set_static_mesh(mesh or cube);comp.set_material(0,mats[mat]);comp.set_collision_profile_name('BlockAll' if collide else 'NoCollision');actor.tags=[unreal.Name('GarageFitout')];created.append(label);return actor
 def box(name,u,v,h,su,sv,sh,mat,**kw):return shape(name,u,v,h,su,sv,sh,mat,**kw)
 def legs(group,u,v,su,sv,height):
  for i,du in enumerate([-su/2+4,su/2-4]):
   for j,dv in enumerate([-sv/2+4,sv/2-4]):box(group+'_Leg%d%d'%(i,j),u+du,v+dv,height/2,4,4,height,'Frame')
 # A: rear-left assembly table, 180 wide x 80 deep, 85 high.
 box('A_TableTop',-230,400,82.5,180,80,5,'Shelf');legs('A',-230,400,180,80,80)
 box('A_LowerShelf',-230,400,20,170,68,4,'Shelf')
 # Large readable engine/gearbox placeholders, no fine surface detail.
 box('A_EngineBlock',-258,400,104,48,56,38,'Tools');box('A_ValveCover',-258,400,127,35,49,8,'Panel')
 box('A_Gearbox',-188,402,98,28,51,26,'Tools');box('A_EngineSump',-258,400,89,36,43,8,'Frame')
 # B: rear-wall spare-parts shelving, 280 wide x 60 deep x 210 high.
 legs('B',90,410,280,60,210)
 for i,h in enumerate([12,72,132,202]):box('B_Shelf%d'%i,90,410,h,280,60,4,'Shelf')
 for i,(u,v,h,su,sv,sh) in enumerate([(-5,411,32,54,40,36),(64,411,27,44,42,26),(155,411,34,65,44,40),(-18,409,89,58,41,30),(75,410,91,52,43,34),(176,410,86,43,40,24),(-6,409,151,66,40,34),(94,410,149,42,38,30),(183,408,150,56,42,32)]):
  box('B_PartsBox%d'%i,u,v,h,su,sv,sh,'Box');box('B_Label%d'%i,u,v-sv/2-.2,h,18,.5,8,'Panel',collide=False)
 # C: workbench against left wall, 260 along wall x 80 deep x 90 high.
 box('C_Worktop',-300,80,87,80,260,6,'Shelf');legs('C',-300,80,80,260,84)
 box('C_Stretcher',-300,80,19,65,247,4,'Frame');box('C_ToolPanel',-344,80,155,3,260,110,'Panel')
 # A few recognisable large silhouettes on the tool board.
 for i,dv in enumerate([-100,-70,-38,0,36,73,105]):
  h=154+(i%2)*12;box('C_ToolStem%d'%i,-340.5,80+dv,h,3,3,26,'Tools',collide=False)
  box('C_ToolHead%d'%i,-339.8,80+dv,h+14,4,13 if i<4 else 19,6,'Tools',collide=False)
 box('C_ViseBase',-282,-11,94,25,25,8,'Frame');box('C_ViseJaws',-280,-11,106,18,21,16,'Tools')
 # D: right wall tyre stand 140 along wall x 70 deep x 170 high.
 # Side door is centred at v=100, spanning v=45..155; rack starts v=210.
 legs('D',305,280,70,140,170)
 for i,h in enumerate([10,84,164]):box('D_RackShelf%d'%i,305,280,h,70,140,4,'Frame')
 # Four upright tyres on lower deck. Cylinder axis parallel to wall (v).
 wheel_rot=unreal.Rotator(pitch=90,yaw=yaw,roll=0)
 for i,v in enumerate([232,264,296,328]):
  # Cylinder default Z is rotated into depth axis. Scale z=tyre width, x/y=diameter.
  tire=shape('D_Tyre%d'%i,305,v,42,60,60,17,'Rubber',mesh=cylinder,rot=wheel_rot)
  for j,dv in enumerate([-8.7,8.7]):shape('D_Rim%d_%d'%(i,j),305,v+dv,42,29,29,1.2,'Tools',mesh=cylinder,rot=wheel_rot,collide=False)
 for i,v in enumerate([244,310]):box('D_StorageBox%d'%i,305,v,104,45,46,36,'Box')
 # E: cabinet at left near gate, 80 along wall x 45 deep x 95 high.
 box('E_Cabinet',-315,-280,47.5,45,80,95,'Frame');box('E_CabinetTop',-315,-280,96.5,45,80,3,'Shelf')
 for i,v in enumerate([-300,-260]):
  box('E_Door%d'%i,-291.8,v,45,1.5,37,83,'Panel');box('E_Handle%d'%i,-289.5,v+(10 if i==0 else -10),62,3,2,14,'Handle',collide=False)
 # Record exact intended footprints, independent of loose tabletop props.
 footprints=[dict(id='A',name='assembly_table',u=-230,v=400,width_cm=180,depth_cm=80,height_cm=85),dict(id='B',name='parts_shelving',u=90,v=410,width_cm=280,depth_cm=60,height_cm=210),dict(id='C',name='workbench',u=-300,v=80,width_cm=80,depth_cm=260,height_cm=90),dict(id='D',name='tyre_stand',u=305,v=280,width_cm=70,depth_cm=140,height_cm=170),dict(id='E',name='cabinet',u=-315,v=-280,width_cm=45,depth_cm=80,height_cm=98)]
 for p in footprints:
  assert abs(p['u'])+p['width_cm']/2<=350 and abs(p['v'])+p['depth_cm']/2<=450
  assert not (p['u']+p['width_cm']/2>340 and p['v']-p['depth_cm']/2<155 and p['v']+p['depth_cm']/2>45),'Side door obstructed'
 baseline=json.load(open(backup));changed=[n for n,r in baseline.items() if n in by and record(by[n])!=r];assert not changed,changed
 E.set_selected_level_actors([]);assert LV.save_current_level()
 json.dump(dict(status='saved',units='cm',coordinate_system='u right from gate; v into garage; origin at slab centre',floor_z=z,garage_interior_cm=[700,900],items=footprints,actor_count=len(created),minimum_car_left_workbench_clearance_cm=260-80.75,side_door_clear_v_cm=[45,155],tyre_rack_v_cm=[210,350],unchanged_existing_actor_transforms=True,created=created),open(Q+'/layout.json','w'),indent=2)
 unreal.log('GARAGE_FITOUT_OK '+str(len(created)))
except BaseException:
 open(Q+'/error.txt','w').write(traceback.format_exc());raise
