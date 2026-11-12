import sys,json,math
sys.path.insert(0,"D:/GameDevelop/FinalCoil/Scripts");import terrain_profile as T
M=json.load(open(T.ROOT+"/SourceArt/Terrain/manifest.json"))
out=[]
for r in M["routes"]:
    p,q=r["p"],r["q"];n=max(1,math.ceil(math.dist(p,q)/100));z=[]
    for i in range(n+1):
        x=p[0]+(q[0]-p[0])*i/n;y=p[1]+(q[1]-p[1])*i/n;z.append(T.height(x,y))
    grade=max(abs(a-b)/(math.dist(p,q)/n) for a,b in zip(z,z[1:]))
    out.append((round(grade*100,2),r["label"]))
print(sorted(out,reverse=True)[:15])
json.dump({"grades_percent":{label:grade for grade,label in out},"carriageway_max_percent":max(g for g,n in out if n.startswith("NET_MainRoad")),"grandpa_drive_max_percent":max(g for g,n in out if n.startswith("NET_GrandpaDrive")),"old_bor_max_percent":max(g for g,n in out if n.startswith("NET_OldBorPath"))},open(T.ROOT+"/Review/TerrainV2/after/grades.json","w"),indent=2)
print("Street",[(y,round(T.height(y*.176,y)/100,2)) for y in [-20000,0,7000,10500,15000,25000,28500,40000]])
