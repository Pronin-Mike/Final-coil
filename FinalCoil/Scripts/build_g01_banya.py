"""Small hollow log banya: separate shower/wash room and steam room. UE cm."""
import unreal,json,math,os,sys,shutil,traceback
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/G01Banya';Q=R+'/Review/G01Banya';D='/Game/FinalCoil/World/G01Banya';B=R+'/../.publishing/g01-before-banya'
for p in [S,Q,B]:os.makedirs(p,exist_ok=True)
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 assert LV.save_current_level()
 if not os.path.exists(B+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',B+'/L_Berezovka_Terrain.umap')
 by={a.get_actor_label():a for a in E.get_all_level_actors()}
 def record(a):
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
 if not os.path.exists(Q+'/baseline.json'):json.dump({n:record(a) for n,a in by.items()},open(Q+'/baseline.json','w'),indent=2)
 baseline=json.load(open(Q+'/baseline.json'));P=json.load(open(R+'/SourceArt/CompactVillage/plan.json'));plot=next(h for h in P['plots'] if h['id']=='G01');yaw=math.degrees(plot['yaw']);c,s=plot['c'],plot['s'];cx=plot['center'][0]+c*1000+s*1050;cy=plot['center'][1]+s*1000-c*1050
 sys.path.insert(0,R+'/Scripts');import terrain_profile as T;terrain_center=T.height(cx,cy)
 terrain_samples=[T.height(cx+c*x-s*y,cy+s*x+c*y) for x in [-300,-150,0,150,300] for y in [-250,-125,0,125,250]]
 ground=max(terrain_center,max(terrain_samples)-18)
 def pos(x,y,z):return unreal.Vector(cx+c*x-s*y,cy+s*x+c*y,ground+z)
 A.make_directory(D);mats={k:unreal.load_asset('/Game/FinalCoil/World/G01HouseV2/'+('M_Glass' if k=='Glass' else 'MI_'+k)) for k in ['Log','Floor','Trim','Roof','Stone','Metal','Glass']};assert all(mats.values())
 for name,color,rough in [('WetFloor',[.27,.30,.29],.78),('WetWall',[.52,.54,.49],.7),('Brick',[.29,.17,.10],.95)]:
  m=unreal.load_asset(D+'/MI_'+name) or A.duplicate_asset('/Game/FinalCoil/World/G01HouseV2/MI_Stone',D+'/MI_'+name);L.set_material_instance_vector_parameter_value(m,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(m,'Roughness',rough);L.update_material_instance(m);assert A.save_loaded_asset(m);mats[name]=m
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder');created=[];logs=[]
 def shape(name,x,y,z,sx,sy,sz,mat='Log',mesh=None,pitch=0,roll=0,collision=True):
  label='G01_Banya_'+name;a=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());by[label]=a;a.set_actor_label(label);a.set_folder_path('61_G01/Banya/'+name.split('_')[0]);a.set_actor_location(pos(x,y,z),False,False);a.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll),False);a.set_actor_scale3d(unreal.Vector(sx/100,sy/100,sz/100));a.static_mesh_component.set_static_mesh(mesh or cube);a.static_mesh_component.set_material(0,mats[mat]);a.static_mesh_component.set_collision_profile_name('BlockAll' if collision else 'NoCollision');created.append(label);return a
 def box(name,x,y,z,sx,sy,sz,mat='Log',**kw):return shape(name,x,y,z,sx,sy,sz,mat,**kw)
 def rect(name,x0,x1,y0,y1,z0,z1,mat='Log',**kw):return box(name,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,x1-x0,y1-y0,z1-z0,mat,**kw)
 from editor_toolset.toolsets.actor import ActorTools
 root=by.get('G01_Banya_Origin') or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());root.set_actor_label('G01_Banya_Origin');root.set_folder_path('61_G01/Banya');root.set_editor_property('sprite_scale',0);root.get_component_by_class(unreal.SceneComponent) or ActorTools.add_component(root,unreal.SceneComponent.static_class(),'Origin');root.set_actor_location(pos(0,0,0),False,False)
 entry_ground=T.height(pos(-440,-110,0).x,pos(-440,-110,0).y);foundation_bottom=min(terrain_samples+[entry_ground])-ground-6
 rect('Foundation',-300,300,-250,250,foundation_bottom,20,'Stone');rect('Floor_Shower',-300,0,-250,250,18,30,'WetFloor');rect('Floor_Steam',0,300,-250,250,18,30,'Floor')
 for oldname,oldactor in by.items():
  if oldname.startswith(('G01_Banya_Entry_Step','G01_Banya_Entry_Stair_')):
   oldactor.set_actor_hidden_in_game(True)
   for comp in oldactor.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 step_count=math.ceil((ground+30-entry_ground)/18);step_rise=(ground+30-entry_ground)/step_count
 for i in range(step_count):
  x=-320-(step_count-i)*30;z=entry_ground-ground+(i+1)*step_rise;a=rect('Entry_Stair_%d'%i,x,x+30,-190,-30,entry_ground-ground-5,z,'Floor');a.set_actor_hidden_in_game(False);a.static_mesh_component.set_visibility(True,True)
 rect('Entry_Landing',-320,-290,-190,-30,0,30,'Floor')
 # Real wall openings. Front/partition doorways: 120cm wide x 210cm clear.
 walls=[('Front','X',-290,-250,250,[(-170,-50,30,240),(70,170,140,230)]),('Back','X',290,-250,250,[(-180,-100,160,220)]),('Left','Y',-240,-280,280,[]),('Right','Y',240,-280,280,[]),('Partition','X',0,-240,240,[(-170,-50,30,240)])]
 def intervals(lo,hi,opens,z):
  result=[(lo,hi)]
  for a,b,z0,z1 in opens:
   if not z0<z<z1:continue
   out=[]
   for l,r in result:
    if b<=l or a>=r:out.append((l,r));continue
    if l<a:out.append((l,a))
    if b<r:out.append((b,r))
   result=out
  return result
 for name,axis,fixed,lo,hi,opens in walls:
  zs=sorted(set([30,280]+[z for o in opens for z in o[2:] if 30<z<280]))
  for j,(z0,z1) in enumerate(zip(zs,zs[1:])):
   for i,(l,r) in enumerate(intervals(lo,hi,opens,(z0+z1)/2)):
    if axis=='X':box('Wall_'+name+'_%d_%d'%(j,i),fixed,(l+r)/2,(z0+z1)/2,20,r-l,z1-z0)
    else:box('Wall_'+name+'_%d_%d'%(j,i),(l+r)/2,fixed,(z0+z1)/2,r-l,20,z1-z0)
  for row in range(11):
   z=42+row*22
   for l,r in intervals(lo,hi,opens,z):
    p=pos(fixed,(l+r)/2,z) if axis=='X' else pos((l+r)/2,fixed,z);rot=unreal.Rotator(pitch=0,yaw=yaw,roll=90) if axis=='X' else unreal.Rotator(pitch=90,yaw=yaw,roll=0);logs.append(unreal.Transform(location=p,rotation=rot,scale=unreal.Vector(.24,.24,(r-l)/100)))
 # Window frames and glass.
 for name,fixed,y,z0,z1,width in [('Wash',-290,120,140,230,100),('Steam',290,-140,160,220,80)]:
  box('Window_'+name+'_Glass',fixed,y,(z0+z1)/2,2,width,z1-z0,'Glass')
  for j,yy in enumerate([y-width/2,y+width/2,y]):box('Window_'+name+'_U%d'%j,fixed,yy,(z0+z1)/2,28,6,z1-z0+12,'Floor')
  for j,zz in enumerate([z0,z1]):box('Window_'+name+'_H%d'%j,fixed,y,zz,28,width+12,8,'Floor')
 # Fixed open leaves preserve clear access; interactive doors are a later task.
 box('Door_Exterior_Open',-360,-174,132.5,120,5,205,'Floor');box('Door_Steam_Open',-60,-174,132.5,120,5,205,'Floor')
 for name,x in [('Exterior',-405),('Steam',-105)]:box('Door_'+name+'_Handle',x,-169,125,12,7,4,'Metal',collision=False)
 for name,x in [('Outer',-300),('Inner',0)]:
  for j,y in enumerate([-175,-45]):box('DoorFrame_'+name+'_%d'%j,x,y,135,28,10,210,'Floor')
  box('DoorFrame_'+name+'_Header',x,-110,244,28,140,8,'Floor')
 # Upper closed loft volume gives a flat interior ceiling; attic is not playable.
 def prism_x(poly,xlo,xhi):
  vs=[(x,y,z) for x in [xlo,xhi] for y,z in poly];fs=[];n=len(poly)
  for i in range(1,n-1):fs.extend([(0,i+1,i),(n,n+i,n+i+1)])
  for i in range(n):j=(i+1)%n;fs.extend([(i,j,n+j),(i,n+j,n+i)])
  return vs,fs
 slope=170/285
 vs,fs=prism_x([(-250,280),(250,280),(250,470-slope*250-10),(0,460),(-250,470-slope*250-10)],-300,300);T.write_obj(S+'/SM_BanyaAttic.obj',vs,fs)
 vs=[];fs=[]
 for y0,y1,z0,z1 in [(-285,.5,300,470.3),(-.5,285,470.3,300)]:
  k=len(vs)
  for dz in [-12,0]:vs.extend([(-340,y0,z0+dz),(340,y0,z0+dz),(340,y1,z1+dz),(-340,y1,z1+dz)])
  fs.extend([tuple(k+i for i in f) for f in [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]])
 T.write_obj(S+'/SM_BanyaRoof.obj',vs,fs)
 for name,mat in [('SM_BanyaAttic','Log'),('SM_BanyaRoof','Roof')]:
  task=unreal.AssetImportTask();task.filename=S+'/'+name+'.obj';task.destination_path=D;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/'+name);assert mesh;mesh.set_material(0,mats[mat]);body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True);assert A.save_loaded_asset(mesh)
  label='G01_Banya_'+name;a=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/Banya/Roof');a.set_actor_location(pos(0,0,0),False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(1,-1,1));a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');created.append(label)
 # Two-tier slatted steam benches and an L-shaped return, inspired by the reference.
 for name,x0,x1,top in [('Lower',135,215,75),('Upper',215,285,120)]:
  width=(x1-x0-1.5)/4
  for j in range(4):rect('Bench_'+name+'_Board%d'%j,x0+j*(width+.5),x0+j*(width+.5)+width,-210,210,top-6,top,'Floor')
  for j,(x,y) in enumerate([(x0+7,-195),(x0+7,195),(x1-7,-195),(x1-7,195)]):box('Bench_'+name+'_Leg%d'%j,x,y,(30+top-6)/2,10,10,top-36,'Trim')
 rect('Bench_L_Return',100,215,-235,-170,114,120,'Floor');rect('Bench_L_Lower',70,135,-235,-170,69,75,'Floor')
 # Stove/hearth/stone charge; no heat or water simulation at this stage.
 rect('Stove_Hearth',15,115,105,220,30,35,'Stone');box('Stove_Brick',65,160,87.5,70,75,105,'Brick');box('Stove_Firebox',27,160,90,5,48,65,'Metal');box('Stove_Handle',22,180,92,8,5,18,'Metal',collision=False)
 for i,(x,y,z) in enumerate([(42,139,146),(68,135,148),(89,145,146),(48,173,148),(79,176,149)]):box('Stove_Rock%d'%i,x,y,z,24,23,19,'Stone',pitch=(i%3-1)*15,roll=(i%2)*17)
 shape('Stove_Chimney',90,185,320,20,20,400,'Metal',mesh=cylinder);box('Stove_ChimneyCap',90,185,522,35,35,7,'Metal')
 # A simple wooden bucket beside the lower platform.
 shape('Steam_Bucket',145,155,90,28,28,30,'Floor',mesh=cylinder,collision=False);shape('Steam_BucketInside',145,155,103,23,23,2,'Trim',mesh=cylinder,collision=False)
 # Separate washing room with shower tray, wall linings, mixer and overhead head.
 rect('Shower_Tray',-275,-165,105,230,30,36,'WetWall');box('Shower_BackLining',-285,167.5,140,3,135,220,'WetWall');box('Shower_SideLining',-220,237,140,130,3,220,'WetWall')
 shape('Shower_Pipe',-220,222,135,3,3,170,'Metal',mesh=cylinder,collision=False);shape('Shower_Arm',-220,201,220,3,3,42,'Metal',mesh=cylinder,roll=90,collision=False);shape('Shower_Head',-220,180,218,18,18,4,'Metal',mesh=cylinder,collision=False);box('Shower_Mixer',-220,220,125,23,10,12,'Metal',collision=False);shape('Shower_Drain',-220,165,36.2,12,12,.5,'Metal',mesh=cylinder,collision=False)
 rect('Wash_Bench',-240,-50,-230,-185,69,75,'Floor')
 for j,x in enumerate([-220,-70]):box('Wash_BenchLeg%d'%j,x,-207.5,49.5,10,30,39,'Trim')
 for j,x in enumerate([-230,-150,-70]):box('Wash_Hook%d'%j,x,-225,180,5,12,5,'Metal',collision=False)
 # Modest timber lean-to with coarse firewood cylinders on the courtyard side.
 box('Woodshed_Roof',180,315,210,210,150,10,'Roof',roll=math.degrees(math.atan2(35,130)))
 for j,x in enumerate([90,270]):
  pp=pos(x,375,0);foot=T.height(pp.x,pp.y)-ground-4;box('Woodshed_Post%d'%j,x,375,(foot+190)/2,12,12,190-foot,'Trim')
 wood_z=max(0,max(T.height(pos(x,y,0).x,pos(x,y,0).y)-ground for x in [90,270] for y in [265,365])+4)
 box('Woodshed_Base',180,315,wood_z+7,180,100,14,'Trim')
 for j,(x,y) in enumerate([(105,275),(105,355),(255,275),(255,355)]):
  pp=pos(x,y,0);foot=T.height(pp.x,pp.y)-ground-4;box('Woodshed_BaseFoot%d'%j,x,y,(foot+wood_z)/2,16,16,max(1,wood_z-foot),'Stone')
 firewood=[]
 for row in range(6):
  for j in range(8):firewood.append(unreal.Transform(location=pos(130+j*14+(row%2)*4,315,wood_z+20.5+row*14),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=90),scale=unreal.Vector(.13,.13,.9)))
 for label,mesh,mat,transforms in [('G01_Banya_LogCladding',cylinder,mats['Log'],logs),('G01_Banya_Firewood',cylinder,mats['Floor'],firewood)]:
  a=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/Banya/Logs');comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Instances');comp.clear_instances();comp.set_static_mesh(mesh);comp.set_material(0,mat);comp.set_collision_profile_name('NoCollision');comp.add_instances(transforms,False,True,False)
 for name,x,y,z,power,color in [('Steam',140,20,245,220,[1,.68,.38]),('Wash',-150,10,245,280,[1,.88,.7]),('Entry',-315,-20,220,70,[1,.72,.45])]:
  label='G01_Banya_Light_'+name;a=by.get(label) or E.spawn_actor_from_class(unreal.PointLight,unreal.Vector());a.set_actor_label(label);a.set_folder_path('61_G01/Banya/Lights');a.set_editor_property('sprite_scale',0);a.set_actor_location(pos(x,y,z),False,False);comp=a.point_light_component;comp.set_mobility(unreal.ComponentMobility.MOVABLE);comp.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);comp.set_intensity(power);comp.set_light_color(unreal.LinearColor(*color,1));comp.set_attenuation_radius(400)
 # A small label for planning views; inherited one-sided material hides it from below.
 label=by.get('G01_Banya_Label') or E.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector());label.set_actor_label('G01_Banya_Label');label.set_folder_path('61_G01/Banya');label.set_editor_property('sprite_scale',0);label.set_actor_location(pos(0,0,900),False,False);label.set_actor_rotation(unreal.Rotator(pitch=90,yaw=yaw+180,roll=0),False);label.text_render.set_text('BANYA');label.text_render.set_world_size(150);label.text_render.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);label.text_render.set_text_material(by['G01_Label'].text_render.get_editor_property('text_material'))
 assert all(record(by[n])==r for n,r in baseline.items() if n in by),'An existing actor moved'
 E.set_selected_level_actors([]);assert LV.save_current_level()
 meta=dict(id='G01_Banya',center=[cx,cy],plot_local_center=[1000,-1050],yaw=yaw,ground_z=ground,foundation_datum_z=ground,terrain_center_z=terrain_center,max_terrain_under_building_z=max(terrain_samples),entrance_terrain_z=entry_ground,entry_steps=step_count,entry_step_rise_cm=step_rise,size_cm=[600,500],floor_above_foundation_datum_cm=30,clear_ceiling_cm=250,entrance='towards courtyard, local -X',rooms=[dict(name='Shower / washing room',x_range=[-290,-10]),dict(name='Steam room',x_range=[10,290])],door_clear_width_cm=120,door_clear_height_cm=210,door_state='fixed open blockout leaves',steam_benches='L-shaped, two tiers at 45 and 90cm above floor',stove='brick placeholder with stone charge and chimney',shower='tray, drain, mixer, pipe, overhead shower head',existing_actors_unchanged=True,created=created)
 json.dump(meta,open(S+'/bath_spec.json','w'),indent=2);json.dump({k:v for k,v in meta.items() if k!='created'},open(Q+'/built.json','w'),indent=2);P['outbuildings']=[b for b in P.get('outbuildings',[]) if b.get('id')!='G01_Banya']+[dict(id='G01_Banya',center=[cx,cy],yaw=plot['yaw'],size_cm=[600,500])];json.dump(P,open(R+'/SourceArt/CompactVillage/plan.json','w'),indent=2);unreal.log('G01_BANYA_SAVED')
except BaseException:
 open(Q+'/error.txt','w').write(traceback.format_exc());raise
