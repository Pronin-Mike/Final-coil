import unreal,sys,os,json,math,time
ROOT="D:/GameDevelop/FinalCoil"
sys.path.insert(0,ROOT+"/Scripts")
import terrain_profile as T
ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world=ed.get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
for key in ["Terrain","Road","Path","Rail"]:
    by["TERRAIN_"+key].set_actor_scale3d(unreal.Vector(1,-1,1))
assert world.get_name()=="L_Berezovka_Terrain"
# Fixed exposure makes broad terrain forms readable and avoids blowing out low-poly assets.
pp=actors.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(0,0,0))
pp.set_actor_label("Terrain_FixedExposure");pp.set_folder_path("90_Lighting");pp.set_editor_property("unbound",True)
settings=pp.get_editor_property("settings")
settings.set_editor_property("override_auto_exposure_min_brightness",True)
settings.set_editor_property("override_auto_exposure_max_brightness",True)
settings.set_editor_property("auto_exposure_min_brightness",0)
settings.set_editor_property("auto_exposure_max_brightness",0)
settings.set_editor_property("override_auto_exposure_bias",True)
settings.set_editor_property("auto_exposure_bias",0)
pp.set_editor_property("settings",settings)
unreal.SystemLibrary.execute_console_command(world,"r.EyeAdaptationQuality 0")
unreal.SystemLibrary.execute_console_command(world,"t.IdleWhenNotForeground 0")
for key in ["Terrain","Road","Path","Rail"]:
    m=by["TERRAIN_"+key].static_mesh_component.static_mesh
    body=m.get_editor_property("body_setup")
    body.set_editor_property("double_sided_geometry",True)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
