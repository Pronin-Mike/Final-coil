import unreal,json,os
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/VillagePlants';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
for name in ['M_Grass_Green','M_Grass_Dry','M_Shrub_Leaf','M_Shrub_Bark']:
 m=unreal.load_asset(D+'/'+name)
 for expr in L.get_material_expressions(m):
  if isinstance(expr,unreal.MaterialExpressionCustom):
   code=expr.get_editor_property('code')
   if not code.startswith('UV.y=1-UV.y;'):expr.set_editor_property('code','UV.y=1-UV.y;\n'+code)
 errors=L.recompile_material(m);assert not errors,str(errors);A.save_loaded_asset(m)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();checks=[]
for a in actors:
 if not a.get_actor_label().startswith('VEG_Village_'):continue
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);assert c and c.get_instance_count()>0
 assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
 for i in [0,c.get_instance_count()//2,c.get_instance_count()-1]:
  q=c.get_instance_transform(i,True).rotation;assert abs(q.x)<.00001 and abs(q.y)<.00001
 checks.append({'name':a.get_actor_label(),'count':c.get_instance_count(),'upright':True,'collision':'NoCollision'})
assert len(checks)==7
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
json.dump({'checks':checks,'shader_errors':[],'uv_v_import_flip_corrected':True},open(R+'/Review/VillagePlants/final_checks.json','w'),indent=2)
unreal.log('VILLAGE_PLANTS_FINAL_OK')
