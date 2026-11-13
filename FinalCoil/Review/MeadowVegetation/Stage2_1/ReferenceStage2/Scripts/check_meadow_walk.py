"""PIE CharacterMovement walk across the test patch; no runtime world save."""
from pathlib import Path
import unreal,time,math,json,traceback,sys
ROOT=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(ROOT/'Scripts'));import meadow_distribution as M
surface=M.Z.HeightfieldSurface();route=[(16800,28800),(19200,28800),(19200,31200),(16800,31200),(18000,30000)]
state=dict(status='waiting',point=0,completed=[],started=time.monotonic(),last_progress=time.monotonic(),last_distance=1e9);runtime={};LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for cmd in ['t.MaxFPS 0','Slate.bAllowThrottling 0','t.IdleWhenNotForeground 0']:unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),cmd)
def finish(status):
 state['status']=status;(ROOT/'Review/MeadowVegetation/PIE_walk.json').write_text(json.dumps(state,indent=2));unreal.unregister_slate_post_tick_callback(handle);LV.editor_request_end_play()
def tick(dt):
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  if not runtime:
   pawn=unreal.GameplayStatics.get_player_character(w,0)
   if not pawn:return
   pc=unreal.GameplayStatics.get_player_controller(w,0);move=pawn.get_component_by_class(unreal.CharacterMovementComponent);half=pawn.get_component_by_class(unreal.CapsuleComponent).get_scaled_capsule_half_height();x,y=route[0];pawn.set_actor_location(unreal.Vector(x,y,surface.sample(x,y)['position'][2]+half+5),False,True);move.max_walk_speed=400;move.set_movement_mode(unreal.MovementMode.MOVE_WALKING);runtime.update(pawn=pawn,pc=pc,move=move);state['last_progress']=time.monotonic();return
  pawn=runtime['pawn'];p=pawn.get_actor_location();x,y=route[state['point']];dx,dy=x-p.x,y-p.y;distance=math.hypot(dx,dy)
  if distance<35:
   state['completed'].append([x,y]);state['point']+=1;state['last_progress']=time.monotonic();state['last_distance']=1e9
   if state['point']==len(route):finish('passed')
   return
  if distance<state['last_distance']-2:state['last_distance']=distance;state['last_progress']=time.monotonic()
  if time.monotonic()-state['last_progress']>12:state['failure']='Character stuck';finish('failed');return
  assert p.z>surface.sample(p.x,p.y)['position'][2]
  pawn.add_movement_input(unreal.Vector(dx/distance,dy/distance,0),1,True)
  runtime['pc'].set_control_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(dy,dx)),roll=0))
 except BaseException:state['failure']=traceback.format_exc();finish('failed')
handle=unreal.register_slate_post_tick_callback(tick)
