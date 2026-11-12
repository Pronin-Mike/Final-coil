import unreal, json, math
ROOT="D:/GameDevelop/FinalCoil"
MAP="/Game/FinalCoil/Maps/L_Berezovka_Region_Blockout"
ASSETS="/Game/FinalCoil/Maps/RegionBlockout"
assert not unreal.EditorAssetLibrary.does_asset_exist(MAP), "Do not overwrite an existing region"
unreal.EditorAssetLibrary.make_directory(ASSETS)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.new_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# Upper regional scheme crop: 1260 x 500 px, uniform scale 3.333333 m/px.
# Bounds 4200 x 1666.666667 m = exactly 7 km2. North +X, east +Y.
S=1000.0/3
def loc(px,py,z=0): return unreal.Vector((447-py)*S,(px-410)*S,z)
palette={"Ground":(.18,.22,.13),"Village":(.65,.40,.15),"Lake":(.06,.32,.65),"Forest":(.13,.30,.13),"OldBor":(.035,.12,.07),"Road":(.55,.49,.35),"Marker":(.95,.65,.08),"Rail":(.23,.23,.26)}
mats={}
for name,rgb in palette.items():
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_"+name,ASSETS,unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    n=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector)
    n.set_editor_property("constant",unreal.LinearColor(*rgb))
    assert unreal.MaterialEditingLibrary.connect_material_property(n,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mats[name]=mat
cube=unreal.load_asset("/Engine/BasicShapes/Cube")
cyl=unreal.load_asset("/Engine/BasicShapes/Cylinder")
records=[]
def shape(label,px,py,width_m,depth_m,height_m,kind,folder="10_Zones",mesh=None,zbase=0,collision=False):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,loc(px,py,zbase+height_m*50))
    a.set_actor_label(label); a.set_folder_path(folder)
    a.static_mesh_component.set_static_mesh(mesh or cube)
    a.static_mesh_component.set_material(0,mats[kind])
    a.static_mesh_component.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    a.set_actor_scale3d(unreal.Vector(depth_m,width_m,height_m))
    a.tags=["RegionalBlockout",kind]
    records.append({"label":label,"pixel":[px,py],"position_cm":list(a.get_actor_location().to_tuple())})
    return a
shape("Ground_4200m_x_1666m_7km2",642,308,4200,500*S/100,2,"Ground","00_Base",zbase=-200,collision=True)
# Broad schematic masses, no buildings or sculpted terrain.
shape("Village_Berezovka_Footprint",393,423,1010,420,.5,"Village",mesh=cyl,zbase=5)
for i,(px,py,w,d) in enumerate([(948,206,1240,600),(910,260,930,560),(1012,238,700,570)]):
    shape("Lake_Mass_%02d"%i,px,py,w,d,.4,"Lake",mesh=cyl,zbase=70)
forests=[(160,200,770,600),(242,297,940,640),(89,390,400,410),(550,120,600,230),(550,295,410,300),(630,492,480,300),(1140,500,650,290),(1190,197,350,390)]
for i,(px,py,w,d) in enumerate(forests):
    old=i in [0,1,2]
    shape(("OldBor" if old else "Forest")+"_Mass_%02d"%i,px,py,w,d,12 if old else 7,"OldBor" if old else "Forest",mesh=cyl,zbase=0)
def segment(label,p,q,width_m,kind):
    mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
    length=math.dist(p,q)*S/100
    a=shape(label,*mid,width_m,length,.2,kind,"20_Routes",zbase=140)
    delta=loc(*q)-loc(*p)
    a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(delta.y,delta.x)),roll=0),False)
def route(name,pts,width,kind="Road"):
    for i in range(len(pts)-1): segment(name+"_%02d"%i,pts[i],pts[i+1],width,kind)
route("MainRoad",[(12,532),(140,497),(280,451),(410,447),(535,425),(670,371),(793,358),(915,382),(1022,430),(1168,449),(1220,417)],9)
route("LakeRoad",[(1220,417),(1230,350),(1203,281),(1204,207),(1160,152),(1091,130)],7)
route("NorthRoad",[(468,442),(515,354),(554,266),(620,207),(714,153),(753,119),(765,91)],7)
route("NarrowGauge",[(90,91),(190,78),(310,82),(480,106),(600,101),(750,82),(850,70),(958,75),(1100,92),(1265,105)],4,"Rail")
markers=[("CHAPEL01_Chapel",323,342,"Часовня"),("DPS01_OldTrafficPost",140,500,"Пост ДПС"),("SAWMILL01",1142,395,"Лесопилка"),("RAIL01_PassingLoop",1091,130,"Разъезд УЖД"),("EXIT01_DistrictCentre",35,523,"Выезд к райцентру"),("STOP01_Temporary",410,447,"Остановка"),("OLD_BOR",245,210,"Старый Бор"),("LAKE",936,220,"Озеро"),("BEREZOVKA",390,405,"Берёзовка")]
for ident,px,py,text in markers:
    shape("MARK_"+ident,px,py,8,8,24,"Marker","30_POI",mesh=cyl,zbase=200)
    p=actors.spawn_actor_from_class(unreal.TargetPoint,loc(px,py,2800))
    p.set_actor_label("POI_"+ident); p.set_folder_path("30_POI")
    p.tags=["POI",ident]
    t=actors.spawn_actor_from_class(unreal.TextRenderActor,loc(px,py,3400),unreal.Rotator(pitch=90,yaw=0,roll=0))
    t.set_actor_label("LABEL_"+ident); t.set_folder_path("40_Labels")
    t.text_render.set_text(text)
    t.text_render.set_world_size(2200)
    t.text_render.set_text_render_color(unreal.Color(255,235,160,255))
start=actors.spawn_actor_from_class(unreal.PlayerStart,loc(410,447,112),unreal.Rotator(pitch=0,yaw=90,roll=0))
start.set_actor_label("PlayerStart_STOP01_Temporary"); start.set_folder_path("01_Gameplay")
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property("default_game_mode",unreal.load_class(None,"/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode.BP_FirstPersonGameMode_C"))
assert levels.save_current_level()
assert levels.load_level(MAP)
saved=actors.get_all_level_actors()
assert len([a for a in saved if isinstance(a,unreal.PlayerStart)])==1
names={a.get_actor_label() for a in saved}
for ident,px,py,text in markers: assert "POI_"+ident in names
ground=next(a for a in saved if a.get_actor_label().startswith("Ground_"))
origin,extent=ground.get_actor_bounds(False)
area=4*extent.x*extent.y/1e10
assert abs(area-7)<.001,area
report={"map":MAP,"area_km2":area,"width_m":4200,"height_m":500*S/100,"meters_per_pixel":S/100,"source_crop":[12,58,1272,558],"stop_pixel":[410,447],"north":"+X","east":"+Y","actor_count":len(saved),"poi":[m[0] for m in markers],"saved_reloaded":True,"forms":records}
with open(ROOT+"/Scripts/Berezovka_region_validation.json","w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
unreal.log("REGION_BLOCKOUT_OK area_km2="+str(area)+" actors="+str(len(saved)))

