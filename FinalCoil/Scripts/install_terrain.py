import unreal,json,os,sys,math
ROOT="D:/GameDevelop/FinalCoil"
sys.path.insert(0,ROOT+"/Scripts")
import terrain_profile as T
BASE="/Game/FinalCoil/Maps/L_Berezovka_Shop_Bor"
OUT="/Game/FinalCoil/Maps/L_Berezovka_Terrain"
DEST="/Game/FinalCoil/World/Terrain"
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert ed.get_editor_world().get_name()=="L_Berezovka_Shop_Bor","Open source level before terrain install"
assert levels.save_current_level()
assert not unreal.EditorAssetLibrary.does_asset_exist(OUT)
manifest=json.load(open(ROOT+"/SourceArt/Terrain/manifest.json"))
unreal.EditorAssetLibrary.make_directory(DEST)
def material(name,rgb,unlit=False):
    p=DEST+"/M_"+name
    if unreal.EditorAssetLibrary.does_asset_exist(p):return unreal.load_asset(p)
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_"+name,DEST,unreal.Material,unreal.MaterialFactoryNew())
    if unlit:m.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided",True)
    e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
    e.set_editor_property("constant",unreal.LinearColor(*rgb))
    assert unreal.MaterialEditingLibrary.connect_material_property(e,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR if unlit else unreal.MaterialProperty.MP_BASE_COLOR)
    rough=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant);rough.set_editor_property("r",.95)
    unreal.MaterialEditingLibrary.connect_material_property(rough,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m
mats={"Terrain":material("Meadow",(.18,.23,.10)),"Road":material("DirtRoad",(.22,.145,.075)),"Path":material("Footpath",(.29,.20,.105)),"Rail":material("RailCorridor",(.17,.18,.18))}
imported={}
for key,filename in [("Terrain","SM_Berezovka_Terrain"),("Road","SM_Conform_Road"),("Path","SM_Conform_Path"),("Rail","SM_Conform_Rail")]:
    task=unreal.AssetImportTask();task.filename=ROOT+"/SourceArt/Terrain/"+filename+".obj";task.destination_path=DEST;task.destination_name=filename;task.automated=True;task.save=True
    options=unreal.FbxImportUI();options.import_mesh=True;options.import_materials=False;options.import_textures=False
    options.static_mesh_import_data.combine_meshes=True
    options.static_mesh_import_data.auto_generate_collision=False
    options.static_mesh_import_data.generate_lightmap_u_vs=False
    task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=next((unreal.load_asset(str(p)) for p in task.imported_object_paths if isinstance(unreal.load_asset(str(p)),unreal.StaticMesh)),None)
    assert mesh,filename
    settings=mesh.get_editor_property("nanite_settings");settings.enabled=False;mesh.set_editor_property("nanite_settings",settings)
    body=mesh.get_editor_property("body_setup")
    body.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    mesh.set_material(0,mats[key])
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    imported[key]=mesh
    unreal.log("TERRAIN_IMPORTED "+key+" "+str(mesh.get_bounding_box()))
# Remove flat support and the old road blocks ONLY in the new level state.
old=actors.get_all_level_actors();replaced=set(manifest["replace_labels"]);moved=[];removed=[]
padheights={p[0]:p[7] for p in T.PADS}
for a in old:
    name=a.get_actor_label();p=a.get_actor_location()
    if name in replaced or name.startswith(("Ground_","Village_Berezovka_Footprint","Forest_Mass_","OldBor_Mass_")):
        removed.append(name);assert actors.destroy_actor(a);continue
    if name.startswith("Lake_Mass_"):
        a.set_actor_location(unreal.Vector(p.x,p.y,-270),False,False);continue
    if name.startswith("MARK_") or name.startswith("LABEL_"):
        a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
        if isinstance(a,unreal.StaticMeshActor):a.static_mesh_component.set_collision_profile_name("NoCollision")
    labelkey=name.split("_")[0]
    if labelkey in padheights:dz=padheights[labelkey]
    else:dz=T.height(p.x,p.y)
    # Adjust standalone trees as rigid trunk+crown pairs using their common XY.
    a.set_actor_location(unreal.Vector(p.x,p.y,p.z+dz),False,False)
    moved.append({"label":name,"xy":[p.x,p.y],"dz":dz})
for key,mesh in imported.items():
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
    a.set_actor_label("TERRAIN_"+key);a.set_folder_path("00_Terrain")
    a.set_actor_scale3d(unreal.Vector(1,-1,1)) # OBJ translator reflects Y into Unreal coordinates.
    a.static_mesh_component.set_static_mesh(mesh)
    a.static_mesh_component.set_material(0,mats[key])
    a.static_mesh_component.set_collision_profile_name("BlockAll")
    a.tags=["TerrainV1",key]
# Lightweight daylight context for reading the surface relief at eye level.
sun=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,10000),unreal.Rotator(pitch=-30,yaw=-40,roll=0))
sun.set_actor_label("Terrain_Sun");sun.set_folder_path("90_Lighting")
sun.light_component.set_editor_property("intensity",5)
sun.light_component.set_editor_property("atmosphere_sun_light",True)
atmo=actors.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(0,0,0));atmo.set_actor_label("Terrain_Sky");atmo.set_folder_path("90_Lighting")
sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000));sky.set_actor_label("Terrain_SkyLight");sky.set_folder_path("90_Lighting")
sky.light_component.set_editor_property("intensity",.8)
# PlayerStart set by exact triangle height, clear of stop platform.
start=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.PlayerStart))
p=start.get_actor_location();start.set_actor_location(unreal.Vector(p.x,p.y,T.height(p.x,p.y)+115),False,False)
# Keep house/garage floor perfectly horizontal: G01 shifts as one pad.
assert unreal.EditorLoadingAndSavingUtils.save_map(ed.get_editor_world(),OUT)
assert levels.load_level(OUT)
saved=actors.get_all_level_actors();by={a.get_actor_label():a for a in saved}
for row in moved:
    if row["label"] not in by:continue
    p=by[row["label"]].get_actor_location()
    assert math.hypot(p.x-row["xy"][0],p.y-row["xy"][1])<.01
assert "G01_Garage_Floor" in by and abs(by["G01_Garage_Floor"].get_actor_rotation().pitch)<.001
assert len([a for a in saved if a.get_actor_label().endswith("_LogHouse")])==19
json.dump({"map":OUT,"moved":moved,"removed_flat_count":len(removed),"inventory_actor_count":len(old),"height_m":[v/100 for v in manifest["z_range_cm"]],"max_route_grade":manifest["max_route_grade"],"xy_preserved":True,"source_map_git_blob":"0725a80b4bc79229f12b16e2632c7ca528316cfe","saved_reloaded":True},open(ROOT+"/Review/Terrain/terrain_install.json","w"),indent=2)
ed.set_level_viewport_camera_info(unreal.Vector(-35000,76000,230000),unreal.Rotator(pitch=-70,yaw=0,roll=0))
unreal.log("TERRAIN_INSTALLED_OK")
