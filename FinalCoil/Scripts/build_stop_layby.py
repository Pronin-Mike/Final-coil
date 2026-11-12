"""Local bus layby and waiting apron on the actual terrain surface."""
import unreal,sys,os,json,shutil,math
R='D:/GameDevelop/FinalCoil';sys.path.insert(0,R+'/Scripts')
import terrain_profile as T
A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
assert LV.save_current_level()
Q=R+'/Review/StopLayby';os.makedirs(Q,exist_ok=True)
backup=R+'/Saved/Backups/BeforeStopLayby';os.makedirs(backup,exist_ok=True)
for rel in ['Content/FinalCoil/Maps/L_Berezovka_Terrain.umap','Content/FinalCoil/World/VillageRoadPass/M_Village_Surface.uasset']:
 target=backup+'/'+os.path.basename(rel)
 if not os.path.exists(target):shutil.copy2(R+'/'+rel,target)
by={a.get_actor_label():a for a in E.get_all_level_actors()}
assert abs(by['STOP01_Pad'].get_actor_location().x-700)<5,'Unexpected stop position'
m=unreal.load_asset('/Game/FinalCoil/World/VillageRoadPass/M_Village_Surface')
n=next(n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5)
code=n.get_editor_property('code');assert '// STOP01_LAYBY' not in code
old='float dist=rd.x, width=rd.y;'
replacement='''float dist=rd.x, width=rd.y;
// STOP01_LAYBY: one-sided 3m widening, 12m standing length and 12m tapers.
float stopLong=1-smoothstep(600,1800,abs(P.y));
float stopSide=smoothstep(-30,80,P.x);
width+=300*stopLong*stopSide;
'''
assert old in code;code=code.replace(old,replacement)
old='color=lerp(color,nextColor,mixWeight);'
replacement='''// STOP01_WAITING: 6.2 x 8m gravel apron, separated from the carriageway.
float stopApron=(1-smoothstep(0,24,max(780-P.x,P.x-1400)))*(1-smoothstep(385,415,abs(P.y)));
float stopAccess=(1-smoothstep(70,100,abs(P.y)))*(1-smoothstep(0,24,max(580-P.x,P.x-820)));
float stopWait=max(stopApron,stopAccess);
float stopGrain=g.noise(P.xy/3.2);
float3 stopGravel=float3(.24,.22,.17)*(.86+.28*stopGrain);
nextColor=lerp(nextColor,stopGravel,stopWait);
float stopBayWeight=stopLong*stopSide*(1-smoothstep(width-20,width+80,dist));
color=lerp(color,nextColor,max(mixWeight,max(stopWait,stopBayWeight)));'''
assert old in code;code=code.replace(old,replacement)
n.set_editor_property('code',code);assert not L.recompile_material(m);assert A.save_loaded_asset(m)
offset=500;newGround=T.height(1200,0);oldFloor=by['STOP01_Pad'].get_actor_location().z+5;dz=newGround+10-oldFloor
moved=[]
for name,a in by.items():
 if name.startswith('STOP01_') and name!='STOP01_RoadApproach':
  p=a.get_actor_location();a.set_actor_location(unreal.Vector(p.x+offset,p.y,p.z+dz),False,False);moved.append(name)
# The old narrow approach is superseded by the ground-level apron.
if 'STOP01_RoadApproach' in by:
 a=by['STOP01_RoadApproach'];a.set_actor_hidden_in_game(True)
 for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_visibility(False,True);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
# Remove only grass rooted inside the widened bay or waiting apron.
removed={}
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for name,a in by.items():
 if not name.startswith('VEG_VillageRoad_'):continue
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);ids=[]
 for i in range(c.get_instance_count()):
  p=c.get_instance_transform(i,True).translation
  if abs(p.y)>1850 or p.x<250 or p.x>1480:continue
  axis=max(0,p.y)*.176
  edge=axis+350+300*(1-smooth(600,1800,abs(p.y)))
  if (abs(p.y)<465 and 650<p.x<1480) or p.x<edge+40:ids.append(i)
 for i in reversed(ids):c.remove_instance(i)
 removed[name]=len(ids)
# Spawn on the waiting apron, facing the road; keep the bus lane free.
start=next(a for a in by.values() if isinstance(a,unreal.PlayerStart));start.set_actor_location(unreal.Vector(940,240,T.height(940,240)+110),False,False);start.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),False)
assert LV.save_current_level()
json.dump(dict(saved=True,layby_extra_width_m=3,standing_length_m=12,tapers_m=12,waiting_apron_m=[6.2,8],shelter_offset_m=5,moved=moved,grass_removed=removed,ground_geometry_unchanged=True),open(Q+'/result.json','w'),indent=2)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-1800,-2400,2400),unreal.Rotator(pitch=-32,yaw=40,roll=0))
unreal.log('STOP_LAYBY_OK saved=True')
