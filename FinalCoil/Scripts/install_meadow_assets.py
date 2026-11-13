"""Import only original meadow assets. Execute in the current Unreal Editor."""
from pathlib import Path
import unreal,json,sys,time
ROOT=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(ROOT/'Scripts'))
from meadow_distribution import config,SOURCE
cfg=config();D='/Game/FinalCoil/Environment/Meadow';AT=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary;SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert not unreal.EditorLevelLibrary.get_game_world()
def asset(name,cls,factory):return unreal.load_asset(D+'/'+name) or AT.create_asset(name,D,cls,factory)
mpc=asset('MPC_MeadowWind',unreal.MaterialParameterCollection,unreal.MaterialParameterCollectionFactoryNew())
p=unreal.CollectionScalarParameter();p.set_editor_property('parameter_name','WindStrength');p.set_editor_property('default_value',cfg['wind_strength']*cfg['presets'][cfg['quality']]['wind']);mpc.set_editor_property('scalar_parameters',[p]);A.save_loaded_asset(mpc,False)
palette={'Leaf':((.040,.065,.015),(.19,.26,.065)),'Stem':((.045,.065,.018),(.17,.22,.055)),'Dry':((.075,.060,.025),(.24,.20,.095)),'Seed':((.08,.075,.025),(.22,.20,.09)),'Pink':((.15,.065,.085),(.28,.13,.17)),'Cream':((.22,.23,.15),(.47,.46,.32)),'Yellow':((.18,.13,.018),(.42,.31,.035))}
materials={}
for slot,(root,tip) in palette.items():
 m=asset('M_Meadow_'+slot,unreal.Material,unreal.MaterialFactoryNew());L.delete_all_material_expressions(m);m.set_editor_property('two_sided',True);m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('dithered_lod_transition',True)
 def node(cls,x,y):return L.create_material_expression(m,cls,x,y)
 def cn(a,b,i):assert L.connect_material_expressions(a,'',b,i)
 def custom(code,names,typ,x,y):
  n=node(unreal.MaterialExpressionCustom,x,y);inputs=[]
  for name in names:k=unreal.CustomInput();k.set_editor_property('input_name',name);inputs.append(k)
  n.set_editor_property('inputs',inputs);n.set_editor_property('output_type',typ);n.set_editor_property('code',code);return n
 uv=node(unreal.MaterialExpressionTextureCoordinate,-900,0);rand=node(unreal.MaterialExpressionPerInstanceRandom,-900,150);pos=node(unreal.MaterialExpressionWorldPosition,-900,300);tm=node(unreal.MaterialExpressionTime,-900,450)
 color=custom('float h=saturate(1-UV.y);float vein=.88+.12*pow(1-abs(UV.x-.5)*2,4);return lerp(float3(%s),float3(%s),smoothstep(0,1,h))*vein*(.86+.26*R);'%(','.join(map(str,root)),','.join(map(str,tip))),['UV','R'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-400,0);cn(uv,color,'UV');cn(rand,color,'R');L.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 ss=node(unreal.MaterialExpressionMultiply,0,100);cn(color,ss,'A');ss.set_editor_property('const_b',.8);L.connect_material_property(ss,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
 fill=node(unreal.MaterialExpressionMultiply,200,100);cn(color,fill,'A');fill.set_editor_property('const_b',.12);L.connect_material_property(fill,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.88,220),(unreal.MaterialProperty.MP_SPECULAR,.08,320)]:
  n=node(unreal.MaterialExpressionConstant,0,y);n.set_editor_property('r',value);L.connect_material_property(n,'',prop)
 collection=node(unreal.MaterialExpressionCollectionParameter,-900,650);collection.set_editor_property('collection',mpc);collection.set_editor_property('parameter_name','WindStrength')
 # Root pins exactly at zero. Height in UV allows one wind parameter for all species.
 bend=node(unreal.MaterialExpressionScalarParameter,-900,800);bend.set_editor_property('parameter_name','BendCm');bend.set_editor_property('default_value',1.)
 wind=custom('float h=saturate(1-UV.y);float amp=h*h*W*B;float a=sin(T*1.35+P.x*.0031+P.y*.0017)+.27*sin(T*2.7+P.y*.009+R*6.28);return float3(a,a*.37,0)*amp;',['UV','W','P','T','R','B'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-350,500)
 for n,k in [(uv,'UV'),(collection,'W'),(pos,'P'),(tm,'T'),(rand,'R'),(bend,'B')]:cn(n,wind,k)
 L.connect_material_property(wind,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
 fade=node(unreal.MaterialExpressionPerInstanceFadeAmount,-350,-220);dither=node(unreal.MaterialExpressionMaterialFunctionCall,0,-220);dither.set_material_function(unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'));cn(fade,dither,'Alpha Threshold');L.connect_material_property(dither,'',unreal.MaterialProperty.MP_OPACITY_MASK)
 errors=L.recompile_material(m);assert not errors,str(errors);assert A.save_loaded_asset(m,False);materials[slot]=m
manifest=json.loads((SOURCE/'meshes.json').read_text());installed=[]
for rec in manifest['meshes']:
 name=rec['name'];task=unreal.AssetImportTask();task.filename=str(SOURCE/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
 AT.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
 ns=mesh.get_editor_property('nanite_settings');ns.enabled=False;mesh.set_editor_property('nanite_settings',ns)
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  key=str(slot.get_editor_property('material_slot_name'));assert key in materials,key
  mi=asset('MI_Meadow_'+rec['group']+'_'+key,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());L.set_material_instance_parent(mi,materials[key]);L.set_material_instance_scalar_parameter_value(mi,'BendCm',cfg['groups'][rec['group']]['wind_cm']);L.update_material_instance(mi);A.save_loaded_asset(mi,False);mesh.set_material(i,mi)
 options=unreal.StaticMeshReductionOptions();options.auto_compute_lod_screen_size=False;options.reduction_settings=[unreal.StaticMeshReductionSettings(1.,1.),unreal.StaticMeshReductionSettings(.48,.023),unreal.StaticMeshReductionSettings(.20,.008)]
 assert SM.set_lods(mesh,options)==3;assert SM.get_lod_count(mesh)==3
 SM.remove_collisions(mesh);assert A.save_loaded_asset(mesh,False)
 installed.append(dict(name=name,lods=3,lod_vertices=[SM.get_number_verts(mesh,i) if hasattr(SM,'get_number_verts') else None for i in range(3)]))
(ROOT/'Review/MeadowVegetation/assets.json').write_text(json.dumps(installed,indent=2))
unreal.log('MEADOW_ASSETS_INSTALLED')
