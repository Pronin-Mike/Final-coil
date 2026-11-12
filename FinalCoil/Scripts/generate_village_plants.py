"""Authored curved-blade and branching leafy shrub meshes, and bounded planting plan."""
import json,math,random,os,sys
sys.path.insert(0,os.path.dirname(__file__));import terrain_profile as T
R=T.ROOT;D=R+'/SourceArt/VillagePlants';os.makedirs(D,exist_ok=True)
class Mesh:
 def __init__(self):self.v=[];self.uv=[];self.f=[];self.mat=[]
 def vert(self,p,uv):self.v.append(p);self.uv.append(uv);return len(self.v)
 def face(self,ids,mat):self.f.append(ids);self.mat.append(mat)
 def write(self,name):
  with open(D+'/'+name+'.obj','w') as f:
   f.write('o '+name+'\n')
   for x,y,z in self.v:f.write('v %.5f %.5f %.5f\n'%(x,y,z))
   for u,v in self.uv:f.write('vt %.5f %.5f\n'%(u,v))
   last=None
   for tri,mat in zip(self.f,self.mat):
    if mat!=last:f.write('usemtl '+mat+'\n');last=mat
    f.write('f '+' '.join('%d/%d'%(i,i) for i in tri)+'\n')
  return {'name':name,'vertices':len(self.v),'triangles':len(self.f)}
def grass(seed,tall=False):
 rng=random.Random(seed);m=Mesh()
 for clump in range(4):
  az=rng.random()*math.tau;rr=rng.uniform(0,29);px=math.cos(az)*rr;py=math.sin(az)*rr
  for k in range(3):
   a=az+k*math.pi/3+rng.uniform(-.2,.2);dx,dy=math.cos(a),math.sin(a)
   h=rng.uniform(38,62) if tall else rng.uniform(24,39);width=rng.uniform(35,51);bend=rng.uniform(4,12);rings=[]
   for j in range(3):
    t=j/2;cx=px-dy*bend*t*t;cy=py+dx*bend*t*t
    rings.append([m.vert((cx-dx*width/2,cy-dy*width/2,h*t),(0,t)),m.vert((cx+dx*width/2,cy+dy*width/2,h*t),(1,t))])
   for j in range(2):
    a,b=rings[j],rings[j+1];m.face((a[0],b[0],a[1]),'Grass');m.face((a[1],b[0],b[1]),'Grass')
 return m
def branch(m,a,b,r):
 dx,dy,dz=[b[i]-a[i] for i in range(3)];ll=math.sqrt(dx*dx+dy*dy+dz*dz);v=(dx/ll,dy/ll,dz/ll)
 q=(-v[1],v[0],0);l=math.hypot(q[0],q[1]);q=(1,0,0) if l<.001 else (q[0]/l,q[1]/l,0)
 w=(v[1]*q[2]-v[2]*q[1],v[2]*q[0]-v[0]*q[2],v[0]*q[1]-v[1]*q[0]);rings=[]
 for p,rad,t in [(a,r,0),(b,r*.45,1)]:
  rings.append([m.vert(tuple(p[j]+rad*(q[j]*math.cos(i*math.tau/5)+w[j]*math.sin(i*math.tau/5)) for j in range(3)),(i/5,t)) for i in range(5)])
 for i in range(5):j=(i+1)%5;m.face((rings[0][i],rings[1][i],rings[0][j]),'Bark');m.face((rings[0][j],rings[1][i],rings[1][j]),'Bark')
def leaf(m,p,angle,tilt,length,width):
 d=(math.cos(angle)*math.cos(tilt),math.sin(angle)*math.cos(tilt),math.sin(tilt));w=(-math.sin(angle),math.cos(angle),0)
 # Six-point leaf with a raised central vein, tapered outline, no opaque quad.
 root=m.vert(p,(.5,0));tip=m.vert(tuple(p[j]+d[j]*length for j in range(3)),(.5,1));center=m.vert(tuple(p[j]+d[j]*length*.52+(0,0,width*.15)[j] for j in range(3)),(.5,.52))
 sides=[]
 for sign in [-1,1]:sides.append(m.vert(tuple(p[j]+d[j]*length*.45+w[j]*width*sign for j in range(3)),(0 if sign<0 else 1,.45)))
 for s in sides:m.face((root,s,center),'Leaf');m.face((center,s,tip),'Leaf')
