import unreal
DEST="/Game/FinalCoil/World/Homesteads"
house=unreal.load_asset(DEST+"/SM_LogHouse_Blockout")
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
sm.add_simple_collisions(house,unreal.ScriptingCollisionShapeType.BOX)
for path in unreal.EditorAssetLibrary.list_assets(DEST,recursive=True,include_folder=False):
    unreal.EditorAssetLibrary.save_asset(path,only_if_is_dirty=False)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if a.get_actor_label().endswith("_Label") and "HomesteadsV1" in [str(t) for t in a.tags]:
        a.set_actor_rotation(unreal.Rotator(pitch=-90,yaw=0,roll=0),False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-6000,-36000,16000),unreal.Rotator(pitch=-55,yaw=0,roll=0))
unreal.log("HOMESTEADS_FINAL_SAVED")
