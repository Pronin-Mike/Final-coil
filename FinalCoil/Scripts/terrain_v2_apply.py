import unreal,sys,os,json,math,importlib
ROOT="D:/GameDevelop/FinalCoil";sys.path.insert(0,ROOT+"/Scripts")
req=json.load(open(ROOT+"/Scripts/terrain_stage_request.json",encoding="utf-8-sig"))
phase=req["phase"]
T=importlib.reload(importlib.import_module("terrain_profile"))
oldT=importlib.reload(importlib.import_module(req["old_module"]))
oldT.GRID=json.load(open(req["old_grid"]))
# Reload T independently when the phase modules share helpers.
T.GRID=json.load(open(ROOT+"/SourceArt/Terrain/heightfield.json"))
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert ed.get_editor_world().get_name()=="L_Berezovka_Terrain"
assert levels.save_current_level()
DEST="/Game/FinalCoil/World/Terrain"
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
original_xy={n:[a.get_actor_location().x,a.get_actor_location().y] for n,a in by.items()}
oldpad={p[0]:p[7] for p in oldT.PADS};newpad={p[0]:p[7] for p in T.PADS}
assets=[("Terrain","SM_Berezovka_Terrain"),("Road","SM_Conform_Road"),("Path","SM_Conform_Path"),("Rail","SM_Conform_Rail"),("Forest","SM_Forest_Zones"),("OldBor","SM_OldBor_Zone")]
for key,name in assets:
    a=by["TERRAIN_"+key];m=a.static_mesh_component.get_material(0)
    task=unreal.AssetImportTask();task.filename=ROOT+"/SourceArt/Terrain/"+name+".obj";task.destination_path=DEST;task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.load_asset(DEST+"/"+name);assert mesh
    ns=mesh.get_editor_property("nanite_settings");ns.enabled=False;mesh.set_editor_property("nanite_settings",ns)
    body=mesh.get_editor_property("body_setup");body.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property("double_sided_geometry",True)
    mesh.set_material(0,m);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,m)
    a.set_actor_scale3d(unreal.Vector(1,-1,1))
    a.static_mesh_component.set_collision_profile_name("NoCollision" if key in ["Forest","OldBor"] else "BlockAll")
moves=[]
for name,a in by.items():
    if name.startswith(("TERRAIN_","Terrain_")) or name.startswith("Lake_Mass_"):continue
    if not isinstance(a,(unreal.StaticMeshActor,unreal.PlayerStart,unreal.TextRenderActor,unreal.TargetPoint)):continue
    p=a.get_actor_location();key=name.split("_")[0]
    oldh=oldpad[key] if key in oldpad else oldT.height(p.x,p.y)
    newh=newpad[key] if key in newpad else T.height(p.x,p.y)
    a.set_actor_location(unreal.Vector(p.x,p.y,p.z+newh-oldh),False,False)
    moves.append({"label":name,"old_datum":oldh,"new_datum":newh})
    if name.startswith(("MARK_","LABEL_")):a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
# Quantitative native collision validation of the rebuilt road support and entry apertures.
world=ed.get_editor_world()
manifest=json.load(open(ROOT+"/SourceArt/Terrain/manifest.json"))
miss=[];checked=0;road_error=0
for r in manifest["routes"]:
    p,q=r["p"],r["q"];steps=max(1,math.ceil(math.dist(p,q)/500))
    for i in range(steps+1):
        x=p[0]+(q[0]-p[0])*i/steps;y=p[1]+(q[1]-p[1])*i/steps;z=T.height(x,y)
        hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,z+90),unreal.Vector(x,y,z-100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
        checked+=1
        if hit is None:miss.append([x,y])
        elif hit.to_tuple()[9].get_actor_label().startswith("TERRAIN_"):road_error=max(road_error,abs(hit.to_tuple()[5].z-z))
assert not miss,str(miss[:5])
entries=[("garage_main",[-7200,16300],[-8200,16300]),("garage_side",[-8100,15800],[-8100,16080]),("shop",[5360,-15000],[5930,-15000]),("stop",[430,0],[650,0])]
for name,p,q in entries:
    z=max(T.height(*p),T.height(*q))+110
    hit=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(*p,z),unreal.Vector(*q,z),42,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
    assert hit is None,"Entry blocked: "+name
# Lake bed is tested below the non-colliding water surface, not against a visual disk.
lake=[]
for x,y in [(62333,166666),(62333,123000),(80333,179333),(100000,185000)]:
    z=T.height(x,y)
    hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,-200),unreal.Vector(x,y,-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
    assert hit is not None,"Missing underwater bed"
    hz=hit.to_tuple()[5].z
    assert abs(hz-z)<.2,(hz,z)
    lake.append({"xy":[x,y],"bed_cm":hz,"water_cm":-250,"depth_cm":-250-hz})
for name,xy in original_xy.items():
    p=by[name].get_actor_location();assert math.hypot(p.x-xy[0],p.y-xy[1])<.001
assert len([n for n in by if n.endswith("_LogHouse")])==19
assert abs(by["G01_Garage_Floor"].get_actor_rotation().pitch)<.001
for path in unreal.EditorAssetLibrary.list_assets(DEST,recursive=True,include_folder=False):unreal.EditorAssetLibrary.save_asset(path,only_if_is_dirty=False)
assert levels.save_current_level()
json.dump({"phase":phase,"xy_preserved":True,"surface_samples":checked,"missing_collision":miss,"road_mesh_offset_max_cm":road_error,"clear_entries":[e[0] for e in entries],"lake_bed_samples":lake,"moves":moves,"garage_inside_m":[7,9],"pit":False},open(ROOT+"/Review/TerrainV2/"+phase+"/native_checks.json","w"),indent=2)
if phase=="after":
    section=[]
    for yy in range(110000,243001,500):
        hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(62333,yy,2500),unreal.Vector(62333,yy,-4000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
        assert hit is not None,"Missing collision along lake transect"
        z=hit.to_tuple()[5].z
        assert abs(z-T.height(62333,yy))<10
        section.append({"distance_m":(yy-110000)/100,"x_cm":62333,"y_cm":yy,"ground_m":z/100,"water_m":-2.5})
    json.dump({"section_x_cm":62333,"samples":section,"source":"Native UE collision traces through final terrain and lake bed"},open(ROOT+"/Review/TerrainV2/lake_section.json","w"),indent=2)
unreal.log("TERRAIN_V2_STAGE_OK "+phase)

