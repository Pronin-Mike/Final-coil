import sys,os,json,math
sys.path.insert(0,os.path.dirname(__file__))
import terrain_profile as T
D=T.ROOT+"/SourceArt/Terrain"
if T.GRID is None:T.height(0,0)
zones=[]
for a in T.INV:
    if a["label"].startswith(("Forest_Mass_","OldBor_Mass_")):
        zones.append((a["label"].startswith("OldBor"),*a["p"][:2],a["s"][0]*50,a["s"][1]*50))
out={True:([],[],{}),False:([],[],{})}
for i in range(T.NX):
    x=(T.XS[i]+T.XS[i+1])*.5
    for j in range(T.NY):
        y=(T.YS[j]+T.YS[j+1])*.5
        inside=[old for old,cx,cy,rx,ry in zones if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1]
        if not inside:continue
        vs,fs,index=out[any(inside)]
        local=[]
        for ii,jj in [(i,j),(i+1,j),(i,j+1),(i+1,j+1)]:
            key=(ii,jj)
            if key not in index:
                index[key]=len(vs);vs.append((T.XS[ii],T.YS[jj],T.GRID[ii][jj]+1))
            local.append(index[key])
        a,b,c,d=local;fs.extend([(a,b,c),(b,d,c)])
for old,(vs,fs,index) in out.items():
    T.write_obj(D+("/SM_OldBor_Zone.obj" if old else "/SM_Forest_Zones.obj"),vs,fs)
pads=[]
for pad in T.PADS:
    name,x,y,hx,hy,c,s,z=pad
    values=[T.height(x+u*c-v*s,y+u*s+v*c) for u in [-hx,0,hx] for v in [-hy,0,hy]]
    pads.append({"name":name,"target_cm":z,"spread_cm":max(values)-min(values)})
print(sorted(pads,key=lambda p:p["spread_cm"],reverse=True)[:5])
json.dump({"flat_pad_count":len(pads),"pads":pads,"grid_vertices":(T.NX+1)*(T.NY+1),"grid_triangles":T.NX*T.NY*2,"footprint_km2":(T.XMAX-T.XMIN)*(T.YMAX-T.YMIN)/1e10,"source_repository":"Pronin-Mike/Final-coil","branch":"main","blob":"0725a80b4bc79229f12b16e2632c7ca528316cfe"},open(T.ROOT+"/Review/Terrain/profile_checks.json","w"),indent=2)
print("FOREST_ZONES_AND_PADS_OK",len(pads))


