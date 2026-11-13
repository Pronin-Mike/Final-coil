"""Final editor audit of metadata, winds, menu, graph and original terrain rays."""
from pathlib import Path
import unreal,json,sys,importlib
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation';sys.path.insert(0,str(ROOT/'Scripts'))
import meadow_distribution as M
import meadow_editor
importlib.reload(meadow_editor);meadow_editor.register_menu()
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=E.get_all_level_actors();ignore=[a for a in actors if a.get_actor_label()!='TERRAIN_Terrain'];surface=M.Z.HeightfieldSurface();rays=[]
for x,y in [(15700+i*1100,27700+j*1100) for i in range(5) for j in range(5)]:
 sample=surface.sample(x,y);z=sample['position'][2];hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,z+300),unreal.Vector(x,y,z-300),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);assert hit;parts=hit.to_tuple();error=abs(parts[5].z-z);assert error<.01;rays.append(error)
component=next(a for a in actors if a.get_actor_label()=='ENV_PCG_Environment').get_component_by_class(unreal.PCGComponent);assert not component.get_editor_property('generation_in_progress')
collection=component.get_generated_graph_output();typed=collection.get_typed_inputs();data=typed[0] if isinstance(typed,tuple) else typed;meadow=diagnostic=0;violations=0
for pd in data:
 legacy=pd.to_point_data();md=legacy.const_metadata()
 for pt in legacy.get_points_copy():
  if pt.get_float_attribute(md,'Exclusion')>.001:violations+=1
 # Dense meadow rows carry the Mesh metadata, diagnostic rows do not.
 try:is_meadow=bool(legacy.get_points_copy()[0].get_string_attribute(md,'Mesh')) if legacy.get_num_points() else False
 except Exception:is_meadow=False
 if is_meadow:meadow+=legacy.get_num_points()
 else:diagnostic+=legacy.get_num_points()
distribution=json.loads((M.SOURCE/('distribution_'+M.config()['quality'].lower()+'.json')).read_text());expected=sum(len(p) for p in distribution['groups'].values())
assert meadow==expected and diagnostic==8116 and violations==0,(meadow,diagnostic,violations)
collection=unreal.load_asset('/Game/FinalCoil/Environment/Meadow/MPC_MeadowWind');p=collection.get_editor_property('scalar_parameters')[0];original=p.get_editor_property('default_value')
# Exercise the common parameter without changing the saved quality/config.
for strength in [0.,original]:
 p.set_editor_property('default_value',strength);collection.set_editor_property('scalar_parameters',[p]);assert collection.get_editor_property('scalar_parameters')[0].get_editor_property('default_value')==strength
assert unreal.EditorAssetLibrary.save_loaded_asset(collection,False)
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK')
result=dict(status='passed',diagnostic_points=diagnostic,dense_meadow_points=meadow,exclusion_violations=violations,terrain_ray_samples=len(rays),maximum_terrain_trace_error_cm=max(rays),wind_parameter_off_and_restore=True,wind_restored=original,menu_registered=True,pcg_generation_trigger=str(component.get_editor_property('generation_trigger')))
(Q/'live_checks.json').write_text(json.dumps(result,indent=2));unreal.log('MEADOW_LIVE_CHECKS_PASSED')
