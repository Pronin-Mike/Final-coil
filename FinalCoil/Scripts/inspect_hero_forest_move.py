import unreal,json,os,shutil
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/HeroForestMove'
LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def v(p):return [p.x,p.y,p.z]
rows=[]
for a in E.get_all_level_actors():
 r=a.get_actor_rotation();d=dict(label=a.get_actor_label(),p=v(a.get_actor_location()),r=[r.pitch,r.yaw,r.roll],s=v(a.get_actor_scale3d()),class_name=a.get_class().get_name(),hidden=a.get_editor_property("hidden"))
 if isinstance(a,unreal.StaticMeshActor):d['mesh']=str(a.static_mesh_component.static_mesh.get_path_name()) if a.static_mesh_component.static_mesh else None
 rows.append(d)
json.dump(rows,open(Q+'/baseline.json','w'),indent=2)
for n in ['TERRAIN_Terrain','G01_House','PLOT10_G01_1000m2','POI_G01_GrandpaEntrance_Provisional']:
 print('MOVE_INSPECT',next((r for r in rows if r['label']==n),None))
unreal.log('HERO_MOVE_INSPECTION_OK')
