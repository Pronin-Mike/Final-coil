"""Authoritative, editor-independent zone evaluator. Coordinates and distances: cm.

Static mesh adapter reuses the existing triangulated heightfield, not a Landscape.
LandscapeAdapter accepts an explicit sampler/export implementing the same contract.
"""
from pathlib import Path
import json, math, bisect, hashlib, struct, zlib, time, argparse
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'SourceArt/EnvironmentZones'
def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def segment_distance(x,y,p,q):
 dx,dy=q[0]-p[0],q[1]-p[1];t=max(0.,min(1.,((x-p[0])*dx+(y-p[1])*dy)/max(1,dx*dx+dy*dy)))
 return math.hypot(x-p[0]-t*dx,y-p[1]-t*dy)
def noise(x,y,seed):
 # Continuous, bounded macro modulation; never changes road/building exclusions.
 return .5+.25*math.sin(x/1721+seed)*math.cos(y/2387-seed)+.25*math.sin((x+y)/791+seed*.7)
class PNG:
 """Lossless RGBA reader, bilinear linear-data sampling; row zero is world minimum Y."""
 def __init__(self,path):
  raw=Path(path).read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';pos=8;payload=b''
  while pos<len(raw):
   n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8];v=raw[pos+8:pos+8+n];pos+=n+12
   if kind==b'IHDR':self.w,self.h,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',v);assert (depth,color,interlace)==(8,6,0)
   elif kind==b'IDAT':payload+=v
  src=zlib.decompress(payload);stride=self.w*4;out=bytearray();prev=bytearray(stride)
  for y in range(self.h):
   f=src[y*(stride+1)];row=bytearray(src[y*(stride+1)+1:(y+1)*(stride+1)])
   for i in range(stride):
    a=row[i-4] if i>=4 else 0;b=prev[i];c=prev[i-4] if i>=4 else 0
    if f==1:row[i]=(row[i]+a)&255
    elif f==2:row[i]=(row[i]+b)&255
    elif f==3:row[i]=(row[i]+(a+b)//2)&255
    elif f==4:
     p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c);row[i]=(row[i]+(a if pa<=pb and pa<=pc else b if pb<=pc else c))&255
    else:assert f==0
   out.extend(row);prev=row
  self.data=out
 def sample(self,u,v):
  x=max(0.,min(self.w-1.,u*self.w-.5));y=max(0.,min(self.h-1.,v*self.h-.5));i,j=int(x),int(y);xx,yy=min(i+1,self.w-1),min(j+1,self.h-1);a,b=x-i,y-j
  return [((1-a)*(1-b)*self.data[(j*self.w+i)*4+k]+a*(1-b)*self.data[(j*self.w+xx)*4+k]+(1-a)*b*self.data[(yy*self.w+i)*4+k]+a*b*self.data[(yy*self.w+xx)*4+k])/255 for k in range(4)]
class HeightfieldSurface:
 def __init__(self,root=ROOT):
  import terrain_profile as T
  self.xs,self.ys=T.XS,T.YS;self.grid=load(root/'SourceArt/Terrain/heightfield.json');self.source='StaticMeshHeightfield'
 def sample(self,x,y):
  i=max(0,min(len(self.xs)-2,bisect.bisect_right(self.xs,x)-1));j=max(0,min(len(self.ys)-2,bisect.bisect_right(self.ys,y)-1));dx=self.xs[i+1]-self.xs[i];dy=self.ys[j+1]-self.ys[j];u=max(0,min(1,(x-self.xs[i])/dx));v=max(0,min(1,(y-self.ys[j])/dy));a,b,c,d=self.grid[i][j],self.grid[i+1][j],self.grid[i][j+1],self.grid[i+1][j+1]
  if u+v<=1:z=a+(b-a)*u+(c-a)*v;gx,gy=(b-a)/dx,(c-a)/dy
  else:z=d+(c-d)*(1-u)+(b-d)*(1-v);gx,gy=(d-c)/dx,(d-b)/dy
  length=math.sqrt(gx*gx+gy*gy+1);return dict(position=[x,y,z],normal=[-gx/length,-gy/length,1/length],slope=math.degrees(math.atan(math.hypot(gx,gy))))
