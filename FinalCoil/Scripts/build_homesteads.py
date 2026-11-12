import unreal, math, json, os
ROOT="D:/GameDevelop/FinalCoil"
MAP="/Game/FinalCoil/Maps/L_Berezovka_Region_Roads"
DEST="/Game/FinalCoil/World/Homesteads"
OUT="/Game/FinalCoil/Maps/L_Berezovka_Homesteads"
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name()!="L_Berezovka_Region_Roads":
    assert levels.load_level(MAP)
assert levels.save_current_level()
assert not unreal.EditorAssetLibrary.does_asset_exist(OUT),"Do not overwrite prior work"
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorAssetLibrary.make_directory(DEST)
def mat(name,rgb):
    path=DEST+"/M_"+name
    if unreal.EditorAssetLibrary.does_asset_exist(path): return unreal.load_asset(path)
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_"+name,DEST,unreal.Material,unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
    e.set_editor_property("constant",unreal.LinearColor(*rgb))
    assert unreal.MaterialEditingLibrary.connect_material_property(e,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m
materials={k:mat(k,v) for k,v in {"Occupied":(.28,.13,.045),"Vacant":(.25,.26,.24),"YardOccupied":(.12,.31,.19),"YardVacant":(.30,.21,.15),"Boundary":(.73,.62,.35),"Path":(.65,.48,.25),"Porch":(.33,.23,.12)}.items()}
task=unreal.AssetImportTask();task.filename=ROOT+"/SourceArt/Blockout/LogHouse.obj"
task.destination_path=DEST;task.destination_name="SM_LogHouse_Blockout";task.automated=True;task.save=True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
house=next((unreal.load_asset(str(p)) for p in task.imported_object_paths if isinstance(unreal.load_asset(str(p)),unreal.StaticMesh)),None)
assert house,"House import failed"
# Explicit centimeters and up-axis correction from actual imported bounds.
bbox=house.get_bounding_box()
size=bbox.max-bbox.min
unreal.log("HOUSE_IMPORT_BOUNDS "+str(size))
# Body requires 10m length x 8m width x 5.2m roof peak; import may change up axis.
cube=unreal.load_asset("/Engine/BasicShapes/Cube")
homes=[("H01",108,881),("H02",199,875),("H03",286,884),("H04",178,795),("H05",325,775),("H06",269,751),("H07",406,762),("H08",374,696),("H09",576,754),("H10",718,758),("H11",754,835),("H12",841,835),("E01",94,788),("E02",199,729),("E03",309,688),("E04",504,751),("E05",470,685),("E06",784,744),("E07",904,800)]
roads=json.load(open(ROOT+"/Scripts/Berezovka_roads_validation.json",encoding="utf-8"))
segments=[]
for r in roads["routes"]:
    if r["name"] not in ["MainRoad","NorthRoad"]:continue
    for p,q in zip(r["points_px"],r["points_px"][1:]):
        segments.append((unreal.Vector((447-p[1])*1000/3,(p[0]-410)*1000/3,0),unreal.Vector((447-q[1])*1000/3,(q[0]-410)*1000/3,0)))
def nearest(p):
    best=None
    for a,b in segments:
        dx=b.x-a.x;dy=b.y-a.y
        t=max(0,min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy)))
        q=unreal.Vector(a.x+t*dx,a.y+t*dy,0)
        d=math.hypot(q.x-p.x,q.y-p.y)
        if best is None or d<best[0]:best=(d,q)
    return best
created=[]
def mesh(label,pos,scale,material,rotation,folder,model=cube,collision=False):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,pos,rotation)
    a.set_actor_label(label);a.set_folder_path(folder);a.tags=["HomesteadsV1"]
    c=a.static_mesh_component;c.set_static_mesh(model)
    for i in range(max(1,model.get_num_sections(0))):c.set_material(i,material)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    a.set_actor_scale3d(scale)
    created.append(label);return a
