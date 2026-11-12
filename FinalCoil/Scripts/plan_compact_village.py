import math,json,os,sys,random
R='D:/GameDevelop/FinalCoil';D=R+'/SourceArt/CompactVillage';os.makedirs(D,exist_ok=True)
S=14000/267
def world(p):return [(450-p[1])*S,(p[0]-707)*S]
def pixel(p):return [p[1]/S+707,450-p[0]/S]
mainpx=[[0,485],[120,468],[280,457],[450,453],[575,452],[707,450],[800,437],[910,413],[1000,395],[1150,360],[1300,328],[1429,295],[1650,241]]
northpx=[[573,450],[572,414],[560,354],[545,316],[518,278],[474,246],[425,236],[368,233],[315,219],[275,187],[248,136],[229,70],[212,0]]
looppx=[[425,236],[480,235],[535,235],[590,230],[648,223],[710,211],[772,194],[820,164],[853,137],[873,101],[878,78]]
southpx=[[909,414],[918,466],[939,502],[975,528],[1020,538],[1080,555],[1150,567]]
roads=[]
for name,px,width in [('Main',mainpx,500),('NorthWest',northpx,350),('NorthLoop',looppx,350),('SouthEast',southpx,350)]:
 pts=[world(p) for p in px]
 if name=='Main':
  pts=[[x-1000*math.exp(-(y/3300)**2),y] for x,y in pts]
 for i,(a,b) in enumerate(zip(pts,pts[1:])):roads.append(dict(name=name,p=a,q=b,width=width))
green=[('H01',598,502),('H02',857,473),('H03',993,586),('H04',410,407),('H05',512,363),('H06',517,188),('H07',585,278),('H08',648,184),('H09',703,250),('H10',750,142),('H11',794,390),('H12',866,376),('H13',982,363),('H14',625,381)]
blue=[('E01',416,502),('E02',417,190),('E03',825,90),('E04',486,314),('E05',817,235),('E06',886,165),('E07',927,546),('E08',510,505),('E09',1053,505),('E10',1125,527),('E11',1067,610)]
def nearest(p,rs=roads):
 best=None
 for r in rs:
  a,b=r['p'],r['q'];dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));q=(a[0]+t*dx,a[1]+t*dy);d=math.dist(p,q)
  if best is None or d-r['width']/2<best[0]:best=(d-r['width']/2,q,r)
 return best
def rect(cx,cy,hx,hy,yaw):
 c,s=math.cos(yaw),math.sin(yaw)
 return [(cx+c*x-s*y,cy+s*x+c*y) for x,y in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]]
def overlaps(a,b,margin=0):
 for poly in [a,b]:
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dx,dy=q[0]-p[0],q[1]-p[1];mag=math.hypot(dx,dy);ax,ay=-dy/mag,dx/mag
   aa=[x*ax+y*ay for x,y in a];bb=[x*ax+y*ay for x,y in b]
   if max(aa)+margin<=min(bb) or max(bb)+margin<=min(aa):return False
 return True
