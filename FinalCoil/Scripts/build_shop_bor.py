import unreal,math,json
ROOT="D:/GameDevelop/FinalCoil"
BASE="/Game/FinalCoil/Maps/L_Berezovka_Stop_G01"
OUT="/Game/FinalCoil/Maps/L_Berezovka_Shop_Bor"
DEST="/Game/FinalCoil/World/ShopAndBor"
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if ed.get_editor_world().get_name()!="L_Berezovka_Stop_G01":assert levels.load_level(BASE)
assert levels.save_current_level()
assert not unreal.EditorAssetLibrary.does_asset_exist(OUT)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorAssetLibrary.make_directory(DEST)
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
mats={k:mat(k,v) for k,v in {"Wood":(.26,.14,.055),"Roof":(.13,.18,.20),"Floor":(.24,.25,.21),"Path":(.47,.30,.13),"Pine":(.035,.15,.075),"Trunk":(.20,.095,.035),"Sign":(.46,.30,.12),"Rock":(.23,.26,.27),"Window":(.21,.36,.38)}.items()}
cube=unreal.load_asset("/Engine/BasicShapes/Cube")
cyl=unreal.load_asset("/Engine/BasicShapes/Cylinder")
cone=unreal.load_asset("/Engine/BasicShapes/Cone")
sphere=unreal.load_asset("/Engine/BasicShapes/Sphere")
def shape(label,p,size,kind,folder,model=cube,collision=True,yaw=0,roll=0):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p),unreal.Rotator(pitch=0,yaw=yaw,roll=roll))
    a.set_actor_label(label);a.set_folder_path(folder);a.tags=["ShopBorV1"]
    c=a.static_mesh_component;c.set_static_mesh(model);c.set_material(0,mats[kind]);c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));return a
def text(label,value,p,size=40,yaw=180):
    a=actors.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector(*p),unreal.Rotator(pitch=0,yaw=yaw,roll=0))
    a.set_actor_label(label);a.set_folder_path("72_Wayfinding");a.tags=["ShopBorV1"]
    a.text_render.set_text(value);a.text_render.set_world_size(size)
    a.text_render.set_text_render_color(unreal.Color(255,245,210,255))
def loc(px,py):return ((447-py)*1000/3,(px-410)*1000/3)
# Shop adjacent to endpoint of ShopPath and StopToShop.
SC=(6010,-15000)
def shop(n,x,y,z,sx,sy,sz,kind="Wood",roll=0):
    return shape("SHOP01_"+n,(SC[0]+x,SC[1]+y,z),(sx,sy,sz),kind,"70_SHOP01",roll=roll)
shop("Floor",0,0,0,570,640,10,"Floor")
shop("BackWall",275,0,152.5,20,640,295)
shop("WallL",0,-310,152.5,530,20,295)
shop("WallR",0,310,152.5,530,20,295)
shop("FrontL",-275,-190,152.5,20,220,295)
shop("FrontR",-275,190,152.5,20,220,295)
shop("EntranceHeader",-275,0,267.5,20,160,65)
angle=math.degrees(math.atan2(100,340))
shop("RoofL",0,-170,350,620,357,10,"Roof",roll=-angle)
shop("RoofR",0,170,350,620,357,10,"Roof",roll=angle)
shop("Approach",-470,0,4,390,180,2,"Path")
shop("Counter",45,-50,52.5,65,450,95)
shop("StorageShelf",220,-120,100,45,280,190)
shop("WindowL",-287,-205,160,3,110,100,"Window")
shop("WindowR",-287,205,160,3,110,100,"Window")
shop("SignBoard",-290,0,255,8,300,42,"Sign")
text("SHOP01_FacadeSign","SHOP-01",(SC[0]-296,SC[1]-130,250),36)
# Chapel marker, 12m off existing trail, with a simple volume and cross.
CP=(35000,-27800)
house=unreal.load_asset("/Game/FinalCoil/World/Homesteads/SM_LogHouse_Blockout")
chap=shape("CHAPEL01_Blockout",(CP[0],CP[1],6),(100,100,100),"Wood","71_OldBor/Chapel",model=house,yaw=180)
chap.set_actor_scale3d(unreal.Vector(600/1100,400/900,.70))
shape("CHAPEL01_Porch",(CP[0]-380,CP[1],15),(180,200,20),"Wood","71_OldBor/Chapel")
shape("CHAPEL01_CrossVertical",(CP[0],CP[1],435),(12,12,160),"Wood","71_OldBor/Chapel",collision=False)
shape("CHAPEL01_CrossBar",(CP[0],CP[1],466),(12,95,12),"Wood","71_OldBor/Chapel",collision=False)
text("CHAPEL01_Name","CHAPEL-01",(CP[0]-420,CP[1]-170,200),35)
def segment(label,p,q,width=200):
    dx=q[0]-p[0];dy=q[1]-p[1]
    return shape(label,((p[0]+q[0])/2,(p[1]+q[1])/2,5),(math.hypot(dx,dy)+30,width,2),"Path","71_OldBor/Trail",yaw=math.degrees(math.atan2(dy,dx)))
