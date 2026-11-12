import unreal,math,json
ROOT="D:/GameDevelop/FinalCoil"
BASE="/Game/FinalCoil/Maps/L_Berezovka_Homesteads"
OUT="/Game/FinalCoil/Maps/L_Berezovka_Stop_G01"
DEST="/Game/FinalCoil/World/StopAndG01"
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if ed.get_editor_world().get_name()!="L_Berezovka_Homesteads": assert levels.load_level(BASE)
assert levels.save_current_level()
assert not unreal.EditorAssetLibrary.does_asset_exist(OUT),"Existing result must be reviewed"
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorAssetLibrary.make_directory(DEST)
cube=unreal.load_asset("/Engine/BasicShapes/Cube")
def mat(name,rgb):
    path=DEST+"/M_"+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):return unreal.load_asset(path)
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_"+name,DEST,unreal.Material,unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
    e.set_editor_property("constant",unreal.LinearColor(*rgb))
    assert unreal.MaterialEditingLibrary.connect_material_property(e,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m
mats={k:mat(k,c) for k,c in {"Timber":(.24,.12,.045),"WoodDark":(.12,.065,.025),"MetalRoof":(.13,.17,.19),"Floor":(.24,.25,.23),"Path":(.55,.39,.20),"Reserved":(.13,.40,.48),"House":(.35,.20,.09),"Yard":(.20,.30,.17)}.items()}
made=[]
def box(label,center,size,kind,folder,yaw=0,roll=0,collision=True,model=cube):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*center),unreal.Rotator(pitch=0,yaw=yaw,roll=roll))
    a.set_actor_label(label);a.set_folder_path(folder);a.tags=["StopG01V1"]
    c=a.static_mesh_component;c.set_static_mesh(model);c.set_material(0,mats[kind]);c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));made.append(a);return a
# Stop: open front points south toward road. Original stop POI and start retained.
stop=(700,0)
def sb(name,x,y,z,sx,sy,sz,kind="Timber",collision=True):
    return box("STOP01_"+name,(stop[0]+x,stop[1]+y,z),(sx,sy,sz),kind,"60_Stop01",collision=collision)
sb("Pad",0,0,0,210,330,10,"Floor")
for x in [-80,80]:
    for y in [-140,140]:sb("Post_%s_%s"%(x,y),x,y,125,14,14,240)
sb("BackWall",85,0,115,12,285,220)
sb("SideWall",0,-145,115,170,12,220)
sb("Roof",0,0,248,230,350,16,"MetalRoof")
sb("BenchSeat",45,0,48,42,240,8)
sb("BenchBack",70,0,80,8,240,65)
for y in [-95,95]:sb("BenchLeg_"+str(y),45,y,25,28,12,42,"WoodDark")
sb("RoadApproach",-230,0,4,270,180,2,"Path")
# Slat accents keep basic timber construction readable at close distance.
for z in range(25,215,25):sb("BackSlat_"+str(z),77,0,z,2,280,3,"WoodDark",False)
# G01: common yard, distinct grandfather house and workshop.
box("G01_Yard",(-7350,15500,2),(4000,3000,1),"Yard","61_G01",collision=False)
house=unreal.load_asset("/Game/FinalCoil/World/Homesteads/SM_LogHouse_Blockout")
assert house
box("G01_House",(-6700,14600,6),(100/11*10,100/9*8,100),"House","61_G01/House",model=house)
# Correct scale is dimensionless when using shared imported 1100x900x520cm mesh.
made[-1].set_actor_scale3d(unreal.Vector(1000/1100,800/900,1))
box("G01_HouseEntrance",(-6120,14600,136),(160,280,260),"Timber","61_G01/House")
box("G01_HousePorch",(-5960,14600,16),(160,180,20),"WoodDark","61_G01/House")
# Garage local -X is open front, +X is back; yaw=180, depth 900 width 700 clear.
GC=(-8000,16300);YAW=180
def gp(x,y,z):return (GC[0]-x,GC[1]-y,z)
def gb(name,x,y,z,sx,sy,sz,kind="Timber",collision=True,roll=0):
    return box("G01_Garage_"+name,gp(x,y,z),(sx,sy,sz),kind,"61_G01/Garage",yaw=YAW,roll=roll,collision=collision)
gb("Floor",0,0,0,940,740,10,"Floor")
gb("BackWall",460,0,167.5,20,740,325)
gb("LeftWall",0,-360,167.5,900,20,325)
# Right wall contains 110cm side door from local x=45 to155.
gb("RightWallFront",-202.5,360,167.5,495,20,325)
gb("RightWallBack",302.5,360,167.5,295,20,325)
gb("SideDoorHeader",100,360,277.5,110,20,105)
# Main gate opening y=-160..160, clear height 280cm above finished floor.
gb("FrontWallL",-460,-255,167.5,20,190,325)
gb("FrontWallR",-460,255,167.5,20,190,325)
gb("GateHeader",-460,0,307.5,20,320,45)
roofroll=math.degrees(math.atan2(140,380))
gb("RoofLeft",0,-190,400,980,405,10,"MetalRoof",roll=-roofroll)
gb("RoofRight",0,190,400,980,405,10,"MetalRoof",roll=roofroll)
# Mark future car parking by flat outline only: 2.2 x4.8m; interior stays empty.
for name,x,y,sx,sy in [("Front",-240,0,4,220),("Back",240,0,4,220),("Left",0,-110,480,4),("Right",0,110,480,4)]:
    gb("FutureCar_"+name,x,y,5.8,sx,sy,1,"Reserved",False)
for z in range(25,315,25):
    gb("LogJoint_Back_"+str(z),448,0,z,2,695,3,"WoodDark",False)
    gb("LogJoint_Left_"+str(z),0,-348,z,895,2,3,"WoodDark",False)
def path(name,p,q,width):
    dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
    box(name,((p[0]+q[0])/2,(p[1]+q[1])/2,4),(length,width,2),"Path","61_G01/Approaches",yaw=math.degrees(math.atan2(dy,dx)))
path("G01_GarageDrive",(-5666.6667,15666.6667),gp(-500,0,0),400)
path("G01_SideDoorPath",gp(100,470,0),gp(100,200,0),110)
path("G01_HouseWalk",(-5666.6667,15666.6667),(-5860,14600),150)
# Move temporary start off carriageway in front of shelter.
start=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.PlayerStart))
start.set_actor_location(unreal.Vector(450,0,112),False,False)
start.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False)
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



