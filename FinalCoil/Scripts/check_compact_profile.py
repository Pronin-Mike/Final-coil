import sys,json,math
R='D:/GameDevelop/FinalCoil';sys.path.insert(0,R+'/Scripts');import terrain_profile as T
P=json.load(open(R+'/SourceArt/CompactVillage/plan.json'));T.GRID=json.load(open(R+'/SourceArt/CompactVillage/heightfield.json'))
grades={};worst=[]
for r in P['roads']+P['walks']:
 a,b=r['p'],r['q'];n=math.ceil(math.dist(a,b)/100);last=None
 for i in range(n+1):
  x,y=a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n;z=T.height(x,y)
  if last:
   grade=abs(z-last[2])/math.hypot(x-last[0],y-last[1]);grades[r['name']]=max(grades.get(r['name'],0),grade)
   if grade>.18:worst.append([r['name'],x,y,grade])
  last=(x,y,z)
out=dict(max_grades_percent={k:round(v*100,2) for k,v in grades.items()},steep_samples=worst)
old=json.load(open(R+'/Saved/Backups/BeforeCompactVillage/heightfield.json'));B=P['erase_bounds'];outside=changed=0
for i,x in enumerate(T.XS):
 for j,y in enumerate(T.YS):
  delta=abs(old[i][j]-T.GRID[i][j])
  if not B[0]<x<B[2] or not B[1]<y<B[3]:assert delta==0;outside+=1
  if delta>1e-6:changed+=1
out.update(outside_vertices_unchanged=outside,changed_vertices=changed)
json.dump(out,open(R+'/Review/CompactVillage/profile_checks.json','w'),indent=2);print(json.dumps(out))
