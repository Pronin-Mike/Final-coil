"""Author-owned world-space control maps; no third-party raster assets. Units cm."""
import os,json,math,struct,zlib,sys,time
sys.path.insert(0,os.path.dirname(__file__))
import terrain_profile as T
ROOT=T.ROOT;D=ROOT+'/SourceArt/GroundMaterial';os.makedirs(D,exist_ok=True)
W,H=1024,2048
def smooth(a,b,t):
 t=max(0,min(1,(t-a)/(b-a)));return t*t*(3-2*t)
def png(path,data):
 def ch(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',zlib.crc32(k+v)&0xffffffff)
 raw=b''.join(b'\0'+data[y*W*4:(y+1)*W*4] for y in range(H))
 open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(raw,6))+ch(b'IEND',b''))
routes=json.load(open(ROOT+'/SourceArt/Terrain/manifest.json'))['routes']
zones=[(*a['p'][:2],a['s'][0]*50,a['s'][1]*50) for a in T.INV if a['label'].startswith(('Forest_Mass_','OldBor_Mass_'))]
bins={};B=10000
for r in routes:
 if r['group']=='Rail':continue
 p,q=r['p'],r['q'];pad=r['width']/2+900
 for i in range(math.floor((min(p[0],q[0])-pad)/B),math.floor((max(p[0],q[0])+pad)/B)+1):
  for j in range(math.floor((min(p[1],q[1])-pad)/B),math.floor((max(p[1],q[1])+pad)/B)+1):bins.setdefault((i,j),[]).append(r)
biome=bytearray(W*H*4);use=bytearray(W*H*4)
def byte(v):return round(max(0,min(1,v))*255)
t0=time.time()
for j in range(H):
 y=T.YMIN+(j+.5)/H*(T.YMAX-T.YMIN)
 for i in range(W):
  x=T.XMIN+(i+.5)/W*(T.XMAX-T.XMIN);z=T.height(x,y)
  broad=(T.height(x+1800,y)+T.height(x-1800,y)+T.height(x,y+1800)+T.height(x,y-1800))*.25-z
  fine=(T.height(x+300,y)+T.height(x-300,y)+T.height(x,y+300)+T.height(x,y-300))*.25-z
  cavity=max(smooth(10,130,broad),smooth(3,22,fine)*.85)
  convex=smooth(20,160,-broad)
  forest=0
  for cx,cy,rx,ry in zones:
   d=(math.hypot((x-cx)/rx,(y-cy)/ry)-1)*min(rx,ry)
   forest=max(forest,1-smooth(-1200,2200,d))
  road=path=rut=0
  for r in bins.get((math.floor(x/B),math.floor(y/B)),[]):
   a,b=r['p'],r['q'];dx=b[0]-a[0];dy=b[1]-a[1];ln=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/ln))
   d=math.hypot(x-a[0]-t*dx,y-a[1]-t*dy);h=r['width']*.5
   weight=1-smooth(h-40,h+180,d)
   if r['group']=='Road':
    road=max(road,weight);rut=max(rut,(1-smooth(32,95,abs(d-105)))*weight)
   else:path=max(path,weight)
  yard=0
  for name,cx,cy,hx,hy,c,s,h in T.PADS:
   dx=x-cx;dy=y-cy;lx=abs(dx*c+dy*s);ly=abs(-dx*s+dy*c)
   yard=max(yard,1-smooth(-150,250,max(lx-hx,ly-hy)))
  lake=1-smooth(8000,18000,T.lake_distance(x,y))
  k=(j*W+i)*4
  biome[k:k+4]=bytes(map(byte,[forest,cavity,lake,convex]))
  use[k:k+4]=bytes(map(byte,[road,path,yard,rut]))
 if j%256==0:print('ROW',j,'seconds',round(time.time()-t0),flush=True)
png(D+'/T_Berezovka_Biome.png',biome);png(D+'/T_Berezovka_Use.png',use)
json.dump({'size':[W,H],'bounds_cm':[T.XMIN,T.YMIN,T.XMAX,T.YMAX],'biome_RGBA':['forest','concavity_wetness','lake_proximity','convex_dryness'],'use_RGBA':['road','path','yard','wheel_tracks'],'source':'Authored from existing terrain geometry, approved road strips and yard extents. Linear, clamp, mipmapped.','generation_seconds':round(time.time()-t0)},open(D+'/mask_manifest.json','w'),indent=2)
print('MASKS_OK',flush=True)
