"""Original geometry: folded tapered leaves, meadow seedheads and three herbs.

No third-party assets. OBJ units are centimetres. UV.x encodes a botanical
part and local leaf U, UV.y is local leaf V. Wind uses local vertex height.
"""
from pathlib import Path
import math, random, json
from meadow_distribution import config, SOURCE
class Mesh:
    def __init__(self,height):self.v=[];self.uv=[];self.f=[];self.height=height
    def vert(self,p,u=.5,v=None):
        self.v.append(p);self.uv.append((u,max(0,min(1,p[2]/self.height)) if v is None else v));return len(self.v)
    def tri(self,a,b,c,mat):self.f.append((a,b,c,mat))
    def leaf(self,root,angle,h,width,bend,mat='Leaf',segments=3):
        rings=[];dx,dy=math.cos(angle),math.sin(angle);wx,wy=-dy,dx
        for j in range(segments+1):
            t=j/segments;w=width*(math.sin(math.pi*(.12+.88*t))**.7 if t<1 else .008)
            p=(root[0]+dx*bend*t*t,root[1]+dy*bend*t*t,root[2]+h*math.sin(t*math.pi*.64))
            rings.append([self.vert((p[0]+wx*w*s,p[1]+wy*w*s,p[2]-(abs(s)*w*.18)),(s+1)/2,t) for s in [-1,0,1]])
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
    def broadleaf(self,p,angle,length,width,lift=1.,mat='Leaf',lobed=False):
        rings=[];dx,dy=math.cos(angle),math.sin(angle);wx,wy=-dy,dx
        for t in [0,.23,.56,.82,1]:
            w=width*math.sin(math.pi*t)**.65
            if lobed:w*=.7 if t==.23 or t==.82 else 1.2
            z=p[2]+lift*math.sin(t*math.pi*.8)
            rings.append([self.vert((p[0]+dx*length*t+wx*w*s,p[1]+dy*length*t+wy*w*s,z-abs(s)*w*.12),(s+1)/2,t) for s in [-1,0,1]])
        for r,q in zip(rings,rings[1:]):
            for k in [0,1]:self.tri(r[k],q[k],r[k+1],mat);self.tri(r[k+1],q[k],q[k+1],mat)
    def write(self,name):
        def area(tri):
            a,b,c=[self.v[i-1] for i in tri[:3]];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
            return sum((u[(k+1)%3]*v[(k+2)%3]-u[(k+2)%3]*v[(k+1)%3])**2 for k in range(3))
        self.f=[f for f in self.f if area(f)>1e-10]
        parts={'Leaf':0,'Stem':1,'Dry':2,'Seed':3,'Pink':4,'Cream':5,'Yellow':6,'Clover':7,'Yarrow':8,'Dandelion':9}
        uv=[];faces=[]
        for a,b,c,mat in self.f:
            ids=[]
            for index in [a,b,c]:
                u,v=self.uv[index-1];uv.append((parts[mat]*2+u,v));ids.append((index,len(uv)))
            faces.append(ids)
        lines=['o '+name]+['v %.5f %.5f %.5f'%p for p in self.v]+['vt %.5f %.5f'%p for p in uv]+['usemtl Meadow']
        for ids in faces:lines.append('f '+' '.join(f'{i}/{t}' for i,t in ids))
        (SOURCE/(name+'.obj')).write_text('\n'.join(lines)+'\n')
        return dict(name=name,triangles=len(self.f),vertices=len(self.v),height_cm=max(p[2] for p in self.v),radius_cm=max(math.hypot(*p[:2]) for p in self.v),slots=['Meadow'],botanical_parts=sorted(set(f[3] for f in self.f)))
