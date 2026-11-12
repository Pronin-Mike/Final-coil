import unreal,json,hashlib,sys,os
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/VillageRoadPass';Q=R+'/Review/VillageRoadPass';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
sys.path.insert(0,R+'/Scripts');import terrain_profile as T
B=json.load(open(R+'/SourceArt/VillageRoadPass/plan.json'))['bounds'];bounds='float4(%.6f,%.6f,%.6f,%.6f)'%tuple(B)
m=unreal.load_asset(D+'/M_Village_Surface');n=next(n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5)
old=open(R+'/SourceArt/VillageRoadPass/SurfaceUpdate_v1.hlsl').read().replace('BOUNDS',bounds);new=open(R+'/SourceArt/VillageRoadPass/SurfaceUpdate.hlsl').read().replace('BOUNDS',bounds)
code=n.get_editor_property('code');assert old in code or new in code;n.set_editor_property('code',code.replace(old,new));errors=L.recompile_material(m);assert not errors,str(errors);A.save_loaded_asset(m)
for name in ['M_Grass_Low_Green','M_Grass_Low_Dry']:
 m=unreal.load_asset(D+'/'+name);m.set_editor_property('tangent_space_normal',False)
 mask=next(n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionCustom) and 'float x=UV.x*' in n.get_editor_property('code'))
 code=mask.get_editor_property('code').replace('float x=UV.x*8;','float x=UV.x*26;').replace('float w=.12*pow','float w=.065*pow');mask.set_editor_property('code',code)
 vn=L.create_material_expression(m,unreal.MaterialExpressionVertexNormalWS,-900,700);sign=L.create_material_expression(m,unreal.MaterialExpressionTwoSidedSign,-900,900);normal=L.create_material_expression(m,unreal.MaterialExpressionCustom,-500,800)
 def inp(name):v=unreal.CustomInput();v.set_editor_property('input_name',name);return v
 normal.set_editor_property('inputs',[inp('VN'),inp('Sign')]);normal.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);normal.set_editor_property('code','return normalize(VN*.15+float3(0,0,.95));')
 L.connect_material_expressions(vn,'',normal,'VN');L.connect_material_expressions(sign,'',normal,'Sign');L.connect_material_property(normal,'',unreal.MaterialProperty.MP_NORMAL)
 errors=L.recompile_material(m);assert not errors,str(errors);A.save_loaded_asset(m)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();checks=[]
for xx,yy in [(0,-10000),(1232,7000),(2640,15000),(4400,25000),(7000,40000)]:
 z=T.height(xx,yy);hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(xx,yy,z+300),unreal.Vector(xx,yy,z-300),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
 assert hit is not None;hz=hit.to_tuple()[5].z;assert abs(hz-z)<6,(xx,yy,hz,z);checks.append({'xy':[xx,yy],'ground_cm':z,'collision_cm':hz})
if 'protected' in globals():
 for file,digest in protected.items():assert hashlib.sha256(open(file,'rb').read()).hexdigest()==digest,file
 json.dump(protected,open(Q+'/protected_asset_hashes.json','w'),indent=2)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
json.dump({'shader_errors':[],'main_road_collision':checks,'surface_mesh_unchanged':True,'village_bounds_cm':B},open(Q+'/final_checks.json','w'),indent=2)
unreal.log('VILLAGE_ROADPASS_FINAL_OK')

exec(open(R+"/Scripts/village_road_playtest.py",encoding="utf-8-sig").read())
