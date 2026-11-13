"""Meaningful source checks: masks, geometry contract, priorities and local determinism."""
from pathlib import Path
import json,sys,math,hashlib,copy,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Scripts'));import environment_zones as Z
start=time.perf_counter();zones=Z.Zones();checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
check('10 unique zone IDs',set(zones.byid)=={f'Z{i:02}' for i in range(1,11)})
a,b,c,d=zones.bounds;check('manifest axes and scale',zones.mask_uv(a,b)==(0,0) and zones.mask_uv(c,d)==(1,1));im=zones.biome
for i,j in [(0,0),(512,1024),(1023,2047)]:
 uv=((i+.5)/im.w,(j+.5)/im.h);expected=[v/255 for v in im.data[(j*im.w+i)*4:(j*im.w+i)*4+4]];check(f'linear pixel-centre sample {i},{j}',max(abs(x-y) for x,y in zip(im.sample(*uv),expected))<1e-8)
counts={k:0 for k in zones.byid};points=[]
for path in (Z.SOURCE/'cells').glob('*.json'):
 cell=Z.load(path)
 for p in cell['points']:
  counts[p['zone']]+=1;checkname=path.stem
  assert abs(sum(p['weights'].values())-1)<1e-7
  assert abs(sum(n*n for n in p['normal'])-1)<1e-7
  assert p['density']==0 if p['exclusion']==1 else p['density']>=0
  if p['water']:assert p['exclusion']==1 and p['tree_density']==0 and p['grass_density']==0
 points.extend(cell['points'])
check('all 10 zones present in sampled world',all(counts.values()));checks.extend(['normalized smooth weights','unit surface normals','hard exclusions suppress all plant groups','no terrestrial candidates below actual water level'])
o=zones.footprints[0];v=zones.evaluate(*o['center'][:2]);check('physical footprint blocks generation',v['exclusion']==1)
r=zones.routes[0];v=zones.evaluate(*r['p']);check('current road centre protected',v['road']>.9 and v['exclusion']==1 and v['tree_density']==0)
p=next(p for p in zones.plots if p['id']=='E02');check('E02 keeps vacant identifier',zones.evaluate(*p['center'])['plot_id']=='E02')
cfg=copy.deepcopy(zones.config);next(z for z in cfg['zones'] if z['id']=='Z08')['enabled']=False;oldcfg=zones.config;zones.config=cfg;zones.byid={z['id']:z for z in cfg['zones']};check('per-biome disable',zones.evaluate(50000,-56000)['weights']['Z08']==0);zones.config=oldcfg;zones.byid={z['id']:z for z in oldcfg['zones']}
prior=zones.overrides;zones.overrides=[dict(id='test',mode='exclude',center=[18000,30000],half_size=[200,200],transition_cm=100)];check('manual complete exclusion',zones.evaluate(18000,30000)['exclusion']==1);zones.overrides=[dict(id='test',mode='zone',zone='Z05',center=[18000,30000],half_size=[200,200],transition_cm=100)];check('manual zone override',zones.evaluate(18000,30000)['zone']=='Z05');zones.overrides=prior
landscape=Z.LandscapeAdapter(lambda x,y:dict(position=[x,y,20],normal=[0,0,1],slope=0));check('future adapter same surface contract',landscape.sample(1,2)['position']==[1,2,20])
cell=next(c for c in zones.config['test_cells'] if c['id']=='stop');first=zones.generate(cell['bounds_cm'],cell['step_cm']);second=zones.generate(cell['bounds_cm'],cell['step_cm']);check('identical local point streams and seeds',first==second)
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Z.SOURCE/'cells').glob('*.json')};result=Z.generate(['stop']);after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Z.SOURCE/'cells').glob('*.json')};check('local rebuild leaves other cells byte-identical',before==after and list(result['cells'])==['stop'] and not result['cells']['stop']['changed'])
report=dict(status='passed',checks=checks,counts=counts,points=len(points),local_regeneration_seconds=result['seconds'],seconds=time.perf_counter()-start)
(ROOT/'Review/EnvironmentZones/source_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
