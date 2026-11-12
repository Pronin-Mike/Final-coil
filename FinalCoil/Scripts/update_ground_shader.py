import unreal,json
R='D:/GameDevelop/FinalCoil';D='/Game/FinalCoil/World/GroundMaterial'
L=unreal.MaterialEditingLibrary;m=unreal.load_asset(D+'/M_Berezovka_Ground')
node=next(n for n in L.get_material_expressions(m) if isinstance(n,unreal.MaterialExpressionCustom) and len(n.get_editor_property('inputs'))>5)
code=open(R+'/SourceArt/GroundMaterial/BerezovkaGround.hlsl').read();lines=[]
for r in json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes']:
 if r['group']=='Road':lines.append('d=min(d,segment(p,float2(%.4f,%.4f),float2(%.4f,%.4f)));'%(*r['p'],*r['q']))
node.set_editor_property('code',code.replace('/* ROAD_SEGMENTS */','\n'.join(lines)))
err=L.recompile_material(m);assert not err,str(err)
unreal.EditorAssetLibrary.save_loaded_asset(m)
json.dump({'errors':list(err or []),'road_segments':len(lines),'material':m.get_path_name()},open(R+'/Review/GroundMaterial/final_compile.json','w'),indent=2)
try:unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
except Exception as ex:unreal.log_warning(str(ex))
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(w,'r.MotionBlurQuality 0')
unreal.SystemLibrary.execute_console_command(w,'r.DepthOfFieldQuality 0')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('GROUND_SHADER_UPDATED_OK')
