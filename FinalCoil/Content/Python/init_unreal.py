"""Register development tools without changing the gameplay world."""
from pathlib import Path
import sys
scripts=Path(__file__).resolve().parents[2]/'Scripts'
if str(scripts) not in sys.path:sys.path.insert(0,str(scripts))
import unreal
if '-run=' not in unreal.SystemLibrary.get_command_line().lower() and '-game' not in unreal.SystemLibrary.get_command_line().lower():
 try:
  import environment_editor
  environment_editor.register_menu()
  import meadow_editor
  meadow_editor.register_menu()
 except Exception as error:unreal.log_warning('Environment editor menu unavailable: '+str(error))
