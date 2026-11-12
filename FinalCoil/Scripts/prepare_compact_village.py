import os,sys,json,math,random,shutil
R='D:/GameDevelop/FinalCoil';sys.path.insert(0,R+'/Scripts');import terrain_profile as T
D=R+'/SourceArt/CompactVillage';P=json.load(open(D+'/plan.json'));B=P['erase_bounds'];C=[-11000,-17500,24000,26500]
P['plant_bounds']=C
original=R+'/Saved/Backups/BeforeCompactVillage/heightfield.json'
old=json.load(open(original if os.path.exists(original) else R+'/SourceArt/Terrain/heightfield.json'));T.GRID=old
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def base(x,y):return (T.height(x,y)*4+T.height(x+1200,y)+T.height(x-1200,y)+T.height(x,y+1200)+T.height(x,y-1200))/8
zones=[(*a['p'][:2],a['s'][0]*50,a['s'][1]*50) for a in T.INV if a['label'].startswith(('Forest_Mass_','OldBor_Mass_'))]
def forest(x,y,pad=0):return any(((x-cx)/(rx+pad))**2+((y-cy)/(ry+pad))**2<1 for cx,cy,rx,ry in zones)
def near(x,y,rs=None):
 best=None
 for r in rs or P['roads']:
  a,b=r['p'],r['q'];dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));q=(a[0]+t*dx,a[1]+t*dy);d=math.hypot(x-q[0],y-q[1])-r['width']/2
  if best is None or d<best[0]:best=(d,q,r)
 return best
# A connected road-height graph limits long grades before terrain is fitted to it.
nodes=[];edges=[]
for r in P['roads']:
 ids=[]
 for p in [r['p'],r['q']]:
  found=next((i for i,n in enumerate(nodes) if math.dist(p,n[:2])<300),None)
  if found is None:
   z=sum(T.height(p[0]+dx,p[1]+dy) for dx in [-2500,0,2500] for dy in [-2500,0,2500])/9;found=len(nodes);nodes.append([*p,z])
  ids.append(found)
 edges.append((r,*ids,math.dist(r['p'],r['q'])))
for iteration in range(80):
 for r,a,b,ln in edges:
  delta=nodes[b][2]-nodes[a][2];limit=ln*.055
  if abs(delta)>limit:
   excess=(abs(delta)-limit)/2;direction=1 if delta>0 else -1;nodes[a][2]+=direction*excess;nodes[b][2]-=direction*excess
for r,a,b,ln in edges:r['z0'],r['z1']=nodes[a][2],nodes[b][2]
def roadheight(q,r):
 if r['name']=='BorLink':return base(*q)
 a,b=r['p'],r['q'];dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/(dx*dx+dy*dy)));return r['z0']+(r['z1']-r['z0'])*t
for h in P['plots']:
 _,q,r=near(*h['center']);z=roadheight(q,r);h['z']=z+max(-65,min(65,base(*h['center'])-z));h['c'],h['s']=math.cos(h['yaw']),math.sin(h['yaw'])
P['service_pads']=[]
for name,xy,hx,hy in [('STOP01',[0,0],450,650),('SHOP01',P['shop'],800,750)]:
 _,q,r=near(*xy);P.setdefault('service_pads',[]).append(dict(id=name,center=xy,hx=hx,hy=hy,c=1,s=0,z=roadheight(q,r)))
pads=P['plots']+P['service_pads'];grid=[row[:] for row in old];changed=0
for i,x in enumerate(T.XS):
 if not B[0]<x<B[2]:continue
 for j,y in enumerate(T.YS):
  if not B[1]<y<B[3] or forest(x,y,500):continue
  edge=min(x-B[0],B[2]-x,y-B[1],B[3]-y);wreg=smooth(0,2000,edge)
  forestDistance=min((math.hypot((x-cx)/rx,(y-cy)/ry)-1)*min(rx,ry) for cx,cy,rx,ry in zones)
  wreg*=smooth(500,3500,forestDistance)
  z=base(x,y);roadDist,q,r=near(x,y);rw=1-smooth(10,750,roadDist)
  rz=roadheight(q,r);z=z*(1-rw)+rz*rw
  best=0;target=z
  for h in pads:
   dx,dy=x-h['center'][0],y-h['center'][1];ex=max(0,abs(dx*h['c']+dy*h['s'])-h['hx']-80);ey=max(0,abs(-dx*h['s']+dy*h['c'])-h['hy']-80);dd=math.hypot(ex,ey);w=1-smooth(0,650,dd)
   if w>best:best=w;target=h['z']
  z=z*(1-best)+target*best
  # Road profile takes priority at the carriageway; pads retain their flat interiors.
  z=z*(1-rw)+rz*rw;grid[i][j]=old[i][j]*(1-wreg)+z*wreg;changed+=1
