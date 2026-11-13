"""Central meadow tuning and editor menu, without runtime Python or regeneration."""
from pathlib import Path
import json,runpy,importlib,os,subprocess,time
import unreal
import meadow_distribution as M
ROOT=Path(__file__).resolve().parents[1]
def configure(**changes):
    """Example: configure(density=1.1, height_scale=.95, cluster_scale=1.2).

    Group example: configure(groups={'tall': {'density_m2': 1.2, 'enabled': True}}).
    Rebuild is explicit, allowing several tweaks before paying generation cost.
    """
    cfg=M.config()
    for name,value in changes.items():
        if name=='groups':
            for group,settings in value.items():
                assert group in cfg['groups']
                for k,v in settings.items():assert k in cfg['groups'][group];cfg['groups'][group][k]=v
        else:
            assert name in ['density','height_scale','width_scale','cluster_scale','wind_strength','seed','edge_fade_cm','quality','ground_strength']
            cfg[name]=value
    assert cfg['quality'] in cfg['presets']
    for k in ['density','height_scale','width_scale','cluster_scale','edge_fade_cm']:assert cfg[k]>0
    assert cfg['wind_strength']>=0
    (M.SOURCE/'config.json').write_text(json.dumps(cfg,indent=2));return cfg
def components():
    return [c for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.static_mesh and '/Environment/Meadow/' in c.static_mesh.get_path_name()]
def toggle():
    cs=components();visible=not any(c.is_visible() for c in cs)
    for c in cs:c.set_visibility(visible,True);c.set_hidden_in_game(not visible,True)
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label()=='MEADOW_Output':
            for c in a.get_components_by_class(unreal.DecalComponent):c.set_visibility(visible,True);c.set_hidden_in_game(not visible,True)
def ground(value=None):
    output=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='MEADOW_Output')
    cs=output.get_components_by_class(unreal.DecalComponent)
    if value is None:
        for c in cs:c.set_visibility(not c.is_visible(),True)
        return
    assert 0<=value<=1
    configure(ground_strength=value)
    mi=unreal.load_asset('/Game/FinalCoil/Environment/Meadow/MI_Meadow_GroundDetail')
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,'GroundStrength',value)
    unreal.EditorAssetLibrary.save_loaded_asset(mi,False)

def wind(value=None):
    cfg=M.config();value=(0 if cfg['wind_strength'] else 1) if value is None else value;configure(wind_strength=value)
    collection=unreal.load_asset('/Game/FinalCoil/Environment/Meadow/MPC_MeadowWind');p=collection.get_editor_property('scalar_parameters')[0];p.set_editor_property('default_value',value*cfg['presets'][cfg['quality']]['wind']);collection.set_editor_property('scalar_parameters',[p]);unreal.EditorAssetLibrary.save_loaded_asset(collection,False)
    for name in ['M_Meadow_Leaf','M_Meadow_Integrated']:
        material=unreal.load_asset('/Game/FinalCoil/Environment/Meadow/'+name)
        if material:unreal.MaterialEditingLibrary.recompile_material(material)
def refresh_ground_mask():
    """Keep local surface detail aligned with current zones, seed and clusters."""
    import generate_meadow_ground
    started=time.perf_counter();result=generate_meadow_ground.bake_ecology()
    task=unreal.AssetImportTask();task.filename=str(M.SOURCE/'T_Meadow_Ecology.png');task.destination_path='/Game/FinalCoil/Environment/Meadow/Textures';task.automated=True;task.replace_existing=True;task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex=unreal.load_asset(task.destination_path+'/T_Meadow_Ecology');tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);unreal.EditorAssetLibrary.save_loaded_asset(tex,False)
    result['seconds']=time.perf_counter()-started
    (ROOT/'Review/MeadowVegetation/Stage2_1/ground_mask_checks.json').write_text(json.dumps(result,indent=2))

def rebuild(quality=None):
    assert not unreal.EditorLevelLibrary.get_game_world(),'Stop PIE before rebuilding meadow'
    cfg=M.config();quality=quality or cfg['quality'];configure(quality=quality)
    M.write(quality)
    if cfg.get('art_stage')=='2.1':refresh_ground_mask()
    runpy.run_path(str(ROOT/'Scripts/install_meadow_pcg.py'),init_globals={'QUALITY':quality})
    E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='ENV_PCG_Environment');pcg=a.get_component_by_class(unreal.PCGComponent)
    def save_when_ready(dt):
        if pcg.get_editor_property('generation_in_progress'):return
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();unreal.unregister_slate_post_tick_callback(_save_handle)
    global _save_handle
    _save_handle=unreal.register_slate_post_tick_callback(save_when_ready)
def benchmark():
    assert not unreal.EditorLevelLibrary.get_game_world()
    quality=M.config()['quality'];Q=ROOT/'Review/MeadowVegetation/Stage2_1';Q.mkdir(parents=True,exist_ok=True)
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    output=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='MEADOW_Output')
    (Q/'benchmark_inventory.json').write_text(json.dumps(dict(actor=output.get_name(),instances=sum(c.get_instance_count() for c in components()),components=[dict(name=c.get_name(),mesh=c.static_mesh.get_name(),instances=c.get_instance_count()) for c in components()])))
    python=Path(unreal.Paths.engine_dir()).resolve()/'Binaries/ThirdParty/Python3/Win64/python.exe';env=dict(os.environ,FINALCOIL_BENCH_INVENTORY='benchmark_inventory.json')
    log_path=ROOT/'Saved/MeadowVegetation/menu_benchmark.log';log_path.parent.mkdir(parents=True,exist_ok=True)
    log=open(log_path,'w');process=subprocess.Popen([str(python),str(ROOT/'Scripts/benchmark_meadow_stage21.py'),'--quality',quality],env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(world,'t.MaxFPS 1')
    def finished(dt):
        if process.poll() is None:return
        log.close();unreal.SystemLibrary.execute_console_command(world,'t.MaxFPS 0');unreal.unregister_slate_post_tick_callback(_benchmark_handle);unreal.log('Meadow standalone benchmark exit '+str(process.returncode)+'; see Review/MeadowVegetation')
    global _benchmark_handle
    _benchmark_handle=unreal.register_slate_post_tick_callback(finished)
def register_menu():
    menu=unreal.ToolMenus.get().extend_menu('LevelEditor.MainMenu.Tools.FinalCoilEnvironment')
    entries=[('Rebuild','Rebuild Meadow Vegetation','rebuild()'),('Toggle','Toggle Meadow Vegetation','toggle()'),('Low','Meadow quality: Low',"rebuild('Low')"),('Medium','Meadow quality: Medium',"rebuild('Medium')"),('High','Meadow quality: High',"rebuild('High')"),('Ground','Toggle meadow ground detail','ground()'),('Wind','Toggle meadow wind','wind()'),('Benchmark','Capture Meadow Benchmark','benchmark()')]
    for name,label,command in entries:
        entry=unreal.ToolMenuEntry(name='FinalCoil.Meadow.'+name,type=unreal.MultiBlockType.MENU_ENTRY);entry.set_label(label);entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,'','import meadow_editor; meadow_editor.'+command);menu.add_menu_entry('Meadow',entry)
    unreal.ToolMenus.get().refresh_all_widgets()
