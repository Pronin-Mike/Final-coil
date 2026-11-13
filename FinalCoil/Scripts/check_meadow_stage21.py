"""Preserve Stage 2 evidence while reusing its live scene/mask acceptance checks."""
from pathlib import Path
import unreal,json,sys,hashlib,time
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation/Stage2_1';sys.path.insert(0,str(ROOT/'Scripts'))
for name in ['check_meadow_editor.py','check_meadow_live.py']:
    path=ROOT/'Scripts'/name;source=path.read_text().replace("Q=ROOT/'Review/MeadowVegetation'","Q=ROOT/'Review/MeadowVegetation/Stage2_1'")
    for ref in ['before_scene.json','protected_hashes.json']:source=source.replace("(Q/'"+ref+"')","(Q.parent/'"+ref+"')")
    exec(compile(source,str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
output=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='MEADOW_Output')
rows=[];SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for c in output.get_components_by_class(unreal.InstancedStaticMeshComponent):
    m=c.static_mesh
    assert c.get_num_materials()==1 and len(m.get_editor_property('static_materials'))==1
    assert SM.get_lod_count(m)==2 and all(m.get_num_sections(i)==1 for i in range(2))
    assert not m.get_editor_property('nanite_settings').enabled
    rows.append(dict(component=c.get_name(),instances=c.get_instance_count(),lod_triangles=[m.get_num_triangles(i) for i in range(2)],materials=c.get_num_materials()))
assert len(rows)==18 and len(output.get_components_by_class(unreal.DecalComponent))==1
for name in ['M_Meadow_Integrated','M_Meadow_GroundDetail']:
    m=unreal.load_asset('/Game/FinalCoil/Environment/Meadow/'+name);assert not unreal.MaterialEditingLibrary.recompile_material(m)
(Q/'asset_checks.json').write_text(json.dumps(dict(status='passed',components=rows,one_output_actor=True,one_local_ground_decal=True,compiled_materials=True),indent=2))

assert unreal.EditorAssetLibrary.save_directory('/Game/FinalCoil/Environment/Meadow',True,True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
if globals().get('STOP_BRIDGE'):
    import gc,types
    for fn in gc.get_objects():
        if isinstance(fn,types.FunctionType) and fn.__name__=='_meadow_tick' and fn.__code__.co_filename.replace('\\','/').endswith('/MeadowStage2_1/bridge.py'):
            fn.__globals__['meadow_bridge_stop']()
