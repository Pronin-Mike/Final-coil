"""Verify mask refresh, seal reference source paths and restore interactive Editor."""
from pathlib import Path
import unreal,sys,json,hashlib,importlib
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation/Stage2_1';sys.path.insert(0,str(ROOT/'Scripts'))
assert not unreal.EditorLevelLibrary.get_game_world()
import meadow_editor
importlib.reload(meadow_editor)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(world,'t.MaxFPS 0')
source=ROOT/'SourceArt/MeadowVegetation/T_Meadow_Ecology.png';before=hashlib.sha256(source.read_bytes()).hexdigest()
meadow_editor.refresh_ground_mask();after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after,'Unchanged config must reproduce exactly the same ecology field'
fixed=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/FinalCoil/Environment/Meadow/ReferenceStage2/Meshes',True,False):
    mesh=unreal.load_asset(path);data=mesh.get_editor_property('asset_import_data');snapshot=Q/'ReferenceStage2/SourceArt'/(mesh.get_name()+'.obj');assert snapshot.is_file()
    data.scripted_add_filename(str(snapshot),0,'Stage 2 preserved source')
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False);fixed.append(mesh.get_name())
assert len(fixed)==18
meadow_editor.register_menu()
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK')
(Q/'finish_checks.json').write_text(json.dumps(dict(status='passed',ecology_source_reproduced=True,ecology_sha256=after,reference_sources_sealed=fixed,editor_fps_limit_restored=0),indent=2))
