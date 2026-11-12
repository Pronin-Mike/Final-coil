"""Deterministic centimeter heightfield shared by mesh generation, alignment and QA."""
import json,math,os
ROOT="D:/GameDevelop/FinalCoil"
INV=json.load(open(ROOT+"/Scripts/terrain_inventory.json",encoding="utf-8"))["actors"]
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)))
    return t*t*(3-2*t)
LAKES=[(a["p"][0],a["p"][1],a["s"][0]*50,a["s"][1]*50) for a in INV if a["label"].startswith("Lake_Mass_")]
def raw(x,y):
    village=1-smooth(45000,85000,math.hypot(x-7000,(y+4000)*.65))
    small=110*math.sin(x/13000)+75*math.sin(y/17000)+45*math.sin((x+y)/11000)
    broad=250*math.sin((x+10000)/45000)+180*math.cos(y/57000)+150*math.sin((x-y)/62000)
    bor=420*math.exp(-((x-48000)/30000)**2-((y+30000)/35000)**2)
    z=80+small*village+broad*(1-village)+bor
    r=min(math.hypot((x-cx)/rx,(y-cy)/ry) for cx,cy,rx,ry in LAKES)
    if r<1.35:
        # -2.5m water plane; bed under water, broad gentle banks outside.
        bank=-470+max(0,min(1,(r-.80)/.55))**1.3*820
        z=z*smooth(1.03,1.35,r)+bank*(1-smooth(1.03,1.35,r))
    return z
PADS=[]
for a in INV:
    if a["label"].endswith("_Yard_30x40m"):
        yaw=math.radians(a["r"][1])
        PADS.append((a["label"].split("_")[0],a["p"][0],a["p"][1],2000,1500,math.cos(yaw),math.sin(yaw),raw(*a["p"][:2])))
for name,x,y,hx,hy in [("G01",-7350,15500,2200,1800),("STOP01",500,0,950,750),("SHOP01",6010,-15000,750,650),("CHAPEL01",35000,-27800,850,850)]:
    PADS.append((name,x,y,hx,hy,1,0,raw(x,y)))
# The shop apron touches H05's yard: share one datum to avoid competing flat pads.
_shop_datum=next(p[7] for p in PADS if p[0]=="H05")
PADS=[p[:7]+(_shop_datum,) if p[0]=="SHOP01" else p for p in PADS]
def analytic(x,y):
    z=raw(x,y);best=0;target=z
    for name,cx,cy,hx,hy,c,s,h in PADS:
        dx=x-cx;dy=y-cy
        if abs(dx)>hx+hy+2000 or abs(dy)>hx+hy+2000:continue
        lx=abs(dx*c+dy*s);ly=abs(-dx*s+dy*c)
        distance=math.hypot(max(0,lx-hx-500),max(0,ly-hy-500))
        w=1-smooth(0,2000,distance)
        if w>best:best=w;target=h
    return z*(1-best)+target*best
XMIN=-37000.;XMAX=129666.66666666666;YMIN=-132666.66666666666;YMAX=287333.3333333333
NX=334;NY=840;DX=(XMAX-XMIN)/NX;DY=(YMAX-YMIN)/NY
GRID=None
def build_grid():
    global GRID
    GRID=[[analytic(XMIN+i*DX,YMIN+j*DY) for j in range(NY+1)] for i in range(NX+1)]
    return GRID
def height(x,y):
    global GRID
    if GRID is None:
        p=ROOT+"/SourceArt/Terrain/heightfield.json"
        GRID=json.load(open(p)) if os.path.exists(p) else build_grid()
    fx=max(0,min(NX-.000001,(x-XMIN)/DX));fy=max(0,min(NY-.000001,(y-YMIN)/DY))
    i=int(fx);j=int(fy);u=fx-i;v=fy-j
    a=GRID[i][j];b=GRID[i+1][j];c=GRID[i][j+1];d=GRID[i+1][j+1]
    # Same diagonal as generated mesh, exact piecewise planar height.
    return a+(b-a)*u+(c-a)*v if u+v<=1 else d+(c-d)*(1-u)+(b-d)*(1-v)
def write_obj(path,verts,faces,groups=None):
    with open(path,"w") as f:
        def line(value): f.write(value+chr(10))
        line("o TerrainMesh")
        for x,y,z in verts:line("v %.4f %.4f %.4f"%(x,y,z))
        line("s 1")
        last=None
        for i,(a,b,c) in enumerate(faces):
            if groups and groups[i]!=last:
                last=groups[i];line("usemtl "+last)
            line("f %d %d %d"%(a+1,b+1,c+1))

def grid_mesh():
    vs=[(XMIN+i*DX,YMIN+j*DY,GRID[i][j]) for i in range(NX+1) for j in range(NY+1)]
    fs=[]
    for i in range(NX):
        for j in range(NY):
            a=i*(NY+1)+j;b=a+NY+1;c=a+1;d=b+1
            fs.extend([(a,b,c),(b,d,c)])
    return vs,fs


