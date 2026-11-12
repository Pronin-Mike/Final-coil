"""Terrain V2: visible street ridge, Bor slope, asymmetric lake basin. Centimeters."""
import json,math,os,bisect
ROOT="D:/GameDevelop/FinalCoil"
INV=json.load(open(ROOT+"/Scripts/terrain_inventory.json",encoding="utf-8"))["actors"]
DETAILS=True
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def gauss(x,y,cx,cy,rx,ry):return math.exp(-((x-cx)/rx)**2-((y-cy)/ry)**2)
LAKES=[(a["p"][0],a["p"][1],a["s"][0]*50,a["s"][1]*50) for a in INV if a["label"].startswith("Lake_Mass_")]
ROAD=[]
for a in INV:
    if a["label"].startswith("NET_MainRoad"):
        yaw=math.radians(a["r"][1]);c=math.cos(yaw);s=math.sin(yaw);h=a["s"][0]*50;x,y=a["p"][:2]
        ROAD.append(((x-c*h,y-s*h),(x+c*h,y+s*h)))
def nearest_road(x,y):
    best=None
    for a,b in ROAD:
        dx=b[0]-a[0];dy=b[1]-a[1]
        t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
        q=(a[0]+t*dx,a[1]+t*dy);d=math.hypot(x-q[0],y-q[1])
        if best is None or d<best[0]:best=(d,q)
    return best
def lake_distance(x,y):
    best=None
    for cx,cy,rx,ry in LAKES:
        u=(x-cx)/rx;v=(y-cy)/ry;r=math.hypot(u,v)
        grad=math.hypot(u/rx,v/ry)/max(r,.0001)
        d=(r-1)/max(grad,1/max(rx,ry))
        if best is None or d<best:best=d
    return best
def raw(x,y):
    village=1-smooth(45000,85000,math.hypot(x-7000,(y+4000)*.65))
    small=110*math.sin(x/13000)+75*math.sin(y/17000)+45*math.sin((x+y)/11000)
    broad=250*math.sin((x+10000)/45000)+180*math.cos(y/57000)+150*math.sin((x-y)/62000)
    z=80+small*village+broad*(1-village)
    # Street rises to a broad crest, then descends into the eastern drainage hollow.
    z+=550*gauss(x,y,8000,10500,25000,8000)
    z-=220*gauss(x,y,5000,28500,17000,8000)
    z+=250*gauss(x,y,0,-25000,18000,10000)
    # Existing curved trail skirts the western knoll, with a hollow to its east.
    bor_mask=math.exp(-((y+29000)/17000)**4)
    z+=850*smooth(8000,30000,x)*bor_mask
    z+=420*gauss(x,y,48000,-30000,30000,35000)
    z+=450*gauss(x,y,23000,-33000,8500,6000)
    z-=220*gauss(x,y,22000,-23000,12000,4000)
    d=lake_distance(x,y)
    if d<16000:
        access=(1-smooth(60000,85000,x))*(1-smooth(180000,220000,y))
        if d<0:
            depth=-d
            shelf=100*smooth(0,2200,depth)+150*smooth(2200,6500,depth)+800*smooth(6500,18000,depth)
            steep=1050*smooth(0,9000,depth)
            z=-250-(shelf*access+steep*(1-access))
        else:
            bank=-250+access*450*smooth(0,7500,d)+(1-access)*650*smooth(0,2200,d)
            w=1-smooth(8500,16000,d);z=z*(1-w)+bank*w
    return z
offsets={"H01":70,"H02":-60,"H03":110,"H04":110,"H05":80,"H06":-70,"H07":50,"H08":120,"H09":-60,"H10":90,"H11":-80,"H12":80,"E01":-70,"E02":70,"E03":100,"E04":-60,"E05":80,"E06":-60,"E07":60}
PADS=[]
for a in INV:
    if a["label"].endswith("_Yard_30x40m"):
        key=a["label"].split("_")[0];x,y=a["p"][:2];yaw=math.radians(a["r"][1])
        _,q=nearest_road(x,y)
        PADS.append((key,x,y,2000,1500,math.cos(yaw),math.sin(yaw),raw(*q)+offsets[key]))
for name,x,y,hx,hy in [("G01",-7350,15500,2200,1800),("STOP01",500,0,950,750),("SHOP01",6010,-15000,750,650),("CHAPEL01",35000,-27800,850,850)]:
    target=raw(x,y)
    if name=="G01":target=raw(2640,15000)+70
    if name=="STOP01":target=raw(0,0)
    PADS.append((name,x,y,hx,hy,1,0,target))
