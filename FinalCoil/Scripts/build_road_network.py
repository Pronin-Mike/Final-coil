import unreal, math, json
ROOT="D:/GameDevelop/FinalCoil"
MAP="/Game/FinalCoil/Maps/L_Berezovka_Region_Blockout"
DEST="/Game/FinalCoil/Maps/RegionBlockout"
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(MAP)
assert not any("RoadNetworkV1" in [str(t) for t in a.tags] for a in actors.get_all_level_actors()),"Network already installed"
cube=unreal.load_asset("/Engine/BasicShapes/Cube")
cyl=unreal.load_asset("/Engine/BasicShapes/Cylinder")
S=1000/3
def loc(p,z):return unreal.Vector((447-p[1])*S,(p[0]-410)*S,z)
def material(name,color):
    path=DEST+"/M_"+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):return unreal.load_asset(path)
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_"+name,DEST,unreal.Material,unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
    e.set_editor_property("constant",unreal.LinearColor(*color))
    assert unreal.MaterialEditingLibrary.connect_material_property(e,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(m)
    assert unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m
mats={"Road":material("RoadNetwork_Dirt",(.43,.30,.17)),"Path":material("RoadNetwork_Footpath",(.77,.62,.34)),"Rail":material("RoadNetwork_RailCorridor",(.28,.30,.36))}
# Lower schematic land-use masses into flat overlays so walking routes are readable
# without suspended roads or invisible overhead forest volumes.
removed=[]
for a in actors.get_all_level_actors():
    label=a.get_actor_label()
    if label.startswith(("MainRoad_","LakeRoad_","NorthRoad_","NarrowGauge_")):
        removed.append(label); assert actors.destroy_actor(a)
    elif label.startswith(("Village_Berezovka_Footprint","Forest_Mass_","OldBor_Mass_")):
        scale=a.get_actor_scale3d(); a.set_actor_scale3d(unreal.Vector(scale.x,scale.y,.01))
        p=a.get_actor_location(); a.set_actor_location(unreal.Vector(p.x,p.y,1),False,False)
net=[
("MainRoad",[(12,532),(140,497),(280,451),(350,447),(410,447),(455,439.08),(468,436.792),(535,425),(670,371),(793,358),(915,382),(1022,430),(1168,449),(1220,417)],7,"Road"),
("LakeRoad",[(1220,417),(1230,350),(1203,281),(1204,207),(1160,152),(1091,130)],7,"Road"),
("NorthRoad",[(468,436.792),(515,354),(554,266),(620,207),(714,153),(753,119),(765,91)],6,"Road"),
("GrandpaDrive",[(455,439.08),(460,451),(459,460),(457,464)],4,"Road"),
("ShopPath",[(350,447),(359,440),(365,430)],2,"Path"),
("StopToShop",[(410,447),(397,440),(379,435),(365,430)],2,"Path"),
("OldBorPath",[(350,447),(345,418),(330,395),(323,370),(323,342),(306,317),(284,294),(270,268),(245,240),(245,210)],2,"Path"),
("GrandpaFootpath",[(410,447),(430,455),(449,462),(457,464)],2,"Path"),
("RailCorridor",[(90,91),(190,78),(310,82),(480,106),(600,101),(750,82),(850,70),(958,75),(1100,92),(1265,105)],10,"Rail"),
("RailPassingLoop",[(1035,84.1),(1063,115),(1091,130),(1130,119),(1160,97.09)],10,"Rail")]
report=[]
def piece(label,p,length,width,yaw,kind,round_joint=False):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,loc(p,3),unreal.Rotator(pitch=0,yaw=yaw,roll=0))
    a.set_actor_label(label); a.set_folder_path("20_Routes/"+kind)
    a.tags=["RoadNetworkV1",kind]
    c=a.static_mesh_component; c.set_static_mesh(cyl if round_joint else cube); c.set_material(0,mats[kind])
    c.set_collision_profile_name("NoCollision" if kind=="Rail" else "BlockAll")
    a.set_actor_scale3d(unreal.Vector(length,width,.04))
    return a
for name,pts,width,kind in net:
    labels=[]
    for i,(p,q) in enumerate(zip(pts,pts[1:])):
        d=loc(q,0)-loc(p,0)
        length=d.length()/100
        label="NET_"+name+"_%02d"%i
        piece(label,((p[0]+q[0])/2,(p[1]+q[1])/2),length,width,math.degrees(math.atan2(d.y,d.x)),kind)
        labels.append(label)
    for i,p in enumerate(pts):
        # Circular joins close any wedge between rotated rectangular segments.
        piece("JOIN_"+name+"_%02d"%i,p,width,width,0,kind,True)
    report.append({"name":name,"width_m":width,"length_m":sum(math.dist(p,q)*S/100 for p,q in zip(pts,pts[1:])),"points_px":pts,"segments":labels})
for ident,p in [("SHOP01_Provisional",(365,430)),("G01_GrandpaEntrance_Provisional",(457,464))]:
    a=actors.spawn_actor_from_class(unreal.TargetPoint,loc(p,100))
    a.set_actor_label("POI_"+ident); a.set_folder_path("30_POI"); a.tags=["RoadNetworkV1","POI","Provisional"]
    t=actors.spawn_actor_from_class(unreal.TextRenderActor,loc(p,3000),unreal.Rotator(pitch=90,yaw=0,roll=0))
    t.set_actor_label("LABEL_"+ident); t.set_folder_path("40_Labels")
    t.text_render.set_text("Магазин" if ident.startswith("SHOP") else "Участок деда: въезд")
    t.text_render.set_world_size(1600);t.tags=["RoadNetworkV1"]
# Start is directly over the new road, capsule bottom remains above the 5 cm surface.
start=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.PlayerStart))
assert abs(start.get_actor_location().x)<1 and abs(start.get_actor_location().y)<1
MAP="/Game/FinalCoil/Maps/L_Berezovka_Region_Roads"
assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), MAP)
assert levels.load_level(MAP)
saved=actors.get_all_level_actors()
byname={a.get_actor_label():a for a in saved}
for r in report:
    for label in r["segments"]:
        c=byname[label].static_mesh_component
        assert str(c.get_collision_profile_name())==("NoCollision" if r["name"].startswith("Rail") else "BlockAll")
        assert abs(byname[label].get_actor_scale3d().y-r["width_m"])<.001
ground=next(a for a in saved if a.get_actor_label().startswith("Ground_"))
_,ext=ground.get_actor_bounds(False)
assert abs(4*ext.x*ext.y/1e10-7)<.001
assert len([a for a in saved if isinstance(a,unreal.PlayerStart)])==1
result={"map":MAP,"area_km2":7,"saved_reloaded":True,"routes":report,"replaced_actor_count":len(removed),"road_top_cm":5,"provisional_poi":True,"validation":"saved actors, widths, collision profiles, start and region area; no PIE"}
with open(ROOT+"/Scripts/Berezovka_roads_validation.json","w",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
unreal.log("ROAD_NETWORK_OK routes="+str(len(report)))

