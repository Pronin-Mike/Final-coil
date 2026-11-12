import unreal
D='/Game/FinalCoil/World/VillageRoadPass';L=unreal.MaterialEditingLibrary
for name in ['M_Grass_Low_Green','M_Grass_Low_Dry']:
 m=unreal.load_asset(D+'/'+name)
 for n in L.get_material_expressions(m):
  if isinstance(n,unreal.MaterialExpressionCustom) and 'normalize(VN*' in n.get_editor_property('code'):n.set_editor_property('code','return normalize(VN*.15+float3(0,0,.95));')
 err=L.recompile_material(m);assert not err,str(err);unreal.EditorAssetLibrary.save_loaded_asset(m)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('LOWGRASS_NORMALS_OK')