datum=next(p[7] for p in PADS if p[0]=="H05")
PADS=[p[:7]+(datum,) if p[0]=="SHOP01" else p for p in PADS]
def detail(x,y):
    if not DETAILS:return 0
    d,q=nearest_road(x,y)
    if y<-55000 or y>65000 or d>4500:return 0
    # Shallow drainage swales outside the road edge, draining off crest into the sag.
    ditch=-(28+14*gauss(x,y,5000,28500,14000,10000))*math.exp(-((d-690)/235)**2)*smooth(400,510,d)
    # Use-disturbed ground and runoff pockets, never on the driveable carriageway.
    lumps=0
    for cx,cy,amp,rx,ry in [(3000,10000,27,320,380),(4700,20000,22,390,300),(3300,27000,-28,420,500),(7600,33000,-35,500,700),(-3500,-12000,20,350,480)]:
        lumps+=amp*gauss(x,y,cx,cy,rx,ry)
    return ditch+lumps*smooth(420,700,d)
def analytic(x,y):
    z=raw(x,y);best=0;target=z
    for name,cx,cy,hx,hy,c,s,h in PADS:
        dx=x-cx;dy=y-cy
        if abs(dx)>hx+hy+5000 or abs(dy)>hx+hy+5000:continue
        lx=abs(dx*c+dy*s);ly=abs(-dx*s+dy*c)
        distance=math.hypot(max(0,lx-hx-450),max(0,ly-hy-450))
        w=1-smooth(0,5000 if name=="G01" else 3500,distance)
        if w>best:best=w;target=h
    z=z*(1-best)+target*best
    d,q=nearest_road(x,y)
    along=(smooth(-4000,0,q[1])*(1-smooth(40000,46000,q[1])))
    if q[1]<=11500:
        roadz=raw(0,0)+520*smooth(0,11500,q[1])
    elif q[1]<=30000:
        roadz=raw(0,0)+520-750*smooth(11500,30000,q[1])
    else:
        roadz=raw(0,0)-230+300*smooth(30000,45000,q[1])
    w=(1-smooth(400,2000,d))*along
    z=z*(1-w)+roadz*w
    return z+detail(x,y)*(1-best)
XMIN=-37000.;XMAX=129666.66666666666;YMIN=-132666.66666666666;YMAX=287333.3333333333
def axis(lo,a,b,hi):
    vals=[lo];x=lo
    for end,step in [(a,1000),(b,200),(hi,1000)]:
        while x+step<end-.001:x+=step;vals.append(x)
        x=end;vals.append(x)
    return vals
XS=axis(XMIN,-15000,50000,XMAX);YS=axis(YMIN,-65000,70000,YMAX)
NX=len(XS)-1;NY=len(YS)-1;DX=(XMAX-XMIN)/NX;DY=(YMAX-YMIN)/NY;GRID=None
def build_grid():
    global GRID
    GRID=[[analytic(x,y) for y in YS] for x in XS];return GRID
def height(x,y):
    global GRID
    if GRID is None:
        p=ROOT+"/SourceArt/Terrain/heightfield.json"
        GRID=json.load(open(p)) if os.path.exists(p) else build_grid()
    i=max(0,min(NX-1,bisect.bisect_right(XS,x)-1));j=max(0,min(NY-1,bisect.bisect_right(YS,y)-1))
    u=max(0,min(1,(x-XS[i])/(XS[i+1]-XS[i])));v=max(0,min(1,(y-YS[j])/(YS[j+1]-YS[j])))
    a=GRID[i][j];b=GRID[i+1][j];c=GRID[i][j+1];d=GRID[i+1][j+1]
    return a+(b-a)*u+(c-a)*v if u+v<=1 else d+(c-d)*(1-u)+(b-d)*(1-v)
def write_obj(path,verts,faces,groups=None):
    with open(path,"w") as f:
        def line(v):f.write(v+chr(10))
        line("o TerrainMesh")
        for x,y,z in verts:line("v %.4f %.4f %.4f"%(x,y,z))
        for x,y,z in verts:line("vt %.6f %.6f"%(x/10000,y/10000))
        last=None
        for i,(a,b,c) in enumerate(faces):
            if groups and groups[i]!=last:last=groups[i];line("usemtl "+last)
            line("f %d/%d %d/%d %d/%d"%(a+1,a+1,b+1,b+1,c+1,c+1))
def grid_mesh():
    vs=[(x,y,GRID[i][j]) for i,x in enumerate(XS) for j,y in enumerate(YS)]
    fs=[]
    for i in range(NX):
        for j in range(NY):
            a=i*(NY+1)+j;b=a+NY+1;c=a+1;d=b+1;fs.extend([(a,b,c),(b,d,c)])
    return vs,fs



