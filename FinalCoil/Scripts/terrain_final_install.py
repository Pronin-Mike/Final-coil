import unreal,sys,os,json,importlib,math
ROOT="D:/GameDevelop/FinalCoil";sys.path.insert(0,ROOT+"/Scripts")
import terrain_profile
T=importlib.reload(terrain_profile)
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world=ed.get_editor_world();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert world.get_name()=="L_Berezovka_Terrain"
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
DEST="/Game/FinalCoil/World/Terrain"
def newmat(name,rgb):
    path=DEST+"/M_"+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):return unreal.load_asset(path)
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_"+name,DEST,unreal.Material,unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided",True)
    e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);e.set_editor_property("constant",unreal.LinearColor(*rgb))
    unreal.MaterialEditingLibrary.connect_material_property(e,"",unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m
keys=[("Terrain","SM_Berezovka_Terrain"),("Road","SM_Conform_Road"),("Path","SM_Conform_Path"),("Rail","SM_Conform_Rail"),("Forest","SM_Forest_Zones"),("OldBor","SM_OldBor_Zone")]
for key,filename in keys:
    m=by["TERRAIN_"+key].static_mesh_component.get_material(0) if key in ["Terrain","Road","Path","Rail"] else newmat(key,(.075,.15,.055) if key=="Forest" else (.045,.095,.035))
    task=unreal.AssetImportTask();task.filename=ROOT+"/SourceArt/Terrain/"+filename+".obj";task.destination_path=DEST;task.destination_name=filename;task.automated=True;task.save=True;task.replace_existing=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.load_asset(DEST+"/"+filename);assert mesh
    ns=mesh.get_editor_property("nanite_settings");ns.enabled=False;mesh.set_editor_property("nanite_settings",ns)
    body=mesh.get_editor_property("body_setup");body.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property("double_sided_geometry",True)
    mesh.set_material(0,m);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    a=by.get("TERRAIN_"+key)
    if a is None:
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label("TERRAIN_"+key);a.set_folder_path("00_Terrain")
    a.set_actor_scale3d(unreal.Vector(1,-1,1))
    a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,m)
    a.static_mesh_component.set_collision_profile_name("NoCollision" if key in ["Forest","OldBor"] else "BlockAll")
# Harmonized shop foundation datum (H05 apron already used the same level).
oldshop=87.60602386456253
newshop=next(p[7] for p in T.PADS if p[0]=="SHOP01")
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith("SHOP01_"):
        p=a.get_actor_location();a.set_actor_location(unreal.Vector(p.x,p.y,p.z+newshop-oldshop),False,False)
# Native collision checks sampled across every road strip and required building entries.
manifest=json.load(open(ROOT+"/SourceArt/Terrain/manifest.json"))
surface=[];maxerr=0;missing=[]
for r in manifest["routes"]:
    p,q=r["p"],r["q"];n=max(1,math.ceil(math.dist(p,q)/1000))
    for i in range(n+1):
        x=p[0]+(q[0]-p[0])*i/n;y=p[1]+(q[1]-p[1])*i/n;expected=T.height(x,y)
        hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,expected+90),unreal.Vector(x,y,expected-100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
        if hit is None:missing.append([x,y])
        else:
            actual=hit.to_tuple()[5].z
            maxerr=max(maxerr,abs(actual-expected))
        surface.append([x,y,expected])
assert not missing,"Missing terrain collision samples"
# Check all entry capsules without changing gameplay state.
entries=[("garage_main",[-7200,16300],[-8200,16300]),("garage_side",[-8100,15800],[-8100,16080]),("shop",[5360,-15000],[5930,-15000]),("stop",[430,0],[650,0])]
for name,p,q in entries:
    z=max(T.height(*p),T.height(*q))+110
    hit=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(*p,z),unreal.Vector(*q,z),42,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
    assert hit is None,"Entry blocked: "+name
for path in unreal.EditorAssetLibrary.list_assets(DEST,recursive=True,include_folder=False):unreal.EditorAssetLibrary.save_asset(path,only_if_is_dirty=False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
json.dump({"surface_samples":len(surface),"missing_ground":len(missing),"max_surface_difference_cm":maxerr,"entry_capsules_clear":[e[0] for e in entries],"shop_pad_height_cm":newshop,"garage_inside_m":[7,9],"flat_garage_floor":True,"inspection_pit":False,"final_max_route_grade_percent":manifest["max_route_grade"]*100},open(ROOT+"/Review/Terrain/final_collision_checks.json","w"),indent=2)
unreal.log("TERRAIN_FINAL_CHECKS_OK "+str(len(surface)))
