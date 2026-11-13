"""Bake author-owned soil/litter microdetail from procedural ground vocabulary.

This creates material inputs, never review screenshots. No third-party bytes.
World-space material sampling breaks the small tile with a second rotated scale.
"""
from pathlib import Path
from array import array
import math,random,struct,zlib,json
from meadow_distribution import SOURCE,config,noise,edge_weight,Z
N=1024
def png(path,w,h,data):
 def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
 raw=b''.join(b'\0'+bytes(data[y*w*4:(y+1)*w*4]) for y in range(h))
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,7))+chunk(b'IEND',b''))

def bake_ecology():
 cfg=config();a,b,c,d=cfg['bounds_cm'];field=bytearray(128*128*4);zones=Z.Zones();maximum_exclusion=0
 for j in range(128):
  for i in range(128):
   x=a+(i+.5)/128*(c-a);y=b+(j+.5)/128*(d-b);row=zones.evaluate(x,y)
   maximum_exclusion=max(maximum_exclusion,row['exclusion'])
   assert 0<=row['position'][2]<256,'Update the local ground height encoding for another terrain range'
   alpha=edge_weight(x,y,cfg)*row['weights']['Z04']*row['grass_density']*(1-row['exclusion'])
   v=[noise(x,y,1100*cfg['cluster_scale'],cfg['seed']+77),noise(x,y,520,cfg['seed']+4),row['position'][2]/256,alpha]
   field[(j*128+i)*4:(j*128+i+1)*4]=bytes(round(max(0,min(1,k))*255) for k in v)
 png(SOURCE/'T_Meadow_Ecology.png',128,128,field)
 return dict(samples=128*128,maximum_exclusion=maximum_exclusion,bounds_cm=cfg['bounds_cm'])

def generate():
 r=random.Random(41220261);color=bytearray(N*N*4);height=array('f',[0.])* (N*N)
 for y in range(N):
  for x in range(N):
   i=y*N+x;grain=r.random();v=(.6*math.sin(x*.037+math.sin(y*.017)*2)+.4*math.sin(y*.043-x*.021))*.09+grain*.17
   for k,c in enumerate([77,68,48]):color[i*4+k]=round(c*(.85+v))
   color[i*4+3]=round(220+grain*24);height[i]=grain*.08
 def dab(x,y,width,c,h):
  rad=max(.65,width)
  for yy in range(math.floor(y-rad),math.ceil(y+rad)+1):
   for xx in range(math.floor(x-rad),math.ceil(x+rad)+1):
    a=max(0,min(1,(rad-math.hypot(xx-x,yy-y))*.9))
    if a<=0:continue
    i=(yy%N)*N+(xx%N)
    for k in range(3):color[i*4+k]=round(color[i*4+k]*(1-a)+c[k]*a)
    height[i]=max(height[i],h*a)
 def stroke(x,y,angle,length,width,c,curvature=.15,h=.18):
  for k in range(max(2,math.ceil(length*1.7))):
   t=k/max(1,math.ceil(length*1.7)-1);a=angle+curvature*t
   dab(x+math.cos(a)*length*t,y+math.sin(a)*length*t,width*(1-.7*t),c,h)
 # A shallow decomposing mat of fine grass fibres; no forest leaves or gravel carpet.
 for _ in range(5600):
  x,y=r.uniform(0,N),r.uniform(0,N);dry=r.random()<.72;c=r.choice([(119,103,67),(140,120,78),(97,87,58)] if dry else [(71,86,44),(88,100,52)])
  stroke(x,y,r.random()*math.tau,r.uniform(10,48),r.uniform(.65,1.4),c,r.uniform(-.6,.6),r.uniform(.13,.35))
 # Small broadleaf basal rosettes in loose clusters, 1-3 cm leaves at 1.2 m tile size.
 for _ in range(360):
  cx,cy=r.uniform(0,N),r.uniform(0,N);base=r.random()*math.tau
  for j in range(r.randrange(3,6)):
   a=base+j*2.4;length=r.uniform(9,23);width=r.uniform(2.5,5);c=r.choice([(73,91,43),(87,102,50),(96,109,58)])
   for k in range(math.ceil(length*2)):
    t=k/(math.ceil(length*2)-1);w=width*math.sin(math.pi*t)**.7
    dab(cx+math.cos(a)*length*t,cy+math.sin(a)*length*t,w,c,.28+.12*math.sin(math.pi*t))
   stroke(cx,cy,a,length,.58,tuple(min(255,v+13) for v in c),0,.45)
 normal=bytearray(N*N*4)
 for y in range(N):
  for x in range(N):
   i=y*N+x;dx=(height[y*N+(x+1)%N]-height[y*N+(x-1)%N])*.85;dy=(height[((y+1)%N)*N+x]-height[((y-1)%N)*N+x])*.85;l=math.sqrt(1+dx*dx+dy*dy)
   normal[i*4:i*4+4]=bytes([round((-dx/l*.5+.5)*255),round((dy/l*.5+.5)*255),round((1/l*.5+.5)*255),255])
 png(SOURCE/'T_Meadow_LitterColor.png',N,N,color);png(SOURCE/'T_Meadow_LitterNormal.png',N,N,normal)
 bake_ecology()
 (SOURCE/'ground_provenance.json').write_text(json.dumps(dict(authoring='Original procedural material inputs derived from the existing author-owned GroundMaterial vocabulary; no third-party images',seed=41220261,tile_width_cm=120,textures=['T_Meadow_LitterColor','T_Meadow_LitterNormal','T_Meadow_Ecology'],sampling_budget='two color + one normal + one shared ecological mask for the local ground decal; one mask sample for foliage'),indent=2))
 print('Ground inputs baked: 1024 color/normal and 128 ecology field')
if __name__=='__main__':generate()