class LandscapeAdapter:
 """Future integration seam. Supply a real Landscape sampler, never mesh layer sampling."""
 def __init__(self,sampler):self.sampler=sampler;self.source='LandscapeExternalSampler'
 def sample(self,x,y):
  result=self.sampler(x,y);assert all(k in result for k in ['position','normal','slope']);return result
class Zones:
 def __init__(self,config=None,surface=None):
  self.config=config or load(SOURCE/'zones.json');self.surface=surface or HeightfieldSurface();self.plan=load(ROOT/'SourceArt/CompactVillage/plan.json');self.manifest=load(ROOT/'SourceArt/GroundMaterial/mask_manifest.json');self.bounds=self.manifest['bounds_cm'];self.biome=PNG(ROOT/'SourceArt/GroundMaterial/T_Berezovka_Biome.png');self.use=PNG(ROOT/'SourceArt/GroundMaterial/T_Berezovka_Use.png');self.inventory=load(ROOT/'Scripts/terrain_inventory.json')['actors'];self.footprints=load(SOURCE/'exclusions.json');self.overrides=load(SOURCE/'overrides.json');self.byid={z['id']:z for z in self.config['zones']}
  assert [self.biome.w,self.biome.h]==self.manifest['size']
  self.plots=self.plan['plots'];self.routes=[]
  for r in self.plan['roads']:self.routes.append(dict(p=r['p'],q=r['q'],width=r['width'],kind='road'))
  for r in self.plan['walks']:self.routes.append(dict(p=r['p'],q=r['q'],width=r['width'],kind='road' if 'Drive' in r['name'] else 'path'))
  self.regional=load(ROOT/'SourceArt/Terrain/manifest.json')['routes'];self.forests=[a for a in self.inventory if a['label'].startswith(('Forest_Mass_','OldBor_Mass_'))];self.lakes=[a for a in self.inventory if a['label'].startswith('Lake_Mass_')]
  self.compact_bounds=[min(p['center'][0]-p['hx']-p['hy'] for p in self.plots)-2500,min(p['center'][1]-p['hx']-p['hy'] for p in self.plots)-2500,max(p['center'][0]+p['hx']+p['hy'] for p in self.plots)+2500,max(p['center'][1]+p['hx']+p['hy'] for p in self.plots)+2500]
 def mask_uv(self,x,y):
  a,b,c,d=self.bounds;return (x-a)/(c-a),(y-b)/(d-b)
 def ellipse_distance(self,x,y,a):
  cx,cy=a['p'][:2];rx,ry=a['s'][0]*50,a['s'][1]*50;u,v=(x-cx)/rx,(y-cy)/ry;r=math.hypot(u,v);return (r-1)/max(1/max(rx,ry),math.hypot(u/rx,v/ry)/max(r,.00001))
 def evaluate(self,x,y):
  cfg=self.config;v=self.surface.sample(x,y);z=v['position'][2];slope=v['slope'];u,vv=self.mask_uv(x,y);bio=v.get('biome_mask',self.biome.sample(u,vv));use=v.get('use_mask',self.use.sample(u,vv));road=path=1e9;road_mask=path_mask=0
  for r in self.routes:
   d=segment_distance(x,y,r['p'],r['q'])-r['width']/2
   if r['kind']=='road':road=min(road,d)
   else:path=min(path,d)
  a,b,c,d=self.compact_bounds;compact=a<=x<=c and b<=y<=d
  if not compact:
   for r in self.regional:
    if r['group']=='Rail':continue
    dist=segment_distance(x,y,r['p'],r['q'])-r['width']/2
    if r['group']=='Road':road=min(road,dist)
    else:path=min(path,dist)
  road_soft=self.byid['Z01']['transition_cm']/150
  road_mask=1-smooth(-25*road_soft,55*road_soft,road);path_mask=1-smooth(-10,40,path)
  if not compact:road_mask=max(road_mask,use[0]);path_mask=max(path_mask,use[1])
  plot_id='';plot_weight=0;abandoned=0;maintained=0
  for p in self.plots:
   dx,dy=x-p['center'][0],y-p['center'][1];xx=abs(p['c']*dx+p['s']*dy)-p['hx'];yy=abs(-p['s']*dx+p['c']*dy)-p['hy'];dist=max(xx,yy);zone_id='Z05' if p['id'].startswith('E') else 'Z03';weight=1-smooth(-50,cfg['plot_transition_cm']*self.byid[zone_id]['transition_cm']/150,dist)
   if weight>plot_weight:plot_id=p['id'];plot_weight=weight
   if p['id'].startswith('E'):abandoned=max(abandoned,weight*cfg['plot_overrides'].get(p['id'],{}).get('abandonment',.9))
   else:maintained=max(maintained,weight*cfg['plot_overrides'].get(p['id'],{}).get('maintenance',.85))
  forest_distance=min([self.ellipse_distance(x,y,a) for a in self.forests]+[1e9]);old_distance=min([self.ellipse_distance(x,y,a) for a in self.forests if a['label'].startswith('OldBor')]+[1e9])
  # Additional existing hero forest mass is derived from its saved authored tree extent.
  for f in cfg.get('additional_forests',[]):
   fd=(math.hypot((x-f['center'][0])/f['radius'][0],(y-f['center'][1])/f['radius'][1])-1)*min(f['radius']);forest_distance=min(forest_distance,fd)
  irregular=(noise(x,y,cfg['seed'])-.5)*cfg['forest_boundary_noise_cm'];forest_distance+=irregular;old_distance+=irregular
  forest_soft=self.byid['Z07']['transition_cm']/1800;old_soft=self.byid['Z08']['transition_cm']/1800
  forest=max(bio[0],1-smooth(-500*forest_soft,500*forest_soft,forest_distance));edge=(1-smooth(0,self.byid['Z06']['transition_cm'],forest_distance))*smooth(-1600,-100,forest_distance);old=1-smooth(-600*old_soft,600*old_soft,old_distance)
  shore_distance=min(self.ellipse_distance(x,y,a) for a in self.lakes);water=shore_distance<0 and z<cfg['water_level_cm']+2;relative=z-cfg['water_level_cm'];wet=bio[1];dry=bio[3]
  shore=(1-smooth(100,cfg['shore_distance_cm']*self.byid['Z10']['transition_cm']/1800,abs(shore_distance)))*(1-smooth(200,700,relative))
  wetland=smooth(cfg['wetland_min_wetness'],.95,wet)*(1-smooth(5,16,slope))*(1-smooth(150,700,relative));wetland=max(wetland,cfg['wetland_hint_strength']*(1-smooth(0,4500,math.hypot(x-cfg['wetland_hint'][0],y-cfg['wetland_hint'][1]))))
  exclusion=1 if water else 0;reasons=['water'] if water else []
  if min(road,path)<cfg['route_clearance_cm']:exclusion=1;reasons.append('road' if road<path else 'footpath')
  for o in self.footprints:
   if abs(x-o['center'][0])<o['extent'][0]+o.get('margin_cm',55) and abs(y-o['center'][1])<o['extent'][1]+o.get('margin_cm',55):exclusion=1;reasons.append(o['label']);break
  # Explicit protected pads are separate from ecological classifications.
  for pad in cfg['protected_pads']:
   if math.hypot(x-pad['center'][0],y-pad['center'][1])<pad['radius_cm']:exclusion=1;maintained=1;reasons.append(pad['id'])
  roadside=(1-smooth(cfg['roadside_width_cm'][0],cfg['roadside_width_cm'][1],road))*(1-road_mask)
  raw={'Z01':road_mask,'Z02':roadside,'Z03':max(maintained,path_mask),'Z04':max(.05,1-max(forest,old,shore,wetland,abandoned))*(.8+.2*noise(x,y,cfg['seed'])),'Z05':abandoned,'Z06':edge,'Z07':forest*(1-old),'Z08':old,'Z09':wetland,'Z10':shore}
  for override in sorted(self.overrides,key=lambda o:o.get('priority',0)):
   dx,dy=x-override['center'][0],y-override['center'][1];dist=max(abs(dx)-override['half_size'][0],abs(dy)-override['half_size'][1]);weight=1-smooth(-1,override.get('transition_cm',100),dist)
   if weight<=0:continue
   if override['mode']=='exclude':exclusion=max(exclusion,weight);reasons.append(override['id'])
   else:
    for k in raw:raw[k]=raw[k]*(1-weight)+(weight if k==override['zone'] else 0)
  # Ordered alpha compositing gives explicit priorities and a normalized soft partition.
  weights={};remaining=1
  for zone in sorted(cfg['zones'],key=lambda zz:(-zz['priority'],zz['id'])):
   k=zone['id'];allowed=zone['enabled'] and zone['height_range_cm'][0]<=z<=zone['height_range_cm'][1] and zone['slope_range_deg'][0]<=slope<=zone['slope_range_deg'][1];w=max(0,min(1,raw[k])) if allowed else 0;weights[k]=remaining*w;remaining*=1-w
  if self.byid['Z04']['enabled']:weights['Z04']+=remaining
  total=sum(weights.values());weights={k:val/total if total else 0 for k,val in weights.items()};winner=max(weights,key=lambda k:(weights[k],self.byid[k]['priority']));density=sum(weights[k]*self.byid[k]['density'] for k in weights)*(1-exclusion)
  group_densities={}
  for group,tokens in [('tree_density',['trees','conifers','deciduous']),('shrub_density',['shrubs','willow','understory']),('grass_density',['grass','herbs','sedges','moss','weeds','reeds'])]:
   group_densities[group]=sum(weights[k]*self.byid[k]['density'] for k in weights if any(any(t in g for t in tokens) for g in self.byid[k]['allowed_groups']))*(1-exclusion)
  tracks=use[3] if not compact else max([1-smooth(32,95,abs(segment_distance(x,y,r['p'],r['q'])-105)) for r in self.routes if r['kind']=='road']+[0])*road_mask
  return dict(**v,**group_densities,weights=weights,zone=winner,density=density,wetness=wet,dryness=dry,forest=forest,road=road_mask,path=path_mask,wheel_tracks=tracks,raw_biome=bio,raw_use=use,plot_id=plot_id,plot_weight=plot_weight,water=water,exclusion=exclusion,reasons=reasons,seed=int(hashlib.sha256(f'{cfg["seed"]}:{self.byid[winner]["seed"]}:{x:.3f}:{y:.3f}'.encode()).hexdigest()[:7],16))
 def generate(self,bounds,step):
  # World anchored lattice: a local rebuild cannot shift neighboring cell samples.
  a,b,c,d=bounds;points=[]
  for ix in range(math.ceil(a/step),math.ceil(c/step)):
   for iy in range(math.ceil(b/step),math.ceil(d/step)):
    x,y=(ix+.5)*step,(iy+.5)*step
    if a<=x<c and b<=y<d:points.append(self.evaluate(x,y))
  return points
def generate(cell_names=None):
 zones=Zones();out=SOURCE/'cells';out.mkdir(parents=True,exist_ok=True);summary={};start=time.perf_counter()
 for cell in zones.config['test_cells']:
  if cell_names and cell['id'] not in cell_names:continue
  points=zones.generate(cell['bounds_cm'],cell['step_cm']);payload=dict(id=cell['id'],bounds_cm=cell['bounds_cm'],step_cm=cell['step_cm'],points=points);raw=json.dumps(payload,separators=(',',':'),sort_keys=True);path=out/(cell['id']+'.json');changed=not path.exists() or path.read_text()!=raw
  if changed:path.write_text(raw)
  summary[cell['id']]=dict(changed=changed,sha256=hashlib.sha256(raw.encode()).hexdigest(),points=len(points),counts={k:sum(p['zone']==k for p in points) for k in zones.byid},excluded=sum(p['exclusion']>.99 for p in points))
 return dict(seconds=time.perf_counter()-start,cells=summary)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--cell',action='append');args=parser.parse_args();print(json.dumps(generate(args.cell),indent=2))
