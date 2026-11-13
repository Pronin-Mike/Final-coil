"""Dense stochastic meadow; independent of the diagnostic lattice. Units: cm."""
from pathlib import Path
import math, random, json, time, hashlib, argparse
import environment_zones as Z
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'SourceArt/MeadowVegetation'
def config():return json.loads((SOURCE/'config.json').read_text(encoding='utf-8-sig'))
def hash01(x,y,seed):
    v=(x*374761393+y*668265263+seed*1442695041)&0xffffffff
    v=((v^(v>>13))*1274126177)&0xffffffff
    return (v^(v>>16))/4294967295
def noise(x,y,scale,seed):
    x/=scale;y/=scale;i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
    u=u*u*(3-2*u);v=v*v*(3-2*v)
    return (1-v)*((1-u)*hash01(i,j,seed)+u*hash01(i+1,j,seed))+v*((1-u)*hash01(i,j+1,seed)+u*hash01(i+1,j+1,seed))
def edge_weight(x,y,cfg):
    a,b,c,d=cfg['bounds_cm'];dist=min(x-a,c-x,y-b,d-y)
    return Z.smooth(0,cfg['edge_fade_cm']*(.75+.5*noise(x,y,310,cfg['seed']+9)),dist)
def generate(cfg=None,quality=None,groups=None):
    started=time.perf_counter();cfg=cfg or config();quality=quality or cfg['quality'];preset=cfg['presets'][quality];zones=Z.Zones();a,b,c,d=cfg['bounds_cm'];result={};stats={}
    for gi,(group,spec) in enumerate(cfg['groups'].items()):
        if groups and group not in groups:continue
        rng=random.Random(cfg['seed']+gi*104729);points=[];bins={};spacing=spec['min_distance_cm'];scale=spec['cluster_cm']*cfg['cluster_scale']
        candidates=math.ceil((c-a)*(d-b)/10000*spec['density_m2']*cfg['presets']['High']['density']*cfg['density']) if spec['enabled'] else 0
        for index in range(candidates):
            x=rng.uniform(a,c);y=rng.uniform(b,d);accept=rng.random();rank=rng.random();yaw=rng.uniform(0,360);sx=rng.uniform(.78,1.22);sy=rng.uniform(.82,1.18);sz=rng.uniform(.8,1.16);variant=rng.randrange(spec['variants']);eco_accept=rng.random()
            patch=.68*noise(x,y,scale,cfg['seed']+gi)+.32*noise(x,y,scale*.27,cfg['seed']+gi+31)
            mosaic=noise(x,y,1100*cfg['cluster_scale'],cfg['seed']+77)
            weight={'short':.75-.45*mosaic,'medium':.62+.34*patch,'tall':Z.smooth(.48,.78,mosaic)*patch,'herbs':.18+.75*patch*patch,'dry':Z.smooth(.52,.85,patch)*.7}[group]
            if accept>weight*edge_weight(x,y,cfg):continue
            row=zones.evaluate(x,y)
            ecology=row['weights']['Z04']*row['grass_density']*(1-row['exclusion'])*(1-Z.smooth(15,32,row['slope']))
            ecology*=1-.65*row['road'] if group in ['tall','dry'] else 1-.2*row['road']
            ecology*=(.6+.4*row['dryness']) if group=='dry' else (.85+.15*row['wetness'])
            if row['exclusion']>.001 or eco_accept>ecology:continue
            ix,iy=math.floor(x/spacing),math.floor(y/spacing)
            if any((x-px)**2+(y-py)**2<spacing**2 for dx in [-1,0,1] for dy in [-1,0,1] for px,py in bins.get((ix+dx,iy+dy),[])):continue
            bins.setdefault((ix,iy),[]).append((x,y))
            if rank>preset['density']/cfg['presets']['High']['density']:continue
            points.append(dict(p=[round(x,4),round(y,4),round(row['position'][2]-.5,4)],n=row['normal'],yaw=yaw,s=[sx*cfg['width_scale'],sy*cfg['width_scale'],sz*cfg['height_scale']],variant=variant,seed=int(hash01(index,gi,cfg['seed'])*2147483646),exclusion=row['exclusion'],z04=row['weights']['Z04'],grass_density=row['grass_density']))
        result[group]=points;stats[group]=dict(candidates=candidates,instances=len(points))
    raw=json.dumps(result,sort_keys=True,separators=(',',':'))
    return dict(quality=quality,bounds_cm=cfg['bounds_cm'],groups=result,sha256=hashlib.sha256(raw.encode()).hexdigest(),stats=stats,seconds=time.perf_counter()-started)
def write(quality=None):
    data=generate(quality=quality);(SOURCE/('distribution_'+data['quality'].lower()+'.json')).write_text(json.dumps(data,separators=(',',':')));return data
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--quality',choices=['Low','Medium','High']);args=p.parse_args();r=write(args.quality);print(json.dumps({k:v for k,v in r.items() if k!='groups'},indent=2))
