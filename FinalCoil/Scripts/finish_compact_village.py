import unreal,json,sys
sys.path.insert(0,'D:/GameDevelop/FinalCoil/Scripts')
import terrain_profile as T
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/CompactVillage';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;by={a.get_actor_label():a for a in E.get_all_level_actors()}
for name,a in by.items():
 if not name.startswith('PLOT10_'):continue
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,True);s=t.scale3d;t.scale3d=unreal.Vector(s.x,.75,s.z);p=t.translation;t.translation=unreal.Vector(p.x,p.y,T.height(p.x,p.y)+15);c.update_instance_transform(i,t,True,i==c.get_instance_count()-1,True)
source=by['H01_Label'].text_render.get_editor_property('text_material')
m=unreal.load_asset(D+'/M_OverheadLabels') if A.does_asset_exist(D+'/M_OverheadLabels') else A.duplicate_asset(source.get_path_name(),D+'/M_OverheadLabels')
m.set_editor_property('two_sided',False);assert not L.recompile_material(m);assert A.save_loaded_asset(m)
for name,a in by.items():
 if (name.endswith('_Label') and name[:1] in ['H','E','G']) or name in ['STOP01_MapLabel','SHOP01_MapLabel','DIM_StopToHero_Text']:
  a.text_render.set_text_material(m)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('COMPACT_FINISH_OK')
