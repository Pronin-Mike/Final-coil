"""Capture banya exterior, both rooms and the requested site corner."""
import json,math,base64,urllib.request,os
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/G01Fence';URL=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp');sid=None
def req(method,params):
 global sid
 h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:h['Mcp-Session-Id']=sid
 with urllib.request.urlopen(urllib.request.Request(URL,json.dumps(dict(jsonrpc='2.0',id=1,method=method,params=params)).encode(),h),timeout=180) as r:sid=r.headers.get('Mcp-Session-Id',sid);v=json.load(r)
 assert not v.get('error') and not v.get('result',{}).get('isError'),str(v)[:400]
 return v
def call(name,args):return json.loads(req('tools/call',dict(name='call_tool',arguments=dict(toolset_name='EditorToolset.EditorAppToolset',tool_name=name,arguments=args)))['result']['content'][0]['text'])['returnValue']
req('initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='BanyaReview',version='1')))
spec=json.load(open(R+'/SourceArt/G01Fence/fence_spec.json'));cx,cy=spec['center'];a=math.radians(spec['yaw']);c,s=math.cos(a),math.sin(a);g=28.71109662337
def w(p):return [cx+c*p[0]-s*p[1],cy+s*p[0]+c*p[1],g+p[2]]
gx,gy=spec['gate_center_local']
views=[('gate',[gx-1000,gy+1250,360],[gx+100,gy,95]),('yard',[-200,100,210],[gx,gy,100]),('overview',[0,0,4200],[0,0,0])]
for name,p,t in views:
 x,y,z=w(p);xx,yy,zz=w(t);cam=dict(location=dict(x=x,y=y,z=z),rotation=dict(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=dict(x=1,y=1,z=1));v=call('CaptureViewport',dict(captureTransform=cam,annotations=None,bShowUI=False));open(Q+'/'+name+'.png','wb').write(base64.b64decode(v['image']['data']))
 if name=='gate':preferred=cam
call('SetCameraTransform',dict(transform=preferred));print('Captured G01 fence')
