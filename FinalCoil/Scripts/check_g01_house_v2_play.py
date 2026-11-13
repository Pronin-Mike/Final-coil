"""Standalone editor launch test: real CharacterMovement, no route teleporting.
Run UnrealEditor -ExecutePythonScript=...; it closes its own test editor on finish.
"""
import unreal,json,math,time,traceback
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/G01HouseV2';spec=json.load(open(R+'/SourceArt/G01HouseV2/house_spec.json'))
cx,cy=spec['house_center'];a=math.radians(spec['yaw']);c,s=math.cos(a),math.sin(a);gz=spec['ground_z']
def point(x,y,z):return unreal.Vector(cx+c*x-s*y,cy+s*x+c*y,gz+z)
route=[(900,0,0),(855,0,15),(825,0,30),(795,0,45),(765,0,60),(620,0,60),(440,0,60),(0,0,60),(-430,0,60),(-430,-190,60),(-385,-190,60)]
stairs=[(-350+28*(i+.5),-190,60+(i+1)*300/18) for i in range(18)]
route+=stairs+[(215,-190,360),(215,0,360),(0,0,360),(300,0,360),(215,0,360),(215,-190,360)]+list(reversed(stairs))+[(-385,-190,60),(-430,-190,60),(-430,0,60),(0,0,60),(-100,140,60),(-100,235,60)]
link=[(-100,277.5+i*35,60-(i+1)*55/4) for i in range(4)]
route+=link+[(-100,450,5),(-100,570,5),(300,570,5),(300,770,5),(300,1000,5),(-300,1000,5),(-300,570,5),(-100,570,5),(-100,450,5)]+list(reversed(link))+[(-100,235,60),(0,0,60),(440,0,60),(620,0,60),(765,0,60),(795,0,45),(825,0,30),(855,0,15),(920,0,0)]
state=dict(status='waiting_for_pie',point=0,total_points=len(route),completed=[],failures=[],samples=0,started=time.monotonic(),last_progress=time.monotonic(),last_distance=1e9,min_z=1e9,max_z=-1e9)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor_world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(editor_world,'Slate.bAllowThrottling 0')
unreal.SystemLibrary.execute_console_command(editor_world,'t.IdleWhenNotForeground 0')
LV.editor_set_viewport_realtime(True)
def write():json.dump({k:v for k,v in state.items() if k not in ['pawn','world','control','move']},open(Q+'/PIE_walk.json','w'),indent=2)
def finish(status):
 state['status']=status;write()
 if state.get('move'):state['move'].stop_movement_immediately()
 unreal.unregister_slate_post_tick_callback(house_walk_handle);LV.editor_request_end_play();unreal.EditorPythonScripting.set_keep_python_script_alive(False)
def tick(dt):
 try:
  now=time.monotonic()
  if not state.get('pawn'):
   world=unreal.EditorLevelLibrary.get_game_world()
   if not world:
    if now-state['started']>90:state['failures'].append('PIE did not start');finish('failed')
    return
   pawn=unreal.GameplayStatics.get_player_character(world,0)
   if not pawn:return
   move=pawn.get_component_by_class(unreal.CharacterMovementComponent);assert move
   half=pawn.get_component_by_class(unreal.CapsuleComponent).get_scaled_capsule_half_height()
   pawn.set_actor_location(point(930,0,half+8),False,True)
   state.update(pawn=pawn,world=world,control=unreal.GameplayStatics.get_player_controller(world,0),move=move,capsule_half_height_cm=half,last_progress=now,status='walking',started_walking=now)
   move.max_walk_speed=160;move.max_simulation_iterations=32;move.max_simulation_time_step=.033333;move.set_movement_mode(unreal.MovementMode.MOVE_WALKING);move.set_component_tick_enabled(True);unreal.GameplayStatics.set_game_paused(world,False);unreal.GameplayStatics.set_global_time_dilation(world,1);unreal.SystemLibrary.execute_console_command(world,'t.IdleWhenNotForeground 0');unreal.SystemLibrary.execute_console_command(world,'r.MotionBlurQuality 0');write();return
  pawn=state['pawn'];move=state['move'];p=pawn.get_actor_location();state['game_time_seconds']=unreal.GameplayStatics.get_time_seconds(state['world'])
  if state['point']>=len(route):finish('passed');return
  x,y,z=route[state['point']];goal=point(x,y,z);dx,dy=goal.x-p.x,goal.y-p.y;distance=math.hypot(dx,dy)
  if distance<11:
   state['completed'].append([x,y,z]);state['point']+=1;state['last_progress']=now;state['last_distance']=1e9;write();return
  if distance<state['last_distance']-3:state['last_progress']=now;state['last_distance']=distance
  if now-state['last_progress']>9:state['failures'].append(dict(reason='stuck',target=[x,y,z],position=[p.x,p.y,p.z],distance=distance));finish('failed');return
  if p.z<gz-100:state['failures'].append('Fell below ground');finish('failed');return
  if now-state['started_walking']>150:state['failures'].append('Walk timeout');finish('failed');return
  state['control'].set_control_rotation(unreal.Rotator(pitch=-3,yaw=math.degrees(math.atan2(dy,dx)),roll=0));pawn.add_movement_input(unreal.Vector(dx/distance,dy/distance,0),1,True)
  state['samples']+=1;state['min_z']=min(state['min_z'],p.z);state['max_z']=max(state['max_z'],p.z)
  if now-state.get('last_write',0)>1:state['last_write']=now;write()
 except BaseException:state['failures'].append(traceback.format_exc());finish('failed')
house_walk_handle=unreal.register_slate_post_tick_callback(tick);write()
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(point(930,0,170),unreal.Rotator(pitch=0,yaw=spec['yaw']+180,roll=0))
LV.editor_request_begin_play()
