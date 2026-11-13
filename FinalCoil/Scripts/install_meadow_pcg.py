"""Extend the master with a bounded, precomputed vegetation subgraph.

Existing zone nodes/data are untouched. Native PCG spawners own their HISM
resources, so rebuilds replace instances without per-plant actors.
"""
from pathlib import Path
import unreal,sys,json,time
_install_started=time.perf_counter()
ROOT=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(ROOT/'Scripts'))
import meadow_distribution as M
cfg=M.config();quality=globals().get('QUALITY',cfg['quality']);preset=cfg['presets'][quality];D='/Game/FinalCoil/Environment/Meadow';P='/Game/FinalCoil/Environment/PCG';A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not unreal.EditorLevelLibrary.get_game_world()
from editor_toolset.toolsets.actor import ActorTools
output=next((a for a in E.get_all_level_actors() if a.get_actor_label()=='MEADOW_Output'),None)
if not output:
 output=E.spawn_actor_from_class(unreal.Actor,unreal.Vector());output.set_actor_label('MEADOW_Output');output.set_folder_path('95_Environment/Meadow');ActorTools.add_component(output,unreal.SceneComponent.static_class(),'MeadowRoot')
output.set_editor_property('is_editor_only_actor',False);output.set_actor_hidden_in_game(False)
source=M.SOURCE/('distribution_'+quality.lower()+'.json')
data=json.loads(source.read_text()) if source.exists() else M.write(quality)
assert data['quality']==quality
graph=unreal.load_asset(P+'/Core/PCG_MeadowVegetation') or AT.create_asset('PCG_MeadowVegetation',P+'/Core',unreal.PCGGraph,unreal.PCGGraphFactory())
existing={str(n.get_editor_property('node_title')):n for n in graph.get_editor_property('nodes')}
def node(title,cls,x,y):
 n=existing.get(title)
 if n:s=n.get_settings()
 else:n,s=graph.add_node_of_type(cls);n.set_editor_property('node_title',title)
 n.set_node_position(x,y);return n,s
