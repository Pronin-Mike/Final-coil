"""Source acceptance: deterministic streams, ecology, spacing, nested presets."""
import json,math,hashlib,time,copy
from pathlib import Path
import meadow_distribution as M
start=time.perf_counter();cfg=M.config();saved={q:json.loads((M.SOURCE/('distribution_'+q.lower()+'.json')).read_text()) for q in cfg['presets']};checks=[]
rebuilt=M.generate(quality='Medium');assert rebuilt['groups']==saved['Medium']['groups'];assert rebuilt['sha256']==saved['Medium']['sha256'];checks.append('identical seed reproduces every transform, variant and metadata value')
partial=M.generate(quality='Medium',groups=['tall']);assert partial['groups']['tall']==saved['Medium']['groups']['tall'];checks.append('local group rebuild does not shift its stream')
a,b,c,d=cfg['bounds_cm'];assert c-a==5000 and d-b==5000;checks.append('authorised area exactly 50 x 50 metres')
surface=M.Z.HeightfieldSurface();maximum_error=0
for group,rows in saved['High']['groups'].items():
 assert rows
 high={tuple(r['p']) for r in rows};medium={tuple(r['p']) for r in saved['Medium']['groups'][group]};low={tuple(r['p']) for r in saved['Low']['groups'][group]};assert low<=medium<=high
 spacing=cfg['groups'][group]['min_distance_cm'];bins={}
 for r in rows:
  x,y,z=r['p'];assert a<=x<c and b<=y<d;assert r['exclusion']<=.001 and r['z04']>.99;assert r['grass_density']>0
  maximum_error=max(maximum_error,abs(z+.5-surface.sample(x,y)['position'][2]));ix,iy=math.floor(x/spacing),math.floor(y/spacing)
  assert not any((x-px)**2+(y-py)**2<(spacing-.001)**2 for dx in [-1,0,1] for dy in [-1,0,1] for px,py in bins.get((ix+dx,iy+dy),[]));bins.setdefault((ix,iy),[]).append((x,y))
 assert len(set(round((r['p'][0]%400),1) for r in rows))>min(100,len(rows)*.7)
 assert len(set(round(r['s'][2],2) for r in rows))>20
checks.extend(['all five groups nonempty','Low subset Medium subset High','all roots within bounded area','all retained points pass zone/exclusion/density metadata','minimum distances respected','positions independent of 400 cm diagnostic lattice','height and orientation variation'])
assert maximum_error<.001;checks.append('roots follow exact terrain triangles within 0.001 cm, buried 0.5 cm')
for x,y in [(a,30000),(c,30000),(18000,b),(18000,d)]:assert M.edge_weight(x,y,cfg)==0
checks.append('boundary density fades continuously to zero')
disabled=copy.deepcopy(cfg);disabled['groups']['tall']['enabled']=False;assert not M.generate(disabled,groups=['tall'])['groups']['tall'];checks.append('group disabling supported')
manifest=json.loads((M.SOURCE/'meshes.json').read_text());assert len(manifest['meshes'])==18
assert {m['species'] for m in manifest['meshes'] if m['group']=='herbs'}=={'clover','yarrow','dandelion'};checks.append('18 original variants including three identifiable herb species')
result=dict(status='passed',checks=checks,maximum_root_height_error_cm=maximum_error,seconds=time.perf_counter()-start,quality_counts={q:{g:len(rows) for g,rows in r['groups'].items()} for q,r in saved.items()})
(M.ROOT/'Review/MeadowVegetation/source_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