# Short entrance section follows the existing centerline, 126m around chapel.
trail=[loc(323,350),loc(323,342),loc(306,317)]
for i,(p,q) in enumerate(zip(trail,trail[1:])):segment("BOR_EntranceTrail_%02d"%i,p,q)
segment("CHAPEL01_Access",(CP[0]-420,CP[1]),(CP[0]-420,-29000))
fork=trail[-1]
spur=(fork[0]+1200,fork[1]-2600)
segment("BOR_ForkShortSpur",fork,spur,180)
# Low polygon pines, trunks solid but clear walking corridor kept at least 4m.
trees=[]
def pine(name,x,y,height=1300):
    shape(name+"_Trunk",(x,y,height*.30),(45,45,height*.60),"Trunk","71_OldBor/Trees",model=cyl)
    shape(name+"_Crown",(x,y,height*.70),(420,420,height*.75),"Pine","71_OldBor/Trees",model=cone,collision=False)
    trees.append((x,y))
for i in range(16):
    t=(i+.5)/16
    a,b=trail[1],trail[2]
    x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
    side=1 if i%2 else -1
    offset=550+(i%3)*120
    pine("BOR_Pine_%02d"%i,x-side*dy/length*offset,y+side*dx/length*offset,1200+(i%4)*130)
for i,(x,y) in enumerate([(CP[0]+600,CP[1]-550),(CP[0]+700,CP[1]+300),(CP[0]-200,CP[1]+650)]):
    pine("CHAPEL01_OldPine_%d"%i,x,y,1900+i*100)
shape("BOR_ForkBoulder",(spur[0]+280,spur[1]+180,110),(360,260,220),"Rock","71_OldBor/Landmarks",model=sphere)
# Wayfinding stays next to route, never on centerline.
signs=[("VillageJunction",loc(350,447),["SHOP-01","CHAPEL-01 / BOR"]),
("ShopSplit",loc(397,440),["SHOP-01","STOP-01"]),
("ChapelFork",loc(323,342),["CHAPEL-01","BOR"]),
("ForestFork",fork,["BOR","BOULDER"])]
for ident,p,labels in signs:
    x,y=p[0]+150,p[1]+240
    shape("SIGN_"+ident+"_Post",(x,y,120),(15,15,240),"Trunk","72_Wayfinding")
    for j,value in enumerate(labels):
        z=210-j*50
        shape("SIGN_"+ident+"_"+str(j),(x-4,y,z),(12,220,38),"Sign","72_Wayfinding")
        text("SIGN_"+ident+"_Text"+str(j),value,(x-12,y-100,z-10),22)
        # Colored end notch distinguishes the two directions.
        shape("SIGN_"+ident+"_Arrow"+str(j),(x-5,y+120 if j==0 else y-120,z),(12,35,35),"Sign","72_Wayfinding",yaw=45)
world=ed.get_editor_world()
def clear(p,q):
    result=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(*p),unreal.Vector(*q),42,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
    assert result is None,"Blocked route "+str(result)
clear((SC[0]-650,SC[1],110),(SC[0]-80,SC[1],110))
for p,q in zip(trail,trail[1:]):clear((*p,110),(*q,110))
clear((*fork,110),(*spur,110))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,OUT)
assert levels.load_level(OUT)
saved=actors.get_all_level_actors();names={a.get_actor_label() for a in saved}
assert "SHOP01_Counter" in names and "CHAPEL01_Blockout" in names
assert len([n for n in names if n.startswith("SIGN_") and n.endswith("_Post")])==4
assert len([n for n in names if n.startswith("BOR_Pine_") and n.endswith("_Trunk")])==16
assert "G01_Garage_Floor" in names
assert len([n for n in names if n.endswith("_LogHouse")])==19
report={"map":OUT,"shop_entrance_clear":True,"forest_capsule_sweeps_clear":True,"trail_section_m":sum(math.dist(p,q) for p,q in zip(trail,trail[1:]))/100,"wayfinding_forks":4,"trees":len(trees),"chapel_marker":True,"saved_reloaded":True}
json.dump(report,open(ROOT+"/Scripts/Shop_Bor_validation.json","w"),indent=2)
ed.set_level_viewport_camera_info(unreal.Vector(SC[0]-1100,SC[1]-950,650),unreal.Rotator(pitch=-18,yaw=43,roll=0))
unreal.log("SHOP_BOR_OK "+json.dumps(report))
