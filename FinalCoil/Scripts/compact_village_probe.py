import unreal,json,os,shutil
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/CompactVillage';os.makedirs(Q+'/before',exist_ok=True);os.makedirs(Q+'/after',exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.save_current_level()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();data={'actors':[],'houses':[]}
for a in actors:
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();o,e=a.get_actor_bounds(False)
 rec={'label':a.get_actor_label(),'path':a.get_path_name(),'p':[p.x,p.y,p.z],'r':[r.pitch,r.yaw,r.roll],'s':[s.x,s.y,s.z],'bounds':[o.x-e.x,o.y-e.y,o.z-e.z,o.x+e.x,o.y+e.y,o.z+e.z],'components':[]}
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  rec['components'].append({'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())],'cast_shadow':c.get_editor_property('cast_shadow'),'visible':c.is_visible(),'instances':c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else None})
 data['actors'].append(rec)
 if a.get_actor_label().endswith('_LogHouse') or a.get_actor_label()=='G01_House':data['houses'].append(rec)
data['bounds']=[min(a['bounds'][0] for a in data['houses']),min(a['bounds'][1] for a in data['houses']),max(a['bounds'][3] for a in data['houses']),max(a['bounds'][4] for a in data['houses'])]
json.dump(data,open(Q+'/baseline.json','w'),indent=1)
B=R+'/Saved/Backups/BeforeCompactVillage';os.makedirs(B,exist_ok=True)
if not os.path.exists(B+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',B+'/L_Berezovka_Terrain.umap')
unreal.log('VILLAGE_ROAD_BASELINE_OK')