# Check a real engine ground trace and store its shape for the QA parser.
hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(450,0,5000),unreal.Vector(450,0,-5000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
json.dump({"hit":str(hit),"tuple":str(hit.to_tuple()) if hit else None},open(ROOT+"/Review/Terrain/trace_probe.json","w"),indent=2)
assert hit is not None,"Terrain has no collision at PlayerStart"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
# Ground-following game test: real CharacterMovement walking, no teleporting between checkpoints.
def L(px,py):return [(447-py)*1000/3,(px-410)*1000/3]
STOP=[450,0];STREET=[0,0];GATE=[-5666.6667,15666.6667];GARAGE=[-8100,16300]
gpath=[STOP,STREET,L(455,439.08),L(460,451),L(459,460),GATE,[-7450,16300],GARAGE]
shop=[GARAGE,[-7450,16300],GATE,L(459,460),L(460,451),L(455,439.08),STREET,L(350,447),L(359,440),L(365,430),[5900,-15000]]
bor=[[5900,-15000],L(365,430),L(359,440),L(350,447),L(345,418),L(330,395),L(323,370),L(323,350),L(323,342),L(306,317)]
shore=[STOP,STREET,L(535,425),L(670,371),[33000,106000],[39500,121000],[43000,130000]]
routes=[("stop_garage_forward",gpath),("stop_garage_reverse",list(reversed(gpath))),("garage_shop_bor_forward",gpath+shop[1:]+bor[1:]),("garage_shop_bor_reverse",list(reversed(gpath+shop[1:]+bor[1:]))),("lake_forward",shore),("lake_reverse",list(reversed(shore)))]
captures={"stop":(STOP,0),"street":(STREET,80),"grandpa":(GATE,165),"bor":(L(323,350),20),"shore":(shore[-1],62)}
# Remove duplicated consecutive points; route boundaries all connect at STOP.
for name,pts in routes:
    for i in range(len(pts)-1,0,-1):
        if math.dist(pts[i],pts[i-1])<1:pts.pop(i)
state={"route":0,"point":0,"running":False,"started":time.monotonic(),"last_write":0,"samples":0,"distance_cm":0,"completed":[],"captured":[],"failures":[],"min_z":1e9,"max_z":-1e9,"max_ground_error_cm":0,"stuck_since":time.monotonic(),"last_progress":None,"pause_until":0,"capture_pending":None}
def write_status(status="running"):
    data={k:v for k,v in state.items() if k not in ["pawn","controller","world","last_progress","previous_pos"]}
    data["status"]=status;data["walking_speed_cm_s"]=600;data["simulation_time_dilation"]=3
    json.dump(data,open(ROOT+"/Review/Terrain/PIE_routes.json","w"),indent=2)
def stop_runner(status):
    if state.get("pawn"):
        state["pawn"].get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
        unreal.GameplayStatics.set_global_time_dilation(state["world"],1)
    write_status(status)
    unreal.unregister_slate_post_tick_callback(terrain_walk_handle)
def terrain_walk_tick(dt):
    try:
        now=time.monotonic()
        if not state["running"]:
            w=unreal.EditorLevelLibrary.get_game_world()
            if not w:return
            pawn=unreal.GameplayStatics.get_player_character(w,0)
            if not pawn:return
            state.update({"world":w,"pawn":pawn,"controller":unreal.GameplayStatics.get_player_controller(w,0),"running":True,"started":now,"stuck_since":now})
            movement=pawn.get_component_by_class(unreal.CharacterMovementComponent);movement.max_walk_speed=600
            unreal.GameplayStatics.set_global_time_dilation(w,3)
        pawn=state["pawn"];control=state["controller"];pos=pawn.get_actor_location()
        if state["route"]>=len(routes):stop_runner("passed");return
        if now<state["pause_until"]:
            pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
            if state["capture_pending"] and now>state["pause_until"]-.4:
                key=state["capture_pending"]
                unreal.AutomationLibrary.take_high_res_screenshot(1280,720,ROOT+"/Review/Terrain/eye_"+key+".png")
                state["captured"].append(key);state["capture_pending"]=None
            return
        name,pts=routes[state["route"]]
        target=pts[state["point"]];dx=target[0]-pos.x;dy=target[1]-pos.y;distance=math.hypot(dx,dy)
        if distance<70:
            for key,(point,yaw) in captures.items():
                if key not in state["captured"] and math.dist(point,target)<1:
                    pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
                    control.set_control_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0))
                    state["pause_until"]=now+1.0;state["capture_pending"]=key
            state["point"]+=1
            state["stuck_since"]=now;state["last_progress"]=[pos.x,pos.y]
            if state["point"]==len(pts):
                state["completed"].append({"route":name,"end":[pos.x,pos.y,pos.z]})
                state["route"]+=1;state["point"]=0
            write_status();return
        control.set_control_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(dy,dx)),roll=0))
        pawn.add_movement_input(unreal.Vector(dx/distance,dy/distance,0),1,True)
        state["samples"]+=1
        state["min_z"]=min(state["min_z"],pos.z);state["max_z"]=max(state["max_z"],pos.z)
        expected=T.height(pos.x,pos.y)
        bottom=pos.z-pawn.get_component_by_class(unreal.CapsuleComponent).get_scaled_capsule_half_height()
        error=bottom-expected
        state["max_ground_error_cm"]=max(state["max_ground_error_cm"],abs(error))
        if pos.z<expected-100:
            state["failures"].append({"reason":"fell_through_terrain","route":name,"position":[pos.x,pos.y,pos.z],"terrain":expected})
            stop_runner("failed");return
        last=state.get("previous_pos")
        if last:state["distance_cm"]+=math.hypot(pos.x-last[0],pos.y-last[1])
        state["previous_pos"]=[pos.x,pos.y]
        progress=state.get("last_progress")
        if progress is None or math.hypot(pos.x-progress[0],pos.y-progress[1])>100:
            state["stuck_since"]=now;state["last_progress"]=[pos.x,pos.y]
        if now-state["stuck_since"]>8:
            state["failures"].append({"reason":"stuck","route":name,"point":state["point"],"position":[pos.x,pos.y,pos.z],"target":target})
            stop_runner("failed");return
        if now-state["last_write"]>2:state["last_write"]=now;state["position"]=[pos.x,pos.y,pos.z];write_status()
    except Exception as exc:
        state["failures"].append({"reason":"test_script_exception","detail":str(exc)})
        try:stop_runner("test_error")
        except:write_status("test_error")
        unreal.log_error(str(exc))
terrain_walk_handle=unreal.register_slate_post_tick_callback(terrain_walk_tick)
write_status("waiting_for_PIE")
unreal.log("TERRAIN_QA_READY")
