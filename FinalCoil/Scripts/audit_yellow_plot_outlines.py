import unreal,json,math
A=unreal.EditorAssetLibrary;L=unreal.MaterialEditingLibrary
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in E.get_all_level_actors()}
plots=[a for n,a in actors.items() if n.startswith('PLOT10_')]
assert len(plots)==20
report=[]
for a in plots:
 c=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
 assert c.static_mesh.get_path_name()=='/Engine/BasicShapes/Cube.Cube'
 points=[]
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,True)
  d=t.rotation.rotate_vector(unreal.Vector(t.scale3d.x*50-.075,0,0))
  p=t.translation-d;points.append((p.x,p.y))
 area=abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(points,points[1:]+points[:1])))/20000
 assert abs(area-1000)<.1,(a.get_actor_label(),area)
 # Segment headings identify the two orthogonal plot axes in world space.
 t=c.get_instance_transform(0,True);axis=t.rotation.rotate_vector(unreal.Vector(1,0,0));mag=math.hypot(axis.x,axis.y);ux,uy=axis.x/mag,axis.y/mag
 px=[x*ux+y*uy for x,y in points];py=[-x*uy+y*ux for x,y in points]
 dimensions=[(max(px)-min(px))/100,(max(py)-min(py))/100]
 report.append(dict(actor=a.get_actor_label(),dimensions_m=dimensions,area_m2=area))
m=unreal.load_asset('/Game/FinalCoil/World/PlotMarkers/M_PlotOutline')
for n in L.get_material_expressions(m):
 if isinstance(n,unreal.MaterialExpressionConstant3Vector):n.set_editor_property('constant',unreal.LinearColor(1.0,.85,.005))
assert not L.recompile_material(m)
assert A.save_loaded_asset(m)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
house_dimensions=[]
for name,a in actors.items():
 if name.endswith('_LogHouse') or name=='G01_House':
  mesh=a.static_mesh_component.static_mesh;box=mesh.get_bounding_box();size=box.max-box.min;s=a.get_actor_scale3d()
  house_dimensions.append(dict(house=name,dimensions_m=[abs(size.x*s.x)/100,abs(size.y*s.y)/100,abs(size.z*s.z)/100]))
json.dump(dict(plots=report,houses=house_dimensions,color='bright yellow',saved=True),open('D:/GameDevelop/FinalCoil/Review/TenArePlots/measured_audit.json','w'),indent=2)
unreal.log('YELLOW_PLOTS_AUDITED_OK count=20 area=1000m2 each')
