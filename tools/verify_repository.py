"""Fast repository checks; does not pretend to build or run Unreal."""
from pathlib import Path
import ast,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
project=json.loads((ROOT/'FinalCoil/FinalCoil.uproject').read_text(encoding='utf-8-sig'))
assert project['EngineAssociation']=='5.8'
assert (ROOT/'FinalCoil/Content/FinalCoil/Maps/L_Berezovka_Terrain.umap').is_file()
plan=json.loads((ROOT/'FinalCoil/SourceArt/CompactVillage/plan.json').read_text())
assert plan['counts']=={'occupied':14,'vacant':11,'hero':1}
assert len(plan['plots'])==26
assert abs(plan['hero_distance_m']-140)<1e-6
for plot in plan['plots']:assert abs(4*plot['hx']*plot['hy']/10000-1000)<1e-6
scripts=list((ROOT/'FinalCoil/Scripts').glob('*.py'))+list((ROOT/'tools').glob('*.py'))
for path in scripts:ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
for path in tracked:
 assert not any(part in path.split('/') for part in ['Saved','Intermediate','DerivedDataCache','.publishing','.git-backups']),path
 if path.endswith(('.uasset','.umap')):
  attr=subprocess.check_output(['git','check-attr','filter','--',path],cwd=ROOT).decode()
  assert attr.rstrip().endswith(': lfs'),path
print(f'OK: UE project, 26 plots, 140m anchor, {len(scripts)} Python files, Git LFS attributes. Unreal runtime is checked separately in the editor.')
