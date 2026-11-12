import unreal,json
A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary
m=unreal.load_asset('/Game/FinalCoil/World/PlotMarkers/M_PlotOutline')
assert m
nodes=[n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionConstant3Vector)]
assert nodes
for n in nodes:n.set_editor_property('constant',unreal.LinearColor(.015,.12,1.0))
errors=L.recompile_material(m);assert not errors,str(errors)
assert A.save_loaded_asset(m)
plots=[a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label().startswith('PLOT10_')]
assert len(plots)==20
for a in plots:
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
 assert c.get_material(0)==m
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('BLUE_PLOT_OUTLINES_OK count=20 saved=True')
