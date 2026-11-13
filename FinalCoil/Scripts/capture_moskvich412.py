"""Capture the live editor through native MCP; run outside Unreal."""
import json,math,base64,urllib.request,os
def req(body,sid=None):
 headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:headers['Mcp-Session-Id']=sid
 url=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp')
 with urllib.request.urlopen(urllib.request.Request(url,json.dumps(body).encode(),headers),timeout=180) as response:
  return json.load(response),response.headers.get('Mcp-Session-Id')
Q='D:/GameDevelop/FinalCoil/Review/Moskvich412'
_,sid=req({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'MoskvichCapture','version':'1'}}})
p=json.load(open(Q+'/ue_placement.json'));cx,cy,z=p['position_cm'];a=math.radians(p['yaw_deg']);c,s=math.cos(a),math.sin(a)
for i,(name,dx,dy,dz) in enumerate([('ue_garage_final',340,-240,165),('ue_gate_eye',650,0,165)]):
 x,y=cx+c*dx-s*dy,cy+s*dx+c*dy
 camera=dict(location=dict(x=x,y=y,z=z+dz),rotation=dict(pitch=math.degrees(math.atan2(80-dz,math.hypot(dx,dy))),yaw=math.degrees(math.atan2(cy-y,cx-x)),roll=0),scale=dict(x=1,y=1,z=1))
 args=dict(toolset_name='EditorToolset.EditorAppToolset',tool_name='CaptureViewport',arguments=dict(captureTransform=camera,annotations=None,bShowUI=False))
 r,_=req(dict(jsonrpc='2.0',id=i+2,method='tools/call',params=dict(name='call_tool',arguments=args)),sid)
 assert not r.get('result',{}).get('isError'),str(r)[:400]
 v=json.loads(r['result']['content'][0]['text'])['returnValue'];open(Q+'/'+name+'.png','wb').write(base64.b64decode(v['image']['data']))
