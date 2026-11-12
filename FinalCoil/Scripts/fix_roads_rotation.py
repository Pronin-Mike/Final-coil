import unreal,json,math
ROOT="D:/GameDevelop/FinalCoil"
MAP="/Game/FinalCoil/Maps/L_Berezovka_Region_Roads"
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name() != 'L_Berezovka_Region_Roads':
    assert levels.load_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
byname={a.get_actor_label():a for a in actors.get_all_level_actors()}
data=json.load(open(ROOT+"/Scripts/Berezovka_roads_validation.json",encoding="utf-8"))
before=[]
for r in data["routes"]:
    pts=r["points_px"]
    for i,(p,q) in enumerate(zip(pts,pts[1:])):
        a=byname[r["segments"][i]]
        before.append(str(a.get_actor_rotation()))
        dx=-(q[1]-p[1]);dy=q[0]-p[0]
        yaw=math.degrees(math.atan2(dy,dx))
        a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
        forward=a.get_actor_forward_vector()
        assert abs(forward.z)<.00001
        length=math.hypot(dx,dy)
        assert (forward.x*dx+forward.y*dy)/length>.9999
        _,bounds=a.get_actor_bounds(False)
        assert bounds.z<3, str(bounds)
for a in byname.values():
    if a.get_actor_label().startswith("LABEL_"):
        a.set_actor_rotation(unreal.Rotator(pitch=90,yaw=0,roll=0),False)
    if isinstance(a,unreal.PlayerStart):
        a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=90,roll=0),False)
assert levels.save_current_level()
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-95000,77000,270000),unreal.Rotator(pitch=-63,yaw=0,roll=0))
json.dump({"first_old_rotations":before[:5],"segments_fixed":len(before),"horizontal_bounds_checked":True},open(ROOT+"/Scripts/Roads_rotation_fix.json","w"),indent=2)
unreal.log("ROADS_ROTATION_FIXED "+str(len(before)))