assets=[]
for gi,(group,points) in enumerate(data['groups'].items()):
 name='DA_Meadow_'+group;asset=unreal.load_asset(D+'/Data/'+name) or AT.create_asset(name,D+'/Data',unreal.PCGDataAsset,None)
 pd=unreal.new_object(unreal.PCGPointData,outer=asset);md=pd.mutable_metadata()
 for k in ['Exclusion','Z04','GrassDensity']:md.create_float_attribute(k,0.,True)
 md.create_string_attribute('Mesh','',False);md.create_vector_attribute('SurfaceNormal',unreal.Vector(0,0,1),True);pts=[]
 for r in points:
  assert r['exclusion']<=.001
  mesh=D+'/Meshes/SM_Meadow_'+group+f'_{r["variant"]:02}'
  assert A.does_asset_exist(mesh)
  pt=unreal.PCGPoint();pt.transform=unreal.Transform(location=unreal.Vector(*r['p']),rotation=unreal.Rotator(pitch=0,yaw=r['yaw'],roll=0),scale=unreal.Vector(*r['s']));pt.density=1;pt.seed=r['seed'];pt.bounds_min=unreal.Vector(-20,-20,0);pt.bounds_max=unreal.Vector(20,20,90);pt.initialize_metadata(md,unreal.PCGPoint())
  pt.set_float_attribute(md,'Exclusion',r['exclusion']);pt.set_float_attribute(md,'Z04',r['z04']);pt.set_float_attribute(md,'GrassDensity',r['grass_density']);pt.set_string_attribute(md,'Mesh',mesh+'.'+mesh.rsplit('/',1)[-1]);pt.set_vector_attribute(md,'SurfaceNormal',unreal.Vector(*r['n']));pts.append(pt)
 pd.set_points(pts);collection=unreal.PCGDataCollection();collection.add_to_collection(pd,'Out',['MeadowVegetation',group]);asset.get_editor_property('data').tagged_data=collection.tagged_data;asset.set_editor_property('name',name);asset.set_editor_property('description','Bounded dense '+quality+' '+group+'; surface + Z04 + exclusion masks evaluated before import.');assert A.save_loaded_asset(asset,False)
 loader,settings=node('SurfaceMasks_'+group,unreal.PCGLoadDataAssetSettings,0,gi*220);settings.set_editor_property('asset',asset)
 spawner,settings=node('Instances_'+group,unreal.PCGStaticMeshSpawnerSettings,500,gi*220);settings.set_editor_property('target_actor',output);settings.set_mesh_selector_type(unreal.PCGMeshSelectorByAttribute);selector=settings.get_editor_property('mesh_selector_parameters');selector.set_editor_property('attribute_name','Mesh')
 descriptor=selector.get_editor_property('template_descriptor');descriptor.set_editor_property('component_class',unreal.HierarchicalInstancedStaticMeshComponent);descriptor.set_editor_property('cast_shadow',False);descriptor.set_editor_property('cast_dynamic_shadow',False);descriptor.set_editor_property('can_ever_affect_navigation',False);descriptor.set_editor_property('use_default_collision',False)
 body=descriptor.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','NoCollision');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.NO_COLLISION);descriptor.set_editor_property('body_instance',body)
 descriptor.set_editor_property('instance_start_cull_distance',preset['cull_start_cm']);descriptor.set_editor_property('instance_end_cull_distance',preset['cull_end_cm']);descriptor.set_editor_property('instance_lod_distance_scale',preset['lod_scale']);descriptor.set_editor_property('world_position_offset_disable_distance',1500 if quality=='Low' else 3000);descriptor.set_editor_property('component_tags',['MeadowVegetation',group]);descriptor.set_editor_property('affect_distance_field_lighting',False);descriptor.set_editor_property('evaluate_world_position_offset',True);selector.set_editor_property('template_descriptor',descriptor)
 graph.add_edge(loader,'Out',spawner,'In');graph.add_edge(spawner,'Out',graph.get_output_node(),'Out');assets.append(dict(group=group,points=len(pts),data=asset.get_path_name()))
assert A.save_loaded_asset(graph,False)
master=unreal.load_asset(P+'/Core/PCG_Environment_Master');assert master
sub=next((n for n in master.get_editor_property('nodes') if str(n.get_editor_property('node_title'))=='Meadow Vegetation 50m'),None)
if sub:settings=sub.get_settings()
else:sub,settings=master.add_node_of_type(unreal.PCGSubgraphSettings);sub.set_editor_property('node_title','Meadow Vegetation 50m');sub.set_node_position(1500,1100)
settings.set_subgraph(graph);master.add_edge(sub,'Out',master.get_output_node(),'Out');assert A.save_loaded_asset(master,False)
mpc=unreal.load_asset(D+'/MPC_MeadowWind');parameters=mpc.get_editor_property('scalar_parameters');p=parameters[0];p.set_editor_property('default_value',cfg['wind_strength']*preset['wind']);mpc.set_editor_property('scalar_parameters',[p]);assert A.save_loaded_asset(mpc,False)
actor=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='ENV_PCG_Environment');component=actor.get_component_by_class(unreal.PCGComponent);_generation_started=time.perf_counter();component.generate(True)
_report=dict(quality=quality,assets=assets,sha256=data['sha256'],distribution_seconds=data['seconds'],data_import_seconds=_generation_started-_install_started,status='generation_requested');_report_path=ROOT/'Review/MeadowVegetation/installation.json';_report_path.write_text(json.dumps(_report,indent=2));_record_state={'ticks':0}
def _record_generation(dt):
 _record_state['ticks']+=1
 if _record_state['ticks']<2 or component.get_editor_property('generation_in_progress'):return
 _report.update(pcg_generation_seconds=time.perf_counter()-_generation_started,status='generated');_report_path.write_text(json.dumps(_report,indent=2));unreal.unregister_slate_post_tick_callback(_record_handle)
_record_handle=unreal.register_slate_post_tick_callback(_record_generation)
unreal.log('MEADOW_PCG_GENERATION_REQUESTED')
