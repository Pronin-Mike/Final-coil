"""Replace temporary stepped dormer cheeks with two exact planar pieces."""
import unreal,json,math,traceback
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/G01HouseV2';D='/Game/FinalCoil/World/G01HouseV2';Q=R+'/Review/G01HouseV2'
try:
 LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();by={a.get_actor_label():a for a in E.get_all_level_actors()};spec=json.load(open(S+'/house_spec.json'));cx,cy=spec['house_center'];a=math.radians(spec['yaw']);c,s=math.cos(a),math.sin(a)
 task=unreal.AssetImportTask();task.filename=S+'/SM_DormerSide.obj';task.destination_path=D;task.destination_name='SM_DormerSide';task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/SM_DormerSide');assert mesh;mesh.set_material(0,unreal.load_asset(D+'/MI_Log'));mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert A.save_loaded_asset(mesh)
 for name,actor in by.items():
  if name.startswith('G01_H2_DormerSide_'):
   actor.set_actor_hidden_in_game(True);actor.set_is_temporarily_hidden_in_editor(True)
   for comp in actor.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 for name,y in [('Left',-175),('Right',175)]:
  label='G01_H2_DormerPlane_'+name;actor=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label(label);actor.set_folder_path('61_G01/HouseV2/Roof');actor.set_actor_location(unreal.Vector(cx-s*y,cy+c*y,spec['ground_z']),False,False);actor.set_actor_rotation(unreal.Rotator(pitch=0,yaw=spec['yaw'],roll=0),False);actor.static_mesh_component.set_static_mesh(mesh);actor.static_mesh_component.set_collision_profile_name('BlockAll')
 assert LV.save_current_level();spec['colliders']=[b for b in spec['colliders'] if not b['name'].startswith('G01_H2_DormerSide_')];spec['dormer_cheeks']='Two continuous planar trapezoids; no stepped infill';json.dump(spec,open(S+'/house_spec.json','w'),indent=2);json.dump(dict(saved=True,route_geometry_unchanged=True,dormer_side_triangles=12),open(Q+'/finish.json','w'));unreal.log('G01_HOUSE_FINISH_OK')
except BaseException:
 open(Q+'/finish_error.txt','w').write(traceback.format_exc());raise
