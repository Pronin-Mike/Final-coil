"""Current native meadow asset entry point; Stage 2 is retained under Review.

Stage 2.1 extends existing assets, MPC, PCG and output. Run inside UE Editor.
"""
from pathlib import Path
import runpy,unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
runpy.run_path(str(ROOT/'Scripts/install_meadow_stage21.py'),run_name='__main__')
