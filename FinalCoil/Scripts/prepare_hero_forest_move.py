"""Prepare a local terrain pad, lane extension and coarse forest around G01."""
import json,math,sys,os,shutil,random
R='D:/GameDevelop/FinalCoil';S=R+'/SourceArt/HeroForestMove';B=R+'/../.publishing/hero-forest-before';os.makedirs(B,exist_ok=True);os.makedirs(S,exist_ok=True)
sys.path.insert(0,R+'/Scripts');import terrain_profile as T
for f in ['plan.json','heightfield.json','Functions.hlsl']:
 if not os.path.exists(B+'/'+f):shutil.copy2(R+'/SourceArt/CompactVillage/'+f,B+'/'+f)
P=json.load(open(B+'/plan.json'));old=json.load(open(B+'/heightfield.json'));T.GRID=old
h=next(x for x in P['plots'] if x['id']=='G01');prior=json.loads(json.dumps(h));new_center=[-8400.,26700.];delta=[new_center[i]-h['center'][i] for i in [0,1]]
for k in ['house','center']:h[k]=[h[k][i]+delta[i] for i in [0,1]]
h['corners']=[[p[i]+delta[i] for i in [0,1]] for p in h['corners']]
h['z']=T.height(*new_center);P['hero']=h['house'];P['original_scale_calibration_m']=140.;P['hero_distance_m']=math.dist(P['stop'],h['house'])/100
P['hero_relocation']=dict(source='User annotated map 2026-11-13, rectangle beyond E10/E11',previous_house=prior['house'],previous_center=prior['center'],center=new_center,translation_cm=delta,preserved_area_m2=1000)
P['walks']=[w for w in P['walks'] if not w['name'].startswith('G01_')]
c,s=math.cos(h['yaw']),math.sin(h['yaw'])
def local(x,y):return [h['house'][0]+c*x-s*y,h['house'][1]+s*x+c*y]
gate=local(-800,1700);porch=local(820,0)
tail=next(r['q'] for r in reversed(P['roads']) if r['name']=='SouthEast')
# Two gentle bends align the final approach with the existing garage opening.
drive=[tail,[-6500.,24500.],[-7000.,26700.],local(100,1700),gate]
drivez=[T.height(*tail),h['z']+80,h['z']+25,h['z'],h['z']]
for i,(p,q) in enumerate(zip(drive,drive[1:])):
 P['walks'].append(dict(name='G01_Drive',p=p,q=q,width=350,z0=drivez[i],z1=drivez[i+1]))
P['walks'].append(dict(name='G01_HouseWalk',p=gate,q=porch,width=160))
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def projection(x,y,p,q):
 dx,dy=q[0]-p[0],q[1]-p[1];t=max(0,min(1,((x-p[0])*dx+(y-p[1])*dy)/(dx*dx+dy*dy)));return math.hypot(x-p[0]-t*dx,y-p[1]-t*dy),t
def plot_distance(x,y,p):
 dx,dy=x-p['center'][0],y-p['center'][1];c,s=p['c'],p['s'];return math.hypot(max(0,abs(c*dx+s*dy)-p['hx']),max(0,abs(-s*dx+c*dy)-p['hy']))
grid=[row[:] for row in old];changed=0
for i,x in enumerate(T.XS):
 if not -13500<x<-4200:continue
 for j,y in enumerate(T.YS):
  if not 22500<y<31500:continue
  # Leave neighbours and their ground pads intact.
  if any(p['id']!='G01' and plot_distance(x,y,p)<200 for p in P['plots']):continue
  base=old[i][j];w=1-smooth(60,1000,plot_distance(x,y,h));value=base*(1-w)+h['z']*w
  nearest=None
  for r in P['walks']:
   if r['name']!='G01_Drive':continue
   d,t=projection(x,y,r['p'],r['q'])
   if nearest is None or d<nearest[0]:nearest=(d,t,r)
  d,t,r=nearest;weight=1-smooth(r['width']/2+120,r['width']/2+800,d);rz=r['z0']+(r['z1']-r['z0'])*t
  value=value*(1-weight)+rz*weight
  if abs(base-value)>1e-7:grid[i][j]=value;changed+=1
