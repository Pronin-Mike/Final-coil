"""Import changed cell point assets and reversible editor-only debug; never alter gameplay geometry."""
from pathlib import Path
import unreal,json,os,sys,math,time,traceback,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'SourceArt/EnvironmentZones';Q=ROOT/'Review/EnvironmentZones';D='/Game/FinalCoil/Environment/PCG';sys.path.insert(0,str(ROOT/'Scripts'))
import environment_zones as Z
try:
 started=time.perf_counter();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.MaterialEditingLibrary
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()!='L_Berezovka_Terrain':assert LV.load_level('/Game/FinalCoil/Maps/L_Berezovka_Terrain')
 assert LV.save_current_level();backup=Q/'before_environment.umap'
 # Binary recovery point is kept in Saved, not a second working level in Content.
 backup=ROOT/'Saved/EnvironmentZones/before_environment.umap';backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():shutil.copy2(ROOT/'Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',backup)
 by={a.get_actor_label():a for a in E.get_all_level_actors()};baseline=json.loads((Q/'before_scene.json').read_text());cfg=Z.load(S/'zones.json');byzone={z['id']:z for z in cfg['zones']}
 def create_data(name):
  path=D+'/Masks/'+name;asset=unreal.load_asset(path)
  if asset:return asset
  asset=AT.create_asset(name,D+'/Masks',unreal.PCGDataAsset,None);assert asset;return asset
 A.make_directory(D+'/Masks');A.make_directory(D+'/Debug');cachepath=S/'import_cache.json';cache=Z.load(cachepath) if cachepath.exists() else {};newcache=dict(cache);tagged=[];imported=[]
 for file in sorted((S/'cells').glob('*.json')):
  payload=Z.load(file);name=payload['id'];hashvalue=hashlib.sha256(b'PCG-cell-ownership-v2'+file.read_bytes()).hexdigest();asset=create_data('DA_Zones_'+name)
  if cache.get(name)!=hashvalue or not asset.get_editor_property('data').tagged_data:
   data=unreal.new_object(unreal.PCGPointData,outer=asset);metadata=data.mutable_metadata();floatkeys=['Exclusion','Slope','Wetness','Dryness','Forest','Road','Path','PlotWeight','WheelTracks','TreeDensity','ShrubDensity','GrassDensity']+list(byzone)
   for key in floatkeys:metadata.create_float_attribute(key,0.,True)
   metadata.create_string_attribute('ZoneID','',False);metadata.create_string_attribute('PlotID','',False);metadata.create_vector_attribute('SurfaceNormal',unreal.Vector(0,0,1),True);points=[]
   for row in payload['points']:
    # The overview is diagnostic only. Overlapping test windows have one owner,
    # preferring the finer sample spacing, then the stable cell ID.
    x,y=row['position'][:2];owners=[c for c in cfg['test_cells'] if c['id']!='world_overview' and c['bounds_cm'][0]<=x<c['bounds_cm'][2] and c['bounds_cm'][1]<=y<c['bounds_cm'][3]]
    if name=='world_overview' or min(owners,key=lambda c:(c['step_cm'],c['id']))['id']!=name:continue
    pt=unreal.PCGPoint();pt.transform=unreal.Transform(location=unreal.Vector(*row['position']),rotation=unreal.Rotator(),scale=unreal.Vector(.1,.1,.1));pt.density=row['density'];pt.seed=row['seed'];pt.color=unreal.Vector4(*byzone[row['zone']]['debug_color'],1);pt.bounds_min=unreal.Vector(-5,-5,-5);pt.bounds_max=unreal.Vector(5,5,5)
    pt.initialize_metadata(metadata,unreal.PCGPoint())
    for key in floatkeys:pt.set_float_attribute(metadata,key,float(row['weights'][key] if key.startswith('Z') else row[{'PlotWeight':'plot_weight','WheelTracks':'wheel_tracks','TreeDensity':'tree_density','ShrubDensity':'shrub_density','GrassDensity':'grass_density'}.get(key,key.lower())]))
    pt.set_string_attribute(metadata,'ZoneID',row['zone']);pt.set_string_attribute(metadata,'PlotID',row['plot_id']);pt.set_vector_attribute(metadata,'SurfaceNormal',unreal.Vector(*row['normal']));points.append(pt)
   data.set_points(points);collection=unreal.PCGDataCollection();collection.add_to_collection(data,'Out',['Cell:'+name,'EnvironmentZones']);asset.get_editor_property('data').tagged_data=collection.tagged_data;asset.set_editor_property('name',name);asset.set_editor_property('description','Heightfield surface + current use masks + weighted zones + exclusions. Rebuild via Scripts/environment_zones.py.');assert A.save_loaded_asset(asset,False);imported.append(name);newcache[name]=hashvalue
  tagged.extend(asset.get_editor_property('data').tagged_data)
 mat=unreal.load_asset(D+'/Debug/M_ZoneDebug')
 if not mat:
  mat=AT.create_asset('M_ZoneDebug',D+'/Debug',unreal.Material,unreal.MaterialFactoryNew());mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
  custom=L.create_material_expression(mat,unreal.MaterialExpressionCustom,0,0);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);inputs=[]
  for k in ['R','G','B','Exclude','Slope','Wet','Mode']:i=unreal.CustomInput();i.set_editor_property('input_name',k);inputs.append(i)
  custom.set_editor_property('inputs',inputs);custom.set_editor_property('code','if(Mode<0.5)return float3(R,G,B);if(Mode<1.5)return lerp(float3(.07,.25,.09),float3(1,.03,.01),Exclude);if(Mode<2.5)return lerp(float3(.05,.6,.1),float3(1,.05,.01),saturate(Slope/30));return lerp(float3(.4,.25,.08),float3(.05,.25,1),Wet);')
  for idx,k in enumerate(['R','G','B','Exclude','Slope','Wet']):
   n=L.create_material_expression(mat,unreal.MaterialExpressionPerInstanceCustomData,-700,idx*110);n.set_editor_property('data_index',idx);v=L.create_material_expression(mat,unreal.MaterialExpressionVertexInterpolator,-450,idx*110);assert L.connect_material_expressions(n,'',v,str(L.get_material_expression_input_names(v)[0]));assert L.connect_material_expressions(v,'',custom,k)
  mode=L.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-400,-120);mode.set_editor_property('parameter_name','DebugMode');mode.set_editor_property('default_value',0);assert L.connect_material_expressions(mode,'',custom,'Mode');assert L.connect_material_property(custom,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);errors=L.recompile_material(mat);assert not errors,str(errors);assert A.save_loaded_asset(mat,False)
 materials={}
 for mode,name in enumerate(['Zones','Exclusions','Slope','Wetness']):
  mi=unreal.load_asset(D+'/Debug/MI_Debug'+name)
  if not mi:
   mi=AT.create_asset('MI_Debug'+name,D+'/Debug',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());L.set_material_instance_parent(mi,mat);L.set_material_instance_scalar_parameter_value(mi,'DebugMode',mode);L.update_material_instance(mi);assert A.save_loaded_asset(mi,False)
  materials[name]=mi
 from editor_toolset.toolsets.actor import ActorTools
 debug_counts={}
 for file in sorted((S/'cells').glob('*.json')):
  payload=Z.load(file);name=payload['id'];label='ENV_Debug_'+name
  if name not in imported and label in by and os.environ.get('FINALCOIL_ENV_DEBUG_REBUILD')!='1':continue
  actor=by.get(label) or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());actor.set_actor_label(label);actor.set_folder_path('95_Environment/Debug');actor.set_editor_property('is_editor_only_actor',True);actor.set_editor_property('sprite_scale',0);actor.tags=[unreal.Name('EnvironmentDebug'),unreal.Name(name)];comp=actor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(actor,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'ZonePoints');comp.clear_instances();comp.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));comp.set_material(0,materials['Zones']);comp.set_collision_profile_name('NoCollision');comp.set_editor_property('cast_shadow',False);comp.set_editor_property('num_custom_data_floats',6);comp.set_cull_distances(0,0)
  step=payload['step_cm'];ts=[]
  for row in payload['points']:
   x,y,z=row['position'];ts.append(unreal.Transform(location=unreal.Vector(x,y,z+45),rotation=unreal.MathLibrary.make_rot_from_z(unreal.Vector(*row['normal'])),scale=unreal.Vector(step*.95/100,step*.95/100,.025)))
  comp.add_instances(ts,False,True,False)
  for index,row in enumerate(payload['points']):
   values=[sum(byzone[k]['debug_color'][channel]*weight for k,weight in row['weights'].items()) for channel in range(3)]+[row['exclusion'],row['slope'],row['wetness']]
   for channel,value in enumerate(values):comp.set_custom_data_value(index,channel,float(value),index==len(ts)-1 and channel==5)
  comp.set_visibility(False,True);actor.set_actor_hidden_in_game(True);actor.set_is_temporarily_hidden_in_editor(True);debug_counts[name]=len(ts)
 # Verification: original transforms, meshes, collision profiles, instance counts and materials.
 changed=[]
 for name,old in baseline.items():
  a=by[name];t=a.get_actor_transform();r=t.rotation.rotator();p=t.translation;s=t.scale3d
  if max(abs(v-w) for v,w in zip([p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],old['transform']))>.001:changed.append(name+':transform')
  comps=a.get_components_by_class(unreal.StaticMeshComponent)
  for before,k in zip(old['components'],comps):
   if (k.static_mesh.get_path_name() if k.static_mesh else None)!=before['mesh'] or str(k.get_collision_enabled())!=before['collision']:changed.append(name+':mesh/collision')
   if [k.get_material(i).get_path_name() if k.get_material(i) else None for i in range(k.get_num_materials())]!=before['materials']:changed.append(name+':materials')
   if isinstance(k,unreal.InstancedStaticMeshComponent) and k.get_instance_count()!=before['instances']:changed.append(name+':instances')
 assert not changed,changed
 E.set_selected_level_actors([]);assert LV.save_current_level();cachepath.write_text(json.dumps(newcache,indent=2));(Q/'installation.json').write_text(json.dumps(dict(status='passed',imported_cells=imported,debug_counts=debug_counts,original_actor_count=len(baseline),unchanged_original_objects=True,seconds=time.perf_counter()-started),indent=2))
except BaseException:
 (Q/'install_error.txt').write_text(traceback.format_exc());raise