def shrub(seed,willow=False):
 rng=random.Random(seed);m=Mesh()
 for stem in range(12):
  az=rng.random()*math.tau;h=rng.uniform(90,160);spread=rng.uniform(28,65);a=(rng.uniform(-12,12),rng.uniform(-12,12),0);b=(math.cos(az)*spread,math.sin(az)*spread,h)
  branch(m,a,b,rng.uniform(.8,1.4))
  for k in range(7):
   t=.20+k*.105;p=tuple(a[j]+(b[j]-a[j])*t for j in range(3));an=az+k*2.4+rng.uniform(-.5,.5);ll=rng.uniform(21,43)
   q=(p[0]+math.cos(an)*ll,p[1]+math.sin(an)*ll,p[2]+rng.uniform(8,25));branch(m,p,q,.42)
   for n in range(11):
    u=.1+n*.08;v=tuple(p[j]+(q[j]-p[j])*u for j in range(3));side=1 if n%2 else -1
    length=rng.uniform(5.5,10) if willow else rng.uniform(4.5,8);width=length*(.14 if willow else .32)
    leaf(m,v,an+side*rng.uniform(.6,1.2),rng.uniform(-.4,.55),length,width)
 return m
meshes=[]
for n in range(4):meshes.append(grass(710+n,n>=2).write('SM_VillageGrass_%02d'%n))
for n in range(3):meshes.append(shrub(910+n,n==2).write('SM_VillageShrub_%02d'%n))
routes=json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes']
zones=[(*a['p'][:2],a['s'][0]*50,a['s'][1]*50) for a in T.INV if a['label'].startswith(('Forest_Mass_','OldBor_Mass_'))]
def road_clearance(x,y):
 best=1e9;group=''
 for r in routes:
  a,b=r['p'],r['q'];dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
  d=math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)-r['width']/2
  if d<best:best=d;group=r['group']
 return best,group
def allowed(x,y,shrub=False):
 # Exact existing village footprint; no lake or forest planting.
 if ((x-8000)/21000)**2+((y+5666.6667)/50500)**2>.94:return False
 margin=430 if shrub else 180
 for name,cx,cy,hx,hy,c,s,z in T.PADS:
  dx=x-cx;dy=y-cy
  if abs(dx*c+dy*s)<hx+margin and abs(-dx*s+dy*c)<hy+margin:return False
 for cx,cy,rx,ry in zones:
  if ((x-cx)/(rx+600))**2+((y-cy)/(ry+600))**2<1:return False
 clear,group=road_clearance(x,y)
 if clear<(330 if shrub else 85):return False
 if T.height(x,y)<-100:return False
 return True
rng=random.Random(20461111);plants=[[] for _ in meshes];candidates=0
# Jittered cells with broad, irregular density fields; no rows or uniform lawn.
for x0 in range(-13000,29000,125):
 for y0 in range(-56100,44900,125):
  x=x0+rng.random()*125;y=y0+rng.random()*125;candidates+=1
  if not allowed(x,y):continue
  d,_=road_clearance(x,y)
  patch=(math.sin(x/830+y/1300)+math.sin(y/570-x/1700)+math.sin(x/3900+y/2100))*.165+.5
  probability=.40+.45*patch
  if rng.random()>probability:continue
  tall=d>220 and patch>.55 and rng.random()<.4
  kind=rng.randrange(2,4) if tall else rng.randrange(0,2)
  # Terrain exact triangular height; bury roots by 1 cm.
  plants[kind].append([round(x,2),round(y,2),round(T.height(x,y)-1,2),round(rng.random()*360,2),round(rng.uniform(.72,1.28),3)])
# Sparse natural shrub groups in unused strips, well outside plots and sight triangles.
centers=[]
for _ in range(1600):
 x=rng.uniform(-11000,27000);y=rng.uniform(-48000,40000)
 if not allowed(x,y,True):continue
 d,_=road_clearance(x,y)
 if not 500<d<2800:continue
 if any(math.hypot(x-a,y-b)<3200 for a,b in centers):continue
 centers.append((x,y))
 if len(centers)>=15:break
for cx,cy in centers:
 for k in range(rng.randint(2,4)):
  x=cx+rng.uniform(-280,280);y=cy+rng.uniform(-280,280)
  if not allowed(x,y,True):continue
  if any(math.hypot(x-p[0],y-p[1])<170 for group in plants[4:] for p in group):continue
  plants[4+rng.randrange(3)].append([round(x,2),round(y,2),round(T.height(x,y)-2,2),round(rng.random()*360,2),round(rng.uniform(.70,1.1),3)])
json.dump({'meshes':meshes,'plants':plants,'seed':20461111,'constraints':'Existing village ellipse only; all plots +1.8m grass/+4.3m shrub exclusion; forest +6m; road/path edges +0.85m grass/+3.3m shrub. No existing actor edits.','counts':[len(p) for p in plants]},open(D+'/planting.json','w'),indent=1)
print('PLANTS_READY', [len(p) for p in plants],meshes)
