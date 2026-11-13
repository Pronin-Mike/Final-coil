"""Standalone PIE walk through both rooms and shower tray; closes its own editor."""
import unreal,json,math,time,traceback
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/G01Banya';spec=json.load(open(R+'/SourceArt/G01Banya/bath_spec.json'));cx,cy=spec['center'];a=math.radians(spec['yaw']);c,s=math.cos(a),math.sin(a);g=spec['ground_z']
def point(x,y,z):return unreal.Vector(cx+c*x-s*y,cy+s*x+c*y,g+z)
steps=spec.get('entry_steps',2);entry_z=spec.get('entrance_terrain_z',g)-g;rise=spec.get('entry_step_rise_cm',15)
stair_points=[(-320-(steps-i)*30+15,-110,entry_z+(i+1)*rise) for i in range(steps)]
route=[(-440,-110,entry_z)]+stair_points+[(-305,-110,30),(-220,-110,30),(-220,65,30),(-220,170,36),(-220,65,30),(-100,-110,30),(-40,-110,30),(40,-110,30),(75,-80,30),(80,0,30),(55,55,30),(60,-110,30),(-40,-110,30),(-200,-110,30),(-305,-110,30)]+list(reversed(stair_points))+[(-450,-110,entry_z)]
state=dict(status='waiting_for_pie',point=0,total_points=len(route),completed=[],failures=[],samples=0,started=time.monotonic(),last_progress=time.monotonic(),last_distance=1e9,min_z=1e9,max_z=-1e9)
unreal.EditorPythonScripting.set_keep_python_script_alive(True);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);ew=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(ew,'Slate.bAllowThrottling 0');unreal.SystemLibrary.execute_console_command(ew,'t.IdleWhenNotForeground 0')
def write():json.dump({k:v for k,v in state.items() if k not in ['world','pawn','move','control']},open(Q+'/PIE_walk.json','w'),indent=2)
def finish(status):
 state['status']=status;write()
 if state.get('move'):state['move'].stop_movement_immediately()
 unreal.unregister_slate_post_tick_callback(banya_walk_handle);LV.editor_request_end_play();unreal.EditorPythonScripting.set_keep_python_script_alive(False)
def tick(dt):
 try:
  now=time.monotonic()
  if not state.get('pawn'):
   w=unreal.EditorLevelLibrary.get_game_world()
   if not w:
    if now-state['started']>90:state['failures'].append('No PIE world');finish('failed')
    return
   pawn=unreal.GameplayStatics.get_player_character(w,0)
   if not pawn:return
   move=pawn.get_component_by_class(unreal.CharacterMovementComponent);half=pawn.get_component_by_class(unreal.CapsuleComponent).get_scaled_capsule_half_height();pawn.set_actor_location(point(-480,-110,entry_z+half+8),False,True);state.update(world=w,pawn=pawn,move=move,control=unreal.GameplayStatics.get_player_controller(w,0),capsule_half_height_cm=half,status='walking',last_progress=now,walking_started=now)
   move.max_walk_speed=140;move.set_movement_mode(unreal.MovementMode.MOVE_WALKING);move.set_component_tick_enabled(True);move.max_simulation_iterations=32;move.max_simulation_time_step=.033333;unreal.GameplayStatics.set_game_paused(w,False);unreal.GameplayStatics.set_global_time_dilation(w,1);write();return
  p=state['pawn'].get_actor_location();state['game_time_seconds']=unreal.GameplayStatics.get_time_seconds(state['world'])
  if state['point']>=len(route):finish('passed');return
  x,y,z=route[state['point']];q=point(x,y,z);dx,dy=q.x-p.x,q.y-p.y;distance=math.hypot(dx,dy)
  if distance<12:state['completed'].append([x,y,z]);state['point']+=1;state['last_distance']=1e9;state['last_progress']=now;write();return
  if distance<state['last_distance']-3:state['last_distance']=distance;state['last_progress']=now
  if now-state['last_progress']>12:state['failures'].append(dict(reason='stuck',target=[x,y,z],position=[p.x,p.y,p.z]));finish('failed');return
  if p.z<g-100:state['failures'].append('Below ground');finish('failed');return
  if now-state['walking_started']>150:state['failures'].append('Walk timeout');finish('failed');return
  state['control'].set_control_rotation(unreal.Rotator(pitch=-3,yaw=math.degrees(math.atan2(dy,dx)),roll=0));state['pawn'].add_movement_input(unreal.Vector(dx/distance,dy/distance,0),1,True);state['samples']+=1;state['min_z']=min(state['min_z'],p.z);state['max_z']=max(state['max_z'],p.z)
  if now-state.get('last_write',0)>1:state['last_write']=now;write()
 except BaseException:state['failures'].append(traceback.format_exc());finish('failed')
banya_walk_handle=unreal.register_slate_post_tick_callback(tick);write();unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(point(-450,-110,165),unreal.Rotator(pitch=0,yaw=spec['yaw'],roll=0));LV.editor_request_begin_play()
