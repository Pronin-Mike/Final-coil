import unreal,json,os
R='D:/GameDevelop/FinalCoil';os.makedirs(R+'/Review/GroundMaterial',exist_ok=True)
lev=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lev.save_current_level()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
data={'level':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name(),'actors':[],'api':{}}
for a in actors:
 if isinstance(a,unreal.StaticMeshActor):
  n=a.get_actor_label(); c=a.static_mesh_component
  data['actors'].append({'label':n,'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]})
for cls in ['MaterialExpressionCustom','CustomInput','CustomOutput','MaterialEditingLibrary']:
 obj=getattr(unreal,cls,None);data['api'][cls]=str(obj.__doc__) if obj else 'missing'
json.dump(data,open(R+'/Review/GroundMaterial/probe.json','w'),indent=2)
unreal.log('GROUND_PROBE_OK')
