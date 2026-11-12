import unreal,json,math,os,sys,shutil,re,time
from editor_toolset.toolsets.actor import ActorTools
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/CompactVillage';D='/Game/FinalCoil/World/CompactVillage';Q=R+'/Review/CompactVillage'
sys.path.insert(0,R+'/Scripts');import terrain_profile as T
P=json.load(open(S+'/plan.json'));T.GRID=json.load(open(S+'/heightfield.json'));B=P['erase_bounds'];C=P['plant_bounds']
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
assert LV.save_current_level();base=json.load(open(Q+'/baseline.json'));rec={a['label']:a for a in base['actors']};by={a.get_actor_label():a for a in E.get_all_level_actors()};A.make_directory(D)
def stage(name):json.dump(dict(stage=name,time=time.time()),open(Q+'/install_progress.json','w'));unreal.log('COMPACT_STAGE '+name)
def dup(src,name):return unreal.load_asset(D+'/'+name) if A.does_asset_exist(D+'/'+name) else A.duplicate_asset(src,D+'/'+name)
def nodes(m):return L.get_material_expressions(m)
master=dup('/Game/FinalCoil/World/GroundMaterial/M_Berezovka_Ground','M_CompactSurface')
source=unreal.load_asset('/Game/FinalCoil/World/GroundMaterial/M_Berezovka_Ground');sn=next(n for n in nodes(source) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5);n=next(n for n in nodes(master) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5)
code=sn.get_editor_property('code');assert '}; GroundFns g;' in code
code=code.replace('}; GroundFns g;',open(S+'/Functions.hlsl').read()+'}; GroundFns g;')
end='return max(color*Tint,0.002);';assert end in code
condition='P.x>%f&&P.x<%f&&P.y>%f&&P.y<%f'%(B[0],B[2],B[1],B[3])
code=code.replace(end,'if('+condition+'){'+open(S+'/Surface.hlsl').read()+'}\n'+end);n.set_editor_property('code',code)
errors=L.recompile_material(master);json.dump(list(errors or []),open(Q+'/material_errors.json','w'),indent=2);assert not errors,str(errors);assert A.save_loaded_asset(master)
mi=dup('/Game/FinalCoil/World/GroundMaterial/MI_Berezovka_Terrain','MI_CompactSurface');L.set_material_instance_parent(mi,master);L.update_material_instance(mi);assert A.save_loaded_asset(mi)
stage('material')
for kind,name in [('Terrain','SM_CompactTerrain'),('Road','SM_RegionalRoad'),('Path','SM_RegionalPath')]:
 task=unreal.AssetImportTask();task.filename=S+'/'+name+'.obj';task.destination_path=D;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/'+name);assert mesh
 ns=mesh.get_editor_property('nanite_settings');ns.enabled=False;mesh.set_editor_property('nanite_settings',ns)
 body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True)
 actor=by['TERRAIN_'+kind];comp=actor.static_mesh_component;mat=mi if kind=='Terrain' else comp.get_material(0);mesh.set_material(0,mat);comp.set_static_mesh(mesh);comp.set_material(0,mat);actor.set_actor_scale3d(unreal.Vector(1,-1,1));comp.set_editor_property('cast_shadow',kind=='Terrain');assert A.save_loaded_asset(mesh)
stage('terrain')
# Retain old authoring actors as hidden recovery references; replace their visible traces.
def hide(a):
 a.set_actor_hidden_in_game(True)
 for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_visibility(False,True);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for name,a in by.items():
 if '_Yard' in name or '_Boundary_' in name or '_Walkway_ToRoad' in name or name.startswith(('DIM_H11','G01_GarageDrive','G01_HouseWalk','G01_SideDoorPath','SHOP01_Approach','STOP01_RoadApproach')):hide(a)
def place_from_record(a,r,old_anchor,new_anchor,deltaYaw,ground):
 ca,sa=math.cos(deltaYaw),math.sin(deltaYaw);dx,dy=r['p'][0]-old_anchor[0],r['p'][1]-old_anchor[1]
 a.set_actor_location(unreal.Vector(new_anchor[0]+ca*dx-sa*dy,new_anchor[1]+sa*dx+ca*dy,ground+r['p'][2]-old_anchor[2]),False,False)
 a.set_actor_rotation(unreal.Rotator(pitch=r['r'][0],yaw=r['r'][1]+math.degrees(deltaYaw),roll=r['r'][2]),False)
