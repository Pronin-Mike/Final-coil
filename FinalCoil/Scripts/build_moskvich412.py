"""Blender authoring source. Metres, +X front, Z up; wheel contact origin."""
import bpy, math, json, os
from mathutils import Vector
ROOT='D:/GameDevelop/FinalCoil'
OUT=ROOT+'/SourceArt/Vehicles/Moskvich412'
REVIEW=ROOT+'/Review/Moskvich412'
os.makedirs(OUT,exist_ok=True);os.makedirs(REVIEW,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
M={}
def material(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[name]=m;return m
material('Paint_OliveCream',(.42,.43,.26),.25,.38)
material('Rubber',(.018,.022,.023),0,.85)
material('Chrome',(.55,.58,.58),.85,.25)
material('Glass',(.045,.085,.105),.32,.2)
material('Grille',(.035,.04,.038),.45,.55)
material('Headlamp',(.72,.77,.66),.1,.25)
material('Amber',(.85,.29,.025),.1,.32)
material('TailRed',(.4,.025,.015),.15,.32)
material('Plate',(.03,.035,.03),.1,.6)
parts=[]
def finish(o,name,mat,bevel=0):
 o.name=name;o.data.materials.append(M[mat]);parts.append(o)
 if bevel:
  mod=o.modifiers.new('Small rounded production edges','BEVEL');mod.width=bevel;mod.segments=2
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def box(name,p,size,mat,bev=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,mat,bev)
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name,mat)
def line(name,pts,r,mat):
 # Mesh rods, exported without dependency on Blender curves.
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);d=b-a
  bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();finish(o,name,mat)
def quad(name,pts,mat,trim=False):
 o=mesh(name,pts,[tuple(range(len(pts)))],mat)
 if trim:line(name+'_seal',pts+[pts[0]],.009,'Chrome')
 return o
def cylinder(name,p,r,depth,mat,axis='Y',vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p);o=bpy.context.object
 o.rotation_euler=(math.pi/2,0,0) if axis=='Y' else (0,math.pi/2,0)
 finish(o,name,mat,.004)
 for poly in o.data.polygons:poly.use_smooth=len(poly.vertices)==4
 return o
# Lower body loft with real, open wheel arch silhouettes.
axles=[-.9575,1.4425];xs={-2.015,-1.85,-1.4,-1.28,-.72,0,.72,1.8,2.015}
for axle in axles:
 for i in range(23):xs.add(axle+.355*math.cos(math.pi*i/22))
xs=sorted(xs);v=[]
for x in xs:
 width=.7775-.065*(abs(x)/2.015)**5
 arch=max([.30+math.sqrt(max(0,.355**2-(x-a)**2)) if abs(x-a)<.355 else .245 for a in axles])
 top=.99-.065*(abs(x)/2.015)**3
 for y,z in [(0,.245),(-width*.96,max(.27,arch)),(-width,max(.33,arch)),(-width,top-.065),(-width*.91,top),(width*.91,top),(width,top-.065),(width,max(.33,arch)),(width*.96,max(.27,arch))]:v.append((x,y,z))
n=9;f=[]
for j in range(len(xs)-1):
 for k in range(n):f.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
f.extend([tuple(reversed(range(n))),tuple((len(xs)-1)*n+i for i in range(n))]);mesh('Body_with_open_arches',v,f,'Paint_OliveCream')
# Three-box cabin. Roof slightly crowned, front and rear screens distinctly sloped.
rings=[(-1.28,.665,1.005),(-.73,.58,1.44),(-.56,.57,1.49),(.13,.57,1.49),(.29,.585,1.435),(.83,.665,1.005)]
v=[]
for x,w,z in rings:v.extend([(x,-w,.985),(x,-w,z),(x,0,z+.01),(x,w,z),(x,w,.985)])
f=[]
for i in range(len(rings)-1):
 for k in range(4):f.append((i*5+k,i*5+k+1,(i+1)*5+k+1,(i+1)*5+k))
f.extend([(4,3,2,1,0),tuple(25+i for i in range(5))]);mesh('Cabin_roof_pillars',v,f,'Paint_OliveCream')
quad('Front_windscreen',[(.826,-.623,1.035),(.352,-.55,1.412),(.352,.55,1.412),(.826,.623,1.035)],'Glass',True)
quad('Rear_windscreen',[(-1.276,.625,1.035),(-.799,.55,1.412),(-.799,-.55,1.412),(-1.276,-.625,1.035)],'Glass',True)
def sidey(z):return .669-(z-1.005)/.435*.085+.003
for s in [-1,1]:
 def q(name,xz):return quad(name,[(x,s*sidey(z),z) for x,z in xz],'Glass',True)
 q('Front_door_window',[(.725,1.025),(.25,1.407),(-.18,1.43),(-.18,1.025)])
 q('Rear_door_window',[(-.235,1.025),(-.235,1.43),(-.69,1.415),(-1.18,1.025)])
 # Four doors, handles and waist trim; no high frequency detailing.
 for x in [-.205,.79,-1.255]:line('Door_shutline',[(x,s*.776,.91),(x,s*.778,.37)],.003,'Grille')
 line('Door_lower_seam',[(-1.255,s*.773,.35),(.79,s*.773,.35)],.003,'Grille')
 line('Waist_chrome',[(-1.9,s*.756,.895),(1.9,s*.756,.895)],.005,'Chrome')
 for x in [-.13,-1.04]:
  box('Handle_recess',(x,s*.778,.855),(.145,.012,.04),'Grille',.004)
  box('Door_handle',(x,s*.788,.864),(.115,.018,.018),'Chrome',.004)
 # Driver mirror only, kept within 1.615m bounding width.
 if s==-1:
  line('Mirror_arm',[(.65,-.65,1.04),(.68,-.78,1.1)],.009,'Chrome')
  box('Driver_mirror',(.68,-.79,1.11),(.11,.035,.07),'Chrome')
