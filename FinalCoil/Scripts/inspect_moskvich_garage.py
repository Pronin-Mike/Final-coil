import unreal,json,os
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def vec(v):return [v.x,v.y,v.z]
rows=[]
for a in E.get_all_level_actors():
 if a.get_actor_label().startswith('G01_'):
  p,e=a.get_actor_bounds(False);r=a.get_actor_rotation()
  rows.append(dict(label=a.get_actor_label(),p=vec(a.get_actor_location()),rotation=[r.pitch,r.yaw,r.roll],scale=vec(a.get_actor_scale3d()),bounds=[vec(p),vec(e)],mesh=str(a.static_mesh_component.static_mesh) if isinstance(a,unreal.StaticMeshActor) else None))
json.dump(rows,open('D:/GameDevelop/FinalCoil/Review/Moskvich412/garage_before.json','w'),indent=2)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('MOSKVICH_GARAGE_INSPECT_OK')