def copy_mesh_actor(src,name):
 a=by.get(name)
 if not a:
  original=by[src];a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(name);a.set_folder_path('50_Homesteads/Compact/'+name.split('_')[0]);a.set_actor_scale3d(original.get_actor_scale3d());c=a.static_mesh_component;c.set_static_mesh(original.static_mesh_component.static_mesh)
  for i in range(original.static_mesh_component.get_num_materials()):c.set_material(i,original.static_mesh_component.get_material(i))
  c.set_collision_profile_name('BlockAll');by[name]=a
 return a
for h in P['plots']:
 ident=h['id']
 if ident=='G01':continue
 src=ident if ident+'_LogHouse' in rec else ('H01' if ident.startswith('H') else 'E01');anchor=rec[src+'_LogHouse'];dyaw=h['yaw']-math.radians(anchor['r'][1]);z=T.height(*h['house'])+6
 for suffix in ['_LogHouse','_ColdEntrance','_Porch']:
  sourceName=src+suffix
  if sourceName not in rec:continue
  actor=copy_mesh_actor(sourceName,ident+suffix);place_from_record(actor,rec[sourceName],anchor['p'],h['house'],dyaw,z)
hero=next(h for h in P['plots'] if h['id']=='G01');anchor=rec['G01_House'];hz=T.height(*hero['house'])+6
for name,r in rec.items():
 if name.startswith('G01_') and name not in ['G01_Yard','G01_Label'] and name not in ['G01_GarageDrive','G01_HouseWalk','G01_SideDoorPath']:
  place_from_record(by[name],r,anchor['p'],hero['house'],hero['yaw'],hz)
for prefix,anchorName,target,pad in [('STOP01_','STOP01_Pad',[0,0],P['service_pads'][0]),('SHOP01_','SHOP01_Floor',P['shop'],P['service_pads'][1])]:
 anchor=rec[anchorName];dyaw=0 if prefix=='STOP01_' else math.pi
 for name,r in rec.items():
  if name.startswith(prefix) and name not in ['STOP01_RoadApproach','SHOP01_Approach']:
   place_from_record(by[name],r,anchor['p'],target,dyaw,T.height(*target)+5)
stage('houses_services')
cube=unreal.load_asset('/Engine/BasicShapes/Cube');outline=unreal.load_asset('/Game/FinalCoil/World/PlotMarkers/M_PlotOutline')
def hism(label,mesh,material,folder):
 a=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label(label);a.set_folder_path(folder);by[label]=a
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Instances');c.clear_instances();c.set_static_mesh(mesh);c.set_material(0,material);c.set_collision_profile_name('NoCollision');c.set_editor_property('cast_shadow',False);c.set_editor_property('can_ever_affect_navigation',False);return a,c
def segment_transforms(points,width=15,zoff=8):
 transforms=[]
 for u,v in zip(points,points[1:]):
  count=math.ceil(math.dist(u,v)/40)
  for j in range(count):
   x,y=u[0]+(v[0]-u[0])*j/count,u[1]+(v[1]-u[1])*j/count;xx,yy=u[0]+(v[0]-u[0])*(j+1)/count,u[1]+(v[1]-u[1])*(j+1)/count;z,zz=T.height(x,y)+zoff,T.height(xx,yy)+zoff;ln=math.sqrt((xx-x)**2+(yy-y)**2+(zz-z)**2)
   transforms.append(unreal.Transform(location=unreal.Vector((x+xx)/2,(y+yy)/2,(z+zz)/2),rotation=unreal.Rotator(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=unreal.Vector((ln+.15)/100,width/100,.02)))
 return transforms
def label(name,text,xy,size=900,zoff=1600):
 a=by.get(name) or E.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector());a.set_actor_label(name);a.set_folder_path('53_PlotOutlines_10Are/HouseLabels');by[name]=a;a.set_actor_location(unreal.Vector(*xy,T.height(*xy)+zoff),False,False);a.set_actor_rotation(unreal.Rotator(pitch=90,yaw=180,roll=0),False);a.set_actor_hidden_in_game(False);a.set_is_temporarily_hidden_in_editor(False)
 c=a.text_render;c.set_visibility(True,True);c.set_hidden_in_game(False);c.set_text(text);c.set_world_size(size);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(unreal.Color(255,255,255,255));c.set_editor_property('cast_shadow',False);return a
