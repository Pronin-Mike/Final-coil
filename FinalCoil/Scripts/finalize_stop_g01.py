import unreal,json
ROOT="D:/GameDevelop/FinalCoil"
OUT="/Game/FinalCoil/Maps/L_Berezovka_Stop_G01"
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def gp(x,y,z):return (-8000-x,16300-y,z)
# Engine collision capsule sweeps: vehicle-sized central walk route and side door.
world=ed.get_editor_world()
def sweep(p,q):
    result=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(*p),unreal.Vector(*q),42,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
    assert result is None,"Blocked player capsule: "+str(result)
    return result is None
main=sweep(gp(-800,0,110),gp(200,0,110))
side=sweep(gp(100,500,110),gp(100,220,110))
stopclear=sweep((430,0,110),(650,0,110))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,OUT)
assert levels.load_level(OUT)
saved=actors.get_all_level_actors();byname={a.get_actor_label():a for a in saved}
assert len([a for a in saved if isinstance(a,unreal.PlayerStart)])==1
assert len([a for a in saved if a.get_actor_label().endswith("_LogHouse")])==19
# Check local wall inner-face distances: transforms are rigid yaw180 and unit primitives.
assert abs(byname["G01_Garage_LeftWall"].get_actor_location().y-byname["G01_Garage_RightWallFront"].get_actor_location().y)-20==700
assert abs(byname["G01_Garage_BackWall"].get_actor_location().x-byname["G01_Garage_FrontWallL"].get_actor_location().x)-20==900
report={"map":OUT,"garage_clear_m":[7,9],"garage_area_m2":63,"inspection_pit":False,"main_opening_m":[3.2,2.8],"side_opening_m":[1.1,2.2],"future_car_outline_m":[2.2,4.8],"capsule_radius_cm":42,"capsule_half_height_cm":96,"main_entry_sweep_clear":main,"side_entry_sweep_clear":side,"stop_entry_sweep_clear":stopclear,"separate_house":True,"stop_size_m":[3.5,2.3,2.56],"saved_reloaded":True}
json.dump(report,open(ROOT+"/Scripts/Stop_G01_validation.json","w"),indent=2)
ed.set_level_viewport_camera_info(unreal.Vector(-4400,12500,2300),unreal.Rotator(pitch=-26,yaw=135,roll=0))
unreal.log("STOP_G01_OK "+json.dumps(report))


