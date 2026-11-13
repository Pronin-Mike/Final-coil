"""Low-poly plank floor, same finished elevation and uninterrupted floor collision."""
import unreal,json,math,os,random,shutil,traceback
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/G01GaragePlanks';Q=R+'/Review/G01GaragePlanks';D='/Game/FinalCoil/World/G01GaragePlanks';B=R+'/../.publishing/g01-garage-before-planks'
for p in [S,Q,B]:os.makedirs(p,exist_ok=True)
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 assert LV.save_current_level()
 if not os.path.exists(B+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',B+'/L_Berezovka_Terrain.umap')
 by={a.get_actor_label():a for a in E.get_all_level_actors()};floor=by['G01_Garage_Floor'];p=floor.get_actor_location();scale=floor.get_actor_scale3d();top=p.z+scale.z*50;yaw=json.load(open(R+'/SourceArt/G01HouseV2/house_spec.json'))['yaw'];angle=math.radians(yaw);c,s=math.cos(angle),math.sin(angle)
 def pos(x,y,z):return unreal.Vector(p.x+c*x-s*y,p.y+s*x+c*y,top+z)
 def rec(a):
  v=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();return [v.x,v.y,v.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
 if not os.path.exists(Q+'/before.json'):json.dump({n:rec(a) for n,a in by.items()},open(Q+'/before.json','w'),indent=2)
 baseline=json.load(open(Q+'/before.json'));A.make_directory(D);source='/Game/FinalCoil/World/G01HouseV2/MI_Floor';parent=unreal.load_asset('/Game/FinalCoil/Vehicles/Moskvich412/M_VehicleBlockout');assert unreal.load_asset(source) and parent
 palette=[(.27,.16,.085),(.31,.185,.10),(.29,.17,.09),(.33,.20,.115)];materials=[]
 for i,color in enumerate(palette):
  name='MI_Planks_%d'%i;m=unreal.load_asset(D+'/'+name) or A.duplicate_asset(source,D+'/'+name);L.set_material_instance_vector_parameter_value(m,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(m,'Roughness',.88);L.set_material_instance_scalar_parameter_value(m,'Metallic',0);L.update_material_instance(m);assert A.save_loaded_asset(m);materials.append(m)
 # The existing continuous collision slab stays at precisely the same elevation.
 floor.set_actor_hidden_in_game(True);floor.static_mesh_component.set_visibility(False,True);floor.static_mesh_component.set_collision_profile_name('BlockAll')
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');rng=random.Random(1311202601);transforms=[[] for _ in palette];boards=[];row_width=740/34;gap=.25
 for row in range(34):
  y=-370+(row+.5)*row_width;x=-470;first=True
  while x<469.999:
   end=min(470,x+rng.uniform(110,320) if first else x+rng.uniform(260,340));first=False
   if 470-end<65:end=470
   length=end-x;shade=rng.randrange(4);transforms[shade].append(unreal.Transform(location=pos((x+end)/2,y,-2.5),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector((length-gap)/100,(row_width-gap)/100,.05)))
   boards.append(dict(row=row,start_x=x,end_x=end,center_y=y,width_cm=row_width-gap,thickness_cm=5,tone=shade));x=end
 from editor_toolset.toolsets.actor import ActorTools
 for i,ts in enumerate(transforms):
  label='G01_Garage_Planks_%d'%i;a=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/GaragePlankFloor');comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Boards');comp.clear_instances();comp.set_static_mesh(cube);comp.set_material(0,materials[i]);comp.set_collision_profile_name('NoCollision');comp.add_instances(ts,False,True,False)
 # Dark backing just below the boards makes the narrow seams readable.
 label='G01_Garage_Planks_Underlay';a=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/GaragePlankFloor');a.set_actor_location(pos(0,0,-1),False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(9.4,7.4,.01));a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,unreal.load_asset('/Game/FinalCoil/World/G01HouseV2/MI_Trim'));a.static_mesh_component.set_collision_profile_name('NoCollision')
 assert all(rec(by[n])==r for n,r in baseline.items() if n in by),'Existing actor moved'
 E.set_selected_level_actors([]);assert LV.save_current_level()
 report=dict(status='saved',center=[p.x,p.y,top],yaw=yaw,floor_size_cm=[940,740],finished_floor_world_z=top,plank_rows=34,board_count=len(boards),nominal_width_cm=row_width,seam_width_cm=gap,thickness_cm=5,layout='Longitudinal boards with staggered end joints and four restrained wood tones',collision='Original continuous slab at unchanged height; render-only boards',car_and_equipment_unchanged=True,boards=boards)
 json.dump(report,open(S+'/floor_spec.json','w'),indent=2);json.dump({k:v for k,v in report.items() if k!='boards'},open(Q+'/installed.json','w'),indent=2);unreal.log('G01_PLANK_FLOOR_SAVED')
except BaseException:
 open(Q+'/error.txt','w').write(traceback.format_exc());raise