for h in P['plots']:
 a,c=hism('PLOT10_'+h['id']+'_1000m2',cube,outline,'53_PlotOutlines_10Are');pts=h['corners']+[h['corners'][0]];ts=segment_transforms(pts);c.add_instances(ts,False,True,False);label(h['id']+'_Label',h['id'],h['house'])
label('STOP01_MapLabel','STOP / WELL',[0,0],800);label('SHOP01_MapLabel','SHOP',P['shop'],750)
# Well at the central public place, outside the waiting platform.
stone=unreal.load_asset('/Game/FinalCoil/World/StopAndG01/M_Floor');wood=unreal.load_asset('/Game/FinalCoil/World/StopAndG01/M_Timber')
def box_actor(name,xy,z,size,mat):
 a=by.get(name) or E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(name);a.set_folder_path('60_Stop01/Well');by[name]=a;a.set_actor_location(unreal.Vector(*xy,T.height(*xy)+z),False,False);a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,mat);a.static_mesh_component.set_collision_profile_name('BlockAll');return a
for i,(dx,dy,sx,sy) in enumerate([(-70,0,20,160),(70,0,20,160),(0,-70,120,20),(0,70,120,20)]):box_actor('STOP01_Well_Rim_'+str(i),[dx,850+dy],40,[sx,sy,80],stone)
for i,dx in enumerate([-85,85]):box_actor('STOP01_Well_Post_'+str(i),[dx,850],120,[12,15,240],wood)
box_actor('STOP01_Well_Beam',[0,850],240,[200,20,15],wood)
# Metric reference for the new layout.
a,c=hism('DIM_StopToHero_140m',cube,outline,'54_ScaleMeasurements');c.add_instances(segment_transforms([[0,0],[0,14000]],20,14),False,True,False);label('DIM_StopToHero_Text','140 m',[0,7000],900,2300)
stage('plots_labels')
# Reproject retained village plants and remove plants from the compact settlement footprint.
for name,a in list(by.items()):
 if not name.startswith('VEG_VillageRoad_'):continue
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);keep=[]
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,True);p=t.translation
  if C[0]<p.x<C[2] and C[1]<p.y<C[3]:continue
  if B[0]<p.x<B[2] and B[1]<p.y<B[3]:t.translation=unreal.Vector(p.x,p.y,T.height(p.x,p.y)-1)
  keep.append(t)
 c.clear_instances();c.add_instances(keep,False,True,False)
conditionC='P.x>%f&&P.x<%f&&P.y>%f&&P.y<%f'%(C[0],C[2],C[1],C[3])
# Existing outside-village foliage stays unchanged outside the new settlement.
for k in ['Green','Dry']:
 m=dup('/Game/FinalCoil/World/VillageRoadPass/M_Grass_'+k+'_OutsideVillage','M_Grass_'+k+'_Regional')
 src=unreal.load_asset('/Game/FinalCoil/World/VillageRoadPass/M_Grass_'+k+'_OutsideVillage');sc=next(n for n in nodes(src) if isinstance(n,unreal.MaterialExpressionCustom) and 'float x=UV.x*' in n.get_editor_property('code'));mc=next(n for n in nodes(m) if isinstance(n,unreal.MaterialExpressionCustom) and 'float x=UV.x*' in n.get_editor_property('code'));mc.set_editor_property('code','if('+conditionC+')return 0;\n'+sc.get_editor_property('code'));assert not L.recompile_material(m);A.save_loaded_asset(m)
 for i in range(4):
  if (i%2==0)==(k=='Green'):by['VEG_Village_Grass_%02d'%i].get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent).set_material(0,m)
