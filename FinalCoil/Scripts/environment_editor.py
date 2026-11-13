"""Editor menu actions. All writes use Unreal's asset/level APIs."""
from pathlib import Path
import sys,runpy,json
import unreal
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Scripts'))
def show_debug(mode='Zones',cell=None):
 assert mode in ['Zones','Exclusions','Slope','Wetness','Points']
 E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 material=unreal.load_asset('/Game/FinalCoil/Environment/PCG/Debug/MI_Debug'+('Zones' if mode=='Points' else mode))
 assert material,'Install environment zone assets first'
 for a in E.get_all_level_actors():
  n=a.get_actor_label()
  if not n.startswith('ENV_Debug_'):continue
  visible=cell is None or n=='ENV_Debug_'+cell
  a.set_is_temporarily_hidden_in_editor(not visible)
  comp=a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent);comp.set_material(0,material);comp.set_visibility(visible,True)
  # Point mode changes only the temporary instance scale, never source points.
  if mode=='Points':
   for i in range(comp.get_instance_count()):
    t=comp.get_instance_transform(i,True);t.scale3d=unreal.Vector(.12,.12,.12);comp.update_instance_transform(i,t,True,i==comp.get_instance_count()-1,True)
  else:
   source=ROOT/'SourceArt/EnvironmentZones/cells'/((n[len('ENV_Debug_'):])+'.json');step=json.loads(source.read_text())['step_cm']
   for i in range(comp.get_instance_count()):
    t=comp.get_instance_transform(i,True);t.scale3d=unreal.Vector(step*.95/100,step*.95/100,.025);comp.update_instance_transform(i,t,True,i==comp.get_instance_count()-1,True)
  a.set_actor_hidden_in_game(True)
def hide_debug():
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if a.get_actor_label().startswith('ENV_Debug_'):
   a.set_is_temporarily_hidden_in_editor(True);a.set_actor_hidden_in_game(True);a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent).set_visibility(False,True)
def regenerate(cell=None):
 import environment_zones
 result=environment_zones.generate([cell] if cell else None)
 runpy.run_path(str(ROOT/'Scripts/install_environment_zones.py'),run_name='__main__')
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if a.get_actor_label()=='ENV_PCG_Environment':
   component=a.get_component_by_class(unreal.PCGComponent);component.generate(True)
 unreal.log('Environment zone rebuild: '+json.dumps(result));return result
def register_menu():
 menus=unreal.ToolMenus.get();parent=menus.extend_menu('LevelEditor.MainMenu.Tools');menu=parent.add_sub_menu('FinalCoil','FinalCoilEnvironment','FinalCoilEnvironment','FINAL COIL — Environment Zones')
 actions=[('Zones','Show zone colours',"show_debug('Zones')"),('Exclusions','Show exclusions',"show_debug('Exclusions')"),('Slope','Show slope',"show_debug('Slope')"),('Wetness','Show wetness',"show_debug('Wetness')"),('Points','Show PCG source points',"show_debug('Points')"),('Hide','Hide debug','hide_debug()'),('Stop','Rebuild stop cell',"regenerate('stop')"),('G01','Rebuild G01 cell',"regenerate('G01')"),('All','Rebuild configured test cells','regenerate()')]
 for name,label,command in actions:
  entry=unreal.ToolMenuEntry(name='FinalCoil.Environment.'+name,type=unreal.MultiBlockType.MENU_ENTRY);entry.set_label(label);entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,'','import environment_editor; environment_editor.'+command);menu.add_menu_entry('Zones',entry)
 menus.refresh_all_widgets()
