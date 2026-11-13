"""In-editor saved inventory / throttle; benchmark never changes the world on disk."""
from pathlib import Path
import unreal,json,sys,time
ROOT=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(ROOT/'Scripts'));Q=ROOT/'Review/MeadowVegetation/Stage2_1'
import meadow_editor,importlib
importlib.reload(meadow_editor)
if globals().get('QUALITY'):
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(world,'t.MaxFPS 0');meadow_editor.rebuild(QUALITY)
else:
 if globals().get('REFRESH_FIELD'):
  task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceArt/MeadowVegetation/T_Meadow_Ecology.png');task.destination_path='/Game/FinalCoil/Environment/Meadow/Textures';task.automated=True;task.replace_existing=True;task.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 output=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='MEADOW_Output')
 rows=[dict(name=c.get_name(),mesh=c.static_mesh.get_name(),instances=c.get_instance_count(),materials=c.get_num_materials()) for c in output.get_components_by_class(unreal.InstancedStaticMeshComponent)]
 (Q/'benchmark_inventory.json').write_text(json.dumps(dict(actor=output.get_name(),components=rows,instances=sum(c['instances'] for c in rows)),indent=2))
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 unreal.SystemLibrary.execute_console_command(output.get_world(),'t.MaxFPS '+str(globals().get('FPS',1)))
