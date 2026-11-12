import unreal,math,json,os,sys
from editor_toolset.toolsets.actor import ActorTools
R='D:/GameDevelop/FinalCoil';sys.path.insert(0,R+'/Scripts');import terrain_profile as T
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert LV.save_current_level()
by={a.get_actor_label():a for a in E.get_all_level_actors()};h=by['H11_LogHouse'];pos=h.get_actor_location();rot=h.get_actor_rotation();scale=h.get_actor_scale3d();box=h.static_mesh_component.static_mesh.get_bounding_box()
ang=math.radians(rot.yaw);c,s=math.cos(ang),math.sin(ang)
cx=pos.x+c*(box.min.x+box.max.x)*scale.x/2-s*(box.min.y+box.max.y)*scale.y/2
cy=pos.y+s*(box.min.x+box.max.x)*scale.x/2+c*(box.min.y+box.max.y)*scale.y/2
best=None
for r in json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes']:
 if not r['label'].startswith('NET_MainRoad'):continue
 a,b=r['p'],r['q'];dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((cx-a[0])*dx+(cy-a[1])*dy)/(dx*dx+dy*dy)));q=(a[0]+t*dx,a[1]+t*dy);d=math.hypot(cx-q[0],cy-q[1])
 if best is None or d<best[0]:best=(d,q,(dx,dy),t,r['label'])
d,q,tangent,t,route=best;assert 0<t<1
nx,ny=(cx-q[0])/d,(cy-q[1])/d
yard=by['H11_Yard_30x40m'];yp=yard.get_actor_location();ya=math.radians(yard.get_actor_rotation().yaw);c,s=math.cos(ya),math.sin(ya)
assert 'PLOT10_H11_1000m2' in by
ox,oy=q[0]-yp.x,q[1]-yp.y
lx,ly=ox*c+oy*s,-ox*s+oy*c;vx,vy=nx*c+ny*s,-nx*s+ny*c
enter,leave=-1e20,1e20
for p,v,lo,hi in [(lx,vx,-2000,2000),(ly,vy,-1250,1250)]:
 if abs(v)<1e-8:assert lo<=p<=hi;continue
 aa,bb=sorted([(lo-p)/v,(hi-p)/v]);enter=max(enter,aa);leave=min(leave,bb)
assert 250<enter<leave
start=(q[0]+250*nx,q[1]+250*ny);end=(q[0]+enter*nx,q[1]+enter*ny);length=enter-250
assert abs(nx*tangent[0]+ny*tangent[1])<.01
a=by.get('DIM_H11_RoadToPlot') or by.get('DIM_H11_RoadToHouse') or E.spawn_actor_from_class(unreal.Actor,unreal.Vector());a.set_actor_label('DIM_H11_RoadToPlot');a.set_folder_path('54_ScaleMeasurements')
comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent) or ActorTools.add_component(a,unreal.HierarchicalInstancedStaticMeshComponent.static_class(),'DimensionLine')
comp.clear_instances();comp.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));comp.set_material(0,unreal.load_asset('/Game/FinalCoil/World/PlotMarkers/M_PlotOutline'));comp.set_collision_profile_name('NoCollision');comp.set_editor_property('cast_shadow',False);comp.set_editor_property('can_ever_affect_navigation',False)
trans=[]
def line(a,b,width):
 n=math.ceil(math.dist(a,b)/40)
 for i in range(n):
  x,y=a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n;xx,yy=a[0]+(b[0]-a[0])*(i+1)/n,a[1]+(b[1]-a[1])*(i+1)/n
  z,zz=T.height(x,y)+16,T.height(xx,yy)+16
  trans.append(unreal.Transform(location=unreal.Vector((x+xx)/2,(y+yy)/2,(z+zz)/2),rotation=unreal.Rotator(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=unreal.Vector(math.sqrt((xx-x)**2+(yy-y)**2+(zz-z)**2)/100+.002,width/100,.025)))
line(start,end,25)
for p in [start,end]:line((p[0]-ny*120,p[1]+nx*120),(p[0]+ny*120,p[1]-nx*120),25)
comp.add_instances(trans,False,True,False)
text=by.get('DIM_H11_Metres') or E.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector());text.set_actor_label('DIM_H11_Metres');text.set_folder_path('54_ScaleMeasurements')
mx,my=(start[0]+end[0])/2,(start[1]+end[1])/2;text.set_actor_location(unreal.Vector(mx,my,T.height(mx,my)+2300),False,False);text.set_actor_rotation(unreal.Rotator(pitch=90,yaw=180,roll=0),False)
tc=text.text_render;tc.set_text('%.1f m'%(length/100));tc.set_world_size(1200);tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);tc.set_text_render_color(unreal.Color(255,240,40,255));tc.set_editor_property('cast_shadow',False)
assert LV.save_current_level()
os.makedirs(R+'/Review/H11Measurement',exist_ok=True)
json.dump(dict(saved=True,length_m=length/100,from_edge='5m carriageway edge, excludes shoulder',to_edge='H11 plot boundary, 25x40m rectangle',start_cm=start,end_cm=end,route=route,perpendicular=True),open(R+'/Review/H11Measurement/result.json','w'),indent=2)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(mx,my,16000),unreal.Rotator(pitch=-90,yaw=0,roll=0))
unreal.log('H11_MEASUREMENT_OK %.3f m'%(length/100))
