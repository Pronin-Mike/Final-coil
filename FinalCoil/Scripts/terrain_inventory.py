import unreal,json
ROOT="D:/GameDevelop/FinalCoil"
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
records=[]
for a in actors.get_all_level_actors():
    p=a.get_actor_location();s=a.get_actor_scale3d();r=a.get_actor_rotation()
    o,e=a.get_actor_bounds(False)
    row={"label":a.get_actor_label(),"class":a.get_class().get_name(),"folder":str(a.get_folder_path()),"path":a.get_path_name(),"p":[p.x,p.y,p.z],"s":[s.x,s.y,s.z],"r":[r.pitch,r.yaw,r.roll],"bounds_center":[o.x,o.y,o.z],"extent":[e.x,e.y,e.z]}
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component;row["mesh"]=c.static_mesh.get_path_name() if c.static_mesh else None
        row["material"]=c.get_material(0).get_path_name() if c.get_material(0) else None
        row["collision"]=str(c.get_collision_profile_name())
    records.append(row)
json.dump({"world":world.get_name(),"actors":records},open(ROOT+"/Scripts/terrain_inventory.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
unreal.log("TERRAIN_INVENTORY_OK "+str(len(records)))
