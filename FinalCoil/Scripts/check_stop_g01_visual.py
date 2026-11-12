import unreal,math
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
angle=math.degrees(math.atan2(140,380))
for name,roll in [("RoofLeft",-angle),("RoofRight",angle)]:
    by["G01_Garage_"+name].set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=roll),False)
assert by["G01_Garage_RoofLeft"].get_actor_right_vector().z>0
assert by["G01_Garage_RoofRight"].get_actor_right_vector().z<0
for path in unreal.EditorAssetLibrary.list_assets("/Game/FinalCoil/World/StopAndG01",recursive=True,include_folder=False):
    unreal.EditorAssetLibrary.save_asset(path,only_if_is_dirty=False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-5600,14300,1600),unreal.Rotator(pitch=-20,yaw=140,roll=0))
unreal.log("STOP_G01_ROOF_FIXED_SAVED")

