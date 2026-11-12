import unreal,os,json,shutil
R='D:/GameDevelop/FinalCoil';L=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert LV.save_current_level()
os.makedirs(R+'/Saved/Backups/BeforeRoad5m',exist_ok=True)
file=R+'/Content/FinalCoil/World/VillageRoadPass/M_Village_Surface.uasset'
dest=R+'/Saved/Backups/BeforeRoad5m/M_Village_Surface.uasset'
if not os.path.exists(dest):shutil.copy2(file,dest)
m=unreal.load_asset('/Game/FinalCoil/World/VillageRoadPass/M_Village_Surface')
n=next(n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5)
code=n.get_editor_property('code');assert '// VILLAGE_ROAD_5M' not in code
old='float dist=rd.x, width=rd.y;';assert old in code
routes=json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes']
fn='float mainRoadDistance(float2 p){float d=1e9;'
for route in routes:
 if not route['label'].startswith('NET_MainRoad'):continue
 fn+='d=min(d,segment(p,float2(%.6f,%.6f),float2(%.6f,%.6f)));'%(*route['p'],*route['q'])
fn+='return d;}\n'
assert '}; GroundFns g;' in code
code=code.replace('}; GroundFns g;',fn+'}; GroundFns g;')
code=code.replace(old,'// VILLAGE_ROAD_5M: 5m carriageway, 0.5-1m shoulders on each side.\nfloat dist=rd.x, width=rd.y-(g.mainRoadDistance(P.xy)<=rd.x+1?100:0);')
old='float irregular=(g.fbm(P.xy/330+warp*1.8)-.5)*150;';assert old in code
code=code.replace(old,'float irregular=clamp((g.fbm(P.xy/330+warp*1.8)-.5)*90,-25,25);')
old='float shoulder=1-smoothstep(width*.67,width+100+irregular,dist);';assert old in code
code=code.replace(old,'float shoulder=1-smoothstep(width,width+75+irregular,dist);')
old='float edge=exp(-pow((dist-width*.91)/65,2));';assert old in code
code=code.replace(old,'float edge=exp(-pow((dist-width-28)/38,2));\nusedSoil=lerp(usedSoil,soil*1.08,smoothstep(width-5,width+35,dist)*.6);')
# Keep the existing pedestrian access connected after the lane becomes narrower.
code=code.replace('max(580-P.x,P.x-820)','max(480-P.x,P.x-820)')
n.set_editor_property('code',code);assert not L.recompile_material(m);assert A.save_loaded_asset(m)
assert '// STOP01_LAYBY' in code and '// STOP01_WAITING' in code
assert LV.save_current_level()
os.makedirs(R+'/Review/Road5m',exist_ok=True)
json.dump(dict(saved=True,scope='village',carriageway_m=5,shoulder_each_m=[.5,1],nominal_corridor_m=6.5,layby_extra_width_m=3,terrain_collision_unchanged=True),open(R+'/Review/Road5m/result.json','w'),indent=2)
open(R+'/Review/Road5m/installed_shader.hlsl','w').write(code)
unreal.log('VILLAGE_ROAD_5M_OK saved=True')
