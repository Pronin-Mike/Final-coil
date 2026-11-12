import unreal,time,json,sys
ROOT="D:/GameDevelop/FinalCoil"
sys.path.insert(0,ROOT+"/Scripts")
import terrain_profile as T
photos=[("stop",[430,0],0),("street",[0,2500],-95),("grandpa",[-5600,15400],165),("bor",[33000,-29000],20),("shore",[43000,130000],62)]
photo_state={"index":0,"phase":"waiting","deadline":0,"shots":[]}
def photo_tick(dt):
    try:
        now=time.monotonic()
        if photo_state["phase"]=="waiting":
            w=unreal.EditorLevelLibrary.get_game_world()
            if not w:return
            p=unreal.GameplayStatics.get_player_character(w,0)
            if not p:return
            photo_state["world"]=w;photo_state["pawn"]=p;photo_state["pc"]=unreal.GameplayStatics.get_player_controller(w,0)
            unreal.GameplayStatics.set_global_time_dilation(w,1)
            photo_state["phase"]="place"
        if photo_state["index"]>=len(photos):
            json.dump({"shots":photo_state["shots"],"eye_height_above_ground_cm":160,"type":"PIE player viewpoints; teleport only for photography"},open(ROOT+"/Review/Terrain/photo_views.json","w"),indent=2)
            unreal.unregister_slate_post_tick_callback(terrain_photo_handle)
            return
        key,xy,yaw=photos[photo_state["index"]];p=photo_state["pawn"];pc=photo_state["pc"]
        movement=p.get_component_by_class(unreal.CharacterMovementComponent)
        if photo_state["phase"]=="place":
            movement.stop_movement_immediately()
            h=T.height(*xy)
            p.set_actor_location(unreal.Vector(*xy,h+110),False,True)
            pc.set_control_rotation(unreal.Rotator(pitch=-4,yaw=yaw,roll=0))
            photo_state["deadline"]=now+2;photo_state["phase"]="settle"
        elif photo_state["phase"]=="settle" and now>=photo_state["deadline"]:
            unreal.AutomationLibrary.take_high_res_screenshot(1280,720,ROOT+"/Review/Terrain/eye_"+key+".png")
            camera=unreal.GameplayStatics.get_player_camera_manager(photo_state["world"],0)
            loc=camera.get_camera_location();rot=camera.get_camera_rotation()
            photo_state["shots"].append({"name":key,"location":[loc.x,loc.y,loc.z],"rotation":[rot.pitch,rot.yaw,rot.roll]})
            photo_state["deadline"]=now+2;photo_state["phase"]="capture"
        elif photo_state["phase"]=="capture" and now>=photo_state["deadline"]:
            photo_state["index"]+=1;photo_state["phase"]="place"
    except Exception as exc:
        json.dump({"error":str(exc)},open(ROOT+"/Review/Terrain/photo_views.json","w"))
        unreal.unregister_slate_post_tick_callback(terrain_photo_handle)
terrain_photo_handle=unreal.register_slate_post_tick_callback(photo_tick)
unreal.log("TERRAIN_PHOTO_TOUR_READY")
