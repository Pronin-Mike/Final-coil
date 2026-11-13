"""Rendered PIE baseline/candidate with fixed views, CSV timings and scene inventory."""
from pathlib import Path
import unreal, json, time, os, math, traceback
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'Review/EnvironmentZones'; OUT.mkdir(parents=True,exist_ok=True)
phase=os.environ.get('FINALCOIL_ENV_PHASE','before'); report={'phase':phase,'status':'starting','views':[]}
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=E.get_all_level_actors()
if phase=='before1080':
 # A transient control world: remove only this stage's additions in this owned
 # test process. Never save it. Original 937 objects are verified separately.
 original=set(json.loads((OUT/'before_scene.json').read_text()))
 for actor in actors:
  if actor.get_actor_label() not in original and (actor.get_actor_label().startswith('ENV_') or actor.get_class().get_name()=='PCGWorldActor'):E.destroy_actor(actor)
 actors=E.get_all_level_actors();report['transient_control_world']=True
def snapshot(a):
 t=a.get_actor_transform();p=t.translation;r=t.rotation.rotator();s=t.scale3d
 return dict(class_name=a.get_class().get_name(),transform=[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],components=[dict(name=k.get_name(),mesh=k.static_mesh.get_path_name() if k.static_mesh else None,collision=str(k.get_collision_enabled()),instances=k.get_instance_count() if isinstance(k,unreal.InstancedStaticMeshComponent) else 1,materials=[str(k.get_material(i).get_path_name()) if k.get_material(i) else None for i in range(k.get_num_materials())]) for k in a.get_components_by_class(unreal.StaticMeshComponent)])
inventory={a.get_actor_label():snapshot(a) for a in actors};(OUT/(phase+'_scene.json')).write_text(json.dumps(inventory,indent=2))
if phase=='after':
 before=json.loads((OUT/'before_scene.json').read_text());changed=[n for n,v in before.items() if inventory.get(n)!=v]
 report['original_scene_unchanged']=not changed;report['changed_original_actors']=changed
 assert not changed,changed
 import sys
 sys.path.insert(0,str(ROOT/'Scripts'));import environment_zones as EZ
 surface=EZ.HeightfieldSurface();world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();ignore=[a for a in actors if a.get_actor_label()!='TERRAIN_Terrain'];rays=[]
 for x,y in [(-30000+i*20000,-110000+j*70000) for i in range(8) for j in range(6)]+[(0,0),(-8400,26700),(18000,30000),(43000,130000)]:
  sample=surface.sample(x,y);z=sample['position'][2];hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,z+500),unreal.Vector(x,y,z-500),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  assert hit is not None,(x,y);parts=hit.to_tuple();err=abs(parts[5].z-z);normal=parts[7];dot=sum(a*b for a,b in zip([normal.x,normal.y,normal.z],sample['normal']));rays.append(dict(x=x,y=y,height_error_cm=err,normal_dot=dot));assert err<.2,(x,y,err);assert dot>.99,(x,y,dot)
 report['surface_collision_validation']=dict(samples=len(rays),max_error_cm=max(r['height_error_cm'] for r in rays),minimum_normal_dot=min(r['normal_dot'] for r in rays));(OUT/'surface_rays.json').write_text(json.dumps(rays,indent=2))
 editor_pcg=next(a.get_component_by_class(unreal.PCGComponent) for a in actors if a.get_actor_label()=='ENV_PCG_Environment');editor_pcg.generate(True)
report['actors']=len(actors);report['static_mesh_components']=sum(len(v['components']) for v in inventory.values());report['instances']=sum(k['instances'] for v in inventory.values() for k in v['components'])
# Existing physical object footprints feed exclusions, without editing those objects.
if phase=='before':
 footprints=[]
 for a in actors:
  n=a.get_actor_label()
  if n.startswith(('G01_','H0','H1','E0','E1','STOP','SHOP','WELL','POI_','CHAPEL')) and not any(t in n for t in ['Label','Text','Origin','Light','Roof','Chimney','Stair','Step','Fence']):
   comps=a.get_components_by_class(unreal.StaticMeshComponent)
   if not comps:continue
   o,e=a.get_actor_bounds(False,False)
   if e.x>3 and e.y>3:footprints.append(dict(label=n,center=[o.x,o.y,o.z],extent=[e.x,e.y,e.z]))
 (OUT/'object_footprints.json').write_text(json.dumps(footprints,indent=2))
 docs={}
 for name in ['PCGDataAsset','PCGPointData','PCGMetadata','PCGPoint','PCGDataCollection','PCGTaggedData','PCGLoadDataAssetSettings','PCGComponent','PCGGraph','PCGGraphFactory']:
  cls=getattr(unreal,name,None)
  if cls:docs[name]=dict(doc=cls.__doc__,methods={m:getattr(cls,m).__doc__ for m in dir(cls) if any(x in m for x in ['point','metadata','attribute','entry','data','graph','generate','output']) and callable(getattr(cls,m,None))})
 (OUT/'ue_pcg_api.json').write_text(json.dumps(docs,indent=2))
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
ew=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for cmd in ['Slate.bAllowThrottling 0','t.IdleWhenNotForeground 0','r.VSync 0','t.MaxFPS 0','r.GPUCsvStatsEnabled 1','csv.TrackWaits 1']:
 unreal.SystemLibrary.execute_console_command(ew,cmd)