# Wheels: 2.4m base, 1.270m centre track, 600mm diameter.
for x in axles:
 for s in [-1,1]:
  cylinder('Tyre',(x,s*.635,.3),.3,.155,'Rubber')
  cylinder('Steel_rim',(x,s*.716,.3),.205,.014,'Chrome')
  cylinder('Rim_recess',(x,s*.727,.3),.157,.012,'Grille')
  cylinder('Domed_hubcap',(x,s*.739,.3),.112,.025,'Chrome')
  for j in range(8):
   a=j*math.tau/8;cylinder('Rim_vent',(x+math.cos(a)*.178,s*.726,.3+math.sin(a)*.178),.015,.006,'Grille',vertices=8)
box('Underbody',(0,0,.245),(3.65,1.12,.12),'Grille',.025)
# Flat front, two round lamps and a narrow grille.
box('Front_grille',(2.018,0,.714),(.024,1.08,.235),'Grille',.012)
for y in [-.53,.53]:
 cylinder('Headlight_chrome_ring',(2.022,y,.735),.112,.024,'Chrome','X')
 cylinder('Round_headlight',(2.039,y,.735),.095,.016,'Headlamp','X')
for y in [-.704,.704]:box('Front_indicator',(2.025,y,.73),(.027,.075,.18),'Amber')
for y in [i*.055 for i in range(-7,8)]:box('Grille_bar',(2.035,y,.713),(.012,.009,.185),'Chrome',.001)
box('Grille_badge',(2.046,0,.742),(.008,.065,.043),'TailRed',.002)
for x in [-2.025,2.025]:
 box('Chrome_bumper',(x,0,.467),(.055,1.615,.085),'Chrome',.018)
 box('Bumper_rubber',(x+( .024 if x>0 else -.024),0,.467),(.007,1.2,.024),'Rubber',.003)
 box('Number_plate',(x,0,.58),(.017,.32,.082),'Plate',.003)
for s in [-1,1]:
 box('Rear_lamp_frame',(-2.019,s*.526,.727),(.025,.35,.10),'Chrome')
 box('Rear_lamp_red',(-2.036,s*.61,.727),(.012,.15,.075),'TailRed',.003)
 box('Rear_lamp_amber',(-2.036,s*.505,.727),(.012,.055,.075),'Amber',.003)
 box('Reverse_lamp',(-2.036,s*.426,.727),(.012,.085,.075),'Headlamp',.003)
# Simple hood/trunk panel lines and wipers reinforce proportions.
for s in [-1,1]:
 line('Hood_seam',[(.88,s*.60,.983),(1.89,s*.60,.94)],.003,'Grille')
 line('Wiper',[(.79,s*.24,1.039),(.57,s*.44,1.205)],.006,'Grille')
# Apply geometry, recalculate consistent normals, join as one reusable static prop.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();car=bpy.context.object;car.name='SM_Moskvich412_Blockout'
scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
tri=car.modifiers.new('Export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
points=[car.matrix_world@v.co for v in car.data.vertices];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
report=dict(name=car.name,units='metres',axis='+X forward, Z up',dimensions_m=[hi[i]-lo[i] for i in range(3)],bounds=[lo,hi],wheelbase_m=2.4,track_m=1.27,triangles=len(car.data.polygons),vertices=len(car.data.vertices),materials=[m.name for m in car.data.materials],source='Original procedural Blender blockout, user supplied IZH-412 dimension reference',scope='Static placeholder; no rig, driving physics or detailed interior')
json.dump(report,open(OUT+'/model_validation.json','w'),indent=2)
assert abs(report['dimensions_m'][0]-4.105)<.03
assert abs(report['dimensions_m'][1]-1.615)<.01
assert abs(report['dimensions_m'][2]-1.5)<.01
bpy.ops.export_scene.fbx(filepath=OUT+'/SM_Moskvich412_Blockout.fbx',use_selection=True,object_types={'MESH'},apply_unit_scale=True,global_scale=1,axis_forward='X',axis_up='Z',add_leaf_bones=False,bake_anim=False)
bpy.ops.export_scene.gltf(filepath=OUT+'/SM_Moskvich412_Blockout.glb',use_selection=True,export_format='GLB')
# Studio preview lives in the .blend, export remains car-only.
box('Preview_ground',(0,0,-.06),(200,200,.1),'Grille',.0);parts[-1].hide_set(False)
scene.world.color=(.22,.22,.22)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,p,power,size in [('Key',(2,-4,6),1500,5),('Fill',(-3,-1,4),900,4),('Rim',(1,4,5),1700,3)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.name='Preview_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,.7))
bpy.ops.object.camera_add(location=(6,-7,3.7));cam=bpy.context.object;cam.name='Preview_camera';cam.data.type='ORTHO';cam.data.ortho_scale=6.2;aim(cam,(0,0,.7));scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=REVIEW+'/blender_front.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/Moskvich412_Blockout.blend');bpy.ops.render.render(write_still=True)
cam.location=(-6,7,3.4);aim(cam,(0,0,.7));scene.render.filepath=REVIEW+'/blender_rear.png';bpy.ops.render.render(write_still=True)
print('MOSKVICH_BUILD_OK',json.dumps(report))