def grass(group,index,spec):
    r=random.Random(7121+index+sum(map(ord,group)));height=spec['height_cm'][1];m=Mesh(height)
    if group=='short':
        if index==0:
            for i in range(19):
                x,y=r.uniform(-16,16),r.uniform(-16,16);a=r.random()*math.tau;m.leaf((x,y,0),a,r.uniform(2,8),r.uniform(.1,.27),r.uniform(2,6),segments=2)
        elif index==1:
            for j in range(3):
                p=(r.uniform(-12,12),r.uniform(-12,12),.1)
                for k in range(4):m.broadleaf(p,k*2.4+j,r.uniform(3.5,7),r.uniform(.7,1.3),r.uniform(1.8,3.5),'Dandelion',True)
        else:
            for j in range(4):
                p=(r.uniform(-15,15),r.uniform(-15,15),r.uniform(.8,2.5))
                for k in range(3):m.broadleaf(p,j+k*2.094,r.uniform(1.7,3.3),r.uniform(.7,1.2),.45,'Clover')
            for j in range(4):m.leaf((r.uniform(-12,12),r.uniform(-12,12),0),r.random()*6.28,r.uniform(3,7),.15,4,'Dry',1)
    elif group=='medium':
        for i in range([24,21,19][index]):
            a=r.random()*math.tau;rr=r.uniform(2,17);p=(math.cos(a)*rr,math.sin(a)*rr,0);h=r.uniform(17,30) if index==0 else r.uniform(18,39);w=r.uniform(.14,.38) if index==0 else r.uniform(.3,.65);bend=h*r.uniform(.1,.3) if index==0 else h*r.uniform(.45,.95)
            m.leaf(p,a+r.uniform(-.8,.8),h,w,bend,segments=3)
        if index==2:
            for j in range(3):
                h=r.uniform(32,42);q=(r.uniform(-7,7),r.uniform(-7,7),h);m.stem((q[0]*.3,q[1]*.3,0),q,.09)
                for k in range(4):m.leaf((q[0],q[1],h-4+k),k*2.4,1.3,.13,1.8,'Seed',1)
    elif group=='tall' and index==2:
        for j in range(4):
            x,y=r.uniform(-12,12),r.uniform(-12,12);h=r.uniform(45,73);m.stem((x,y,0),(x+2,y,h),.16)
            for k in range(3):m.broadleaf((x,y,h*(.28+k*.19)),j+k*2.4,r.uniform(5,10),r.uniform(1,1.9),r.uniform(1,3),'Yarrow',True)
    elif group=='tall' and index==1:
        for j in range(7):
            x,y=r.uniform(-13,13),r.uniform(-13,13);h=r.uniform(58,86);q=(x+3,y-2,h);m.stem((x,y,0),q,.09)
            for k in range(2):m.leaf((x,y,12+k*20),j+k*2.4,r.uniform(19,28),r.uniform(.25,.5),r.uniform(10,22),segments=2)
            for k in range(5):
                p=(q[0],q[1],h-7+k*1.3);m.leaf(p,k*2.4,1.3,.15,2.7,'Seed',1)
    else:
        for i in range(10 if group=='tall' else 7):
            a=r.random()*math.tau;rr=r.uniform(0,15);p=(math.cos(a)*rr,math.sin(a)*rr,0);h=r.uniform(45,86) if group=='tall' else r.uniform(20,56)
            m.leaf(p,a,h,r.uniform(.65,1.2) if group=='tall' else r.uniform(.12,.35),h*r.uniform(.25,.7),'Leaf' if group=='tall' else 'Dry',3 if group=='tall' else 2)
        if group=='dry':
            for j in range(6):m.leaf((r.uniform(-15,15),r.uniform(-15,15),.1),j*2.4,r.uniform(.5,2),.22,r.uniform(5,13),'Dry',1)
    return m
def herb(index,spec):
    r=random.Random(981+index);kind=index//2;height=[18,42,26][kind];m=Mesh(height)
    if kind==0: # clover: branching petioles, trifoliate low leaves, subdued pink heads
        for n in range(4):
            a=r.random()*math.tau;h=r.uniform(6,13);q=(math.cos(a)*r.uniform(4,13),math.sin(a)*r.uniform(4,13),h);m.stem((0,0,0),q,.12)
            for j in range(3):m.broadleaf(q,a+j*2.094,2.3,1.05,.35,'Clover')
        q=(2,-1,17);m.stem((0,0,0),q,.13)
        for j in range(9):m.petal((q[0],q[1],q[2]+r.uniform(-.3,.5)),j*math.tau/9,.8,.32,'Pink')
    elif kind==1: # yarrow: pinnate foliage, flat cream umbels
        top=(2,1,39);m.stem((0,0,0),top,.19)
        for n in range(5):
            a=n*2.4;z=5+n*5
            for j in range(4):
                p=(math.cos(a)*j,math.sin(a)*j,z+j*.5)
                for side in [-1,1]:m.leaf(p,a+side*.8,.6,.16,2.2,'Yarrow',1)
        for n in range(6):
            a=n*math.tau/6;q=(2+math.cos(a)*3.6,1+math.sin(a)*3.6,40+r.random()*1.2);m.stem((1,0,33),q,.1)
            for j in range(5):m.petal(q,j*math.tau/5,.6,.3,'Cream')
    else: # dandelion: basal rosette, sparse yellow capitulum
        for n in range(6):m.broadleaf((0,0,.1),n*2.4,r.uniform(7,13),r.uniform(.6,1.1),r.uniform(1,2.8),'Dandelion',True)
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
