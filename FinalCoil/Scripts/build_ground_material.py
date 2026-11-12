import unreal,os,json,time
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/GroundMaterial'
os.makedirs(R+'/Review/GroundMaterial',exist_ok=True)
L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.save_current_level()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
factory=unreal.AssetToolsHelpers.get_asset_tools();textures={}
for name in ['T_Berezovka_Biome','T_Berezovka_Use']:
 task=unreal.AssetImportTask();task.filename=R+'/SourceArt/GroundMaterial/'+name+'.png';task.destination_path=D;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
 factory.import_asset_tasks([task]);t=unreal.load_asset(D+'/'+name);assert t
 t.set_editor_property('srgb',False);t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
 t.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);t.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP)
 A.save_loaded_asset(t);textures[name]=t
name='M_Berezovka_Ground'
m=unreal.load_asset(D+'/'+name)
if not m:m=factory.create_asset(name,D,unreal.Material,unreal.MaterialFactoryNew())
L.delete_all_material_expressions(m)
m.set_editor_property('two_sided',False);m.set_editor_property('tangent_space_normal',False)
def inp(name):
 n=unreal.CustomInput();n.set_editor_property("input_name",name);return n
def output(name,typ):
 n=unreal.CustomOutput();n.set_editor_property("output_name",name);n.set_editor_property("output_type",typ);return n
def node(cls,x=0,y=0):return L.create_material_expression(m,cls,x,y)
def connect(src,pin,dst,input):assert L.connect_material_expressions(src,pin,dst,input),(str(src),pin,input)
def scalar(name,value,x,y):
 n=node(unreal.MaterialExpressionScalarParameter,x,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
def vector(name,value,x,y):
 n=node(unreal.MaterialExpressionVectorParameter,x,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',unreal.LinearColor(*value));return n
world=node(unreal.MaterialExpressionWorldPosition,-1300,-600)
vn=node(unreal.MaterialExpressionVertexNormalWS,-1300,-400)
# World XY to linear atlas UV, explicit world bounds. OBJ's reflected local Y is irrelevant.
uv=node(unreal.MaterialExpressionCustom,-1050,-200);uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);uv.set_editor_property('inputs',[inp('P')]);uv.set_editor_property('code','return (P.xy-float2(-37000,-132666.6667))/float2(166666.6667,420000);')
connect(world,'',uv,'P')
samples=[]
for j,name in enumerate(textures):
 n=node(unreal.MaterialExpressionTextureSampleParameter2D,-780,-100+j*250);n.set_editor_property('parameter_name',name);n.set_editor_property('texture',textures[name]);n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);connect(uv,'',n,'UVs');samples.append(n)
params={'WaterLevel':-250,'Wetness':1,'MacroScale':2300,'ForestAmount':1,'GravelAmount':.72,'NormalStrength':.65,'SurfaceKind':0}
nodes={k:scalar(k,v,-1300,300+i*95) for i,(k,v) in enumerate(params.items())}
tint=vector('Tint',(1,1,1,1),-1300,1050)
custom=node(unreal.MaterialExpressionCustom,-250,0)
names=['P','VN','Biome','Use']+list(params)+['Tint']
custom.set_editor_property('inputs',[inp(n) for n in names]);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
custom.set_editor_property('additional_outputs',[output('GroundNormal',unreal.CustomMaterialOutputType.CMOT_FLOAT3),output('Roughness',unreal.CustomMaterialOutputType.CMOT_FLOAT1),output('AO',unreal.CustomMaterialOutputType.CMOT_FLOAT1)])
code=open(R+'/SourceArt/GroundMaterial/BerezovkaGround.hlsl').read()
routes=json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes'];lines=[]
for r in routes:
 if r['group']=='Road':
  a,b=r['p'],r['q'];lines.append('d=min(d,segment(p,float2(%.4f,%.4f),float2(%.4f,%.4f)));'%(*a,*b))
custom.set_editor_property('code',code.replace('/* ROAD_SEGMENTS */','\n'.join(lines)))
connect(world,'',custom,'P');connect(vn,'',custom,'VN')
for i,n in enumerate(['Biome','Use']):connect(samples[i],'RGBA',custom,n)
for n,v in nodes.items():connect(v,'',custom,n)
connect(tint,'RGB',custom,'Tint')
for pin,prop in [('',unreal.MaterialProperty.MP_BASE_COLOR),('GroundNormal',unreal.MaterialProperty.MP_NORMAL),('Roughness',unreal.MaterialProperty.MP_ROUGHNESS),('AO',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)]:assert L.connect_material_property(custom,pin,prop)
spec=scalar('Specular',.28,-250,600);assert L.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
L.layout_material_expressions(m)
errors=L.recompile_material(m)
json.dump({'errors':list(errors or []),'road_segments':len(lines),'parameters':params},open(R+'/Review/GroundMaterial/compile.json','w'),indent=2)
assert not errors,str(errors)
A.save_loaded_asset(m)
instances={}
for suffix,kind in [('Terrain',0),('Road',1),('Path',2),('Yard',0),('Rail',4)]:
 name='MI_Berezovka_'+suffix;mi=unreal.load_asset(D+'/'+name)
 if not mi:mi=factory.create_asset(name,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
 L.set_material_instance_parent(mi,m);L.set_material_instance_scalar_parameter_value(mi,'SurfaceKind',kind)
 if suffix=='Rail':L.set_material_instance_scalar_parameter_value(mi,'GravelAmount',1)
 L.update_material_instance(mi);A.save_loaded_asset(mi);instances[suffix]=mi
changes=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor):continue
 n=a.get_actor_label();kind=None
 if n in ['TERRAIN_Terrain','TERRAIN_Forest','TERRAIN_OldBor']:kind='Terrain'
 elif n=='TERRAIN_Road':kind='Road'
 elif n=='TERRAIN_Path':kind='Path'
 elif n=='TERRAIN_Rail':kind='Rail'
 elif '_Yard' in n:kind='Yard'
 elif n in ['STOP01_Pad','G01_GarageDrive']:kind='Road'
 if kind:
  c=a.static_mesh_component;c.set_material(0,instances[kind]);changes.append({'actor':n,'material':instances[kind].get_path_name()})
assert levels.save_current_level()
json.dump({'level':'L_Berezovka_Terrain','changes':changes,'compile_errors':list(errors or []),'surface_geometry_changed':False,'textures':[t.get_path_name() for t in textures.values()]},open(R+'/Review/GroundMaterial/applied.json','w'),indent=2)
unreal.log('BEREZOVKA_GROUND_MATERIAL_OK '+str(len(changes)))