state={'frames':0,'view':0,'samples':[],'started':time.monotonic()}
plan=json.loads((ROOT/'SourceArt/CompactVillage/plan.json').read_text());stop=plan['stop'];house=next(p for p in plan['plots'] if p['id']=='H04');vacant=next(p for p in plan['plots'] if p['id']=='E02')
views=[('stop',stop[0]-300,stop[1]-500,0),('occupied',*house['center'],40),('abandoned',*vacant['center'],70),('meadow',18000,30000,100),('edge',-11200,29000,180)]
import sys
sys.path.insert(0,str(ROOT/'Scripts'));import terrain_profile as T
def write(): (OUT/(phase+'_benchmark.json')).write_text(json.dumps(report,indent=2))
def finish(status):
 report['status']=status;write();unreal.unregister_slate_post_tick_callback(env_bench_handle);LV.editor_request_end_play();unreal.EditorPythonScripting.set_keep_python_script_alive(False)
def tick(dt):
 try:
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:
   if time.monotonic()-state['started']>120:report['error']='PIE startup timeout';finish('failed')
   return
  pc=unreal.GameplayStatics.get_player_controller(w,0);pawn=unreal.GameplayStatics.get_player_pawn(w,0)
  if not pawn or not pc:return
  n,x,y,yaw=views[state['view']]
  if state['frames']==0:
   pawn.set_actor_location(unreal.Vector(x,y,T.height(x,y)+100),False,True);pc.set_control_rotation(unreal.Rotator(pitch=-5,yaw=yaw,roll=0));state['samples']=[]
  state['frames']+=1
  if state['frames']==91:
   if phase=='after' and 'pcg_validation' not in report:
    collection=editor_pcg.get_generated_graph_output();typed=collection.get_typed_inputs();data=typed[0] if isinstance(typed,tuple) else typed;total=0;violations=[]
    for pd in data:
     legacy=pd.to_point_data();md=legacy.const_metadata();total+=legacy.get_num_points()
     for pt in legacy.get_points_copy():
      if pt.get_float_attribute(md,'Exclusion')>.001:violations.append('Excluded point in PCG output')
    report['pcg_validation']=dict(points=total,exclusion_violations=len(violations));assert total>0 and not violations,report['pcg_validation']
   unreal.SystemLibrary.execute_console_command(w,'csvprofile start');state['measure_started']=time.monotonic()
  if 91<state['frames']<=391:state['samples'].append(float(dt))
  if state['frames']==392:
   unreal.SystemLibrary.execute_console_command(w,'csvprofile stop');samples=state['samples'];elapsed=time.monotonic()-state['measure_started'];report['views'].append(dict(name=n,frames=len(samples),average_fps=len(samples)/elapsed,frame_ms=elapsed/len(samples)*1000,wall_seconds=elapsed,slate_callback_ms=sum(samples)/len(samples)*1000,measurement_source='wall clock; prefer CSV FrameTime for final comparison',viewport_size=list(pc.get_viewport_size())));write();state['view']+=1;state['frames']=0
   if state['view']==len(views):finish('passed')
 except BaseException:report['error']=traceback.format_exc();finish('failed')
env_bench_handle=unreal.register_slate_post_tick_callback(tick);write()
if os.environ.get('FINALCOIL_ENV_FLOATING')=='1':
 settings=unreal.get_default_object(unreal.LevelEditorPlaySettings);settings.set_editor_property('new_window_width',1920);settings.set_editor_property('new_window_height',1080)
else:LV.editor_request_begin_play()
