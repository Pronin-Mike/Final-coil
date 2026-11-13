"""Read-only review captures from the live editor MCP endpoint."""
import json,math,base64,urllib.request,os
R='D:/GameDevelop/FinalCoil';Q=R+'/Review/G01HouseV2';URL=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp');sid=None
def req(method,params):
 global sid
 h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:h['Mcp-Session-Id']=sid
 with urllib.request.urlopen(urllib.request.Request(URL,json.dumps(dict(jsonrpc='2.0',id=1,method=method,params=params)).encode(),h),timeout=180) as r:
  sid=r.headers.get('Mcp-Session-Id',sid);v=json.load(r)
 assert not v.get('error') and not v.get('result',{}).get('isError'),str(v)[:500]
 return v
def call(name,args):
 r=req('tools/call',dict(name='call_tool',arguments=dict(toolset_name='EditorToolset.EditorAppToolset',tool_name=name,arguments=args)));return json.loads(r['result']['content'][0]['text'])['returnValue']
req('initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='HouseV2Review',version='1')))
spec=json.load(open(R+'/SourceArt/G01HouseV2/house_spec.json'));cx,cy=spec['house_center'];a=math.radians(spec['yaw']);c,s=math.cos(a),math.sin(a);g=spec['ground_z']
def w(p):return [cx+c*p[0]-s*p[1],cy+s*p[0]+c*p[1],g+p[2]]
views=[('exterior',[1700,-1600,1150],[0,250,330]),('attached_garage',[1800,2100,1350],[0,350,300]),('porch_eye',[1100,-350,180],[480,0,210]),('living_room',[350,200,225],[-160,-160,160]),('garage_passage',[-100,145,225],[-100,390,25]),('loft',[250,250,525],[-50,-190,450]),('garage_gate',[1000,770,165],[0,770,100])]
for name,p,t in views:
 x,y,z=w(p);xx,yy,zz=w(t);cam=dict(location=dict(x=x,y=y,z=z),rotation=dict(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=dict(x=1,y=1,z=1))
 v=call('CaptureViewport',dict(captureTransform=cam,annotations=None,bShowUI=False));open(Q+'/'+name+'.png','wb').write(base64.b64decode(v['image']['data']))
 if name=='attached_garage':preferred=cam
call('SetCameraTransform',dict(transform=preferred));print('Captured',len(views),'house review views')
