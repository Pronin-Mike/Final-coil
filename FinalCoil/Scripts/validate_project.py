import unreal
for folder in ["Core", "Player", "Interaction", "Items", "Vehicles", "World", "UI", "Audio", "Art", "Maps", "Developers"]:
    unreal.EditorAssetLibrary.make_directory("/Game/FinalCoil/" + folder)
assets = unreal.EditorAssetLibrary.list_assets("/Game/FirstPerson", recursive=True)
blueprints = []
for path in assets:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if isinstance(asset, unreal.Blueprint):
        unreal.BlueprintEditorLibrary.compile_blueprint(asset)
        blueprints.append(path)
assert unreal.EditorAssetLibrary.does_asset_exist("/Game/FirstPerson/Lvl_FirstPerson")
unreal.log("FINALCOIL_BOOTSTRAP_OK blueprints=" + str(len(blueprints)))
