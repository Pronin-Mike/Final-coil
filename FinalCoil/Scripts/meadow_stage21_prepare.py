"""Save recovery point and preserve renderable Stage 2 mesh references in UE."""
from pathlib import Path
import unreal,json,sys
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation/Stage2_1';D='/Game/FinalCoil/Environment/Meadow';AT=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not (Q/'stage2_render_audit.json').exists(),'Stage 2 reference already sealed; do not overwrite its audit'
assert not unreal.EditorLevelLibrary.get_game_world()
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
manifest=json.loads((ROOT/'SourceArt/MeadowVegetation/meshes.json').read_text());rows=[]
for rec in manifest['meshes']:
 mesh=unreal.load_asset(D+'/Meshes/'+rec['name']);assert mesh
 path=D+'/ReferenceStage2/Meshes/'+rec['name'];reference=unreal.load_asset(path)
 if not reference:reference=AT.duplicate_asset(rec['name'],D+'/ReferenceStage2/Meshes',mesh);assert reference;assert A.save_loaded_asset(reference,False)
 rows.append(dict(name=rec['name'],reference=reference.get_path_name(),material_slots=len(mesh.get_editor_property('static_materials')),sections=[mesh.get_num_sections(i) for i in range(unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_lod_count(mesh))],triangles=[mesh.get_num_triangles(i) for i in range(unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_lod_count(mesh))]))
components=[]
output=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='MEADOW_Output')
for c in output.get_components_by_class(unreal.InstancedStaticMeshComponent):components.append(dict(name=c.get_name(),mesh=c.static_mesh.get_name(),instances=c.get_instance_count(),class_name=c.get_class().get_name(),materials=[str(c.get_material(i).get_path_name()) for i in range(c.get_num_materials())],cast_shadow=c.get_editor_property('cast_shadow')))
(Q/'stage2_render_audit.json').write_text(json.dumps(dict(meshes=rows,components=components,instances=sum(c['instances'] for c in components),actor_name=output.get_name()),indent=2))
unreal.log('STAGE21_REFERENCE_SAVED')
