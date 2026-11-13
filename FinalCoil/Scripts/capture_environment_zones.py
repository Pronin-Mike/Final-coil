"""MCP debug captures; restores all debug visibility to off in a finally block."""
from pathlib import Path
import os,json,urllib.request,base64,math
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'Review/EnvironmentZones';URL=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp');sid=None
def request(method,params):
 global sid
 headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:headers['Mcp-Session-Id']=sid
 with urllib.request.urlopen(urllib.request.Request(URL,json.dumps(dict(jsonrpc='2.0',id=1,method=method,params=params)).encode(),headers),timeout=180) as r:sid=r.headers.get('Mcp-Session-Id',sid);v=json.load(r)
 assert not v.get('error') and not v.get('result',{}).get('isError'),str(v)[:600]
 return v
request('initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='EnvironmentReview',version='1')))
def tool(ts,action,**kw):return json.loads(request('tools/call',dict(name='call_tool',arguments=dict(toolset_name=ts,tool_name=action,arguments=kw)))['result']['content'][0]['text'])['returnValue']
OBJECT='editor_toolset.toolsets.object.ObjectTools';ACTOR='editor_toolset.toolsets.actor.ActorTools';APP='EditorToolset.EditorAppToolset'
components=[];cell_components={}
for cell in json.loads((ROOT/'SourceArt/EnvironmentZones/zones.json').read_text())['test_cells']:
 actors=tool('editor_toolset.toolsets.scene.SceneTools','find_actors',name='ENV_Debug_'+cell['id'],tag='',collision_channels=[])
 cell_components[cell['id']]=[]
 for actor in actors:
  cell_components[cell['id']].extend(tool(ACTOR,'get_components',actor=actor,component_type=dict(refPath='/Script/Engine.HierarchicalInstancedStaticMeshComponent')))
 components.extend(cell_components[cell['id']])
for co in components[:1]:tool(OBJECT,'list_properties',instance=co)
def debug(visible,mode='Zones',names=None):
 for comp in components:
  # The owner actor name is not a stable label, so match via source-cell metadata below.
  show=visible and (names is None or comp['refPath'] in names)
  tool(OBJECT,'set_properties',instance=comp,values=json.dumps(dict(bVisible=show,overrideMaterials=[dict(refPath='/Game/FinalCoil/Environment/PCG/Debug/MI_Debug'+mode+'.MI_Debug'+mode)])))
def camera(p,t):
 x,y,z=p;xx,yy,zz=t;return dict(location=dict(x=x,y=y,z=z),rotation=dict(pitch=math.degrees(math.atan2(zz-z,math.hypot(xx-x,yy-y))),yaw=math.degrees(math.atan2(yy-y,xx-x)),roll=0),scale=dict(x=1,y=1,z=1))
def capture(name,p,t):
 cam=camera(p,t);tool(APP,'CaptureViewport',captureTransform=cam,annotations=None,bShowUI=False);v=tool(APP,'CaptureViewport',captureTransform=cam,annotations=None,bShowUI=False);(Q/(name+'.png')).write_bytes(base64.b64decode(v['image']['data']))
try:
 for mode in ['Zones','Exclusions','Slope','Wetness']:
  debug(True,mode,[c['refPath'] for c in cell_components['stop']]);capture('debug_'+mode.lower(),[9000,-9000,15000],[0,-1500,0])
 debug(True,'Zones',[c['refPath'] for c in cell_components['world_overview']]);capture('debug_world',[-250000,77333,310000],[46333,77333,0])
 debug(True,'Zones',[c['refPath'] for c in cell_components['forest_edge']]);capture('debug_forest_edge',[-17000,37000,16000],[-14000,29500,0])
finally:
 debug(False)
print('Environment debug captures saved; debug disabled')
