"""Import the Blender FBX and place one static scale prop in G01 garage."""
import unreal,json,math,traceback
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/Moskvich412';S=R+'/SourceArt/Vehicles/Moskvich412';D='/Game/FinalCoil/Vehicles/Moskvich412'
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools()
 assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
 assert not unreal.EditorLevelLibrary.get_game_world(),'Stop PIE before importing'
 assert LV.save_current_level();A.make_directory(D)
 # No existing generic colour/metal/roughness parameter parent in project: create
 # one compact reusable master, then instances rather than nine duplicated graphs.
 parent=unreal.load_asset(D+'/M_VehicleBlockout')
 if not parent:
  parent=AT.create_asset('M_VehicleBlockout',D,unreal.Material,unreal.MaterialFactoryNew())
  for name,value,cls,prop,y in [('Tint',unreal.LinearColor(.42,.43,.26,1),unreal.MaterialExpressionVectorParameter,unreal.MaterialProperty.MP_BASE_COLOR,0),('Metallic',.25,unreal.MaterialExpressionScalarParameter,unreal.MaterialProperty.MP_METALLIC,160),('Roughness',.4,unreal.MaterialExpressionScalarParameter,unreal.MaterialProperty.MP_ROUGHNESS,320)]:
   n=L.create_material_expression(parent,cls,-400,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);n.set_editor_property('group','Vehicle appearance');assert L.connect_material_property(n,'',prop)
  parent.set_editor_property('two_sided',True);assert not L.recompile_material(parent);assert A.save_loaded_asset(parent)
 palette={'Paint_OliveCream':([.42,.43,.26],.25,.38),'Rubber':([.018,.022,.023],0,.85),'Chrome':([.55,.58,.58],.85,.25),'Glass':([.045,.085,.105],.32,.2),'Grille':([.035,.04,.038],.45,.55),'Headlamp':([.72,.77,.66],.1,.25),'Amber':([.85,.29,.025],.1,.32),'TailRed':([.4,.025,.015],.15,.32),'Plate':([.03,.035,.03],.1,.6)}
 materials={}
 for name,(color,metal,rough) in palette.items():
  mi=unreal.load_asset(D+'/MI_'+name) or AT.create_asset('MI_'+name,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
  L.set_material_instance_parent(mi,parent);L.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(mi,'Metallic',metal);L.set_material_instance_scalar_parameter_value(mi,'Roughness',rough);L.update_material_instance(mi);assert A.save_loaded_asset(mi);materials[name]=mi
 task=unreal.AssetImportTask();task.filename=S+'/SM_Moskvich412_Blockout.fbx';task.destination_path=D;task.destination_name='SM_Moskvich412_Blockout';task.automated=True;task.replace_existing=True;task.save=True
 opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.convert_scene=True;opts.static_mesh_import_data.convert_scene_unit=True;opts.static_mesh_import_data.generate_lightmap_u_vs=True;opts.static_mesh_import_data.auto_generate_collision=False
 task.options=opts;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/SM_Moskvich412_Blockout');assert mesh
 bounds=mesh.get_bounds();ex=bounds.box_extent;dims=[ex.x*2,ex.y*2,ex.z*2]
 assert abs(dims[0]-410.5)<1 and abs(dims[1]-161.5)<1 and abs(dims[2]-150)<1,('Unexpected FBX axes/units',dims)
 slots=[]
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  name=str(slot.get_editor_property('imported_material_slot_name'));name=name.split('.')[0]
  assert name in materials,('Unmapped Blender material',name)
  mesh.set_material(i,materials[name]);slots.append(name)
 body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 assert A.save_loaded_asset(mesh)
 by={a.get_actor_label():a for a in E.get_all_level_actors()};floor=by['G01_Garage_Floor'];p=floor.get_actor_location();floor_top=p.z+floor.get_actor_scale3d().z*50
 car=by.get('G01_Moskvich412') or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector())
 car.set_actor_label('G01_Moskvich412');car.set_folder_path('61_G01/Vehicles');car.static_mesh_component.set_static_mesh(mesh);car.static_mesh_component.set_collision_profile_name('BlockAll');car.static_mesh_component.set_simulate_physics(False)
 yaw=floor.get_actor_rotation().yaw+180
 car.set_actor_scale3d(unreal.Vector(1,1,1));car.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);car.set_actor_location(unreal.Vector(p.x,p.y,floor_top-(bounds.origin.z-ex.z)),False,False)
 car.tags=[unreal.Name('FinalCoil'),unreal.Name('Moskvich412'),unreal.Name('StaticBlockout')]
 for name,a in by.items():
  if name.startswith('G01_Garage_FutureCar_'):
   a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
   for comp in a.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 E.set_selected_level_actors([car]);assert LV.save_current_level()
 # Actual local garage wall inner faces: +-450cm longitudinal, +-350cm lateral.
 # Car centred on slab; front bumper faces the open gate (-garage local X).
 result=dict(status='placed_and_saved',level='/Game/FinalCoil/Maps/L_Berezovka_Terrain',asset=mesh.get_path_name(),actor=car.get_path_name(),label=car.get_actor_label(),dimensions_cm=dims,position_cm=[p.x,p.y,car.get_actor_location().z],yaw_deg=yaw,scale=[1,1,1],floor_top_cm=floor_top,tyre_contact_error_cm=0,side_clearance_cm=(700-dims[1])/2,front_back_clearance_cm=(900-dims[0])/2,gate_width_cm=320,gate_clearance_each_side_cm=(320-dims[1])/2,materials=slots,collision='Complex as simple, BlockAll, static prop; no driving rig',garage_unchanged=True)
 json.dump(result,open(Q+'/ue_placement.json','w'),indent=2)
 unreal.log('MOSKVICH_INSTALL_OK '+json.dumps(result))
except BaseException:
 open(Q+'/install_error.txt','w').write(traceback.format_exc());raise
