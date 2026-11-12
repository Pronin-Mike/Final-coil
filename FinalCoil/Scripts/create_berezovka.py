import unreal, json, os
ROOT = "D:/GameDevelop/FinalCoil"
MAP = "/Game/FinalCoil/Maps/L_Berezovka_Blockout"
REF = "/Game/FinalCoil/Maps/Reference"
assert not unreal.EditorAssetLibrary.does_asset_exist(MAP), "Existing level must not be overwritten"
unreal.EditorAssetLibrary.make_directory(REF)
task = unreal.AssetImportTask()
task.filename = ROOT + "/SourceArt/Maps/Berezovka_PreAlpha_v1.png"
task.destination_path = REF
task.destination_name = "T_Berezovka_Plan"
task.automated = True
task.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
tex = unreal.EditorAssetLibrary.load_asset(REF + "/T_Berezovka_Plan")
assert tex
mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Berezovka_Plan", REF, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property("two_sided", True)
lib = unreal.MaterialEditingLibrary
def node(cls, x=0,y=0):
    return lib.create_material_expression(mat, cls, x,y)
def constant(v):
    n=node(unreal.MaterialExpressionConstant); n.set_editor_property("r",v); return n
def connect(a,b,input_name, output=""):
    assert lib.connect_material_expressions(a,output,b,input_name)
# Full source image sampled using world coordinates. +X north, +Y east.
pos=node(unreal.MaterialExpressionWorldPosition)
def channel(mask):
    n=node(unreal.MaterialExpressionComponentMask)
    n.set_editor_property("r",mask=="r"); n.set_editor_property("g",mask=="g")
    connect(pos,n,""); return n
def affine(source,mult,offset):
    m=node(unreal.MaterialExpressionMultiply); connect(source,m,"A"); connect(constant(mult),m,"B")
    a=node(unreal.MaterialExpressionAdd); connect(m,a,"A"); connect(constant(offset),a,"B"); return a
cm_per_pixel=20000.0/155.0
u=affine(channel("g"),1.0/(cm_per_pixel*1280),457.0/1280)
v=affine(channel("r"),-1.0/(cm_per_pixel*960),837.0/960)
uv=node(unreal.MaterialExpressionAppendVector); connect(u,uv,"A"); connect(v,uv,"B")
sample=node(unreal.MaterialExpressionTextureSample); sample.set_editor_property("texture",tex)
connect(uv,sample,lib.get_material_expression_input_names(sample)[0])
assert lib.connect_material_property(sample,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
lib.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.new_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
plane=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(8645.16129,4516.12903,0))
plane.set_actor_label("REF_Berezovka_Plan_200m_per_155px")
plane.set_folder_path("00_Reference")
comp=plane.static_mesh_component
comp.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Plane"))
comp.set_material(0,mat)
plane.set_actor_scale3d(unreal.Vector(340*cm_per_pixel/100,960*cm_per_pixel/100,1))
comp.set_collision_profile_name("BlockAll")
plane.tags=["ReferenceOnly","Scale_1px_1.29032258m"]
start=actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,110),unreal.Rotator(pitch=0,yaw=90,roll=0))
start.set_actor_label("PlayerStart_STOP01_Temporary")
start.set_folder_path("01_Gameplay")
start.tags=["STOP-01","Temporary"]
for label,px,py in [("Scale_0m",35,632),("Scale_200m",190,632),("North_CHAPEL01",696,650)]:
    marker=actors.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector((837-py)*cm_per_pixel,(px-457)*cm_per_pixel,30))
    marker.set_actor_label(label); marker.set_folder_path("00_Reference/Calibration")
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property("default_game_mode",unreal.load_class(None,"/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode.BP_FirstPersonGameMode_C"))
assert levels.save_current_level()
assert levels.load_level(MAP)
saved=actors.get_all_level_actors()
assert len([a for a in saved if isinstance(a,unreal.PlayerStart)])==1
points={a.get_actor_label():a.get_actor_location() for a in saved}
distance=(points["Scale_0m"]-points["Scale_200m"]).length()
assert abs(distance-20000)<0.1
report={"map":MAP,"cm_per_pixel":cm_per_pixel,"scale_pixels":[[35,632],[190,632]],"scale_distance_cm":distance,"crop_pixels":[12,600,972,940],"stop_pixel":[457,837],"player_start_cm":[0,0,110],"north":"+X","east":"+Y","width_m":960*cm_per_pixel/100,"height_m":340*cm_per_pixel/100,"saved_and_reloaded":True,"houses":False,"terrain":False}
with open(ROOT+"/Scripts/Berezovka_validation.json","w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
unreal.log("BEREZOVKA_LEVEL_OK "+json.dumps(report))



