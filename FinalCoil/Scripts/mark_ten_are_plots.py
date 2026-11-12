"""Live editor: terrain-following nonblocking 25x40m plot outlines only."""
import unreal, math, json, os, sys, shutil
from editor_toolset.toolsets.actor import ActorTools
R='D:/GameDevelop/FinalCoil'
sys.path.insert(0,R+'/Scripts')
import terrain_profile as T
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
A=unreal.EditorAssetLibrary
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='L_Berezovka_Terrain'
assert LV.save_current_level()
os.makedirs(R+'/Saved/Backups/BeforeTenArePlots',exist_ok=True)
if not os.path.exists(R+'/Saved/Backups/BeforeTenArePlots/L_Berezovka_Terrain.umap'):
 shutil.copy2(R+'/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap',R+'/Saved/Backups/BeforeTenArePlots/L_Berezovka_Terrain.umap')
actors={a.get_actor_label():a for a in E.get_all_level_actors()}
homes=sorted([n for n in actors if n.endswith('_LogHouse')])+['G01_House']
assert len(homes)==20
plots=[]
for name in homes:
 ident=name.split('_')[0]
 yard=actors.get(ident+'_Yard_30x40m') or actors[ident+'_Yard']
 p=yard.get_actor_location();yaw=yard.get_actor_rotation().yaw
 cx,cy=p.x,p.y
 # Grandfather's separate house and garage span 24.7m across Y.
 # Centre between the outer walls of the house and garage.
 if ident=='G01':cy=15435
 ang=math.radians(yaw);c,s=math.cos(ang),math.sin(ang)
 hx,hy=(1600,1562.5) if ident=='G01' else (2000,1250)
 corners=[(cx+c*x-s*y,cy+s*x+c*y) for x,y in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]]
 plots.append(dict(id=ident,house=name,center_cm=[cx,cy],yaw=yaw,corners_cm=corners,area_m2=1000,dimensions_m=[hx/50,hy/50]))
def overlaps(a,b):
 for ps in [a,b]:
  for p,q in zip(ps,ps[1:]+ps[:1]):
   ax,ay=-(q[1]-p[1]),q[0]-p[0]
   aa=[x*ax+y*ay for x,y in a];bb=[x*ax+y*ay for x,y in b]
   if max(aa)<=min(bb) or max(bb)<=min(aa):return False
 return True
assert not [(a['id'],b['id']) for i,a in enumerate(plots) for b in plots[i+1:] if overlaps(a['corners_cm'],b['corners_cm'])],'Plots overlap'
D='/Game/FinalCoil/World/PlotMarkers';A.make_directory(D)
m=unreal.load_asset(D+'/M_PlotOutline') if A.does_asset_exist(D+'/M_PlotOutline') else unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_PlotOutline',D,unreal.Material,unreal.MaterialFactoryNew())
m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
n=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
n.set_editor_property('constant',unreal.LinearColor(1.0,.85,.005))
unreal.MaterialEditingLibrary.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.MaterialEditingLibrary.recompile_material(m);assert A.save_loaded_asset(m)
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
hidden=[]
for name,a in actors.items():
 if '_Boundary_' in name and name.split('_')[0] in [p['id'] for p in plots]:
  for comp in a.get_components_by_class(unreal.PrimitiveComponent):comp.set_visibility(False,True)
  a.set_actor_hidden_in_game(True);hidden.append(name)
for p in plots:
 a=actors.get('PLOT10_'+p['id']+'_1000m2') or actors.get('PLOT10_'+p['id']+'_25x40m') or E.spawn_actor_from_class(unreal.Actor,unreal.Vector(0,0,0),unreal.Rotator())
 a.set_actor_label('PLOT10_'+p['id']+'_1000m2');a.set_folder_path('53_PlotOutlines_10Are');a.tags=['Plot10Are','Area1000m2']
 comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'Outline')
 comp.clear_instances()
 comp.set_static_mesh(cube);comp.set_material(0,m);comp.set_collision_profile_name('NoCollision');comp.set_editor_property('cast_shadow',False);comp.set_editor_property('can_ever_affect_navigation',False)
 transforms=[]
 ps=p['corners_cm']
 for u,v in zip(ps,ps[1:]+ps[:1]):
  count=math.ceil(math.dist(u,v)/40)
  for j in range(count):
   x=u[0]+(v[0]-u[0])*j/count;y=u[1]+(v[1]-u[1])*j/count
   xx=u[0]+(v[0]-u[0])*(j+1)/count;yy=u[1]+(v[1]-u[1])*(j+1)/count
   z=T.height(x,y)+3;zz=T.height(xx,yy)+3
   length=math.sqrt((xx-x)**2+(yy-y)**2+(zz-z)**2)
   transforms.append(unreal.Transform(location=unreal.Vector((x+xx)/2,(y+yy)/2,(z+zz)/2),rotation=unreal.Rotator(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=unreal.Vector((length+.15)/100,.15,.015)))
 comp.add_instances(transforms,False,True,False)
 assert comp.get_instance_count()==len(transforms)
 p['outline_segments']=comp.get_instance_count()
assert LV.save_current_level()
os.makedirs(R+'/Review/TenArePlots',exist_ok=True)
json.dump(dict(map='/Game/FinalCoil/Maps/L_Berezovka_Terrain',plots=plots,old_boundaries_hidden=hidden,overlaps=[],saved=True),open(R+'/Review/TenArePlots/result.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(6500,6000,65000),unreal.Rotator(pitch=-90,yaw=0,roll=0))
unreal.log('TEN_ARE_PLOTS_OK count=20 area=1000m2 each')
