"""Terrain-following G01 timber pickets and fixed-open paired driveway gates. UE cm."""
import unreal, json, math, os, sys, shutil, random, traceback
R='D:/GameDevelop/FinalCoil'; S=R+'/SourceArt/G01Fence'; Q=R+'/Review/G01Fence'; D='/Game/FinalCoil/World/G01Fence'
for path in [S,Q,R+'/../.publishing/g01-before-fence']:os.makedirs(path,exist_ok=True)
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); A=unreal.EditorAssetLibrary; AT=unreal.AssetToolsHelpers.get_asset_tools(); L=unreal.MaterialEditingLibrary
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 assert LV.save_current_level()
 backup=R+'/../.publishing/g01-before-fence/L_Berezovka_Terrain.umap'
 if not os.path.exists(backup):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',backup)
 by={a.get_actor_label():a for a in E.get_all_level_actors()}
 def record(a):
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
 baseline={n:record(a) for n,a in by.items() if not n.startswith('G01_Fence_')}
 json.dump(baseline,open(Q+'/baseline.json','w'),indent=2)
 P=json.load(open(R+'/SourceArt/CompactVillage/plan.json'));h=next(x for x in P['plots'] if x['id']=='G01');cx,cy=h['center'];c,s=h['c'],h['s'];yaw=math.degrees(h['yaw']);hx,hy=h['hx'],h['hy']
 sys.path.insert(0,R+'/Scripts');import terrain_profile as T
 def xy(x,y):return cx+c*x-s*y,cy+s*x+c*y
 def ground(x,y):return T.height(*xy(x,y))
 def local(p):return [c*(p[0]-cx)+s*(p[1]-cy),-s*(p[0]-cx)+c*(p[1]-cy)]
 crossings=[]
 for road in P['walks']:
  if road['name']!='G01_Drive':continue
  p,q=local(road['p']),local(road['q'])
  if (p[0]-hx)*(q[0]-hx)<0:
   t=(hx-p[0])/(q[0]-p[0]);gy=p[1]+t*(q[1]-p[1]);width=road['width']*math.dist(p,q)/abs(q[0]-p[0]);crossings.append((gy,width,p,q))
 assert len(crossings)==1,crossings
 gy,projected,p,q=crossings[0];gap=math.ceil((projected+100)/10)*10;lo,hi=gy-gap/2,gy+gap/2
 assert -hy+100<lo<hi<hy-100
 A.make_directory(D);mats=[]
 for i,color in enumerate([[.25,.19,.125],[.29,.225,.15],[.215,.17,.115],[.32,.25,.17],[.265,.215,.16]]):
  if A.does_asset_exist(D+'/MI_Timber'+str(i)):mats.append(unreal.load_asset(D+'/MI_Timber'+str(i)));continue
  m=unreal.load_asset(D+'/MI_Timber'+str(i)) or A.duplicate_asset('/Game/FinalCoil/World/G01HouseV2/MI_Log',D+'/MI_Timber'+str(i));L.set_material_instance_vector_parameter_value(m,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(m,'Roughness',.94);L.update_material_instance(m);assert A.save_loaded_asset(m,False);mats.append(m)
 # A six-sided profile gives each board a modest chamfered cap, not a sharp point.
 profile=[(-50,0),(50,0),(50,94),(32,100),(-32,100),(-50,94)];verts=[(x,y,z) for y in [-50,50] for x,z in profile];faces=[]
 for j in range(1,5):faces.extend([(0,j+1,j),(6,6+j,6+j+1)])
 for j in range(6):k=(j+1)%6;faces.extend([(j,k,6+k),(j,6+k,6+j)])
 with open(S+'/SM_Picket.obj','w') as f:
  for v in verts:f.write('v %g %g %g\n'%v)
  for face in faces:f.write('f %d %d %d\n'%tuple(i+1 for i in face))
 picket=unreal.load_asset(D+'/SM_Picket')
 if not picket:
  task=unreal.AssetImportTask();task.filename=S+'/SM_Picket.obj';task.destination_path=D;task.destination_name='SM_Picket';task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);picket=unreal.load_asset(D+'/SM_Picket');assert picket
  picket.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);ns=picket.get_editor_property('nanite_settings');ns.enabled=False;picket.set_editor_property('nanite_settings',ns);assert A.save_loaded_asset(picket,False)
 from editor_toolset.toolsets.actor import ActorTools
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');components={};counts={};rng=random.Random(412)
 for key,mesh in [('Pickets'+str(i),picket) for i in range(5)]+[('Posts',cube),('Rails',cube),('GateFrame',cube),('GateBoards',picket),('Hinges',cube)]:
  label='G01_Fence_'+key;a=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/Fence');a.set_editor_property('sprite_scale',0);comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Timber');comp.clear_instances();comp.set_static_mesh(mesh);comp.set_material(0,mats[int(key[-1])] if key.startswith('Pickets') else mats[2]);comp.set_collision_profile_name('BlockAll');comp.set_cull_distances(0,100000);components[key]=comp;counts[key]=0
 components['Hinges'].set_material(0,unreal.load_asset('/Game/FinalCoil/World/G01HouseV2/MI_Metal'))
 def add(key,x,y,z,dx,dy,dz,angle=0,pitch=0,roll=0):
  xx,yy=xy(x,y);components[key].add_instance(unreal.Transform(location=unreal.Vector(xx,yy,z),rotation=unreal.Rotator(pitch=pitch,yaw=yaw+angle,roll=roll),scale=unreal.Vector(dx/100,dy/100,dz/100)),True);counts[key]+=1
 def beam(key,p,q,width,depth):
  dx,dy,dz=[q[i]-p[i] for i in range(3)];add(key,(p[0]+q[0])/2,(p[1]+q[1])/2,(p[2]+q[2])/2,math.dist(p,q),depth,width,math.degrees(math.atan2(dy,dx)),math.degrees(math.atan2(dz,math.hypot(dx,dy))))
 segments=[((-hx,-hy),(hx,-hy)),((hx,-hy),(hx,lo)),((hx,hi),(hx,hy)),((hx,hy),(-hx,hy)),((-hx,hy),(-hx,-hy))]
 posts=set()
 for p0,p1 in segments:
  length=math.dist(p0,p1);dx,dy=(p1[0]-p0[0])/length,(p1[1]-p0[1])/length;angle=math.degrees(math.atan2(dy,dx));bays=math.ceil(length/240)
  for i in range(bays+1):
   x,y=p0[0]+dx*length*i/bays,p0[1]+dy*length*i/bays
   token=(round(x,3),round(y,3))
   if token not in posts:
    posts.add(token);z=ground(x,y);add('Posts',x,y,z+76,14,14,164,angle)
  n=math.ceil(length/17)
  for i in range(n):
   d=length*(i+.5)/n;x,y=p0[0]+dx*d,p0[1]+dy*d;z=ground(x,y)+3;height=142+rng.uniform(-4,4);add('Pickets'+str(rng.randrange(5)),x,y,z,11.5,2.8,height,angle+rng.uniform(-.7,.7),0,rng.uniform(-.5,.5))
  for i in range(bays):
   a=[p0[0]+dx*length*i/bays,p0[1]+dy*length*i/bays];b=[p0[0]+dx*length*(i+1)/bays,p0[1]+dy*length*(i+1)/bays]
   for z in [38,112]:beam('Rails',[*a,ground(*a)+z],[*b,ground(*b)+z],9,5)
 # Open one leaf inward and the other outward: both stay clear of the oblique lane.
 leaf=gap/2-12;gate_floor=max(ground(hx,lo),ground(hx,hi),ground(hx,lo-leaf),ground(hx,hi+leaf))+12
 for i,hingey in enumerate([lo,hi]):
  add('Posts',hx,hingey,ground(hx,hingey)+90,23,23,190)
  direction=-1 if i==0 else 1; gate_floor=max(ground(hx,hingey),ground(hx+direction*leaf,hingey))+10; n=math.ceil(leaf/17)
  for j in range(n):
   x=hx+direction*(12+leaf*(j+.5)/n);y=hingey;top=155+18*math.sin(math.pi*(j+.5)/n);add('GateBoards',x,y,gate_floor,11.5,3.5,top)
  for z in [28,125]:beam('GateFrame',[hx+direction*12,hingey-5,gate_floor+z],[hx+direction*(12+leaf),hingey-5,gate_floor+z],12,6)
  beam('GateFrame',[hx+direction*12,hingey-5,gate_floor+25],[hx+direction*(12+leaf),hingey-5,gate_floor+128],10,6)
  for z in [30,125]:add('Hinges',hx-4,hingey,gate_floor+z,16,9,12)
 # Exact original transforms preserved, including house, garage, car, banya and yellow outline.
 assert all(record(by[n])==v for n,v in baseline.items())
 E.set_selected_level_actors([]);assert LV.save_current_level()
 meta=dict(plot='G01',center=h['center'],yaw=yaw,hx=hx,hy=hy,height_cm=145,gate_center_local=[hx,gy],gate_opening_cm=gap,projected_driveway_width_cm=projected,gate_posts_y=[lo,hi],leaf_length_cm=leaf,gate_floor_z=gate_floor,gate_state='two fixed-open leaves, 90 degrees; lower leaf inward, upper leaf outward to clear angled lane',road_crossing_local=[p,q],counts=counts,existing_actor_transforms_unchanged=True)
 json.dump(meta,open(S+'/fence_spec.json','w'),indent=2);json.dump(meta,open(Q+'/built.json','w'),indent=2)
 print('G01 FENCE SAVED',counts)
except BaseException:
 open(Q+'/error.txt','w').write(traceback.format_exc());raise
