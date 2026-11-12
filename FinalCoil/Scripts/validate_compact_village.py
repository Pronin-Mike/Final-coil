import unreal,json,math,sys,hashlib,os
R='D:/GameDevelop/FinalCoil';sys.path.insert(0,R+'/Scripts');import terrain_profile as T
P=json.load(open(R+'/SourceArt/CompactVillage/plan.json'));T.GRID=json.load(open(R+'/SourceArt/CompactVillage/heightfield.json'));B=P['erase_bounds']
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in E.get_all_level_actors()};world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();out={'plots':[],'collision_checks':[],'remote_transforms_unchanged':[]}
for h in P['plots']:
 name=h['id']+('_House' if h['id']=='G01' else '_LogHouse');p=by[name].get_actor_location();assert math.hypot(p.x-h['house'][0],p.y-h['house'][1])<.01
 c=by['PLOT10_'+h['id']+'_1000m2'].get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);points=[]
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,True);d=t.rotation.rotate_vector(unreal.Vector(t.scale3d.x*50-.075,0,0));p=t.translation-d;points.append([p.x,p.y])
 area=abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(points,points[1:]+points[:1])))/20000;assert abs(area-1000)<.01
 out['plots'].append(dict(id=h['id'],area_m2=area,setback_m=h['setback_m']))
for r in P['roads']:
 x,y=(r['p'][0]+r['q'][0])/2,(r['p'][1]+r['q'][1])/2;z=T.height(x,y)
 hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,z+300),unreal.Vector(x,y,z-300),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
 assert hit is not None,(x,y);hz=hit.to_tuple()[5].z;assert abs(hz-z)<6,(r['name'],x,y,hz,z);out['collision_checks'].append(dict(route=r['name'],xy=[x,y],error_cm=abs(hz-z)))
for rec in json.load(open(R+'/Review/CompactVillage/baseline.json'))['actors']:
 name=rec['label'];p=rec['p']
 if name.startswith(('Lake_','Forest_','OldBor_','BOR_','CHAPEL01_','MARK_LAKE','MARK_OLD_BOR')) or (not B[0]<p[0]<B[2] or not B[1]<p[1]<B[3]) and not name.startswith('VEG_'):
  a=by[name];q=a.get_actor_location();rot=a.get_actor_rotation();scale=a.get_actor_scale3d();assert max(abs(q.x-p[0]),abs(q.y-p[1]),abs(q.z-p[2]))<.01,name
  assert max(abs(rot.pitch-rec['r'][0]),abs(rot.yaw-rec['r'][1]),abs(rot.roll-rec['r'][2]))<.01,name
  out['remote_transforms_unchanged'].append(name)
stop=by['STOP01_Pad'].get_actor_location();hero=by['G01_House'].get_actor_location();out['anchor_horizontal_m']=math.hypot(hero.x-stop.x,hero.y-stop.y)/100;assert abs(out['anchor_horizontal_m']-140)<.0001
out['counts']=dict(occupied=sum(n.startswith('H') and n.endswith('_LogHouse') for n in by),vacant=sum(n.startswith('E') and n.endswith('_LogHouse') for n in by),hero=1);assert out['counts']==dict(occupied=14,vacant=11,hero=1)
hashes=json.load(open(R+'/Review/VillageRoadPass/protected_asset_hashes.json'));out['protected_original_assets_unchanged']=0
for file,digest in hashes.items():assert hashlib.sha256(open(file,'rb').read()).hexdigest()==digest,file;out['protected_original_assets_unchanged']+=1
out['saved']=True;json.dump(out,open(R+'/Review/CompactVillage/validation.json','w'),indent=2);unreal.log('COMPACT_VALIDATION_OK')