json.dump(grid,open(D+'/heightfield.json','w'));T.GRID=grid
vs,fs=T.grid_mesh();T.write_obj(D+'/SM_CompactTerrain.obj',vs,fs)
def height(x,y):return T.height(x,y)
P['walks']=[]
for h in P['plots']:
 if h['id']=='G01':continue
 x,y=h['house'];c,s=math.cos(h['yaw']),math.sin(h['yaw']);porch=[x+c*820,y+s*820];_,q,r=near(*porch)
 ln=math.dist(porch,q);dx,dy=(porch[0]-q[0])/ln,(porch[1]-q[1])/ln;edge=[q[0]+dx*(r['width']/2+15),q[1]+dy*(r['width']/2+15)]
 P['walks'].append(dict(name=h['id']+'_Walk',p=edge,q=porch,width=160))
hero=next(h for h in P['plots'] if h['id']=='G01');hx,hy=hero['house'];cc,ss=math.cos(hero['yaw']),math.sin(hero['yaw'])
def hero_local(x,y):return [hx+cc*x-ss*y,hy+ss*x+cc*y]
garage_gate=hero_local(-800,1700);d,q,r=near(*garage_gate);ln=math.dist(q,garage_gate);nx,ny=(garage_gate[0]-q[0])/ln,(garage_gate[1]-q[1])/ln
P['walks'].append(dict(name='G01_Drive',p=[q[0]+nx*r['width']/2,q[1]+ny*r['width']/2],q=garage_gate,width=320))
P['walks'].append(dict(name='G01_HouseWalk',p=garage_gate,q=hero_local(820,0),width=160))
P['walks'].append(dict(name='SHOP01_Walk',p=P['shop'],q=[-1000,0],width=220))
# Clip former road/path overlays completely out of the authored village rectangle.
def clip(poly,axis,value,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=value if greater else a[axis]<=value;ib=b[axis]>=value if greater else b[axis]<=value
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(5)))
 return out
for kind in ['Road','Path']:
 vs=[];uv=[];faces=[]
 for line in open(R+'/SourceArt/Terrain/SM_Conform_'+kind+'.obj'):
  v=line.split()
  if not v:continue
  if v[0]=='v':vs.append(tuple(map(float,v[1:4])))
  elif v[0]=='vt':uv.append(tuple(map(float,v[1:3])))
  elif v[0]=='f':faces.append([tuple(int(i)-1 for i in p.split('/')[:2]) for p in v[1:]])
 outv=[];outf=[]
 def emit(poly):
  k=len(outv);outv.extend(poly)
  for j in range(1,len(poly)-1):outf.append((k,k+j,k+j+1))
 for face in faces:
  poly=[(*vs[v],*uv[u]) for v,u in face]
  if all(forest(p[0],p[1],-500) for p in poly):emit(poly);continue
  for axis,value,greater in [(0,B[0],True),(0,B[2],False),(1,B[1],True),(1,B[3],False)]:
   outside=clip(poly,axis,value,not greater)
   if len(outside)>2:emit(outside)
   poly=clip(poly,axis,value,greater)
   if not poly:break
 T.write_obj(D+'/SM_Regional'+kind+'.obj',[(p[0],p[1],p[2]) for p in outv],outf)
# Shader functions are evaluated only in the village. All remote surfaces remain unchanged.
def roadfn(name,rs):
 code='float4 '+name+'(float2 p){float best=1e9,d=1e9,w=0,k=0,v;'
 for r in rs:
  half=r['width']/2;code+='v=segment(p,float2(%.5f,%.5f),float2(%.5f,%.5f));if(v-%.3f<best){best=v-%.3f;d=v;w=%.3f;k=%.1f;}'%(*r['p'],*r['q'],half,half,half,1 if r['name'].startswith('Main') else 0)
 return code+'return float4(d,w,k,0);}\n'
functions=roadfn('compactRoad',P['roads'])+roadfn('compactWalk',P['walks'])
functions+='float compactYard(float2 p){float w=0;float2 d;float v;'
for h in P['plots']:
 functions+='d=p-float2(%.5f,%.5f);v=max(abs(dot(d,float2(%.8f,%.8f)))-%.3f,abs(dot(d,float2(%.8f,%.8f)))-%.3f);w=max(w,1-smoothstep(-20,90,v));'%(*h['center'],h['c'],h['s'],h['hx'],-h['s'],h['c'],h['hy'])
