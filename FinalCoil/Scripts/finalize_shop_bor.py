import unreal
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if a.get_actor_label() in ["MARK_CHAPEL01_Chapel","LABEL_CHAPEL01_Chapel","LABEL_SHOP01_Provisional"]:
        a.set_actor_hidden_in_game(True)
        a.set_is_temporarily_hidden_in_editor(True)
for path in unreal.EditorAssetLibrary.list_assets("/Game/FinalCoil/World/ShopAndBor",recursive=True,include_folder=False):
    unreal.EditorAssetLibrary.save_asset(path,only_if_is_dirty=False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(30300,-37300,6000),unreal.Rotator(pitch=-24,yaw=55,roll=0))
unreal.log("SHOP_BOR_FINAL_SAVED")
