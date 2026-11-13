"""PIE approach to table, shelving, bench, tyre rack; side door and main gate."""
import unreal,math,json,time,traceback
Q='D:/GameDevelop/FinalCoil/Review/GarageFitout'
p=json.load(open('D:/GameDevelop/FinalCoil/Review/Moskvich412/ue_placement.json'));cx,cy,z=p['position_cm'];angle=math.radians(p['yaw_deg']);c,s=math.cos(angle),math.sin(angle)
def world(x,y,h=100):return unreal.Vector(cx+c*x-s*y,cy+s*x+c*y,z+h)
route=[(310,0),(300,200),(-80,200),(-300,220),(-300,-90),(-280,-205),(-100,-200),(-100,-430),(-100,-200),(300,-200),(310,0),(620,0)]
state=dict(status='running',point=0,points=len(route),samples=0,failures=[],completed=[],start=time.monotonic(),last_progress=time.monotonic(),last_distance=1e9)
w=unreal.EditorLevelLibrary.get_game_world();assert w
pawn=unreal.GameplayStatics.get_player_character(w,0);assert pawn
control=unreal.GameplayStatics.get_player_controller(w,0);move=pawn.get_component_by_class(unreal.CharacterMovementComponent);move.max_walk_speed=250
unreal.SystemLibrary.execute_console_command(w,'t.IdleWhenNotForeground 0')
car=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StaticMeshActor) if a.get_actor_label()=='G01_Moskvich412')
# A waist-height trace must hit the car body; four tyre bottom bounds match slab top.
hit=unreal.SystemLibrary.line_trace_single(w,world(0,-200,70),world(0,200,70),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,False)
unpack=hit.to_tuple();state['collision_probe_actor']=str(unpack[9].get_name()) if len(unpack)>9 and unpack[9] else str(unpack)
state['collision_probe_hit']=bool(unpack[0]);assert state['collision_probe_hit'],'Car collision trace missed'
def write():json.dump({k:v for k,v in state.items()},open(Q+'/PIE_walk.json','w'),indent=2)
def end(status):
 state['status']=status;move.stop_movement_immediately();write();unreal.unregister_slate_post_tick_callback(moskvich_walk_handle)
def tick(dt):
 try:
  now=time.monotonic();pos=pawn.get_actor_location()
  if state['point']>=len(route):end('passed');return
  target=world(*route[state['point']]);d=target-pos;dist=math.hypot(d.x,d.y)
  if dist<35:
   state['completed'].append(list(route[state['point']]));state['point']+=1;state['last_progress']=now;state['last_distance']=1e9;write();return
  if dist<state['last_distance']-10:state['last_distance']=dist;state['last_progress']=now
  if now-state['last_progress']>8:state['failures'].append('No walking progress');end('failed');return
  if abs(pos.z-(z+96))>80:state['failures'].append('Unexpected floor height: '+str(pos.z));end('failed');return
  control.set_control_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(d.y,d.x)),roll=0));pawn.add_movement_input(unreal.Vector(d.x/dist,d.y/dist,0),1,True);state['samples']+=1
  if now-state.get('last_write',0)>1:state['last_write']=now;write()
 except BaseException:
  state['failures'].append(traceback.format_exc());end('failed')
moskvich_walk_handle=unreal.register_slate_post_tick_callback(tick);write()