functions+='return w;}\n';open(D+'/Functions.hlsl','w').write(functions)
snippet='''float4 rd=g.compactRoad(P.xy);float dist=rd.x,width=rd.y;
float stopLong=1-smoothstep(600,1800,abs(P.y));float stopSide=smoothstep(-1030,-920,P.x);width+=300*stopLong*stopSide;
float irregular=clamp((g.fbm(P.xy/330+warp*1.8)-.5)*90,-25,25);
float shoulder=1-smoothstep(width,width+75+irregular,dist);
float greens=saturate(.67+.35*macro+.2*wet-dry*.3)*smoothstep(.21,.42,patch+.15*macro);
float3 field=lerp(soil*.95,grassCol*1.05,greens);
float3 usedSoil=soil*lerp(.88,1.04,patch);float lane=1-smoothstep(28,64,abs(dist-105));float marks=lane*(.24+.76*wet)*smoothstep(.28,.62,g.fbm(P.xy/820+17));
usedSoil*=1-marks*lerp(.045,.22,wet);usedSoil+=lane*(1-wet)*.012;
float center=(1-smoothstep(35,72,dist))*smoothstep(.36,.68,macro+.15*small)*(.14+.24*wet);usedSoil=lerp(usedSoil,grassCol*.92,center);
float edge=exp(-pow((dist-width-28)/38,2));float chips=smoothstep(.83,.95,g.noise(P.xy/3.7))*edge*microFade;usedSoil=lerp(usedSoil,float3(.20,.185,.145),chips*.33);
float3 nc=lerp(field,usedSoil,shoulder);float4 walk=g.compactWalk(P.xy);float walkMask=1-smoothstep(walk.y-15,walk.y+60,walk.x);
float yard=g.compactYard(P.xy);nc=lerp(nc,lerp(field,soil*.95,.35),yard*.5);nc=lerp(nc,soil*.90,walkMask);
float wait=(1-smoothstep(0,30,max(-350-P.x,P.x-350)))*(1-smoothstep(420,460,abs(P.y)));
float access=(1-smoothstep(80,120,abs(P.y)))*(1-smoothstep(0,25,max(-550-P.x,P.x+250)));
float shop=(1-smoothstep(0,60,max(abs(P.x-SHOPX)-700,abs(P.y-SHOPY)-650)));
float gravel=max(shop,max(wait,access));nc=lerp(nc,float3(.24,.22,.17)*(.86+.28*g.noise(P.xy/3.2)),gravel);
float boundary=smoothstep(0,1200,P.x-ERASEX0)*smoothstep(0,1200,ERASEX1-P.x)*smoothstep(0,1200,P.y-ERASEY0)*smoothstep(0,1200,ERASEY1-P.y);
float protect=1-smoothstep(.08,.4,Biome.r);float region=boundary*protect;
color=lerp(color,nc,region);Roughness=lerp(Roughness,lerp(.94,.76,max(shoulder,gravel)),region);AO=lerp(AO,.96,region);
'''
for k,v in dict(SHOPX=P['shop'][0],SHOPY=P['shop'][1],ERASEX0=B[0],ERASEX1=B[2],ERASEY0=B[1],ERASEY1=B[3]).items():snippet=snippet.replace(k,'('+str(v)+')')
open(D+'/Surface.hlsl','w').write(snippet)
# Low cover plus irregular taller groups; no vegetation roots in the new plots or roads.
rng=random.Random(12112026);plants=[[],[],[],[]];minx,miny,maxx,maxy=C
def inplot(x,y,margin=120):
 for h in pads:
  dx,dy=x-h['center'][0],y-h['center'][1]
  if abs(dx*h['c']+dy*h['s'])<h['hx']+margin and abs(-dx*h['s']+dy*h['c'])<h['hy']+margin:return True
 return False
def blocked(x,y):
 if forest(x,y,500) or inplot(x,y):return True
 d,q,r=near(x,y)
 if d<95:return True
 if -350<x<350 and abs(y)<500:return True
 return any(near(x,y,[r])[0]<70 for r in P['walks'])
for ix in range(math.ceil((maxx-minx)/110)):
 for iy in range(math.ceil((maxy-miny)/110)):
  x=minx+(ix+rng.random())*110;y=miny+(iy+rng.random())*110
  if blocked(x,y):continue
  patch=.5+.25*math.sin(x/1700+math.sin(y/1100))+.2*math.sin(y/2300+x/3400)
  if rng.random()>.65*patch+.28:continue
  dry=rng.random()<.13;plants[int(dry)].append([x,y,height(x,y)-1,rng.random()*360,rng.uniform(1.1,2.0),rng.uniform(.18,.4)])
for _ in range(55):
 x=rng.uniform(minx+1000,maxx-1000);y=rng.uniform(miny+1000,maxy-1000)
 if blocked(x,y) or near(x,y)[0]<400:continue
 for j in range(rng.randint(10,45)):
  xx=x+rng.gauss(0,250);yy=y+rng.gauss(0,250)
  if not (minx<xx<maxx and miny<yy<maxy) or blocked(xx,yy):continue
  dry=rng.random()<.22;plants[2+int(dry)].append([xx,yy,height(xx,yy)-1,rng.random()*360,rng.uniform(.65,1.25),rng.uniform(.45,1.05)])
json.dump(plants,open(D+'/plants.json','w'));P['terrain_vertices_changed']=changed;P['plant_counts']=list(map(len,plants));json.dump(P,open(D+'/plan.json','w'),indent=2)
print(json.dumps(dict(vertices_changed=changed,plants=P['plant_counts'],anchor_m=140)))
