"""Real PIE viewpoints, terrain-scale evidence, optional transient sun rotation."""
from pathlib import Path
import unreal,sys,json,time,math,traceback
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation';sys.path.insert(0,str(ROOT/'Scripts'))
import meadow_distribution as M
surface=M.Z.HeightfieldSurface();distribution=json.loads((M.SOURCE/'distribution_medium.json').read_text());tall=distribution['groups']['tall'];tallpoint=tall[len(tall)//2]['p'];views=[('open_meadow',18000,29600,-9,90,170),('close_grass',18000,29600,-36,90,170),('among_tall',tallpoint[0],tallpoint[1],-24,30,170),('transition',17600,30200,-14,20,170),('raised_8m',18000,29300,-35,90,800),('aerial',18000,29400,-75,90,3500),('alternate_light',18000,29600,-15,90,170)]
views=globals().get('VIEWS',views)
state={'index':0,'frames':0,'started':time.monotonic(),'views':[]};LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
capture_after=globals().get('WARMUP_FRAMES',45)
ew=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for cmd in ['Slate.bAllowThrottling 0','t.IdleWhenNotForeground 0','r.VSync 0','t.MaxFPS 0']:unreal.SystemLibrary.execute_console_command(ew,cmd)
def finish(status):
 state['status']=status;(Q/'PIE_visual.json').write_text(json.dumps(state,indent=2));unreal.unregister_slate_post_tick_callback(handle);LV.editor_request_end_play()
def tick(dt):
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:
   if time.monotonic()-state['started']>120:finish('startup_timeout')
   return
  pc=unreal.GameplayStatics.get_player_controller(w,0);pawn=unreal.GameplayStatics.get_player_character(w,0)
  if not pc or not pawn:return
  name,x,y,pitch,yaw,height=views[state['index']]
  if state['frames']==0:
   z=surface.sample(x,y)['position'][2];half=pawn.get_component_by_class(unreal.CapsuleComponent).get_scaled_capsule_half_height();pawn.set_actor_location(unreal.Vector(x,y,z+half+2),False,True);pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately();pc.set_control_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
   for camera_component in pawn.get_components_by_class(unreal.CameraComponent):camera_component.set_world_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False,False)
   if height!=170:
    pawn.get_component_by_class(unreal.CharacterMovementComponent).set_movement_mode(unreal.MovementMode.MOVE_FLYING);pawn.set_actor_location(unreal.Vector(x,y,z+height-80),False,True)
   else:pawn.get_component_by_class(unreal.CharacterMovementComponent).set_movement_mode(unreal.MovementMode.MOVE_WALKING)
   for mesh_component in pawn.get_components_by_class(unreal.SkeletalMeshComponent):mesh_component.set_visibility(height==170,True)
   pc.set_view_target_with_blend(pawn,0)
   if name=='alternate_light':
    sun=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.DirectionalLight)),None)
    if sun:
     sun.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(unreal.ComponentMobility.MOVABLE);assert sun.set_actor_rotation(unreal.Rotator(pitch=-28,yaw=145,roll=0),False)
  state['frames']+=1
  if state['frames']==capture_after:
   cam=pc.player_camera_manager.get_camera_location();state['views'].append(dict(name=name,camera=[cam.x,cam.y,cam.z],eye_height_cm=cam.z-surface.sample(cam.x,cam.y)['position'][2],viewport=list(pc.get_viewport_size()),screenshot_render=[1920,1080],lighting='transient PIE sun' if name=='alternate_light' else 'original'))
   unreal.SystemLibrary.execute_console_command(w,'HighResShot 1920x1080 filename="'+str(Q/(name+'.png'))+'"',pc)
  if state['frames']>=capture_after+20:
   state['frames']=0;state['index']+=1
   if state['index']==len(views):finish('passed')
 except BaseException:state['error']=traceback.format_exc();finish('failed')
handle=unreal.register_slate_post_tick_callback(tick)