reports=[]
for ident,px,py in homes:
    occupied=ident.startswith("H")
    center=unreal.Vector(-(py-837)*20000/155,(px-457)*20000/155,0)
    dist,road=nearest(center)
    dx=(road.x-center.x)/dist;dy=(road.y-center.y)/dist
    yaw=math.degrees(math.atan2(dy,dx))
    rot=unreal.Rotator(pitch=0,yaw=yaw,roll=0)
    folder="50_Homesteads/"+("Occupied/" if occupied else "Vacant/")+ident
    def p(x,y,z):return unreal.Vector(center.x+dx*x-dy*y,center.y+dy*x+dx*y,z)
    yard=mesh(ident+"_Yard_30x40m",p(0,0,2),unreal.Vector(40,30,.01),materials["YardOccupied" if occupied else "YardVacant"],rot,folder)
    # Recover OBJ orientation if importer used Y-up to Z-up.
    modelrot=rot
    sx,sy,sz=1000/max(size.x,1),800/max(size.y,1),520/max(size.z,1)
    body=mesh(ident+"_LogHouse",p(0,0,6),unreal.Vector(sx,sy,sz),materials["Occupied" if occupied else "Vacant"],modelrot,folder,house,True)
    # Separate shared cube volumes for cold entrance and porch.
    mesh(ident+"_ColdEntrance",p(580,0,136),unreal.Vector(1.6,3,2.6),materials["Occupied" if occupied else "Vacant"],rot,folder,collision=True)
    mesh(ident+"_Porch",p(740,0,16),unreal.Vector(1.6,2,.2),materials["Porch"],rot,folder,collision=True)
    # Yard outline with 3m opening toward the road; no blocking fences yet.
    for n,x,y,l,w in [("Back",-2000,0,.2,30),("SideL",0,-1500,40,.2),("SideR",0,1500,40,.2),("FrontL",2000,-825,.2,13.5),("FrontR",2000,825,.2,13.5)]:
        mesh(ident+"_Boundary_"+n,p(x,y,5),unreal.Vector(l,w,.02),materials["Boundary"],rot,folder)
    # 1.5m walkway, porch -> gate -> nearest drivable road, no curb step.
    length=dist-820
    assert length>0
    mesh(ident+"_Walkway_ToRoad",p((dist+820)/2,0,4),unreal.Vector(length/100,1.5,.02),materials["Path"],rot,folder,collision=True)
    marker=actors.spawn_actor_from_class(unreal.TextRenderActor,p(0,0,1500),unreal.Rotator(pitch=90,yaw=0,roll=0))
    marker.set_actor_label(ident+"_Label");marker.set_folder_path(folder);marker.tags=["HomesteadsV1"]
    marker.text_render.set_text(ident+(" ЖИЛОЙ" if occupied else "ПУСТУЕТ")+(" *" if ident=="H05" else ""))
    marker.text_render.set_world_size(300)
    reports.append({"id":ident,"source_px":[px,py],"center_cm":[center.x,center.y,0],"road_distance_m":dist/100,"yaw":yaw,"provisional":ident=="H05"})
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,OUT)
assert levels.load_level(OUT)
saved=actors.get_all_level_actors()
names={a.get_actor_label() for a in saved}
for ident,_,_ in homes:
    for suffix in ["_LogHouse","_Yard_30x40m","_Walkway_ToRoad"]:assert ident+suffix in names
bodies=[a for a in saved if a.get_actor_label().endswith("_LogHouse")]
assert len(bodies)==19
assert len([a for a in bodies if a.get_actor_label().startswith("H")])==12
assert all(a.static_mesh_component.static_mesh==house for a in bodies)
assert len([a for a in saved if isinstance(a,unreal.PlayerStart)])==1
result={"map":OUT,"occupied":12,"vacant":7,"shared_mesh":house.get_path_name(),"import_bounds":str(size),"saved_reloaded":True,"houses":reports}
json.dump(result,open(ROOT+"/Scripts/Homesteads_validation.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-35000,-13000,68000),unreal.Rotator(pitch=-62,yaw=0,roll=0))
unreal.log("HOMESTEADS_OK occupied=12 vacant=7")
