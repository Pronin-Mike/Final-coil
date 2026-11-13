"""Live scene invariants and PCG resource audit; run after generation finishes."""
from pathlib import Path
import unreal,json,hashlib
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
before=json.loads((Q/'before_scene.json').read_text());by={a.get_actor_label():a for a in E.get_all_level_actors()};changed=[];instances=[]
for name,old in before.items():
 a=by.get(name)
 if not a:changed.append(name+':missing');continue
 t=a.get_actor_transform();p=t.translation;r=t.rotation.rotator();s=t.scale3d
 if max(abs(x-y) for x,y in zip(old['transform'],[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]))>.001:changed.append(name+':transform')
 comps={c.get_name():c for c in a.get_components_by_class(unreal.StaticMeshComponent)}
 for row in old['components']:
  c=comps.get(row['name'])
  if not c:changed.append(name+':component missing');continue
  rec=dict(name=c.get_name(),mesh=c.static_mesh.get_path_name() if c.static_mesh else None,collision=str(c.get_collision_enabled()),instances=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1,materials=[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())])
  if row!=rec:changed.append(name+':'+c.get_name())
for a in by.values():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if c.static_mesh and '/Environment/Meadow/' in c.static_mesh.get_path_name():
   assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
   assert not c.get_editor_property('cast_shadow')
   assert c.is_visible()
   instances.append(dict(actor=a.get_actor_label(),component=c.get_name(),mesh=c.static_mesh.get_name(),count=c.get_instance_count(),class_name=c.get_class().get_name(),collision=str(c.get_collision_enabled()),cull_end=c.get_editor_property('instance_end_cull_distance')))
protected=json.loads((Q/'protected_hashes.json').read_text());hash_changes=[name for name,digest in protected.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
report=dict(original_actors=len(before),changed_original_objects=changed,protected_file_changes=hash_changes,components=instances,total_instances=sum(x['count'] for x in instances),output_actor_name=by['MEADOW_Output'].get_name())
assert not changed,changed
assert not hash_changes,hash_changes
assert report['total_instances']>0
assert LV.save_current_level()
for p in unreal.EditorAssetLibrary.list_assets('/Game/FinalCoil/Environment/Meadow',True,False):unreal.EditorAssetLibrary.save_asset(p,True)
(Q/'editor_validation.json').write_text(json.dumps(report,indent=2));unreal.log('MEADOW_EDITOR_VALIDATED')
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(18000,29600,290),unreal.Rotator(pitch=-9,yaw=90,roll=0))
unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(Q/'editor_eye.png'))
