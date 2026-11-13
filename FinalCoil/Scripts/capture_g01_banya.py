"""Capture banya exterior, both rooms and the requested site corner."""
import json,math,base64,urllib.request,os
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/G01Banya';URL=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp');sid=None
def req(method,params):
 global sid
 h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:h['Mcp-Session-Id']=sid
 with urllib.request.urlopen(urllib.request.Request(URL,json.dumps(dict(jsonrpc='2.0',id=1,method=method,params=params)).encode(),h),timeout=180) as r:sid=r.headers.get('Mcp-Session-Id',sid);v=json.load(r)
 assert not v.get('error') and not v.get('result',{}).get('isError'),str(v)[:400]
 return v
def call(name,args):return json.loads(req('tools/call',dict(name='call_tool',arguments=dict(toolset_name='EditorToolset.EditorAppToolset',tool_name=name,arguments=args)))['result']['content'][0]['text'])['returnValue']
req('initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='BanyaReview',version='1')))
spec=json.load(open(R+'/SourceArt/G01Banya/bath_spec.json'));cx,cy=spec['center'];a=math.radians(spec['yaw']);c,s=math.cos(a),math.sin(a);g=spec['ground_z']
def w(p):return [cx+c*p[0]-s*p[1],cy+s*p[0]+c*p[1],g+p[2]]
views=[('exterior',[-1000,1100,700],[0,0,150]),('steam_room',[40,-140,195],[200,70,110]),('shower_room',[-250,-25,195],[-220,190,130])]
for name,p,t in views:
 x,y,z=w(p);xx,yy,zz=w(t);cam=dict(location=dict(x=x,y=y,z=z),rotation=dict(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=dict(x=1,y=1,z=1));v=call('CaptureViewport',dict(captureTransform=cam,annotations=None,bShowUI=False));open(Q+'/'+name+'.png','wb').write(base64.b64decode(v['image']['data']))
 if name=='exterior':preferred=cam
p=json.load(open(R+'/SourceArt/CompactVillage/plan.json'));h=next(h for h in p['plots'] if h['id']=='G01');cam=dict(location=dict(x=h['center'][0],y=h['center'][1],z=g+5000),rotation=dict(pitch=-90,yaw=spec['yaw']+180,roll=0),scale=dict(x=1,y=1,z=1));v=call('CaptureViewport',dict(captureTransform=cam,annotations=None,bShowUI=False));open(Q+'/site_overview.png','wb').write(base64.b64decode(v['image']['data']));call('SetCameraTransform',dict(transform=preferred));print('Captured banya and both rooms')
