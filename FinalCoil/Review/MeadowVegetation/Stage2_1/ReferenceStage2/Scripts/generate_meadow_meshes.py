"""Original geometry: folded tapered leaves, meadow seedheads and three herbs.

No third-party assets or textures. OBJ units are centimetres. UV.y is root-to-tip
height for root-pinned wind; importer flips V, handled by the material.
"""
from pathlib import Path
import math, random, json
from meadow_distribution import config, SOURCE
class Mesh:
    def __init__(self,height):self.v=[];self.uv=[];self.f=[];self.height=height
    def vert(self,p,u=.5):
        self.v.append(p);self.uv.append((u,max(0,min(1,p[2]/self.height))));return len(self.v)
    def tri(self,a,b,c,mat):self.f.append((a,b,c,mat))
    def leaf(self,root,angle,h,width,bend,mat='Leaf',segments=3):
        rings=[];dx,dy=math.cos(angle),math.sin(angle);wx,wy=-dy,dx
        for j in range(segments+1):
            t=j/segments;w=width*(math.sin(math.pi*(.12+.88*t))**.7 if t<1 else .008)
            p=(root[0]+dx*bend*t*t,root[1]+dy*bend*t*t,root[2]+h*t)
            rings.append([self.vert((p[0]+wx*w*s,p[1]+wy*w*s,p[2]-(abs(s)*w*.35)),(s+1)/2) for s in [-1,0,1]])
        for r,q in zip(rings,rings[1:]):
            for k in [0,1]:self.tri(r[k],q[k],r[k+1],mat);self.tri(r[k+1],q[k],q[k+1],mat)
    def stem(self,p,q,width=.18,mat='Stem'):
        angle=math.atan2(q[1]-p[1],q[0]-p[0]);dx,dy=math.cos(angle),math.sin(angle)
        # Two narrow bent ribbons with different normals; leaf silhouettes are geometry.
        for a in [angle,angle+1.2]:
            wx,wy=math.cos(a)*width,math.sin(a)*width
            ids=[self.vert((v[0]+wx*s,v[1]+wy*s,v[2])) for v in [p,q] for s in [-1,1]]
            self.tri(ids[0],ids[2],ids[1],mat);self.tri(ids[1],ids[2],ids[3],mat)
    def petal(self,p,angle,length,width,mat):
        x,y,z=p;dx,dy=math.cos(angle),math.sin(angle);wx,wy=-dy*width,dx*width
        ids=[self.vert(v) for v in [(x,y,z),(x+dx*length*.65+wx,y+dy*length*.65+wy,z+.28),(x+dx*length,y+dy*length,z-.2),(x+dx*length*.65-wx,y+dy*length*.65-wy,z+.28),(x+dx*length*.5,y+dy*length*.5,z+.55)]]
        for k in range(4):self.tri(ids[k],ids[(k+1)%4],ids[4],mat)
    def write(self,name):
        lines=['o '+name]+['v %.5f %.5f %.5f'%p for p in self.v]+['vt %.5f %.5f'%p for p in self.uv];last=None
        for a,b,c,mat in self.f:
            if mat!=last:lines.append('usemtl '+mat);last=mat
            lines.append('f '+' '.join(f'{i}/{i}' for i in [a,b,c]))
        (SOURCE/(name+'.obj')).write_text('\n'.join(lines)+'\n')
        return dict(name=name,triangles=len(self.f),vertices=len(self.v),height_cm=max(p[2] for p in self.v),radius_cm=max(math.hypot(*p[:2]) for p in self.v),slots=sorted(set(f[3] for f in self.f)))
def grass(group,index,spec):
    r=random.Random(7121+index+sum(map(ord,group)));height=spec['height_cm'][1];m=Mesh(height)
    count={'short':30,'medium':30,'tall':16,'dry':9}[group]
    for i in range(count):
        a=r.random()*math.tau;rr=r.uniform(0,10 if group=='short' else 16);root=(math.cos(a)*rr,math.sin(a)*rr,0)
        h=r.uniform(*spec['height_cm']);w=r.uniform(.45,1.0) if group in ['medium','tall'] else r.uniform(.22,.55)
        m.leaf(root,a+r.uniform(-1,1),h,w,h*r.uniform(.18,.65),'Dry' if group=='dry' else 'Leaf',2 if group in ['short','medium'] else 3)
    if group in ['tall','dry']:
        for i in range(3):
            a=r.random()*math.tau;h=r.uniform(height*.78,height);q=(math.cos(a)*7,math.sin(a)*7,h);m.stem((0,0,0),q,.13,'Dry' if group=='dry' else 'Stem')
            for k in range(5):
                p=(q[0],q[1],h-8+k*1.5);an=a+k*2.4;m.leaf(p,an,2,.17,3,'Seed',1)
    return m
def herb(index,spec):
    r=random.Random(981+index);kind=index//2;height=[18,42,26][kind];m=Mesh(height)
    if kind==0: # clover: branching petioles, trifoliate low leaves, subdued pink heads
        for n in range(7):
            a=r.random()*math.tau;h=r.uniform(6,13);q=(math.cos(a)*r.uniform(4,13),math.sin(a)*r.uniform(4,13),h);m.stem((0,0,0),q,.12)
            for j in range(3):m.leaf(q,a+j*2.1,1.4,1.4,3.0,'Leaf',2)
        q=(2,-1,17);m.stem((0,0,0),q,.13)
        for j in range(7):m.petal(q,j*math.tau/7,1.15,.5,'Pink')
    elif kind==1: # yarrow: pinnate foliage, flat cream umbels
        top=(2,1,39);m.stem((0,0,0),top,.19)
        for n in range(5):
            a=n*2.4;z=5+n*5
            for j in range(4):
                p=(math.cos(a)*j,math.sin(a)*j,z+j*.5)
                for side in [-1,1]:m.leaf(p,a+side*.8,1,.24,3.0,'Leaf',1)
        for n in range(6):
            a=n*math.tau/6;q=(2+math.cos(a)*3.6,1+math.sin(a)*3.6,40+r.random()*1.2);m.stem((1,0,33),q,.1)
            for j in range(5):m.petal(q,j*math.tau/5,.6,.3,'Cream')
    else: # dandelion: basal rosette, sparse yellow capitulum
        for n in range(8):m.leaf((0,0,.1),n*2.4,3,.7,r.uniform(7,13),'Leaf',3)
        q=(1.7,.8,25);m.stem((0,0,0),q,.2)
        for n in range(16):m.petal(q,n*math.tau/16,1.15,.18,'Yellow')
    return m,['clover','yarrow','dandelion'][kind]
def generate():
    cfg=config();manifest=[]
    for group,spec in cfg['groups'].items():
        for index in range(spec['variants']):
            if group=='herbs':m,species=herb(index,spec)
            else:m=grass(group,index,spec);species=group
            rec=m.write(f'SM_Meadow_{group}_{index:02}');rec.update(group=group,variant=index,species=species);manifest.append(rec)
    (SOURCE/'meshes.json').write_text(json.dumps(dict(provenance='Original procedural geometry authored for Final Coil; no external dependencies',units='cm',meshes=manifest),indent=2))
    print(json.dumps(manifest,indent=1))
if __name__=='__main__':generate()