T.GRID=grid;json.dump(grid,open(S+'/heightfield.json','w'))
v,f=T.grid_mesh();T.write_obj(S+'/SM_HeroForestTerrain.obj',v,f)
def roadfn(name,rs):
 code='float4 '+name+'(float2 p){float best=1e9,d=1e9,w=0,k=0,v;'
 for r in rs:
  half=r['width']/2;code+='v=segment(p,float2(%.5f,%.5f),float2(%.5f,%.5f));if(v-%.3f<best){best=v-%.3f;d=v;w=%.3f;k=%.1f;}'%(*r['p'],*r['q'],half,half,half,1 if r['name'].startswith('Main') else 0)
 return code+'return float4(d,w,k,0);}\n'
functions=roadfn('compactRoad',P['roads'])+roadfn('compactWalk',P['walks'])+'float compactYard(float2 p){float w=0;float2 d;float v;'
for p in P['plots']:functions+='d=p-float2(%.5f,%.5f);v=max(abs(dot(d,float2(%.8f,%.8f)))-%.3f,abs(dot(d,float2(%.8f,%.8f)))-%.3f);w=max(w,1-smoothstep(-20,90,v));'%(*p['center'],p['c'],p['s'],p['hx'],-p['s'],p['c'],p['hy'])
functions+='return w;}\n';open(S+'/Functions.hlsl','w').write(functions);json.dump(P,open(S+'/plan.json','w'),indent=2)
# Low polygon tree meshes, centimetres. Symmetric axes are safe under OBJ conversion.
def tree(name,pine):
 verts=[];faces=[];groups=[]
 def cone(cx,cy,z,r,height,top=0,mat='Crown',n=8):
  k=len(verts)
  for zz,rr in [(z,r),(z+height,top)]:
   for i in range(n):a=i*math.tau/n;verts.append((cx+rr*math.cos(a),cy+rr*math.sin(a),zz))
  for i in range(n):faces.extend([(k+i,k+(i+1)%n,k+n+i),(k+(i+1)%n,k+n+(i+1)%n,k+n+i)]);groups.extend([mat,mat])
  for i in range(1,n-1):faces.append((k,k+i+1,k+i));groups.append(mat)
 cone(0,0,0,16,900,10,'Bark')
 if pine:
  for z,r,height in [(180,215,460),(430,165,430),(650,115,370)]:cone(0,0,z,r,height)
 else:
  for cx,cy,z,r in [(-65,0,400,200),(65,10,420,205),(0,0,620,150)]:
   cone(cx,cy,z,r,210,85);cone(cx,cy,z-110,75,110,r)
 T.write_obj(S+'/'+name+'.obj',verts,faces,groups)
tree('SM_ForestPine_Blockout',True);tree('SM_ForestLeaf_Blockout',False)
rng=random.Random(13112026);trees=[]
for attempt in range(5000):
 x,y=rng.uniform(-22000,-4300),rng.uniform(22000,40500)
 # Forest crescent on the far/right and lower sides in the annotated map.
 mask=(((x+12800)/8500)**2+((y-33200)/8500)**2<1) or (((x+17500)/4500)**2+((y-26000)/6500)**2<1)
 if not mask or plot_distance(x,y,h)<850:continue
 if any(plot_distance(x,y,p)<500 for p in P['plots'] if p['id']!='G01'):continue
 if any(projection(x,y,r['p'],r['q'])[0]<r['width']/2+550 for r in P['roads']+P['walks']):continue
 if any(math.hypot(x-t[0],y-t[1])<680 for t in trees):continue
 trees.append([x,y,T.height(x,y),rng.uniform(0,360),rng.uniform(.8,1.4),rng.uniform(.8,1.55),0 if rng.random()<.65 else 1])
 if len(trees)>=175:break
json.dump(trees,open(S+'/trees.json','w'))
grades=[]
for r in P['walks']:
 if r['name']!='G01_Drive':continue
 last=None
 for i in range(101):
  x=r['p'][0]+(r['q'][0]-r['p'][0])*i/100;y=r['p'][1]+(r['q'][1]-r['p'][1])*i/100;z=T.height(x,y)
  if last:grades.append(abs(z-last[2])/math.hypot(x-last[0],y-last[1]))
  last=x,y,z
assert max(grades)<.16,('Drive slope',max(grades))
out=dict(delta_cm=delta,old_plot=prior,new_plot=h,drive=drive,tree_count=len(trees),changed_terrain_vertices=changed,max_drive_grade_percent=max(grades)*100)
json.dump(out,open(S+'/prepared.json','w'),indent=2);print(json.dumps({k:v for k,v in out.items() if k not in ['old_plot','new_plot']}))
