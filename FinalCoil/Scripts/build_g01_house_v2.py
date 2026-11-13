"""Hollow log cabin blockout, walkable loft and attached existing G01 garage. UE cm."""
import unreal,json,math,os,sys,shutil,traceback
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/G01HouseV2';Q=R+'/Review/G01HouseV2';D='/Game/FinalCoil/World/G01HouseV2';B=R+'/../.publishing/g01-house-before'
for p in [S,Q,B]:os.makedirs(p,exist_ok=True)
try:
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 if not world or world.get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 assert LV.save_current_level()
 if not os.path.exists(B+'/L_Berezovka_Terrain.umap'):shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',B+'/L_Berezovka_Terrain.umap')
 by={a.get_actor_label():a for a in E.get_all_level_actors()}
 def xyz(p):return [p.x,p.y,p.z]
 def rec(a):
  r=a.get_actor_rotation();return dict(p=xyz(a.get_actor_location()),r=[r.pitch,r.yaw,r.roll],s=xyz(a.get_actor_scale3d()))
 if not os.path.exists(Q+'/baseline.json'):json.dump({n:rec(a) for n,a in by.items()},open(Q+'/baseline.json','w'),indent=2)
 baseline=json.load(open(Q+'/baseline.json'));P=json.load(open(R+'/SourceArt/CompactVillage/plan.json'));plot=next(p for p in P['plots'] if p['id']=='G01');yaw=math.degrees(plot['yaw']);ca,sa=math.cos(plot['yaw']),math.sin(plot['yaw']);ground=plot['z']
 # Keep the garage and all its contents fixed. Place the new house against the
 # garage's door side, touching at outer wall faces, not at the porch.
 garage=by['G01_Garage_Floor'];gp=garage.get_actor_location();gyaw=garage.get_actor_rotation().yaw
 cx=gp.x+sa*770;cy=gp.y-ca*770
 def pos(x,y,z):return unreal.Vector(cx+ca*x-sa*y,cy+sa*x+ca*y,ground+z)
 A.make_directory(D);parent=unreal.load_asset('/Game/FinalCoil/Vehicles/Moskvich412/M_VehicleBlockout');assert parent
 mats={}
 for name,color,metal,rough in [('Log',[.28,.12,.055],0,.9),('Trim',[.12,.055,.025],0,.9),('Floor',[.36,.21,.10],0,.8),('Roof',[.055,.085,.115],.25,.8),('Stone',[.28,.29,.25],0,.95),('Metal',[.12,.14,.15],.6,.5)]:
  m=unreal.load_asset(D+'/MI_'+name) or AT.create_asset('MI_'+name,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());L.set_material_instance_parent(m,parent);L.set_material_instance_vector_parameter_value(m,'Tint',unreal.LinearColor(*color,1));L.set_material_instance_scalar_parameter_value(m,'Metallic',metal);L.set_material_instance_scalar_parameter_value(m,'Roughness',rough);L.update_material_instance(m);assert A.save_loaded_asset(m);mats[name]=m
 glass=unreal.load_asset(D+'/M_Glass')
 if not glass:
  glass=AT.create_asset('M_Glass',D,unreal.Material,unreal.MaterialFactoryNew());glass.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);glass.set_editor_property('two_sided',True)
  for name,val,cls,prop,yy in [('Tint',unreal.LinearColor(.13,.25,.31,1),unreal.MaterialExpressionVectorParameter,unreal.MaterialProperty.MP_BASE_COLOR,0),('Opacity',.17,unreal.MaterialExpressionScalarParameter,unreal.MaterialProperty.MP_OPACITY,150),('Roughness',.15,unreal.MaterialExpressionScalarParameter,unreal.MaterialProperty.MP_ROUGHNESS,300)]:
   n=L.create_material_expression(glass,cls,-300,yy);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',val);assert L.connect_material_property(n,'',prop)
  assert not L.recompile_material(glass);assert A.save_loaded_asset(glass)
 mats['Glass']=glass;cube=unreal.load_asset('/Engine/BasicShapes/Cube');cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder');created=[];logs=[];colliders=[]
 def box(name,x,y,z,sx,sy,sz,mat='Log',pitch=0,roll=0,collision=True,group=None):
  label='G01_H2_'+name;actor=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());by[label]=actor;actor.set_actor_label(label);actor.set_folder_path('61_G01/HouseV2/'+(group or name.split('_')[0]));actor.set_actor_location(pos(x,y,z),False,False);actor.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll),False);actor.set_actor_scale3d(unreal.Vector(sx/100,sy/100,sz/100));comp=actor.static_mesh_component;comp.set_static_mesh(cube);comp.set_material(0,mats[mat]);comp.set_collision_profile_name('BlockAll' if collision else 'NoCollision');actor.tags=[unreal.Name('G01HouseV2')];created.append(label)
  if collision:colliders.append(dict(name=label,center=[x,y,z],size=[sx,sy,sz],pitch=pitch,roll=roll))
  return actor
 def rect(name,x0,x1,y0,y1,z0,z1,mat='Log',**kw):return box(name,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,x1-x0,y1-y0,z1-z0,mat,**kw)
 # Archive opaque previous house blocks, retain recoverability without collision.
 for name in ['G01_House','G01_HouseEntrance','G01_HousePorch']:
  actor=by.get(name)
  if actor and 'ARCHIVE_'+name not in by:
   actor.set_actor_label('ARCHIVE_'+name);actor.set_folder_path('99_Archive/G01_PreHouseV2');actor.set_actor_hidden_in_game(True);actor.set_is_temporarily_hidden_in_editor(True)
   for comp in actor.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
   by['ARCHIVE_'+name]=actor;del by[name]
 from editor_toolset.toolsets.actor import ActorTools
 root=by.get('G01_House') or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());root.set_actor_label('G01_House');root.set_folder_path('61_G01/HouseV2');root.set_editor_property('sprite_scale',0);rootcomp=root.get_component_by_class(unreal.SceneComponent) or ActorTools.add_component(root,unreal.SceneComponent.static_class(),'HouseOrigin');root.set_actor_location(pos(0,0,60),False,False);root.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
 # Raised floor with a real notch for four descending garage-link steps.
 for i,b in enumerate([(-500,-170,-400,400),(-30,500,-400,400),(-170,-30,-400,260)]):rect('GroundFloor_%d'%i,*b,40,60,'Floor')
 # Foundation skirt; garage doorway reaches down to the garage's lower floor.
 rect('Foundation_Front',480,500,-400,400,-10,40,'Stone');rect('Foundation_Back',-500,-480,-400,400,-10,40,'Stone');rect('Foundation_Left',-480,480,-400,-380,-10,40,'Stone')
 for i,(a,b) in enumerate([(-480,-170),(-30,480)]):rect('Foundation_Link%d'%i,a,b,380,400,-10,40,'Stone')
 # Wall faces: axis X means fixed X, tangent Y; axis Y means fixed Y.
 walls=[('Front','X',490,[(-300,-150,150,285),(150,300,150,285),(-65,65,60,290)]),('Back','X',-490,[(-300,-140,150,280),(100,260,150,280)]),('Left','Y',-390,[(-250,-80,150,280),(150,320,150,280)]),('Link','Y',390,[(-170,-30,5,290)])]
 def intervals(lo,hi,opens,z):
  parts=[(lo,hi)]
  for a,b,z0,z1 in opens:
   if not z0<z<z1:continue
   result=[]
   for l,r in parts:
    if b<=l or a>=r:result.append((l,r));continue
    if l<a:result.append((l,a))
    if b<r:result.append((b,r))
   parts=result
  return parts
 for name,axis,fixed,opens in walls:
  lo,hi=(-400,400) if axis=='X' else (-480,480);zs=sorted(set([60,420]+[z for o in opens for z in o[2:] if 60<z<420]))
  for zi,(z0,z1) in enumerate(zip(zs,zs[1:])):
   for i,(l,r) in enumerate(intervals(lo,hi,opens,(z0+z1)/2)):
    if axis=='X':box('Wall_'+name+'_%d_%d'%(zi,i),fixed,(l+r)/2,(z0+z1)/2,20,r-l,z1-z0)
    else:box('Wall_'+name+'_%d_%d'%(zi,i),(l+r)/2,fixed,(z0+z1)/2,r-l,20,z1-z0)
  # Separate instanced round logs provide the coarse log-cabin silhouette.
  for row in range(16):
   z=72+row*22
   if z>410:continue
   for l,r in intervals(lo,hi,opens,z):
    if axis=='X':logs.append(unreal.Transform(location=pos(fixed,(l+r)/2,z),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=90),scale=unreal.Vector(.24,.24,(r-l)/100)))
    else:logs.append(unreal.Transform(location=pos((l+r)/2,fixed,z),rotation=unreal.Rotator(pitch=90,yaw=yaw,roll=0),scale=unreal.Vector(.24,.24,(r-l)/100)))
 # Window frames and transparent panes. Doors stay open at this blockout stage.
 for wall,axis,fixed,opens in walls:
  for i,(a,b,z0,z1) in enumerate(opens):
   if z0<100:continue
   t=(a+b)/2;z=(z0+z1)/2;w=b-a;h=z1-z0
   if axis=='X':
    box('Window_'+wall+str(i)+'_Glass',fixed,t,z,2,w,h,'Glass');box('Window_'+wall+str(i)+'_Sill',fixed,t,z0,32,w+16,10,'Trim')
    for j,tt in enumerate([a,b,t]):box('Window_'+wall+str(i)+'_U'+str(j),fixed,tt,z,28,8,h+16,'Trim')
    for j,zz in enumerate([z0,z1,z]):box('Window_'+wall+str(i)+'_H'+str(j),fixed,t,zz,28,w+16,8,'Trim')
   else:
    box('Window_'+wall+str(i)+'_Glass',t,fixed,z,w,2,h,'Glass');box('Window_'+wall+str(i)+'_Sill',t,fixed,z0,w+16,32,10,'Trim')
    for j,tt in enumerate([a,b,t]):box('Window_'+wall+str(i)+'_U'+str(j),tt,fixed,z,8,28,h+16,'Trim')
    for j,zz in enumerate([z0,z1,z]):box('Window_'+wall+str(i)+'_H'+str(j),t,fixed,zz,w+16,28,8,'Trim')
 # Upper floor has a proper stairwell: no slab spans the staircase.
 for i,b in enumerate([(-500,-400,-400,400),(154,500,-400,400),(-400,154,-400,-270),(-400,154,-110,400)]):rect('LoftFloor_%d'%i,*b,338,360,'Floor')
 for i in range(18):
  x=-350+28*(i+.5);top=60+(i+1)*300/18;rect('Stair_Main_%02d'%i,x-14,x+14,-250,-130,60,top,'Floor')
 # Upper stair guard rails, open at the top landing (x=154).
 for yside in [-270,-110]:
  box('LoftRail_Top_'+str(yside),-123,yside,460,554,8,10,'Trim')
  for j in range(8):box('LoftRail_Post_%d_%d'%(yside,j),-395+j*77,yside,410,8,8,100,'Trim')
 box('LoftRail_Back',-400,-190,460,8,160,10,'Trim')
 # Sloping handrails along both sides of the stair, with 1.2m clear treads.
 angle=math.degrees(math.atan2(300,504))
 for i,y in enumerate([-260,-120]):
  box('Stair_Handrail%d'%i,-98,y,300,math.hypot(504,300),7,7,'Trim',pitch=angle)
  for j in [0,4,8,12,17]:
   top=60+(j+1)*300/18;box('Stair_Post%d_%d'%(i,j),-350+28*(j+.5),y,top+45,7,7,90,'Trim')
 # Four 13.75cm risers down to the retained garage floor, 35cm treads.
 for i in range(4):
  top=60-(i+1)*55/4;rect('Stair_Garage_%d'%i,-170,-30,260+i*35,295+i*35,0,top,'Floor')
 # Garage existing 1.1m side opening is widened to 1.4m and its header raised.
 ga=math.radians(gyaw);gc,gs=math.cos(ga),math.sin(ga);gf=gp.z+5
 def garage_wall(name,v,sx,h,sz):
  a=by[name];a.set_actor_location(unreal.Vector(gp.x+gc*v-gs*360,gp.y+gs*v+gc*360,gf+h),False,False);a.set_actor_scale3d(unreal.Vector(sx/100,.2,sz/100))
 garage_wall('G01_Garage_RightWallFront',-210,480,162.5,325);garage_wall('G01_Garage_RightWallBack',310,280,162.5,325);garage_wall('G01_Garage_SideDoorHeader',100,140,305,40)
 # Gable prism with an actual central window opening. Reused at both ends.
 verts=[];faces=[]
 def prism(poly):
  k=len(verts);n=len(poly)
  for y in [-10,10]:verts.extend([(x,y,z) for x,z in poly])
  for i in range(1,n-1):faces.extend([(k,k+i+1,k+i),(k+n,k+n+i,k+n+i+1)])
  for i in range(n):j=(i+1)%n;faces.extend([(k+i,k+j,k+n+j),(k+i,k+n+j,k+n+i)])
 prism([(-500,420),(-90,420),(-90,715.2)]);prism([(90,420),(500,420),(90,715.2)])
 prism([(-90,420),(90,420),(90,450),(-90,450)]);prism([(-90,650),(90,650),(90,715.2),(0,780),(-90,715.2)])
 sys.path.insert(0,R+'/Scripts');import terrain_profile as T;T.write_obj(S+'/SM_GableWindow.obj',verts,faces)
 task=unreal.AssetImportTask();task.filename=S+'/SM_GableWindow.obj';task.destination_path=D;task.destination_name='SM_GableWindow';task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);gable=unreal.load_asset(D+'/SM_GableWindow');assert gable;gable.set_material(0,mats['Log']);gable.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert A.save_loaded_asset(gable)
 for i,y in enumerate([-390,390]):
  a=by.get('G01_H2_Gable%d'%i) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label('G01_H2_Gable%d'%i);a.set_folder_path('61_G01/HouseV2/Roof');a.set_actor_location(pos(0,y,0),False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.static_mesh_component.set_static_mesh(gable);a.static_mesh_component.set_collision_profile_name('BlockAll');created.append(a.get_actor_label())
  box('GableGlass%d'%i,0,y,550,180,2,200,'Glass')
  for j,x in enumerate([-90,0,90]):box('GableFrame%d_%d'%(i,j),x,y,550,8,28,216,'Trim')
  for j,z in enumerate([450,550,650]):box('GableHorizontal%d_%d'%(i,j),0,y,z,196,28,8,'Trim')
 # Main roof slopes around a real dormer opening on the porch-facing slope.
 def roof(name,x0,x1,y0,y1,z0,z1):box('Roof_'+name,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,math.hypot(x1-x0,z1-z0),y1-y0,14,'Roof',pitch=math.degrees(math.atan2(z1-z0,x1-x0)))
 roof('Back',-550,0,-450,450,384,780)
 roof('FrontLeft',0,550,-450,-170,780,384);roof('FrontRight',0,550,170,450,780,384)
 roof('FrontUpper',0,130,-170,170,780,686.4);roof('FrontApron',450,550,-170,170,456,384)
 roof('Dormer',130,450,-185,185,720,688)
 # Continuous planar dormer cheeks avoid teeth along the sloping interior roof.
 for oldname,oldactor in by.items():
  if oldname.startswith('G01_H2_DormerSide_'):
   oldactor.set_actor_hidden_in_game(True);oldactor.set_is_temporarily_hidden_in_editor(True)
   for comp in oldactor.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 task=unreal.AssetImportTask();task.filename=S+'/SM_DormerSide.obj';task.destination_path=D;task.destination_name='SM_DormerSide';task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);cheek=unreal.load_asset(D+'/SM_DormerSide');assert cheek;cheek.set_material(0,mats['Log']);cheek.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert A.save_loaded_asset(cheek)
 for name,y in [('Left',-175),('Right',175)]:
  label='G01_H2_DormerPlane_'+name;actor=by.get(label) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label(label);actor.set_folder_path('61_G01/HouseV2/Roof');actor.set_actor_location(pos(0,y,0),False,False);actor.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);actor.static_mesh_component.set_static_mesh(cheek);actor.static_mesh_component.set_collision_profile_name('BlockAll');created.append(label)
 # Dormer face with twin windows, no opaque wall behind its glazing.
 for i,(ya,yb,za,zb) in enumerate([(-175,-145,470,688),(-30,30,470,688),(145,175,470,688),(-145,145,470,500),(-145,145,655,688)]):rect('DormerFace%d'%i,430,450,ya,yb,za,zb,'Log')
 for i,(a,b) in enumerate([(-145,-30),(30,145)]):
  box('DormerGlass%d'%i,440,(a+b)/2,577.5,2,b-a,155,'Glass')
  for j,y in enumerate([a,b]):box('DormerFrameU%d_%d'%(i,j),440,y,577.5,30,8,171,'Trim')
  for j,z in enumerate([500,655]):box('DormerFrameH%d_%d'%(i,j),440,(a+b)/2,z,30,b-a+16,8,'Trim')
 # Porch remains 1m laterally clear of garage wall; 6m x 2.5m deck.
 rect('Porch_Deck',500,750,-300,300,40,60,'Floor');roof('Porch',480,800,-320,320,370,325)
 for i,(x,y) in enumerate([(520,-285),(520,285),(750,-285),(750,285)]):
  top=370-(x-480)*45/320;box('Porch_Post%d'%i,x,y,(60+top)/2,18,18,top-60,'Trim');box('Porch_Footing%d'%i,x,y,20,34,34,40,'Stone')
 for i,(a,b) in enumerate([(-300,-100),(100,300)]):
  box('Porch_FrontRail%d'%i,750,(a+b)/2,155,10,b-a,10,'Trim')
  for j in range(7):box('Porch_FrontPicket%d_%d'%(i,j),750,a+(j+.5)*(b-a)/7,105,6,6,90,'Trim')
 for i,y in enumerate([-300,300]):
  box('Porch_SideRail%d'%i,625,y,155,250,10,10,'Trim')
  for j in range(8):box('Porch_SidePicket%d_%d'%(i,j),515+j*32,y,105,6,6,90,'Trim')
 for i in range(4):rect('Porch_Step%d'%i,840-i*30,870-i*30,-80,80,0,(i+1)*15,'Floor')
 # Chunky stone chimney and cap, away from staircase and garage-link opening.
 box('Chimney_Shaft',-260,270,470,70,70,820,'Stone');box('Chimney_Cap',-260,270,887,95,95,14,'Metal')
 box('Fireplace_Hearth',-260,250,65,110,115,10,'Stone');box('Fireplace_Front',-260,225,120,90,15,110,'Stone')
 # Cheap instancing keeps the log facade editable without hundreds of actors.
 la=by.get('G01_H2_LogCladding') or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());la.set_actor_label('G01_H2_LogCladding');la.set_folder_path('61_G01/HouseV2/Walls');lc=la.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(la,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Logs');lc.clear_instances();lc.set_static_mesh(cylinder);lc.set_material(0,mats['Log']);lc.set_collision_profile_name('NoCollision');lc.add_instances(logs,False,True,False)
 # Warm utility lighting is part of this house, outdoor lighting stays intact.
 for name,x,y,z,intensity,radius in [('Living',0,20,310,800,650),('Loft',0,0,650,600,650),('Porch',505,110,260,160,350),('Garage',0,770,270,1000,650)]:
  label='G01_H2_Light_'+name;light=by.get(label) or E.spawn_actor_from_class(unreal.PointLight,unreal.Vector());light.set_actor_label(label);light.set_folder_path('61_G01/HouseV2/Lights');light.set_actor_location(pos(x,y,z),False,False);comp=light.point_light_component;comp.set_mobility(unreal.ComponentMobility.MOVABLE);comp.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);comp.set_intensity(intensity);comp.set_light_color(unreal.LinearColor(1,.72,.43,1));comp.set_attenuation_radius(radius)
  for sprite in light.get_components_by_class(unreal.BillboardComponent):sprite.set_visibility(False)
  light.set_editor_property('sprite_scale',0)
 # Label and logical entrance follow the new house within the same plot.
 if 'G01_Label' in by:by['G01_Label'].set_actor_location(pos(0,0,1600),False,False)
 if 'POI_G01_GrandpaEntrance_Provisional' in by:by['POI_G01_GrandpaEntrance_Provisional'].set_actor_location(pos(900,0,120),False,False)
 # New front walk; all other roads and the site boundary stay exactly as before.
 oldfunctions=open(R+'/SourceArt/CompactVillage/Functions.hlsl').read();open(S+'/Functions_before.hlsl','w').write(oldfunctions)
 gate=[gp.x+ca*500,gp.y+sa*500];turn=[pos(800,770,0).x,pos(800,770,0).y];approach=[pos(900,0,0).x,pos(900,0,0).y]
 P['walks']=[r for r in P['walks'] if r['name']!='G01_HouseWalk'];P['walks']+=[dict(name='G01_HouseWalk',p=p,q=q,width=160) for p,q in zip([gate,turn],[turn,approach])]
 def roadfn(name,rs):
  code='float4 '+name+'(float2 p){float best=1e9,d=1e9,w=0,k=0,v;'
  for r in rs:
   half=r['width']/2;code+='v=segment(p,float2(%.5f,%.5f),float2(%.5f,%.5f));if(v-%.3f<best){best=v-%.3f;d=v;w=%.3f;k=%.1f;}'%(*r['p'],*r['q'],half,half,half,1 if r['name'].startswith('Main') else 0)
  return code+'return float4(d,w,k,0);}\n'
 newwalk=roadfn('compactWalk',P['walks']);start=oldfunctions.index('float4 compactWalk(');end=oldfunctions.index('float compactYard(',start);newfunctions=oldfunctions[:start]+newwalk+oldfunctions[end:]
 master=unreal.load_asset(D+'/M_HouseGround') or A.duplicate_asset('/Game/FinalCoil/World/HeroForestMove/M_HeroForestSurface',D+'/M_HouseGround');node=next(n for n in L.get_material_expressions(master) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5);code=node.get_editor_property('code');assert oldfunctions in code;node.set_editor_property('code',code.replace(oldfunctions,newfunctions));assert not L.recompile_material(master);assert A.save_loaded_asset(master)
 mi=unreal.load_asset(D+'/MI_HouseGround') or A.duplicate_asset('/Game/FinalCoil/World/HeroForestMove/MI_HeroForestSurface',D+'/MI_HouseGround');L.set_material_instance_parent(mi,master);L.update_material_instance(mi);assert A.save_loaded_asset(mi);by['TERRAIN_Terrain'].static_mesh_component.set_material(0,mi)
 plot['house']=[cx,cy];P['hero']=[cx,cy];P['hero_distance_m']=math.dist(P['hero'],P['stop'])/100;P['hero_house_version']='Hollow log cabin V2 with loft and attached garage'
 # Ensure every non-G01 neighbour and all garage furniture keep their transforms.
 modified_allowed={'G01_House','G01_HouseEntrance','G01_HousePorch','G01_Label','POI_G01_GrandpaEntrance_Provisional','G01_Garage_RightWallFront','G01_Garage_RightWallBack','G01_Garage_SideDoorHeader'};unexpected=[]
 for name,r in baseline.items():
  if name in modified_allowed or name not in by:continue
  if rec(by[name])!=r:unexpected.append(name)
 assert not unexpected,unexpected
 E.set_selected_level_actors([]);assert LV.save_current_level()
 json.dump(P,open(R+'/SourceArt/CompactVillage/plan.json','w'),indent=2);open(R+'/SourceArt/CompactVillage/Functions.hlsl','w').write(newfunctions);open(S+'/Functions.hlsl','w').write(newfunctions)
 config=dict(status='saved',house_center=[cx,cy],yaw=yaw,ground_z=ground,house_size_cm=[1000,800],porch_size_cm=[250,600],garage_size_cm=[900,700],ground_floor_height_cm=60,loft_height_cm=360,roof_eave_height_cm=420,roof_ridge_height_cm=780,main_stair=dict(steps=18,rise_cm=300/18,tread_cm=28,width_cm=120,start_x=-350,end_x=154,y=-190),garage_link=dict(x=-100,y=390,width_cm=140,headroom_at_house_cm=230,steps=4,rise_cm=13.75,tread_cm=35),porch_gap_to_garage_cm=100,porch_roof_gap_to_garage_cm=80,original_garage_contents_unchanged=True,colliders=colliders,created=created)
 json.dump(config,open(S+'/house_spec.json','w'),indent=2);json.dump({k:v for k,v in config.items() if k not in ['colliders','created']},open(Q+'/built.json','w'),indent=2);unreal.log('G01_HOUSE_V2_SAVED')
except BaseException:
 open(Q+'/error.txt','w').write(traceback.format_exc());raise
