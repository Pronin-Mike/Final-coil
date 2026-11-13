"""Native UE material/mesh changes, local decal only; retained PCG and positions."""
from pathlib import Path
import unreal,json,sys,time
ROOT=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(ROOT/'Scripts'))
from meadow_distribution import SOURCE,config
D='/Game/FinalCoil/Environment/Meadow';Q=ROOT/'Review/MeadowVegetation/Stage2_1';AT=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);cfg=config()
assert not unreal.EditorLevelLibrary.get_game_world()
def asset(name,cls,factory):return unreal.load_asset(D+'/'+name) or AT.create_asset(name,D,cls,factory)
textures={}
for name in ['T_Meadow_LitterColor','T_Meadow_LitterNormal','T_Meadow_Ecology']:
 task=unreal.AssetImportTask();task.filename=str(SOURCE/(name+'.png'));task.destination_path=D+'/Textures';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);tex=unreal.load_asset(D+'/Textures/'+name);assert tex
 tex.set_editor_property('srgb',name=='T_Meadow_LitterColor')
 if name.endswith('Normal'):tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP)
 elif name.endswith('Ecology'):tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP)
 A.save_loaded_asset(tex,False);textures[name]=tex
def setup(mat):
 L.delete_all_material_expressions(mat)
 def node(cls,x=0,y=0):return L.create_material_expression(mat,cls,x,y)
 def connect(a,b,p,out=''):assert L.connect_material_expressions(a,out,b,p)
 def custom(code,names,typ=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
  c=node(unreal.MaterialExpressionCustom);inputs=[]
  for name in names:i=unreal.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
  c.set_editor_property('inputs',inputs);c.set_editor_property('code',code);c.set_editor_property('output_type',typ);return c
 def scalar(value,prop):n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',value);assert L.connect_material_property(n,'',prop);return n
 def sample(texture,uv,normal=False):
  n=node(unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',texture);n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if normal else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if texture.get_editor_property('srgb') else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);connect(uv,n,'UVs');return n
 return node,connect,custom,scalar,sample
m=asset('M_Meadow_Integrated',unreal.Material,unreal.MaterialFactoryNew());node,cn,custom,scalar,sample=setup(m)
m.set_editor_property('two_sided',True);m.set_editor_property('tangent_space_normal',False);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE);m.set_editor_property('dithered_lod_transition',True)
m.set_editor_property('material_decal_response',unreal.MaterialDecalResponse.MDR_NONE)
uv=node(unreal.MaterialExpressionTextureCoordinate);pos=node(unreal.MaterialExpressionWorldPosition);rand=node(unreal.MaterialExpressionPerInstanceRandom)
field_uv=custom('return (P.xy-float2(15500,27500))/5000;',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);cn(pos,field_uv,'P');field=sample(textures['T_Meadow_Ecology'],field_uv)
color=custom((SOURCE/'MeadowIntegrated.hlsl').read_text(),['UV','F','R']);cn(uv,color,'UV');cn(field,color,'F','RGB');cn(rand,color,'R');L.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
sub=node(unreal.MaterialExpressionMultiply);cn(color,sub,'A');sub.set_editor_property('const_b',.65);L.connect_material_property(sub,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
fill=node(unreal.MaterialExpressionMultiply);cn(color,fill,'A');fill.set_editor_property('const_b',.035);L.connect_material_property(fill,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
scalar(.86,unreal.MaterialProperty.MP_ROUGHNESS);scalar(.12,unreal.MaterialProperty.MP_SPECULAR)
vn=node(unreal.MaterialExpressionVertexNormalWS);vi=node(unreal.MaterialExpressionVertexInterpolator);cn(vn,vi,str(L.get_material_expression_input_names(vi)[0]));sign=node(unreal.MaterialExpressionTwoSidedSign)
normal=custom('return normalize(lerp(N*S,float3(0,0,1),.55));',['N','S']);cn(vi,normal,'N');cn(sign,normal,'S');L.connect_material_property(normal,'',unreal.MaterialProperty.MP_NORMAL)
local=node(unreal.MaterialExpressionPreSkinnedPosition);tm=node(unreal.MaterialExpressionTime);collection=node(unreal.MaterialExpressionCollectionParameter);collection.set_editor_property('collection',unreal.load_asset(D+'/MPC_MeadowWind'));collection.set_editor_property('parameter_name','WindStrength')
wind=custom('float z=max(0,L.z);float amp=z*z/(z+20)*.055*W;float phase=P.x*.0031+P.y*.0017+R*3.7;float a=sin(T*1.35+phase)+.22*sin(T*2.4+P.y*.008+R*6.28);return float3(a,a*.37,0)*amp;',['L','P','R','T','W'])
for n,k in [(local,'L'),(pos,'P'),(rand,'R'),(tm,'T'),(collection,'W')]:cn(n,wind,k)
L.connect_material_property(wind,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
fade=node(unreal.MaterialExpressionPerInstanceFadeAmount);dither=node(unreal.MaterialExpressionMaterialFunctionCall);dither.set_material_function(unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));cn(fade,dither,'Alpha Threshold');L.connect_material_property(dither,'',unreal.MaterialProperty.MP_OPACITY_MASK)
errors=L.recompile_material(m);assert not errors,str(errors);assert A.save_loaded_asset(m,False)
installed=[]
for rec in json.loads((SOURCE/'meshes.json').read_text())['meshes']:
 name=rec['name'];task=unreal.AssetImportTask();task.filename=str(SOURCE/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
 slots=mesh.get_editor_property('static_materials');slot=slots[0];slot.set_editor_property('material_slot_name','Meadow');slot.set_editor_property('material_interface',m);mesh.set_editor_property('static_materials',[slot]);mesh.set_material(0,m)
 ns=mesh.get_editor_property('nanite_settings');ns.enabled=False;mesh.set_editor_property('nanite_settings',ns)
 options=unreal.StaticMeshReductionOptions();options.auto_compute_lod_screen_size=False;options.reduction_settings=[unreal.StaticMeshReductionSettings(1.,1.),unreal.StaticMeshReductionSettings(.28,.018)];assert SM.set_lods(mesh,options)==2;SM.remove_collisions(mesh);assert A.save_loaded_asset(mesh,False)
 installed.append(dict(name=name,slots=len(mesh.get_editor_property('static_materials')),sections=[mesh.get_num_sections(i) for i in range(2)],triangles=[mesh.get_num_triangles(i) for i in range(2)]))
# Local DBuffer decal retains the existing terrain material and actor untouched.
ground=asset('M_Meadow_GroundDetail',unreal.Material,unreal.MaterialFactoryNew());node,cn,custom,scalar,sample=setup(ground);ground.set_editor_property('material_domain',unreal.MaterialDomain.MD_DEFERRED_DECAL);ground.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
p=node(unreal.MaterialExpressionWorldPosition);ground_uv=custom('return P.xy/120;',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);cn(p,ground_uv,'P')
uv2=custom('return float2(-U.y,U.x)*1.731+float2(.31,.73);',['U'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);cn(ground_uv,uv2,'U');a=sample(textures['T_Meadow_LitterColor'],ground_uv);b=sample(textures['T_Meadow_LitterColor'],uv2);n=sample(textures['T_Meadow_LitterNormal'],ground_uv,True)
fuv=custom('return (P.xy-float2(15500,27500))/5000;',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT2);cn(p,fuv,'P');ecology=sample(textures['T_Meadow_Ecology'],fuv)
col=custom('float3 c=lerp(A,B,.28+.14*F.r);return c*lerp(float3(.90,.96,.91),float3(1.1,1.04,.86),F.g)*lerp(.87,1.1,F.r);',['A','B','F']);cn(a,col,'A','RGB');cn(b,col,'B','RGB');cn(ecology,col,'F','RGB');L.connect_material_property(col,'',unreal.MaterialProperty.MP_BASE_COLOR)
L.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_NORMAL);scalar(.91,unreal.MaterialProperty.MP_ROUGHNESS);scalar(.08,unreal.MaterialProperty.MP_SPECULAR)
strength=node(unreal.MaterialExpressionScalarParameter);strength.set_editor_property('parameter_name','GroundStrength');strength.set_editor_property('default_value',cfg.get('ground_strength',.85))
opacity=custom('float2 e=min(P.xy-float2(15500,27500),float2(20500,32500)-P.xy);float terrain=1-smoothstep(2,4,abs(P.z-F.b*256));return S*F.a* smoothstep(0,80,min(e.x,e.y))*terrain;',['P','F','S'],unreal.CustomMaterialOutputType.CMOT_FLOAT1);cn(p,opacity,'P');cn(ecology,opacity,'F','RGBA');cn(strength,opacity,'S');L.connect_material_property(opacity,'',unreal.MaterialProperty.MP_OPACITY)
errors=L.recompile_material(ground);assert not errors,str(errors);assert A.save_loaded_asset(ground,False)
from editor_toolset.toolsets.actor import ActorTools
output=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='MEADOW_Output');decal=next((c for c in output.get_components_by_class(unreal.DecalComponent) if c.get_name()=='MeadowGroundDetail'),None) or ActorTools.add_component(output,unreal.DecalComponent.static_class(),'MeadowGroundDetail')
ground_instance=asset('MI_Meadow_GroundDetail',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());L.set_material_instance_parent(ground_instance,ground);L.set_material_instance_scalar_parameter_value(ground_instance,'GroundStrength',cfg.get('ground_strength',.85));assert A.save_loaded_asset(ground_instance,False)
decal.set_editor_property('decal_size',unreal.Vector(180,2500,2500));decal.set_world_location(unreal.Vector(18000,30000,170),False,False);decal.set_world_rotation(unreal.Rotator(pitch=-90,yaw=0,roll=0),False,False);decal.set_decal_material(ground_instance);decal.set_editor_property('fade_screen_size',.0001);decal.set_visibility(True,True);decal.set_hidden_in_game(False,True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(Q/'stage21_assets.json').write_text(json.dumps(dict(meshes=installed,shared_material=m.get_path_name(),ground_material=ground.get_path_name(),ground_component=decal.get_name(),textures=[v.get_path_name() for v in textures.values()],instance_count_unchanged=True),indent=2))
unreal.log('MEADOW_STAGE21_INSTALLED')