def point_segment(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def setback(poly):
 best=1e20
 for r in roads:
  a,b=r['p'],r['q'];dx,dy=b[0]-a[0],b[1]-a[1];ln=math.hypot(dx,dy);w=r['width']/2+150
  strip=[(a[0]-dy/ln*w,a[1]+dx/ln*w),(b[0]-dy/ln*w,b[1]+dx/ln*w),(b[0]+dy/ln*w,b[1]-dx/ln*w),(a[0]+dy/ln*w,a[1]-dx/ln*w)]
  if overlaps(poly,strip):return -1
  for p,q in zip(poly,poly[1:]+poly[:1]):
   best=min(best,point_segment(p,a,b)-r['width']/2,point_segment(a,p,q)-r['width']/2,point_segment(b,p,q)-r['width']/2)
 return best
houses=[]
for ident,x,y in green+blue:
 p=world((x,y));d,q,r=nearest(p);yaw=math.atan2(q[1]-p[1],q[0]-p[0])
 houses.append(dict(id=ident,source_px=[x,y],house=p,yaw=yaw,road=r['name']))
# Hero's house retains the exact metric anchor. Separate garage stays in its plot.
hero=world((974,450));d,q,r=nearest(hero);hyaw=math.atan2(q[1]-hero[1],q[0]-hero[0]);c,s=math.cos(hyaw),math.sin(hyaw)
heroCenter=[hero[0]-650*c-835*s,hero[1]-650*s+835*c]
hp=dict(id='G01',source_px=[974,450],house=hero,yaw=hyaw,road=r['name'],center=heroCenter,hx=1600,hy=1562.5)
hp['corners']=rect(*heroCenter,1600,1562.5,hyaw)
assert setback(hp['corners'])>100
assigned=[hp];failed=[]
# Place constrained street-front plots first, retaining every house position.
for h in sorted(houses,key=lambda h:nearest(h['house'])[0]):
 px,py=h['house'];base=h['yaw'];c,s=math.cos(base),math.sin(base);candidates=[]
 for hx,hy in [(2000,1250),(1600,1562.5),(1250,2000),(2500,1000)]:
  for da in [0,-.12,.12,-.25,.25]:
   yaw=base+da
   for back in [0,250,500,750,1000,1250,1500,-250,-500]:
    for lateral in [0,-250,250,-500,500,-750,750]:
     cx,cy=px-c*back-s*lateral,py-s*back+c*lateral;poly=rect(cx,cy,hx,hy,yaw)
     if any(overlaps(poly,a['corners'],100) for a in assigned):continue
     # Ensure the house and its porch fit in the proposed plot.
     cc,ss=math.cos(yaw),math.sin(yaw);dx,dy=px-cx,py-cy
     if abs(dx*cc+dy*ss)+850>hx or abs(-dx*ss+dy*cc)+480>hy:continue
     gap=setback(poly)
     if gap<200:continue
     score=abs(back)*.7+abs(lateral)*1.2+abs(da)*1600+abs(gap-450)*.18+(0 if hx==2000 else 180)
     candidates.append((score,cx,cy,hx,hy,yaw,poly,gap))
 if not candidates:failed.append(h['id']);continue
 _,cx,cy,hx,hy,yaw,poly,gap=min(candidates,key=lambda a:a[0]);h.update(center=[cx,cy],hx=hx,hy=hy,yaw=yaw,corners=poly,setback_m=gap/100);assigned.append(h)
if failed:raise RuntimeError('Plot placement failed '+str(failed))
for h in assigned:
 h['setback_m']=setback(h['corners'])/100;h['area_m2']=4*h['hx']*h['hy']/10000
 assert abs(h['area_m2']-1000)<.001
assert len(assigned)==26
shop=world((692,493));stop=[0,0]
plan=dict(scale_cm_per_px=S,stop=stop,hero=hero,hero_distance_m=math.dist(stop,hero)/100,counts=dict(occupied=14,vacant=11,hero=1),roads=roads,plots=assigned,shop=shop,erase_bounds=[-15000,-52000,26000,63000])
# Join the scaled village to the unchanged regional roads at the edit boundary.
old=json.load(open(R+'/SourceArt/Terrain/manifest.json'))['routes']
for yy,endpoint in [(-52000,roads[0]['p']),(63000,next(r for r in reversed(roads) if r['name']=='Main')['q'])]:
 r=next(r for r in old if r['label'].startswith('NET_MainRoad') and min(r['p'][1],r['q'][1])<=yy<=max(r['p'][1],r['q'][1]))
 t=(yy-r['p'][1])/(r['q'][1]-r['p'][1]);p=[r['p'][0]+t*(r['q'][0]-r['p'][0]),yy]
 roads.append(dict(name='MainConnector',p=p,q=endpoint,width=500))
# A continuous link from the north-west lane to the existing Bor trail.
roads.append(dict(name='BorLink',p=world((212,0)),q=[26000,-29000],width=220))
json.dump(plan,open(D+'/plan.json','w'),indent=2)
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="180 20 1050 660"><rect x="180" y="20" width="1050" height="660" fill="#232c23"/>']
for r in roads:
 a,b=pixel(r['p']),pixel(r['q']);svg.append('<path d="M%f,%f L%f,%f" stroke="#ba6660" stroke-width="%f"/>'%(*a,*b,r['width']/S))
for h in assigned:
 poly=' '.join('%f,%f'%tuple(pixel(p)) for p in h['corners']);p=pixel(h['house']);color='white' if h['id']=='G01' else '#20b244' if h['id'].startswith('H') else '#176aff'
 svg.append('<polygon points="%s" fill="none" stroke="#eadb59" stroke-width="1"/><circle cx="%f" cy="%f" r="8" fill="%s"/><text x="%f" y="%f" fill="white" font-size="10">%s %.1fm</text>'%(poly,*p,color,p[0]-10,p[1]-12,h['id'],h['setback_m']))
svg.append('<circle cx="707" cy="450" r="7" fill="white"/></svg>');open(D+'/layout.svg','w').write(''.join(svg))
print(json.dumps(dict(plots=len(assigned),occupied=14,vacant=11,anchor_m=plan['hero_distance_m'],setbacks_m={h['id']:round(h['setback_m'],1) for h in assigned})))
