import os,json,math,random,sys
sys.path.insert(0,os.path.dirname(__file__));import terrain_profile as T
R=T.ROOT;D=R+'/SourceArt/VillageRoadPass';os.makedirs(D,exist_ok=True)
base=json.load(open(R+'/Review/VillageRoadPass/baseline.json'));B=base['bounds'];xmin,ymin,xmax,ymax=B
routes=json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes']
forests=[(*a['p'][:2],a['s'][0]*50,a['s'][1]*50) for a in T.INV if a['label'].startswith(('Forest_Mass_','OldBor_Mass_'))]
def forest(x,y,margin=0):return any(((x-cx)/(rx+margin))**2+((y-cy)/(ry+margin))**2<1 for cx,cy,rx,ry in forests)
def plot(x,y,margin=0):
 for name,cx,cy,hx,hy,c,s,z in T.PADS:
  if not (name.startswith(('H','E')) or name=='G01'):continue
  dx=x-cx;dy=y-cy
  if abs(dx*c+dy*s)<hx+margin and abs(-dx*s+dy*c)<hy+margin:return True
 return False
def clip(poly,axis,value,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[axis]>=value) if greater else (a[axis]<=value);ib=(b[axis]>=value) if greater else (b[axis]<=value)
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(5)))
 return out
mesh_report={}
for kind in ['Road','Path']:
 vs=[];uv=[];faces=[]
 for line in open(R+'/SourceArt/Terrain/SM_Conform_'+kind+'.obj'):
  v=line.split()
  if not v:continue
  if v[0]=='v':vs.append(tuple(map(float,v[1:4])))
  elif v[0]=='vt':uv.append(tuple(map(float,v[1:3])))
  elif v[0]=='f':faces.append([tuple(int(i)-1 for i in s.split('/')[:2]) for s in v[1:]])
 outv=[];outf=[];kept=0;removed=0
 def emit(poly):
  if len(poly)<3:return
  start=len(outv);outv.extend(poly)
  for i in range(1,len(poly)-1):outf.append((start,start+i,start+i+1))
 for f in faces:
  p=[vs[a]+uv[b] for a,b in f];cx=sum(a[0] for a in p)/3;cy=sum(a[1] for a in p)/3
  # The protected forest and yards retain their existing strips unchanged.
  protected=any(forest(a[0],a[1],200) or plot(a[0],a[1]) for a in p)
  if protected:emit(p);kept+=1;continue
  remaining=p
  for axis,edge,greater in [(0,xmin,True),(0,xmax,False),(1,ymin,True),(1,ymax,False)]:
   if not remaining:break
   emit(clip(remaining,axis,edge,not greater));remaining=clip(remaining,axis,edge,greater)
  if remaining:removed+=1
 with open(D+'/SM_'+kind+'_OutsideVillage.obj','w') as f:
  for x,y,z,u,v in outv:f.write('v %.6f %.6f %.6f\n'%(x,y,z))
  for x,y,z,u,v in outv:f.write('vt %.7f %.7f\n'%(u,v))
  for a,b,c in outf:f.write('f %d/%d %d/%d %d/%d\n'%(a+1,a+1,b+1,b+1,c+1,c+1))
 mesh_report[kind]={'old_triangles':len(faces),'new_triangles':len(outf),'village_triangles_removed':removed,'protected_triangles':kept}
bins={};bs=5000
for r in routes:
 a,b=r['p'],r['q'];pad=r['width']/2+2500
 for i in range(math.floor((min(a[0],b[0])-pad)/bs),math.floor((max(a[0],b[0])+pad)/bs)+1):
  for j in range(math.floor((min(a[1],b[1])-pad)/bs),math.floor((max(a[1],b[1])+pad)/bs)+1):bins.setdefault((i,j),[]).append(r)
def proximity(x,y):
 best=(1e9,1e9,None)
 for r in bins.get((math.floor(x/bs),math.floor(y/bs)),[]):
  a,b=r['p'],r['q'];dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));d=math.hypot(x-a[0]-dx*t,y-a[1]-dy*t);clear=d-r['width']/2
  if clear<best[0]:best=(clear,d,r)
 return best
def field(x,y):return .5+.18*math.sin(x/950+y/1250)+.16*math.sin(x/2300-y/1700)+.12*math.sin(x/340+y/530)
def land(x,y,margin):return xmin+margin<x<xmax-margin and ymin+margin<y<ymax-margin and not plot(x,y,margin+70) and not forest(x,y,600)
def wetness(x,y):
 z=T.height(x,y);c=(T.height(x+1200,y)+T.height(x-1200,y)+T.height(x,y+1200)+T.height(x,y-1200))*.25-z
 return max(0,min(1,(c+10)/70))
rng=random.Random(12012026);plants=[[],[],[],[]]
for xx in range(math.floor(xmin),math.ceil(xmax),90):
 for yy in range(math.floor(ymin),math.ceil(ymax),90):
  x=xx+rng.random()*90;y=yy+rng.random()*90
  if not land(x,y,140):continue
  clear,d,r=proximity(x,y);f=field(x,y);wet=wetness(x,y);ridge=max(0,min(1,(T.height(x,y)-450)/450))
  center=r and r['label'].startswith('NET_MainRoad') and d<42 and f>.56 and rng.random()<.28
  if clear<(-35+65*math.sin(y/280+x/480)) and not center:continue
  if r and r['group']=='Path' and clear<90:continue
  probability=max(.12,min(.98,.42+f*.5+wet*.23-ridge*.23))
  if clear<180:probability*=.18+.55*max(0,clear+35)/215
  if f<.28:probability*=.12
  if rng.random()>probability and not center:continue
  dry=rng.random()<(.10+ridge*.18)*(1-wet*.65);kind=1 if dry else 0
  xy=rng.uniform(1.15,2.1);h=rng.uniform(.18,.42) if not center else rng.uniform(.12,.22)
  plants[kind].append([round(x,2),round(y,2),round(T.height(x,y)-1.0,2),round(rng.random()*360,2),round(xy,3),round(h,3)])
centers=[]
for _ in range(3500):
 x=rng.uniform(xmin+1200,xmax-1200);y=rng.uniform(ymin+1200,ymax-1200)
 if not land(x,y,650) or proximity(x,y)[0]<400:continue
 wet=wetness(x,y)
 if rng.random()>.3+wet*.6:continue
 if any(math.hypot(x-a,y-b)<2400 for a,b,w in centers):continue
 centers.append((x,y,wet))
 if len(centers)>=62:break
for cx,cy,wet in centers:
 radius=rng.uniform(170,600);count=rng.randint(7,60)
 for _ in range(count):
  a=rng.random()*math.tau;rr=radius*math.sqrt(rng.random());x=cx+math.cos(a)*rr;y=cy+math.sin(a)*rr
  if not land(x,y,180) or proximity(x,y)[0]<220:continue
  kind=3 if rng.random()<(.14+.25*(1-wet)) else 2
  plants[kind].append([round(x,2),round(y,2),round(T.height(x,y)-1,2),round(rng.random()*360,2),round(rng.uniform(.65,1.3),3),round(rng.uniform(.45,1.15),3)])
json.dump({'bounds':B,'mesh_report':mesh_report,'plants':plants,'counts':[len(p) for p in plants],'tall_groups':centers,'seed':12012026},open(D+'/plan.json','w'),indent=1)
print('PREPARED',B,[len(p) for p in plants],mesh_report,flush=True)