plants=json.load(open(S+'/plants.json'))
for i,kind in enumerate(['Low_Green','Low_Dry','Tall_Green','Tall_Dry']):
 src=unreal.load_asset('/Game/FinalCoil/World/VillageRoadPass/M_Grass_'+kind);m=dup(src.get_path_name(),'M_Grass_'+kind)
 sc=next(n for n in nodes(src) if isinstance(n,unreal.MaterialExpressionCustom) and 'float x=UV.x*' in n.get_editor_property('code'));mc=next(n for n in nodes(m) if isinstance(n,unreal.MaterialExpressionCustom) and 'float x=UV.x*' in n.get_editor_property('code'));code=sc.get_editor_property('code');code=re.sub(r'\(\(P\.x>[^?]+\)\?1\.0:0\.0\)','(('+conditionC+')?1.0:0.0)',code);mc.set_editor_property('code',code);assert not L.recompile_material(m);A.save_loaded_asset(m)
 a,c=hism('VEG_Compact_'+kind,unreal.load_asset('/Game/FinalCoil/World/VillagePlants/SM_VillageGrass_%02d'%i),m,'90_Vegetation/CompactVillage');c.set_cull_distances(3500 if i<2 else 6000,6000 if i<2 else 10000)
 transforms=[unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(xy,xy,h)) for x,y,z,yaw,xy,h in plants[i]];c.add_instances(transforms,False,True,False);assert c.get_instance_count()==len(transforms)
# Bushes inside new plots or road corridors are removed, all others reprojected.
for name,a in by.items():
 if not name.startswith('VEG_Village_Shrub'):continue
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);keep=[]
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,True);p=t.translation
  if C[0]<p.x<C[2] and C[1]<p.y<C[3]:continue
  if B[0]<p.x<B[2] and B[1]<p.y<B[3]:t.translation=unreal.Vector(p.x,p.y,T.height(p.x,p.y))
  keep.append(t)
 c.clear_instances();c.add_instances(keep,False,True,False)
stage('vegetation')
start=next(a for a in by.values() if isinstance(a,unreal.PlayerStart));start.set_actor_location(unreal.Vector(-240,220,T.height(-240,220)+110),False,False);start.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),False)
# Update hidden logical POIs to follow their corresponding buildings.
for name,xy in [('POI_STOP01_Temporary',[0,0]),('MARK_STOP01_Temporary',[0,0]),('POI_SHOP01_Provisional',P['shop']),('POI_G01_GrandpaEntrance_Provisional',P['hero'])]:
 if name in by:by[name].set_actor_location(unreal.Vector(*xy,T.height(*xy)+150),False,False)
for path in A.list_assets(D,recursive=True,include_folder=False):A.save_asset(path,only_if_is_dirty=False)
assert LV.save_current_level()
backup=R+'/Saved/Backups/BeforeCompactVillage';os.makedirs(backup,exist_ok=True)
if not os.path.exists(backup+'/heightfield.json'):shutil.copy2(R+'/SourceArt/Terrain/heightfield.json',backup+'/heightfield.json')
shutil.copy2(S+'/heightfield.json',R+'/SourceArt/Terrain/heightfield.json')
json.dump(dict(saved=True,counts=P['counts'],plots=26,anchor_m=140,plants=P['plant_counts'],terrain_mesh='/Game/FinalCoil/World/CompactVillage/SM_CompactTerrain',setbacks_m={h['id']:h['setback_m'] for h in P['plots']}),open(Q+'/installed.json','w'),indent=2)
stage('saved');unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(4500,2500,40000),unreal.Rotator(pitch=-90,yaw=0,roll=0));unreal.log('COMPACT_VILLAGE_INSTALLED_OK')
exec(compile(open(R+'/Scripts/validate_compact_village.py',encoding='utf-8-sig').read(),'validate_compact_village.py','exec'),{})
exec(compile(open(R+'/Scripts/compact_village_walktest.py',encoding='utf-8-sig').read(),'compact_village_walktest.py','exec'),globals())
