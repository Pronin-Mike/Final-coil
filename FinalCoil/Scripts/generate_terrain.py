import os,json,math,sys
sys.path.insert(0,os.path.dirname(__file__))
import terrain_profile as T
ROOT=T.ROOT;D=ROOT+"/SourceArt/Terrain";os.makedirs(D,exist_ok=True)
T.build_grid()
json.dump(T.GRID,open(D+"/heightfield.json","w"))
vs,fs=T.grid_mesh();T.write_obj(D+"/SM_Berezovka_Terrain.obj",vs,fs)
bundles={};replace=[];routes=[]
def group_for(a):
    n=a["label"]
    if n.startswith(("NET_Rail","JOIN_Rail")):return "Rail"
    if n.startswith(("NET_","JOIN_")):
        return "Road" if any(k in n for k in ["MainRoad","LakeRoad","NorthRoad","GrandpaDrive"]) else "Path"
    if any(k in n for k in ["_Walkway_ToRoad","G01_GarageDrive","G01_HouseWalk","G01_SideDoorPath","SHOP01_Approach","STOP01_RoadApproach","BOR_EntranceTrail_","BOR_ForkShortSpur","CHAPEL01_Access"]):return "Path" if a["s"][1]<3 else "Road"
    return None
def strip(group,p,q,width,label):
    vs,fs=bundles.setdefault(group,([],[]));offset=len(vs)
    dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
    if length<.001:return
    n=max(1,math.ceil(length/200))
    for i in range(n+1):
        t=i/n;x=p[0]+t*dx;y=p[1]+t*dy
        for k in [-1,0,1]:
            xx=x-dy/length*width*.5*k;yy=y+dx/length*width*.5*k
            vs.append((xx,yy,T.height(xx,yy)+3))
    for i in range(n):
        for k in range(2):
            a=offset+i*3+k;b=a+3;fs.extend([(a,b,a+1),(b,b+1,a+1)])
    routes.append({"label":label,"p":p,"q":q,"width":width,"group":group})
for a in T.INV:
    g=group_for(a)
    if not g:continue
    replace.append(a["label"]);yaw=math.radians(a["r"][1]);c=math.cos(yaw);s=math.sin(yaw);x,y=a["p"][:2]
    if a["label"].startswith("JOIN_"):
        vs,fs=bundles.setdefault(g,([],[]));o=len(vs)
        radius=a["s"][0]*50;vs.append((x,y,T.height(x,y)+3.2))
        for i in range(33):
            xx=x+radius*math.cos(i*math.tau/32);yy=y+radius*math.sin(i*math.tau/32)
            vs.append((xx,yy,T.height(xx,yy)+3.2))
        fs.extend((o,o+i+1,o+i+2) for i in range(32))
    else:
        half=a["s"][0]*50
        strip(g,[x-c*half,y-s*half],[x+c*half,y+s*half],a["s"][1]*100,a["label"])
shore=[[25333.333333,86666.666667],[33000,106000],[39500,121000],[43000,130000]]
for i,(p,q) in enumerate(zip(shore,shore[1:])):strip("Path",p,q,220,"LakeAccess_%02d"%i)
for g,(v,f) in bundles.items():T.write_obj(D+"/SM_Conform_"+g+".obj",v,f)
minz=min(z for row in T.GRID for z in row);maxz=max(z for row in T.GRID for z in row)
grades=[]
for r in routes:
    p,q=r["p"],r["q"];n=max(1,math.ceil(math.dist(p,q)/100))
    last=None
    for i in range(n+1):
        x=p[0]+(q[0]-p[0])*i/n;y=p[1]+(q[1]-p[1])*i/n;z=T.height(x,y)
        if last:grades.append(abs(z-last[2])/math.hypot(x-last[0],y-last[1]))
        last=(x,y,z)
json.dump({"replace_labels":replace,"routes":routes,"shore":shore,"z_range_cm":[minz,maxz],"max_route_grade":max(grades),"pads":[list(p) for p in T.PADS],"grid":[T.NX,T.NY,T.DX,T.DY],"terrain_vertices":(T.NX+1)*(T.NY+1),"terrain_triangles":T.NX*T.NY*2},open(D+"/manifest.json","w"),indent=2)
print(json.dumps({"vertices":len(vs),"triangles":len(fs),"height_m":[minz/100,maxz/100],"max_grade_percent":max(grades)*100,"roadstrips":len(routes)}))

