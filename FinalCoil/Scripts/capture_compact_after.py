import json,urllib.request,base64,sys
sys.path.insert(0,'D:/GameDevelop/FinalCoil/Scripts')
import terrain_profile as T
R='D:/GameDevelop/FinalCoil/Review/CompactVillage/after'
def req(body,sid=None):
 h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:h['Mcp-Session-Id']=sid
 with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8001/mcp',data=json.dumps(body).encode(),headers=h),timeout=180) as f:return json.load(f),f.headers.get('Mcp-Session-Id')
_,sid=req({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'StopCapture','version':'1'}}})
for i,(name,x,y,z,pitch,yaw) in enumerate([('overview',4500,2500,40000,-90,0),('same_scale',4500,2500,65000,-90,0),('centre',-3500,-4500,2200,-15,48),('hero',2200,11000,1700,-15,150),('centre_eye',-1300,-1700,0,-3,48),('hero_eye',2300,16400,0,-3,207)]):
 if name.endswith('_eye'):z=T.height(x,y)+165
 args={'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureViewport','arguments':{'captureTransform':{'location':dict(x=x,y=y,z=z),'rotation':dict(pitch=pitch,yaw=yaw,roll=0),'scale':dict(x=1,y=1,z=1)},'annotations':None,'bShowUI':False}}
 r,_=req({'jsonrpc':'2.0','id':i+2,'method':'tools/call','params':{'name':'call_tool','arguments':args}},sid)
 assert not r.get('result',{}).get('isError'),str(r)[:400]
 v=json.loads(r['result']['content'][0]['text'])['returnValue']
 open(R+'/'+name+'.png','wb').write(base64.b64decode(v['image']['data']))
print('CAPTURED 2')

