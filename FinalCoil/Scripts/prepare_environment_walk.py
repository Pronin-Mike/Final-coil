"""Build a connected centreline route from the current plan, including junctions."""
from pathlib import Path
import json,math,heapq
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'SourceArt/CompactVillage/plan.json').read_text());roads=p['roads']+[r for r in p['walks'] if r['name']=='G01_Drive'];key=lambda p:(round(p[0],2),round(p[1],2));nodes={key(r[k]) for r in roads for k in ['p','q']}
for i,r in enumerate(roads):
 for z in roads[i+1:]:
  a,b,c,d=r['p'],r['q'],z['p'],z['q'];rx,ry=b[0]-a[0],b[1]-a[1];sx,sy=d[0]-c[0],d[1]-c[1];den=rx*sy-ry*sx
  if abs(den)<.0001:continue
  t=((c[0]-a[0])*sy-(c[1]-a[1])*sx)/den;u=((c[0]-a[0])*ry-(c[1]-a[1])*rx)/den
  if 0<=t<=1 and 0<=u<=1:nodes.add(key((a[0]+t*rx,a[1]+t*ry)))
graph={n:[] for n in nodes}
for r in roads:
 a,b=r['p'],r['q'];dx,dy=b[0]-a[0],b[1]-a[1];ln=dx*dx+dy*dy;ons=[]
 for n in nodes:
  t=((n[0]-a[0])*dx+(n[1]-a[1])*dy)/ln
  if -.00001<=t<=1.00001 and math.hypot(n[0]-a[0]-t*dx,n[1]-a[1]-t*dy)<2:ons.append((t,n))
 ons.sort()
 for (_,u),(_,v) in zip(ons,ons[1:]):graph[u].append((math.dist(u,v),v));graph[v].append((math.dist(u,v),u))
# Authored junction centreline endpoints can differ by under 2 m inside the
# overlapping road widths. Connect those short, physically continuous joins.
for u in nodes:
 for v in nodes:
  if u<v and math.dist(u,v)<200:graph[u].append((math.dist(u,v),v));graph[v].append((math.dist(u,v),u))
a=min(nodes,key=lambda n:math.dist(n,p['stop']));b=key([r for r in p['walks'] if r['name']=='G01_Drive'][-1]['q']);queue=[(0,a)];dist={a:0};prev={}
while queue:
 d,u=heapq.heappop(queue)
 if u==b:break
 if d>dist[u]:continue
 for w,v in graph[u]:
  nd=d+w
  if nd<dist.get(v,1e20):dist[v]=nd;prev[v]=u;heapq.heappush(queue,(nd,v))
assert b in dist,('Disconnected road graph',a,b,min((math.dist(u,v),u,v) for u in dist for v in nodes if v not in dist))
path=[b]
while path[-1]!=a:path.append(prev[path[-1]])
path.reverse();h=json.loads((ROOT/'SourceArt/G01HouseV2/house_spec.json').read_text());cx,cy=h['house_center'];c,s=math.cos(math.radians(h['yaw'])),math.sin(math.radians(h['yaw']));path+=[(cx+c*x-s*770,cy+s*x+c*770) for x in [500,450,310]];route=path+list(reversed(path[:-1]));(ROOT/'Review/EnvironmentZones/walk_route.json').write_text(json.dumps(dict(name='stop to G01 garage and return',length_m=sum(math.dist(a,b) for a,b in zip(route,route[1:]))/100,points=route),indent=2))
template=(ROOT/'Scripts/check_g01_fence_play.py').read_text();a=template.index('R=');b=template.index('state=dict(')
header="""from pathlib import Path
R=str(Path(__file__).resolve().parents[1]);Q=R+'/Review/EnvironmentZones';spec={'yaw':0}
import sys
sys.path.insert(0,R+'/Scripts');import terrain_profile as T
g=0
route=[(x,y,0) for x,y in json.load(open(Q+'/walk_route.json'))['points']]
def point(x,y,z):return unreal.Vector(x,y,z)
spawn=point(*route[0]);spawn.z=T.height(spawn.x,spawn.y)
"""
template=template[:a]+header+template[b:];template=template.replace('Standalone PIE walk through both rooms and shower tray; closes its own editor.','Standalone PIE walk: stop approach to G01 garage and back; closes its owned editor.').replace('move.max_walk_speed=140','move.max_walk_speed=400').replace('if distance<12:','if distance<32:').replace("state['walking_started']>150","state['walking_started']>600");(ROOT/'Scripts/check_environment_routes_play.py').write_text(template)
print('Route metres:',round(sum(math.dist(a,b) for a,b in zip(route,route[1:]))/100,1),'waypoints:',len(route))
